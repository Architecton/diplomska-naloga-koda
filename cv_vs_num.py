import numpy as np
import scipy.io as sio

import os

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold

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

# constants
NUM_FEATURES_TO_SELECT_LIM = 300
NUM_RUNS_CV = 10
NUM_FOLDS_CV = 5
K_PARAM = 10

# Initialize classifier.
clf = KNeighborsClassifier(n_neighbors=5)

# Load data and target values.
data = sio.loadmat('./datasets/ecoli/data.mat')['data']
target = np.ravel(sio.loadmat('./datasets/ecoli/target.mat')['target'])

# Define RBAs to use.
rbas = {'ECReliefF' : ECRelieff(),
        #'SURF' : SURF(),
        #'SURF*' : SURFStar(),
        #'MultiSURF*' : MultiSURFStar(),
        #'MultiSURF' : MultiSURF(),
        #'BoostedSURF' : BoostedSURF(),
        }

# Initialize dictionary for storing results.
res_dict = dict.fromkeys(rbas.keys())
for key in res_dict.keys():
    res_dict[key] = np.empty(NUM_FEATURES_TO_SELECT_LIM, dtype=np.float)

# Go over RBAs.
for rba_name in rbas.keys():

    print("### Testing {0} ###".format(rba_name))

    # Initialize next pipeline.
    clf_pipeline = Pipeline([('scaling', StandardScaler()), ('rba', rbas[rba_name]), ('clf', clf)])
    
    # Go over values on x axis.
    for num_features_to_select in np.arange(1, NUM_FEATURES_TO_SELECT_LIM+1):

        print("{0}/{1}".format(num_features_to_select, NUM_FEATURES_TO_SELECT_LIM))

        # Set parameter.  
        clf_pipeline.set_params(rba__n_features_to_select=num_features_to_select)
        
        # Compute score of 10 runs of 10 fold cross-validation.
        score = np.mean(cross_val_score(clf_pipeline, data, target, 
                cv=StratifiedKFold(n_splits=NUM_FOLDS_CV, shuffle=True, random_state=1)))

        # Add computed CV score to vector of values in results dictionary.
        (res_dict[rba_name])[num_features_to_select-1] = score

# create .mat files in folders.
for key in res_dict.keys():
    # Create folder if it does not exist.
    if not os.path.isdir('./cv-vs-num-results'):
        os.mkdir('./cv-vs-num-results')
    
    # Save results matrix.
    sio.savemat('./cv-vs-num-results/' + key + '.mat', {key : res_dict[key]})

