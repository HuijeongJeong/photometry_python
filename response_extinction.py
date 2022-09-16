from functions.load import *
from functions.plot import *
from functions.photometry import *
import os
import numpy as np
import matplotlib.pyplot as plt

directory = 'D:/OneDrive - University of California, San Francisco/Huijeong'
dathetlist = ['M2','M3','M4','M5','M6','M7']
datwtlist = ['F1']
wtlist = ['F1','F2','F3','M1','M2','M3']
mouselist = ['HJ_FP_datHT_stGtACR_'+i for i in dathetlist] + ['HJ_FP_datWT_stGtACR_'+i for i in datwtlist]\
            + ['HJ_FP_WT_stGtACR_'+i for i in wtlist]
daylist = []

version = 5
doricdatanames = ['AIn-1 - Dem (AOut-1)', 'AIn-1 - Dem (AOut-2)', 'DI--O-1','DI--O-2']
ppddatanames = ['analog_1','analog_2','digital_1','digital_2']
datanames_new = ['405', '470', 'ttl1', 'ttl2']
binsize_interpolation = 10

cs1index = 15
cs2index = 16
window = [0,1500]

cs1rsp = np.full((len(mouselist),4),np.nan)
cs2rsp = np.full((len(mouselist),4),np.nan)
cs2onlyrsp = np.full((len(mouselist),1),np.nan)

for im,mousename in enumerate(mouselist):
    photometryfiles, days = findfiles(os.path.join(directory,mousename,'pavlovian'), ['.doric', '.ppd'], daylist)
    probeidx = [i for i,v in enumerate(photometryfiles) if 'probetest' in v]
    if len(probeidx)==0:
        continue
    photometryfiles = photometryfiles[probeidx[0]-1:]

    for iD, v in enumerate(photometryfiles):
        print(v)
        try:
            matfile, _ = findfiles(os.path.dirname(v), '.mat', [])
            matfile = load_mat(matfile[0])

            if '.doric' in v:
                photometryfile = load_doric(v, version, doricdatanames, datanames_new)
            elif '.ppd' in v:
                photometryfile = load_ppd(v, ppddatanames, datanames_new)

            dff, time = preprocessing(photometryfile, matfile, binsize_interpolation, cs1index)

            cs1times = matfile['eventlog'][matfile['eventlog'][:, 0] == cs1index, 1]
            cs2times = matfile['eventlog'][matfile['eventlog'][:, 0] == cs1index, 1]

            dopaminebaseline = calculate_auc(dff, time, cs1times[range(0, len(cs1times), 2)] - 1000, window)
            dopaminecs1rsp = calculate_auc(dff, time, cs1times[range(0, len(cs1times), 2)], window) - dopaminebaseline
            dopaminecs2rsp = calculate_auc(dff, time, cs1times[range(1, len(cs1times), 2)], window) - dopaminebaseline

            cs1rsp[im, iD] = np.mean(dopaminecs1rsp / 1000)
            cs2rsp[im, iD] = np.mean(dopaminecs2rsp / 1000)

            if iD==1:
                cs2onlytimes = matfile['eventlog'][matfile['eventlog'][:, 0] == cs2index, 1]
                dopaminebaseline = calculate_auc(dff, time, cs2onlytimes - 1000, window)
                dopaminecs2onlyrsp = calculate_auc(dff, time, cs2onlytimes,window) - dopaminebaseline
                cs2onlyrsp[im] = np.mean(dopaminecs2onlyrsp / 1000)
        except:
            print('an error occurred')

fig = plt.figure()
subfigs = fig.subfigures(2,1)
for itype in range(0,2):
    (ax1, ax2) = subfigs.flat[itype].subplots(1,2)
    if itype==0:
        intype = [i for i,v in enumerate(mouselist) if 'HT' in v]
    else:
        intype = [i for i,v in enumerate(mouselist) if np.logical_or('WT' in v,'wt' in v)]
    [ax1.plot(cs1rsp[i,:]/cs1rsp[i,0], linewidth=0.75) for i in intype]
    [ax2.plot(cs2rsp[i,:]/cs1rsp[i,0], linewidth=0.75) for i in intype]
    [ax2.scatter(01,cs2onlyrsp[i]/cs1rsp[i,0]) for i in intype]
    ax1.set_ylim(-1, 2)
    ax2.set_ylim(-1, 2)

