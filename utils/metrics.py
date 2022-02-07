import numpy as np 
from sklearn.metrics import pairwise_distances
import matplotlib.pyplot as plt

class NumpyMetrics():
    def __init__(self, metric='euclidean'):
        self.metric = metric

    def rank(self, x,y, x_labels, y_labels):
        distances = pairwise_distances(x,y,self.metric)
        batch_size = x_labels.shape[0]
        sorted_distances_indices = np.argsort(distances, axis=1)
        labels_matrix = np.tile(x_labels, batch_size).reshape((batch_size, batch_size))
        retrived_labels = np.take(labels_matrix, sorted_distances_indices)
        labels_equal = np.equal(np.expand_dims(y_labels,axis=1), retrived_labels)
        rank = np.argmax(labels_equal.astype(float), axis=1) + 1
        return rank 

    def elements_by_class(self, x_labels):
        '''Count the total of elements of each class in the eval set
        Return unique_labels -> A numpy array with the index of the labels
                count -> Number of elements of each class in the test set
        '''
        unique_labels = np.unique(x_labels) # Make and array of unique labels
        label_matrix = np.equal(np.expand_dims(unique_labels, axis=1), np.expand_dims(x_labels, axis=0)) #shape [No.classes,1],[1,Eval_size] -> [No_classes,Eval_size]
        count = label_matrix.sum(axis=1)
        return unique_labels,count
    
    def true_positives(self, distances, x_labels, y_labels, k):
        '''
        Find the k nearest y given x, then check if the label of y correnspond to x, and accumulate. 
        '''
        sorted_distances_indices = np.argsort(distances,axis=1) #
        batch_size = x_labels.shape[0]
        labels_matrix = np.tile(x_labels, batch_size).reshape((batch_size, batch_size)) # True label matrix
        retrieved_labels = np.take(labels_matrix,sorted_distances_indices)   #The sorted retrieved labels matrix
        labels_equal = np.equal(np.expand_dims(y_labels, axis=1), retrieved_labels) # Where the retrieved label == true label
        tp = np.sum(labels_equal[:,0:k], axis=1) # Aparece cuando debe aparecer
        return tp

    def false_negative(self, distances, x_labels, y_labels, k):
        sorted_distances_indices = np.argsort(distances,axis=1) #
        batch_size = x_labels.shape[0]
        labels_matrix = np.tile(x_labels, batch_size).reshape((batch_size, batch_size)) # True label matrix
        retrieved_labels = np.take(labels_matrix,sorted_distances_indices)   #The sorted retrieved labels matrix
        labels_equal = np.equal(np.expand_dims(y_labels, axis=1), retrieved_labels) # Where the retrieved label == true label
        fn = np.sum(labels_equal[:,k:], axis=1)
        return fn

    def false_positives(self, distances, x_labels, y_labels, k):
        'Estan y no deberian estar'
        sorted_distances_indices = np.argsort(distances,axis=1) #
        batch_size = x_labels.shape[0]
        labels_matrix = np.tile(x_labels, batch_size).reshape((batch_size, batch_size)) # True label matrix
        retrieved_labels = np.take(labels_matrix,sorted_distances_indices)   #The sorted retrieved labels matrix
        labels_equal = np.equal(np.expand_dims(y_labels, axis=1), retrieved_labels) # Where the retrieved label == true label
        labels_not_equal = np.logical_not(labels_equal)
        fp = np.sum(labels_not_equal[:,0:k], axis=1)
        return fp     

    def precision_at_k(self, x,y, x_labels, y_labels, k):
        ''' The ability of a classificator model to identify only the relevant points.
        Precision = true_positives /(true_positives + false_positives) '''
        distances = pairwise_distances(x,y,self.metric)
        tp = self.true_positives(distances, x_labels, y_labels, k)
        #fp = self.false_positives(distances, x_labels, y_labels, k)
        fn = self.false_negative(distances, x_labels, y_labels, k)
        fp = np.minimum(k - tp, fn)
        precision_at_k = tp / (tp + fp)
        return precision_at_k

    def recall_at_k(self, x, y, x_labels, y_labels, k):
        '''
        Percentage of total relevant results correctly classified by the algorithm
        The ability of a model to find all relevant cases within a dataset.
        Recall = true_positives / (true_positives + false_negatives)
        The ability of the model to retrieve a relevenat pair of one domain given a query of the other domain
        '''
        distances = pairwise_distances(x,y,self.metric)
        tp = self.true_positives(distances, x_labels, y_labels, k)
        fn = self.false_negative(distances, x_labels, y_labels, k) 
        fn = np.minimum(fn,k-tp)
        recall_at_k = tp / (tp + fn)
        return recall_at_k  


    def average_rank_at_k(self, x, y, labels):
        rank = self.rank(x,y,labels, labels)
        for k in [1,5,10,20,50,100,500,5000]:
            percentage = (rank <= k).sum() / x.shape[0]
            print(' Top {:.3f}, {:.3f}'.format(k,percentage))

    def rank_curve(self, x, y, labels):
        rank = self.rank(x,y,labels,labels)
        print("Average rank", rank.mean())
        count_percentage = np.zeros((x.shape[0]), dtype=float)
        for i in range(x.shape[0]):
            count_percentage[i] = (rank <= i+1).sum() / x.shape[0]
        plt.plot(count_percentage)
        plt.show() 
        plt.waitforbuttonpress()

    