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
foldername = ['randomrewards','pavlovian']
daylist = []

cs1index = 15
rewardindex = 10
bgdrewardindex = 7
refindex = [bgdrewardindex,cs1index]
lickindex = 5
window = [0,500]
window_step = range(-500,1500,500)
window_baseline = [-500,-2000]

dopamine_inh = np.full((len(mouselist),len(window_step)),np.nan)
dopamine_reward = np.full((len(mouselist),1),np.nan)
for im,mousename in enumerate(mouselist):
    print(mousename)

    dfffiles, _ = findfiles(os.path.join(directory, mousename, 'pavlovian'), '.p', daylist)
    dfffiles_rr, _ = findfiles(os.path.join(directory, mousename, 'randomrewards'), '.p', daylist)
    probetestidx = [i for i, v in enumerate(dfffiles) if 'probetest' in v]
    if len(probetestidx) > 0:
        dfffiles = dfffiles[:probetestidx[0]]
    dfffiles = dfffiles_rr[:1] + dfffiles[:1] + dfffiles[-1:]

    for i,v in enumerate(dfffiles):
        matfile, _ = findfiles(os.path.dirname(v), '.mat', [])
        matfile = load_mat(matfile[0])
        dff = load_pickle(v)
        dff = dff[0]

        reftimes = matfile['eventlog'][matfile['eventlog'][:, 0] == refindex[i], 1]
        if i==0:
            dopamine_baseline = np.nanmean(calculate_auc(dff['dff'], dff['time'], reftimes+window_baseline[i], window))
            dopamine_reward[im] = np.nanmean(calculate_auc(dff['dff'], dff['time'], reftimes, window))-dopamine_baseline
        else:
            reftimes = reftimes[range(1, len(reftimes), 2)]
            dopamine_inh[im,:] = [np.nanmean(calculate_auc(dff['dff'], dff['time'], reftimes+i, window))-dopamine_baseline for i in window_step]


clr = ['red','black']
clr_light = ['pink','grey']
fig = plt.figure(figsize=(3,4))
for itype in range(0,2):
    if itype == 0:
        intype = [i for i, v in enumerate(mouselist) if 'HT' in v]
    else:
        intype = [i for i, v in enumerate(mouselist) if np.logical_or('WT' in v, 'wt' in v)]
    [plt.plot(dopamine_inh[im,:]/dopamine_reward[im],color = clr_light[itype],linewidth = 0.75) for im in intype]
    plt.errorbar(range(0,4),np.mean([dopamine_inh[im,:]/dopamine_reward[im] for im in intype],0),
                 np.std([dopamine_inh[im,:]/dopamine_reward[im] for im in intype],0)/np.sqrt(len(intype)),
                 color=clr[itype],linewidth=1)
    plt.xticks(range(0,4),labels=[-0.25,0.25,0.75,1.25])
    plt.xlabel('Time from CS2 (s)')
    plt.ylabel('Normalized DA response\n (1 = response to random reward)')
fig.savefig('D:\OneDrive - UCSF//figures\manuscript\dopamine_contingency//revision\inhibition.png',bbox_inches='tight')