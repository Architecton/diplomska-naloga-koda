import os
import numpy as np
import scipy.io as sio

"""
Script that prints dimensionalities of datasets from selected folder of datasets.

Author: Jernej Vivod

"""

print("### Files In Current Folder ###")
for file_name in os.listdir():
    print(file_name)
print("###############################")
while True:
    selected_folder = input("Select datasets folder: ")
    try:
        for dirname in os.listdir(selected_folder):
            print("dataset {0}:".format(dirname))
            print(sio.loadmat("./final/" + dirname + "/data.mat")['data'].shape)
        break;
    except:
        print("No such datasets directory!")

