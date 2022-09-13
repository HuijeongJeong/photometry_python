from functions.load import *
from functions.plot import *
from functions.photometry import *
import matplotlib.pyplot as plt
import os.path
import numpy as np

#directory = 'D:/OneDrive - UCSF/Huijeong'
directory = 'D:/OneDrive - University of California, San Francisco/Huijeong'
mouselist = ['HJ_FP_WT_stGtACR_M3']
foldername = 'pavlovian'
daylist = []


lickindex = 5
cs1index = 15

window = [0,3000]
clr = ['black']


for mousename in mouselist:
    matfiles = findfiles(directory, mousename, '.mat', foldername, daylist)

    anticipatorylicknum = [None] * len(matfiles)
    for im,v in enumerate(matfiles):
        print(v)
        #filepath = os.path.dirname(v)
        matfile = load_mat(v)

        cuetimes = matfile['eventlog'][matfile['eventlog'][:,0]==cs1index,1]
        cuetimes = cuetimes[range(0,len(cuetimes),2)]
        licktimes = matfile['eventlog'][matfile['eventlog'][:,0]==lickindex,1]

        anticipatorylicknum[im] = [np.sum(np.logical_and(licktimes>=window[0]+c, licktimes<=window[1]+c)) for c in cuetimes]

plt.plot([item for a in anticipatorylicknum for item in a])