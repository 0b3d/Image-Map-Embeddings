import torch
import torch.nn as nn

class softTriplet(nn.Module):
    def __init__(self, alpha, squared, device):
        super(softTriplet, self).__init__()
        self.alpha = alpha
        self.squared = squared
        self.device = device

    def _pairwise_distances(self, X,Y):
        dot_product = torch.matmul(X,torch.t(Y))
        X_norm = torch.norm(X,p=2, dim=1, keepdim=True)
        Y_norm = torch.norm(Y,p=2, dim=1, keepdim=True)
        # Compute the pairwise distance matrix as we have:
        # ||a - b||^2 = ||a||^2  - 2 <a, b> + ||b||^2
        # shape (batch_size, batch_size)
        distances = torch.pow(X_norm,2) - 2.0 * dot_product + torch.pow(torch.t(Y_norm),2)
        # Because of computation errors, some distances might be negative so we put everything >= 0.0
        distances = torch.max(distances, torch.zeros_like(distances))

        if not self.squared:
            # Because the gradient of sqrt is infinite when distances == 0.0 (ex: on the diagonal)
            # we need to add a small epsilon where distances == 0.0
            mask = torch.eq(distances, 0.0).float()

            distances = distances + mask * 1e-16
            distances = torch.sqrt(distances)

            # # Correct the epsilon added: set the distances on the mask to be exactly 0.0
            distances = distances * (1.0 - mask)
        return distances

    def _get_same_label_mask(self, labels):
        """Return a 2D mask where mask[a, p] is True if a and p have same label.
        Args:
            labels: tf.int32 `Tensor` with shape [batch_size]
        Returns:
            mask: tf.bool `Tensor` with shape [batch_size, batch_size]
        """
        labels = labels.expand(labels.shape[0],labels.shape[0])
        labels_equal = torch.eq(labels, labels.t())
        return labels_equal

    def _get_anchor_positive_triplet_mask(self, labels):
        """Return a 2D mask where mask[a, p] is True iff a and p are distinct and have same label.
        Args:
            labels: tf.int32 `Tensor` with shape [batch_size]
        Returns:
            mask: tf.bool `Tensor` with shape [batch_size, batch_size]
        """
        indices_equal = torch.eye(labels.size()[0], device=self.device).byte() # There is going to be an issue here in a future
        indices_not_equal = ~ indices_equal
        labels_equal = self._get_same_label_mask(labels)
        mask = indices_not_equal & labels_equal
        return mask

    def _get_anchor_negative_triplet_mask(self, labels):
        """Return a 2D mask where mask[a, n] is True iff a and n have distinct labels.
        Args:
            labels: tf.int32 `Tensor` with shape [batch_size]
        Returns:
            mask: tf.bool `Tensor` with shape [batch_size, batch_size]
        """
        # Check if labels[i] != labels[k]
        # Uses broadcasting where the 1st argument has shape (1, batch_size) and the 2nd (batch_size, 1)
        labels_equal = self._get_same_label_mask(labels)
        mask = ~ labels_equal
        return mask

    def _get_X_Y_triplet_mask(self, labels):
        """Return a 3D mask where mask[a, p, n] is True if the triplet (a, p, n) is valid.
        Triplet (Xi, Yj, Yk) is valid if:
            labels[i] == labels[j] and labels[i] != labels[k]
        Args:
            labels: tf.int32 `Tensor` with shape [batch_size]
        """
        same_label_mask = self._get_same_label_mask(labels)
        li_equal_lj = same_label_mask.expand(1,labels.size()[0], labels.size()[0]).permute(2,1,0) 
        lj_not_equal_lk = ~ li_equal_lj.permute(2,1,0)
        valid_triplet_mask = li_equal_lj & lj_not_equal_lk
        return valid_triplet_mask

    def _get_triplet_mask(self, labels):
        """Return a 3D mask where mask[a, p, n] is True if the triplet (a, p, n) is valid.
        Triplet (Xi, Xj, Xk) is valid if:
            i != j != k
            labels[i] == labels[j] and labels[i] != labels[k]
        Args:
            labels: tf.int32 `Tensor` with shape [batch_size]
        """
        # Indices mask
        i_not_equal_j = ~torch.eye(labels.size()[0], device=self.device).expand(labels.size()[0],labels.size()[0],labels.size()[0]).bool().permute(2,1,0)
        # Labels mask
        same_label_mask = self._get_same_label_mask(labels)
        li_equal_lj = same_label_mask.expand(1,labels.size()[0], labels.size()[0]).permute(2,1,0) 
        lj_not_equal_lk = ~li_equal_lj.permute(2,1,0)
        valid_triplet_mask = (li_equal_lj & lj_not_equal_lk) & i_not_equal_j
        return valid_triplet_mask

    def batchall(self, X,labels,final_strategy):
        pairwise_dist = self._pairwise_distances(X,X).expand(1,labels.size()[0],labels.size()[0]) 
        # Compute a tensor with all the posible triplets
        anchor_positive_dist = pairwise_dist.permute(1,2,0) #[4,4,1]
        anchor_negative_dist = pairwise_dist.permute(1,0,2)
        # triplet_loss[i, j, k] will contain the triplet loss of anchor=i, positive=j, negative=k
        triplet_loss_tensor = torch.log( 1 + torch.exp( self.alpha * (anchor_positive_dist - anchor_negative_dist)))
        triplet_loss = torch.mul(triplet_loss_tensor, self._get_triplet_mask(labels).float())

        # Count the number of valid triplets (where triplet loss> 0)
        valid_triplets = torch.gt(triplet_loss,1e-16).sum()
        # Get the final mean triplet loss over all valid triplets

        if final_strategy == "mean":
            loss = triplet_loss.sum() / (valid_triplets + 1e-16)
            return loss
        elif final_strategy is "mean_all":
            loss = triplet_loss.mean()
            return loss
        elif final_strategy is "sum":
            loss = triplet_loss.sum()
            return loss
        else:
            print("Final strategy not found")

    def batch_all_X_Y(self, X, Y, labels,final_strategy):
        pairwise_dist = self._pairwise_distances(X,Y).expand(1, labels.size(0), labels.size(0))
        # Compute a tensor with all the posible triplets
        anchor_positive_dist = pairwise_dist.permute(1,2,0) #[4,4,1]
        anchor_negative_dist = pairwise_dist.permute(1,0,2)
        # triplet_loss[i, j, k] will contain the triplet loss of anchor=i, positive=j, negative=k
        triplet_loss_tensor = torch.log(1 + torch.exp( self.alpha * (anchor_positive_dist - anchor_negative_dist)))
        triplet_loss = torch.mul(triplet_loss_tensor, self._get_X_Y_triplet_mask(labels).float())
        # Count the number of valid triplets (where triplet loss> 0)
        valid_triplets = torch.gt(triplet_loss,1e-16).sum()
        # Get the final mean triplet loss over all valid triplets
        if final_strategy == "mean":
            loss = triplet_loss.sum() / (valid_triplets + 1e-16)
            return loss
        elif final_strategy is "mean_all":
            loss = triplet_loss.mean()
            return loss
        elif final_strategy is "sum":
            loss = triplet_loss.sum()
            return loss
        else: 
            print("Final strategy not found")

    def batch_hard_X_Y(self, X, Y, labels):
        pairwise_distances = self._pairwise_distances(X,Y)
        # Valid anchor positives x-y have same label
        anchor_positive_distance = torch.mul(pairwise_distances, self._get_same_label_mask(labels).float())
        hardest_positive_distance, _ = torch.max(anchor_positive_distance, dim=1)
        
        # Valid anchor negatives x-y have different label
        anchor_negative_distance = torch.mul(pairwise_distances, 1.0 - self._get_anchor_negative_triplet_mask(labels).float())
        max_anchor_negative_dist, _ = torch.max(pairwise_distances, dim=1, keepdim=True)
        anchor_negative_dist = pairwise_distances + max_anchor_negative_dist * self._get_anchor_positive_triplet_mask(labels).float()
        hardest_negative_distance, _ = torch.min(anchor_negative_dist, dim=1, keepdim=True)

        triplet_loss = (hardest_positive_distance - hardest_negative_distance).mean()
        triplet_loss = torch.log( 1 + torch.exp( self.alpha * (   (hardest_positive_distance - hardest_negative_distance).mean()   )))
        return triplet_loss

    def batch_hard(self, X, labels):
        pairwise_distances = self._pairwise_distances(X,X)
        # Valid anchor positives have same label and i != j
        anchor_positive_distance = torch.mul(pairwise_distances, self._get_anchor_positive_triplet_mask(labels).float())
        hardest_positive_distance, _ = torch.max(anchor_positive_distance, dim=1)
        
        # Valid anchor negatives x-y have different label
        anchor_negative_distance = torch.mul(pairwise_distances, 1.0 - self._get_anchor_negative_triplet_mask(labels).float())
        max_anchor_negative_dist, _ = torch.max(pairwise_distances, dim=1, keepdim=True)
        anchor_negative_dist = pairwise_distances + max_anchor_negative_dist * self._get_anchor_positive_triplet_mask(labels).float()
        hardest_negative_distance, _ = torch.min(anchor_negative_dist, dim=1, keepdim=True)
        triplet_loss = torch.log( 1 + torch.exp( self.alpha * (   (hardest_positive_distance - hardest_negative_distance).mean()   )))

        return triplet_loss

class SoftTripletLoss(softTriplet):
    def __init__(self, cfg, device):
        super(SoftTripletLoss, self).__init__(cfg.alpha, False, device)
        self.cfg = cfg
        self.device = device

    def batch_all(self, X,Y,Labels, final_strategy):
        l1 = super().batch_all_X_Y(X,Y,Labels,final_strategy)
        l2 = super().batch_all_X_Y(Y,X,Labels,final_strategy)
        l3 = super().batchall(X,Labels,final_strategy) 
        l4 = super().batchall(Y,Labels,final_strategy)               
        return l1, l2, l3, l4  

    def batch_hard(self, X,Y,Labels, final_strategy):
        l1 = super().batch_hard_X_Y(X,Y,Labels) 
        l2 = super().batch_hard_X_Y(Y,X,Labels) 
        l3 = super().batch_hard(X,Labels) 
        l4 = super().batch_hard(Y,Labels)               
        return l1, l2, l3, l4  


