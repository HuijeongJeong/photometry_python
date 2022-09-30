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
rewardindex = 10
lickindex = 5
window = [0,1500]
window_step = [-1500,0,1500]

ref = ['cs1','cs2','reward','lick']
response = {}
for i in ref:
    response[i] = {}
licks = np.full((len(mouselist),1),np.nan)
for im,mousename in enumerate(mouselist):
    print(mousename)

    dfffiles, _ = findfiles(os.path.join(directory, mousename, 'pavlovian'), '.p', daylist)
    dfffiles_rr, _ = findfiles(os.path.join(directory, mousename, 'randomrewards'), '.p', daylist)
    probetestidx = [i for i, v in enumerate(dfffiles) if 'probetest' in v]
    if len(probetestidx) > 0:
        dfffiles = dfffiles[:probetestidx[0]]

    for i in ref:
        response[i][mousename] = []

    for i,v in enumerate(dfffiles):
        matfile, _ = findfiles(os.path.dirname(v), '.mat', [])
        matfile = load_mat(matfile[0])
        dff = load_pickle(v)
        dff = dff[0]

        cuetimes = matfile['eventlog'][matfile['eventlog'][:, 0] == cs1index, 1]
        cuetimes = cuetimes[range(0, len(cuetimes), 2)]
        firstlicktimes = first_event_time_after_reference(matfile['eventlog'],lickindex,rewardindex,5000)
        licktimes = matfile['eventlog'][matfile['eventlog'][:,0]==lickindex,1]

        dopamine_rsp = [calculate_auc(dff['dff'], dff['time'], cuetimes+iw, window) for iw in window_step]+\
                       [calculate_auc(dff['dff'],dff['time'],firstlicktimes,window)]
        for ir,vr in enumerate(ref[:-1]):
            response[vr][mousename].append(np.subtract(dopamine_rsp[ir + 1], dopamine_rsp[0]))

        lick_rsp = [[np.sum(np.logical_and(licktimes>=ic+j,licktimes<ic+j+3000)) for ic in cuetimes] for j in [-3000,0]]
        response[ref[-1]][mousename].append(np.subtract(lick_rsp[1],lick_rsp[0]))



fig = plt.figure(figsize=(22, 6))
subfigs = fig.subfigures(2, 1)
for itype in range(0, 2):
    if itype == 0:
        intype = [i for i, v in enumerate(mouselist) if 'HT' in v]
    else:
        intype = [i for i, v in enumerate(mouselist) if np.logical_or('WT' in v, 'wt' in v)]
    axs = subfigs.flat[itype].subplots(1,7)

    for i, ax in enumerate(axs.flat):
        if i>=len(intype):
            ax.remove()
            continue
        cs1rsp = flatten(response['cs1'][mouselist[intype[i]]])
        cs2rsp = flatten(response['cs2'][mouselist[intype[i]]])
        rwrsp = flatten(response['reward'][mouselist[intype[i]]])
        out = np.logical_or.reduce(np.array((np.isnan(cs1rsp),np.isnan(cs2rsp),np.isnan(rwrsp))))
        cs1rsp = list(compress(cs1rsp, ~out))
        rwrsp = list(compress(rwrsp, ~out))
        _, changetrial_cs1, signalcs1, _ = cumulative_analysis(cs1rsp, np.nan)
        _, changetrial_rw, signalrw, _ = cumulative_analysis(rwrsp, np.nan)
        ax.plot(signalcs1,color='k')
        ax.plot(signalrw,color='b')
        ax.scatter(changetrial_cs1, signalcs1[changetrial_cs1],color='k')
        ax.scatter(changetrial_rw, signalrw[changetrial_rw],color='b')

        if itype==1:
            cs2rsp = list(compress(cs2rsp, ~out))
            _, changetrial_cs2, signalcs2, _ = cumulative_analysis(cs2rsp, np.nan)
            ax.plot(signalcs2 * np.sum(cs2rsp) / np.sum(cs1rsp),color='r')
            ax.scatter(changetrial_cs2, signalcs2[changetrial_cs2] * np.sum(cs2rsp) / np.sum(cs1rsp),color='r')

        ax.set_title(mouselist[intype[i]],fontsize=8)
        ax.set_ylim([-0.2, 1.2])
        if i>0:
            ax.set_yticklabels([])
fig.savefig('D:\OneDrive - UCSF//figures\manuscript\dopamine_contingency//revision\dynamics.png',bbox_inches='tight')


nblock = 2
fig = plt.figure(figsize=(6,3))
for itype in range(0, 2):
    plt.subplot(1, 2, itype + 1)
    if itype == 0:
        intype = [i for i, v in enumerate(mouselist) if 'HT' in v]
        plt.title('DAT')
        plt.ylabel('Normalized DA')
    else:
        intype = [i for i, v in enumerate(mouselist) if np.logical_or('WT' in v, 'wt' in v)]
        plt.title('WT')

    cs1rsp = [flatten([movmean(v,int(np.floor(len(v)/nblock)),int(np.floor(len(v)/nblock))) for v in response['cs1'][mouselist[i]]]) for i in intype]
    cs2rsp = [flatten([movmean(v,int(np.floor(len(v)/nblock)),int(np.floor(len(v)/nblock))) for v in response['cs2'][mouselist[i]]]) for i in intype]
    rwrsp = [flatten([movmean(v,int(np.floor(len(v)/nblock)),int(np.floor(len(v)/nblock))) for v in response['reward'][mouselist[i]]]) for i in intype]

    [plt.plot(np.divide(x,y[0]),color='lightgray',linewidth=0.75) for x,y in zip(cs1rsp,rwrsp)]
    [plt.plot(np.divide(x,y[0]),color='pink',linewidth=0.75) for x,y in zip(cs2rsp,rwrsp)]
    [plt.plot(np.divide(x,x[0]),color='lightskyblue',linewidth=0.75) for x in rwrsp]
    plt.plot([sum(x) / len(x) for x in zip(*[np.divide(x,y[0]).tolist() for x,y in zip(cs1rsp,rwrsp)])],color='k',linewidth=1.5)
    plt.plot([sum(x) / len(x) for x in zip(*[np.divide(x,y[0]).tolist() for x,y in zip(cs2rsp,rwrsp)])],color='r',linewidth=1.5)
    plt.plot([sum(x) / len(x) for x in zip(*[np.divide(x,x[0]).tolist() for x in rwrsp])],color='b',linewidth=1.5)
    plt.xlabel('Block ('+str(nblock)+'/session)')
    plt.ylim([-0.5,2.5])
fig.savefig('D:\OneDrive - UCSF//figures\manuscript\dopamine_contingency//revision\dynamics_sessionave_'+str(nblock)+'_block.png',bbox_inches='tight')
