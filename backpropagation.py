from functions.load import *
from functions.plot import *
from functions.general import *
import os
import matplotlib.pyplot as plt
import numpy as np
from itertools import compress

directory = 'D:/OneDrive - UCSF/Huijeong'
dathetlist = ['M2','M3','M4','M5','M6','M7']
datwtlist = ['F1']
wtlist = ['F1','F2','F3','M1','M2','M3']
mouselist = ['HJ_FP_datHT_stGtACR_'+i for i in dathetlist] + ['HJ_FP_datWT_stGtACR_'+i for i in datwtlist]\
            + ['HJ_FP_WT_stGtACR_'+i for i in wtlist]
foldername = ['randomrewards','pavlovian']
daylist = []

cs1index = 15
window = [0, 3000]
window_bl = [-2000, 0]
binsize = 20

for im,mousename in enumerate(mouselist):
    print(mousename)

    dfffiles, _ = findfiles(os.path.join(directory, mousename, 'pavlovian'), '.p', daylist)
    probetestidx = [i for i, v in enumerate(dfffiles) if 'probetest' in v]
    if len(probetestidx) > 0:
        dfffiles = dfffiles[:probetestidx[0]]

    for i,v in enumerate(dfffiles):
        matfile, _ = findfiles(os.path.dirname(v), '.mat', [])
        matfile = load_mat(matfile[0])
        dff = load_pickle(v)
        dff = dff[0]

        signal, _, _, time = align_signal_to_reference(dff['dff'], dff['time'], matfile['eventlog'], cs1index, [-2000, 3000], 0)
        mov_signal = movmean(signal[:, np.logical_and(time >= 0, time <= 3000)], int(binsize / np.mean(np.diff(dff['time']))), 2, 1)
        mov_baseline = movmean(signal[:, np.logical_and(time >= -2000, time < 0)], int(binsize / np.mean(np.diff(dff['time']))), 2, 1)

        peakidx, peakval = peaksearch(mov_signal, [np.std(i) for i in mov_baseline], 'peak')
        cuetimes = matfile['eventlog'][matfile['eventlog'][:, 0] == cs1index, 1]
        cuetimes = cuetimes[range(0, len(cuetimes), 2)]


