import numpy as np
from scipy.stats import rankdata
from functools import partial
from nptyping import Array
from sklearn.metrics import pairwise_distances
from sklearn.base import BaseEstimator, TransformerMixin

class BoostedSURF(BaseEstimator, TransformerMixin):

    """sklearn compatible implementation of the boostedSURF algorithm
        
    Gediminas Bertasius, Delaney Granizo-Mackenzie, Ryan Urbanowicz, Jason H. Moore.
    Boosted Spatially Uniform ReliefF Algorithm for Genome-Wide Genetic Analysis.

    author: Jernej Vivod

    """

    def __init__(self, n_features_to_select=10, phi=5, 
            dist_func=lambda w, x1, x2: np.sum(w*np.logical_xor(x1, x2), 1), learned_metric_func=None):

        self.n_features_to_select = n_features_to_select  # Number of features to select.
        self.phi = phi                                    # the phi parameter (update weights when iteration_counter mod phi == 0)
        self.dist_func = dist_func                        # Distance function to use.
        self.learned_metric_func = learned_metric_func    # learned metric function.


    def fit(self, data, target):

        """
        Rank features using BoostedSURF feature selection algorithm

        Args:
            data : Array[np.float64] -- matrix of examples
            target : Array[np.int] -- vector of target values of examples

        Returns:
            self
        """

        # Run Boosted SURF feature selection algorithm.
        if self.learned_metric_func != None:
            self.rank, self.weights = self._boostedSURF(data, target, self.phi, self.dist_func, 
                    learned_metric_func=self.learned_metric_func(data, target))
        else:
            self.rank, self.weights = self._boostedSURF(data, target, self.phi, self.dist_func)

        return self


    def transform(self, data):

        """
        Perform feature selection using computed feature ranks

        Args:
            data : Array[np.float64] -- matrix of examples on which to perform feature selection

        Returns:
            Array[np.float64] -- result of performing feature selection
        """

        msk = self.rank <= self.n_features_to_select  # Compute mask.
        return data[:, msk]  # Perform feature selection.


    def fit_transform(self, data, target):

        """
        Compute ranks of features and perform feature selection
        Args:
            data : Array[np.float64] -- matrix of examples on which to perform feature selection
            target : Array[np.int] -- vector of target values of examples

        Returns:
            Array[np.float64] -- result of performing feature selection
        """

        self.fit(data, target)
        return self.transform(data)


    def _boostedSURF(self, data, target, phi, dist_func, **kwargs):

        """Compute feature scores using boostedSURF algorithm

        Args:
            data : Array[np.float64] -- Matrix containing examples' data as rows
            target : Array[np.int] -- matrix containing the example's target variable value
            phi: int -- parameter specifying number of iterations before recomputing distance weights
            dist_func : Callable[[Array[np.float64], Array[np.float64]], Array[np.float64]] -- function for evaluating
            distances between examples. The function should acept two examples or two matrices of examples and return the dictances.
            **kwargs: can contain argument with key 'learned_metric_func' that maps to a function that accepts a distance
            function and indices of two training examples and returns the distance between the examples in the learned
            metric space.

        Returns:
            Array[np.int], Array[np.float64] -- Array of feature enumerations based on the scores, array of feature scores

        """
        
        # Initialize distance weights.
        dist_weights = np.ones(data.shape[1], dtype=np.float)

        # weighted distance function
        dist_func_w = partial(dist_func, dist_weights)

        # Initialize weights.
        weights = np.zeros(data.shape[1], dtype=np.int)

        for idx in np.arange(data.shape[0]):
            
            # Recompute distance matrix.
            if np.mod(idx, phi) == 0:
                dist_weights = np.maximum(weights, np.ones(data.shape[1], dtype=np.float))
                dist_func_w = partial(dist_func, dist_weights)
                if 'learned_metric_func' in kwargs:
                    dist_func_w_learned = partial(kwargs['learned_metric_func'], dist_func_w)
           

            # Compute distances from current examples to all other examples.
            if 'learned_metric_func' in kwargs:
                dists = dist_func_w_learned(idx, np.arange(data.shape[0]))
            else:
                dists = dist_func_w(data[idx, :], data)


            # Compute mean and standard deviation of distances and set thresholds.
            t_next = np.mean(dists[np.arange(data.shape[0]) != idx])
            sigma_nxt = np.std(dists[np.arange(data.shape[0]) != idx])
            thresh_near = t_next - sigma_nxt/2.0
            thresh_far = t_next + sigma_nxt/2.0

            # Get mask of examples that are close.
            msk_close = dists < thresh_near
            msk_close[idx] = False

            # Get mask of examples that are far.
            msk_far = dists > thresh_far

            # Get examples that are close.
            examples_close = data[msk_close, :]
            target_close = target[msk_close]
            
            # Get examples that are far.
            examples_far = data[msk_far, :]
            target_far = target[msk_far]

            # Get considered features of close examples.
            features_close = data[idx, :] != examples_close
            # Get considered features of far examples.
            features_far = data[idx, :] == examples_far 

            # Get mask for close examples with same class.
            msk_same_close = target_close == target[idx]

            # Get mask for far examples with same class.
            msk_same_far = target_far == target[idx]


            ### WEIGHTS UPDATE ###

            # Get penalty weights update values for close examples. 
            wu_close_penalty = np.sum(features_close[msk_same_close, :], 0)
            # Get reward weights update values for close examples. 
            wu_close_reward = np.sum(features_close[np.logical_not(msk_same_close), :], 0)

            # Get penalty weights update values for far examples.
            wu_far_penalty = np.sum(features_far[msk_same_far, :], 0)
            # Get reward weights update values for close examples. 
            wu_far_reward = np.sum(features_far[np.logical_not(msk_same_far), :], 0)

            # Update weights.
            weights = weights - (wu_close_penalty + wu_far_penalty) + (wu_close_reward + wu_far_reward)

            ### /WEIGHTS UPDATE ###


        # Create array of feature enumerations based on score.
        rank = rankdata(-weights, method='ordinal')
        return rank, weights

