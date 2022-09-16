from functions.load import *
from functions.plot import *
import os
import matplotlib.pyplot as plt
import numpy as np

directory = 'D:/OneDrive - UCSF/Huijeong'
dathetlist = ['M2','M3','M4','M5','M6','M7']
datwtlist = ['F1']
wtlist = ['F1','F2','F3','M1','M2','M3']
mouselist = ['HJ_FP_datHT_stGtACR_'+i for i in dathetlist] + ['HJ_FP_datWT_stGtACR_'+i for i in datwtlist]\
            + ['HJ_FP_WT_stGtACR_'+i for i in wtlist]
foldername = 'pavlovian'
daylist = []

cs1index = 15
rewardindex = 10
bgdrewardindex = 7
lickindex = 5
window = [0,250]
window_step = range(-250,1500,250)
window_baseline = -1750

dopaminersp = np.full((len(mouselist),len(window_step)+1),np.nan)
for im,mousename in enumerate(mouselist):
    print(mousename)
    dfffiles, _ = findfiles(os.path.join(directory, mousename, foldername), '.p', daylist)
    dfffiles = dfffiles[0]

    matfile, _ = findfiles(os.path.dirname(dfffiles), '.mat', [])
    matfile = load_mat(matfile[0])
    dff = load_pickle(dfffiles)
    dff = dff[0]

    cuetimes = matfile['eventlog'][matfile['eventlog'][:, 0] == cs1index, 1]
    cuetimes = cuetimes[range(1, len(cuetimes), 2)]

    dopamine_baseline = np.nanmean(calculate_auc(dff['dff'], dff['time'], cuetimes+window_baseline, window))
    dopamine_inh = [np.nanmean(calculate_auc(dff['dff'], dff['time'], cuetimes+i, window)) for i in window_step]
    dopaminersp[im,:] = [dopamine_baseline] + dopamine_inh


fig = plt.figure()
[plt.plot(dopaminersp[im,1:]/np.abs(dopaminersp[im,0])) for im in range(0,len(mouselist))]
fig.savefig('D:\OneDrive - UCSF\figures\manuscript\dopamine_contingency\revision\inhibition.png')