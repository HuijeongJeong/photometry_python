from functions.load import *
from functions.plot import *
import os
import matplotlib.pyplot as plt
import numpy as np

onedrivedir = ['D:/OneDrive - University of California, San Francisco','D:/OneDrive - UCSF']
icom = 0
directory = os.path.join(onedrivedir[icom],'Huijeong')
dathetlist = ['M2','M3','M4','M5','M6','M7']
datwtlist = ['F1']
wtlist = ['F1','F2','F3','M1','M2','M3']
mouselist = ['HJ_FP_datHT_stGtACR_'+i for i in dathetlist] + ['HJ_FP_datWT_stGtACR_'+i for i in datwtlist]\
            + ['HJ_FP_WT_stGtACR_'+i for i in wtlist]
foldername = ['pavlovian']
daylist = []

cs1index = 15
rewardindex = 10
lickindex = 5
window = [0,3000]
window_baseline = [-3000,0]

licks = {}
days = {}
for im,mousename in enumerate(mouselist):
    print(mousename)

    matfiles, _ = findfiles(os.path.join(directory, mousename, 'pavlovian'), '.mat', daylist)
    reacquisitionidx = [i for i, v in enumerate(matfiles) if 'reacquisition' in v]
    optorewardidx = [i for i, v in enumerate(matfiles) if 'optoreward' in v]
    if len(optorewardidx)==0:
        continue
    matfiles = matfiles[reacquisitionidx[0]:]

    days[mousename] = [np.subtract(optorewardidx,reacquisitionidx)[0]-1, len(matfiles)-1]
    licks[mousename] = {}
    licks[mousename]['consummatory'] = {}
    licks[mousename]['anticipatory'] = {}
    for i,v in enumerate(matfiles):
        matfile, _ = findfiles(os.path.dirname(v), '.mat', [])
        matfile = load_mat(matfile[0])

        cuetimes = matfile['eventlog'][matfile['eventlog'][:,0]==cs1index,1]
        cuetimes = cuetimes[range(0, len(cuetimes), 2)]
        firstlicktime = first_event_time_after_reference(matfile['eventlog'],lickindex,rewardindex,np.diff(window))

        outcues = [i for i,v in enumerate(cuetimes) if v>=firstlicktime[-1]]
        if len(outcues)>0:
            cuetimes = [np.delete(cuetimes,j) for j in outcues][0]

        anticipatorylick = calculate_numevents(matfile['eventlog'],lickindex,cuetimes,window)
        consumlick = calculate_numevents(matfile['eventlog'],lickindex,firstlicktime,window)
        baselinelick = calculate_numevents(matfile['eventlog'],lickindex,cuetimes,window_baseline)

        licks[mousename]['consummatory'][i] = np.subtract(consumlick,baselinelick)
        licks[mousename]['anticipatory'][i] = np.subtract(anticipatorylick,baselinelick)

anticipatorylick_ave = [[np.mean(licks[x]['anticipatory'][i]) for i in range(days[x][0]-1,days[x][1])] for x in mouselist]
consummatorylick_ave = [[np.mean(licks[x]['consummatory'][i]) for i in range(days[x][0]-1,days[x][1])] for x in mouselist]

clr = ['black','red']
clr_light = ['grey','pink']

fig = plt.figure()
for itype in range(0,2):
    if itype == 0:
        intype = [i for i, v in enumerate(mouselist) if np.logical_or('WT' in v, 'wt' in v)]
    else:
        intype = [i for i, v in enumerate(mouselist) if 'HT' in v]
    plt.subplot(2,2,itype+1)
    [plt.plot(anticipatorylick_ave[im], color=clr_light[itype], linewidth=0.75) for im in intype]
    plt.errorbar(range(0, itype+2), np.mean([anticipatorylick_ave[im][:itype+2] for im in intype], 0),
                 np.std([anticipatorylick_ave[im][:itype+2] for im in intype], 0) / np.sqrt(len(intype)),
                 color=clr[itype], linewidth=1)

    plt.subplot(2, 2, itype + 3)
    [plt.plot(anticipatorylick_ave[im]/anticipatorylick_ave[im][0], color=clr_light[itype], linewidth=0.75) for im in intype]
    plt.errorbar(range(0, itype+2), np.mean([anticipatorylick_ave[im][:itype+2]/anticipatorylick_ave[im][0] for im in intype], 0),
                 np.std([anticipatorylick_ave[im][:itype+2]/anticipatorylick_ave[im][0] for im in intype], 0) / np.sqrt(len(intype)),
                 color=clr[itype], linewidth=1)
    plt.ylim([0,2])

