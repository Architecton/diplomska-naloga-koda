import numpy as np
import pandas as pd
import scipy.io as sio

from collections import namedtuple, OrderedDict

import os
import sys
import pickle as pkl

from algorithms.relief import Relief
from algorithms.relieff import Relieff
from algorithms.reliefmss import ReliefMSS
from algorithms.reliefseq import ReliefSeq
from algorithms.turf import TuRF
from algorithms.vlsrelief import VLSRelief
from algorithms.iterative_relief import IterativeRelief
from algorithms.irelief import IRelief
from algorithms.boostedsurf2 import BoostedSURF
from algorithms.ecrelieff import ECRelieff
from algorithms.multisurf2 import MultiSURF
from algorithms.multisurfstar2 import MultiSURFStar
from algorithms.surf import SURF
from algorithms.surfstar import SURFStar
from algorithms.swrfstar import SWRFStar

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.model_selection import RepeatedKFold

"""
Algorithm evaluations script.

This script produces the scores matrices needed for performing the Bayesian hierarchical correlated t-test.
The results are saved in child 'evaluation_results' folder.

Author: Jernej Vivod

"""

# Set number of CV folds and runs.
NUM_FOLDS_CV = 10
NUM_RUNS_CV = 10
RATIO_FEATURES_TO_SELECT = 0.25

# Set default value for parameter k - number of nearest misses to find (needed for a subset of implemented algorithms).
PARAM_K = 10

# Define named tuple for specifying names of compared algorithms and the scores matrix of comparisons.
comparePair = namedtuple('comparePair', 'algorithm1 algorithm2 scores')

### UNCOMMENT TO USE LEARNED METRIC FUNCTION ###
# SIMILAR FOR OTHER METRIC FUNCTION (see ./algorithms/augmentations)

# get_dist_func = jl.include(script_path[:script_path.rfind('/')] + "/algorithms/augmentations/me_dissim.jl")
# 
# # Get learned metric function.
# num_itrees = 10
# produce_learned_metric_func = lambda x, _ : get_dist_func(num_itrees, x)

# Specifiy RBAs to compare (filled with example values).
GROUP_TAG = "iterative"  # Results tag
algs = OrderedDict([
    ('iterative_relief',IterativeRelief(max_iter=70)),
    ('I-RELIEF', IRelief(max_iter=70))
])

# Initialize classifier.
clf = KNeighborsClassifier(n_neighbors=3)

# Set path to datasets folder.
data_dirs_path = os.path.dirname(os.path.realpath(__file__)) + '/datasets/' + 'selected'

# Count datasets and allocate array for results.
num_datasets = len(os.listdir(data_dirs_path))

# Initialize dictionaries for storing results and results counter.
results = dict()
results_count = 0

# Go over all pairs of algorithms (iterate over indices in ordered dictionary).
num_algs = len(algs.keys())
for idx_alg1 in np.arange(num_algs-1):
    for idx_alg2 in np.arange(idx_alg1+1, num_algs):

        # Initialize results matrix and results tuple.
        results_mat = np.empty((num_datasets, NUM_FOLDS_CV*NUM_RUNS_CV), dtype=np.float)
        nxt = comparePair(list(algs.keys())[idx_alg1], list(algs.keys())[idx_alg2], results_mat)
      
        # Initialize pipelines for evaluating algorithms.
        clf_pipeline1 = Pipeline([('scaling', StandardScaler()), ('rba1', algs[nxt.algorithm1]), ('clf', clf)])
        clf_pipeline2 = Pipeline([('scaling', StandardScaler()), ('rba2', algs[nxt.algorithm2]), ('clf', clf)])

        print("### COMPARING {0} and {1} ###".format(nxt.algorithm1, nxt.algorithm2))
       
        # Initialize row index counter in scores matrix.
        scores_row_idx = 0

        # Go over dataset directories in direstory of datasets.
        for idx_dataset, dirname in enumerate(os.listdir(data_dirs_path)):

            # Load data and target matrices.
            data = sio.loadmat(data_dirs_path + '/' + dirname + '/data.mat')['data']
            target = np.ravel(sio.loadmat(data_dirs_path + '/' + dirname + '/target.mat')['target'])

            # Select number of features to select.
            num_features_to_select = min(max(2, np.int(np.ceil(RATIO_FEATURES_TO_SELECT*data.shape[1]))), 100)
            clf_pipeline1.set_params(rba1__n_features_to_select=num_features_to_select)
            clf_pipeline2.set_params(rba2__n_features_to_select=num_features_to_select)

            print("performing {0} runs of {1}-fold cross validation on dataset '{2}' " \
                    "(dataset {3}/{4}).".format(NUM_RUNS_CV, NUM_FOLDS_CV, dirname, idx_dataset+1, num_datasets))
            print("Selecting {0}/{1} features.".format(num_features_to_select, data.shape[1]))

            # Get scores for first algorithm (create pipeline).
            scores1_nxt = cross_val_score(clf_pipeline1, data, target, 
                    cv=RepeatedKFold(n_splits=NUM_FOLDS_CV, n_repeats=NUM_RUNS_CV, random_state=1), verbose=1, n_jobs=-1)

            # Get scores for second algorithm (create pipeline).
            scores2_nxt = cross_val_score(clf_pipeline2, data, target, 
                    cv=RepeatedKFold(n_splits=NUM_FOLDS_CV, n_repeats=NUM_RUNS_CV, random_state=1), verbose=1, n_jobs=-1)

            # Compute differences of scores.
            res_nxt = scores1_nxt - scores2_nxt

            # Add row of scores to results matrix.
            nxt.scores[scores_row_idx, :] = res_nxt

            print("Testing on the '{0}' dataset finished".format(dirname))
           
            # Increment row index counter.
            scores_row_idx += 1

        # Save data structure containing results to results dictionary and increment results index counter.
        results[results_count] = nxt
        results_count += 1

# Save results to file.
script_path = os.path.abspath(__file__)
script_path = script_path[:script_path.rfind('/')]
with open(script_path + "/evaluation_results/results_group_" + str(GROUP_TAG) + ".p", "wb") as handle:
    pkl.dump(results, handle)

