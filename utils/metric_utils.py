import numpy as np
import sklearn.metrics

def rank(x,y, x_labels, y_labels):
    distances = sklearn.metrics.pairwise_distances(x,y,'euclidean')
    batch_size = x_labels.shape[0]
    sorted_distances_indices = np.argsort(distances, axis=1)
    labels_matrix = np.tile(x_labels, batch_size).reshape((batch_size, batch_size))
    retrived_labels = np.take(labels_matrix, sorted_distances_indices)
    labels_equal = np.equal(np.expand_dims(y_labels,axis=1), retrived_labels)
    rank = np.argmax(labels_equal.astype(float), axis=1) + 1
    return rank 