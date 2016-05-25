import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
import pickle
import os, sys
norm = np.linalg.norm

def get_matrix_from_url(url):
    import requests
    response = requests.get(url)
    d = eval(response.text)
    return np.array(d['features_all'])

results_file = "./2016-05-25/i_hats_['OFUL'].pkl"
results = pickle.load(open(results_file, 'rb'))

if not 'features_matrix.npy' in os.listdir():
    home_dir = '/Users/scott/'
    X = loadmat(home_dir + 'Dropbox/Public/features_allshoes_8_normalized.mat')
    X = X['features_all'].T
    X = np.save('features_matrix.npy', X)
else:
    X = np.load('features_matrix.npy')

x_star = X[:, results['i_star']].copy()
x_hats = X[:, results['i_hats']].copy()

diffs = np.array([x_star - x_hats[:, i] for i in range(x_hats.shape[1])])
norm_diffs = norm(diffs, axis=1)

plt.figure()
plt.plot(norm_diffs)
plt.show()
