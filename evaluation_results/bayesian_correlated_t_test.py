import numpy as np
import matplotlib.pyplot as plt
import glob
import pickle as pkl
from collections import namedtuple
import bayesiantests as bt
import matplotlib.pyplot as plt
import seaborn as snb
import scipy.io as sio


# Define named tuple that was used to store results.
comparePair = namedtuple('comparePair', 'algorithm1 algorithm2 scores')

# Load accuracies (filled with example values).
acc1 = np.ravel(sio.loadmat('irelief.mat')['res'])         # pleft
acc2 = np.ravel(sio.loadmat('iterative_relief.mat')['res'])     # pright

# names (filled with example values)
names = ("I-RELIEF", "Iterativni Relief")

# Comput differences vector.
diff_vec = acc2 - acc1

# Set rope values
rope=0.01
pleft, prope, pright = bt.correlated_ttest(diff_vec, rope=rope, runs=10, verbose=True, names=names)
with open('results_bctt.res', 'a') as f:
    f.write('{0}, {1}, {2}, {3}, {4}\n'.format(names[0], names[1], pleft, prope, pright))


# generate samples from posterior (it is not necesssary because the posterior is a Student)
samples=bt.correlated_ttest_MC(diff_vec, rope=rope, runs=10, nsamples=50000)

# plot posterior
snb.kdeplot(samples, shade=True)

# plot rope region
plt.axvline(diff_vec=-rope,color='orange')
plt.axvline(diff_vec=rope,color='orange')

# add label
plt.xlabel('Iterativni Relief - I-RELIEF')

# Show plot.
plt.show()

