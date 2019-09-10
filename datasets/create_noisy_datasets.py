import numpy as np
import os
import sys
import scipy.io as sio

"""
Script for adding noise features to datasets
"""

# proportion of noise features to add
PROP_ADDITIONAL_NOISE = 0.7

while True: 
    selected_folder = input("Select datasets folder: ")
    try:
        # Go over dataset folders.
        for dirname in os.listdir(sys.path[0] + '/' + selected_folder):
            # Ignore hidden folders.
            if '.' not in dirname:

                # Load data.
                data = sio.loadmat(sys.path[0] + '/' + selected_folder + '/' + dirname + '/data.mat')['data']
                target = sio.loadmat(sys.path[0] + '/' + selected_folder + '/' + dirname + '/target.mat')['target']

                # Generate noise features.
                min_features_val = np.min(data)
                max_features_val = np.max(data)
                add_noise = np.random.uniform(min_features_val, max_features_val, (data.shape[0], int(np.ceil(data.shape[1]*PROP_ADDITIONAL_NOISE))))

                # Add noise features and permute columns.
                data = np.hstack((data, add_noise))
                data = data[:, np.random.choice(data.shape[1], data.shape[1], replace=False)]

                # Save created dataset.
                os.system('mkdir ' + sys.path[0] + '/noisy/' + dirname)
                sio.savemat(sys.path[0] + '/noisy/' + dirname + '/data.mat', {'data' : data})
                sio.savemat(sys.path[0] + '/noisy/' + dirname + '/target.mat', {'target' : target})
        print("Success!")
        break;
    except:
        print("No such datasets folder!")

