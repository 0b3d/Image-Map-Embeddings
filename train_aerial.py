import tensorflow as tf
import tensorboard as tb
tf.io.gfile = tb.compat.tensorflow_stub.io.gfile

import os
import sys
import time 
import torch
import random
import numpy as np
from argparse import Namespace

from options.train_options import TrainOptions
from data import create_dataset
from models import create_model
from torch.utils.tensorboard import SummaryWriter
from utils.metrics import NumpyMetrics


def evaluate_batch(model, dataset, opt, writer, total_iters):
    model.eval()
    idx = random.randint(0,len(dataset)-1)
    data = next(iter(dataset))
    n = opt.batch_size * opt.num_augmentations
    
    with torch.no_grad():
        model.set_input(data)  
        model.forward()
        x = model.X_o.cpu().data.numpy()
        y = model.Y_o.cpu().data.numpy()
        labels = model.labels.cpu().data.numpy()
    
    recall = metrics.recall_at_k(y,x,labels,labels,opt.num_augmentations).mean()

    # prepare batch embedding for visualization
    if total_iters < 100 or total_iters % opt.save_epoch_freq == 0:
        data = np.concatenate((x,y),axis=0)
        labels = list(labels) * 2
        domain = ['x'] * n + ['y'] * n
        meta = [str(d)+str(l) for d,l in zip(domain,labels)]
        writer.add_embedding(data,metadata=meta, tag='batch_embedding', global_step=total_iters)
    
    model.train()
    
    return recall

def evaluate_epoch(model, dataset, opt, writer, epoch):
    print("Evaluating model ... ")
    model.eval()
    n = len(dataset) * opt.num_augmentations
    X = np.zeros((n,opt.embedding_dim))
    Y = np.zeros((n,opt.embedding_dim))
    Labels = np.zeros((n))

    # predict descriptors
    with torch.no_grad():
        for i, data in enumerate(dataset):
            model.set_input(data)  # unpack data from data loader
            k1 = opt.batch_size*opt.num_augmentations
            model.forward()
            x = model.X_o.cpu().data.numpy()
            y = model.Y_o.cpu().data.numpy()
            labels = model.labels.cpu().data.numpy()
            
            k2 = x.shape[0]
            X[i*k1:(i*k1+k2),:] = x
            Y[i*k1:(i*k1+k2),:] = y
            Labels[i*k1:(i*k1+k2)] = labels
            if i % 1000:
                print("Number of locations processed: ", i ,end='\r')

    rank = metrics.rank(Y,X,Labels,Labels)
    recall = (rank <= int(n*0.01)).sum() / n
    print('Recall: {:3f}'.format(recall))

    data = np.concatenate((Y,X),axis=0)
    labels = list(Labels) * 2   
    domain = ['x'] * n + ['y'] * n
    meta = [str(d)+str(l) for d,l in zip(domain,labels)]
    writer.add_embedding(data,metadata=meta, tag='epoch_embedding', global_step=epoch)

    model.train()
    return recall        

if __name__ == '__main__':
    
    opt = TrainOptions().parse()   
    dataset = create_dataset(opt) 
    dataset_size = len(dataset)     
    print('The number of training images = %d' % dataset_size)

    # Create a dataset for running evaluation 
    eval_opt = Namespace(**vars(opt))
    eval_opt.isTrain = False 
    eval_opt.drop_last = True
    eval_opt.flips = False
    eval_opt.preprocess = 'normalize'
    eval_opt.tile_zoom = [18]
    eval_opt.N = 5000

    eval_dataset = create_dataset(eval_opt)
    print('The number of training images = %d' % len(eval_dataset))

    # Create a dataset for epoch evaluation
    epoch_eval_opt = Namespace(**vars(eval_opt))
    epoch_eval_opt.num_augmentations = 1
    epoch_eval_opt.drop_last = True
    epoch_eval_opt.no_shifts = True
    epoch_eval_opt.no_rotations = True

    epoch_eval_dataset = create_dataset(epoch_eval_opt)
    print('The number of training images = %d' % len(epoch_eval_dataset))

    # Tensorboard writer
    logdir = os.path.join(opt.checkpoints_dir,opt.name,'metadir')
    writer = SummaryWriter(log_dir=logdir)

    # Initialize loss log file
    log_name = os.path.join(opt.checkpoints_dir, opt.name, 'loss_log.txt')
    with open(log_name, "a") as log_file:
        now = time.strftime("%c")
        log_file.write('================ Training Loss (%s) ================\n' % now)

    if opt.show_dataset:
        print("Examples in train dataset")
        dataset.dataset.show_dataset(5) 
        print("Examples in batch validation dataset")
        eval_dataset.dataset.show_dataset(5)
        print("Epoch in epoch validation dataset")
        epoch_eval_dataset.dataset.show_dataset(5) 
        sys.exit()

    # Create model
    model = create_model(opt)
    model.setup(opt)
    total_iters = model.total_iters               
    epoch_iter = model.epoch_iters                
    t_data = 0
    old_recall = 0.0 if model.metric_value is None else model.metric_value
    
    # define metrics
    metrics = NumpyMetrics()

    # ----- Epoch loop ----------------
    
    for epoch in range(opt.epoch_count, opt.n_epochs + opt.n_epochs_decay + 1):    
        epoch_start_time = time.time()  
        iter_data_time = time.time()    
        iters_per_epoch = int(len(dataset)/opt.batch_size)
        if not opt.drop_last:
            iters_per_epoch += 1 

        for i, data in enumerate(dataset): 
            iter_start_time = time.time()  
            if total_iters % opt.print_freq == 0:
                t_data = iter_start_time - iter_data_time

            
            total_iters += 1 
            epoch_iter += 1
            model.set_input(data)         
            model.optimize_parameters()   

            if total_iters % opt.display_freq == 0:   
                model.compute_visuals(writer, total_iters)
                
                # Evaluate on train (batch)
                x = model.X_o.detach().cpu().data.numpy()
                y = model.Y_o.detach().cpu().data.numpy()
                labels = model.labels.detach().cpu().data.numpy()
                batch_train_recall = metrics.recall_at_k(y,x,labels,labels,opt.num_augmentations).mean()

                # Evaluate on val (batch)
                batch_eval_recall = evaluate_batch(model, eval_dataset, eval_opt, writer, total_iters)
                writer.add_scalars('recall',{'train': batch_train_recall, 'val':batch_eval_recall},total_iters)
                
            if total_iters % opt.print_freq == 0:    
                losses = model.get_current_losses()
                t_comp = (time.time() - iter_start_time) / opt.batch_size
                message = '(epoch: %d, iters: %d, time: %.3f, data: %.3f) ' % (epoch,total_iters,t_comp, t_data)
                data = {'date':time.strftime("%d/%m/%Y %H:%M:%S"),'epoch':epoch, 'iters':total_iters, 'time': t_comp, 'data':t_data}
                
                for k, v in losses.items():
                    message += '%s: %.6f ' % (k, v)
                    data[k] = v

                print(message)  
                
                with open(log_name, "a") as log_file:
                    log_file.write('%s\n' % message)  # save the message
                
                writer.add_scalars('loss',losses, total_iters)
            
            if total_iters % opt.save_latest_freq == 0:   # Save latest net
                print('saving the latest model (epoch %d, total_iters %d)' % (epoch, total_iters))
                save_suffix = 'iter_%d' % total_iters if opt.save_by_iter else 'latest'
                model.save_networks(save_suffix, epoch, epoch_iter, total_iters, metric_value=None)
                
            iter_data_time = time.time()
        
        if epoch % opt.save_epoch_freq == 0:  
            recall = evaluate_epoch(model, epoch_eval_dataset, epoch_eval_opt, writer, epoch) 
            writer.add_scalar('epoch_recall', recall, total_iters)

            model.save_networks(epoch, epoch, epoch_iter, total_iters, metric_value=recall)
            model.save_networks('latest', epoch, epoch_iter, total_iters, metric_value=recall)

            if recall > old_recall:
                print('saving the model at the end of epoch %d, iters %d' % (epoch, total_iters))
                model.save_networks('best', epoch, epoch_iter, total_iters, metric_value=recall)
                model.metric_value = recall
                old_recall = recall 

        print('End of epoch %d / %d \t Time Taken: %d sec' % (epoch, opt.n_epochs + opt.n_epochs_decay, time.time() - epoch_start_time))
        model.update_learning_rate()                     
        epoch_iter = 0                                   
    
    writer.close()
