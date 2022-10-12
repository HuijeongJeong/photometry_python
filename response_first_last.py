from functions.load import *
from functions.plot import *
import os
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stat

directory = 'D:/OneDrive - University of California, San Francisco/Huijeong'
dathetlist = ['M2','M3','M4','M5','M6','M7','M8']
datwtlist = ['F1']
wtlist = ['F1','F2','F3','M1','M2','M3']
mouselist = ['HJ_FP_datHT_stGtACR_'+i for i in dathetlist] + ['HJ_FP_datWT_stGtACR_'+i for i in datwtlist]\
            + ['HJ_FP_WT_stGtACR_'+i for i in wtlist]
foldername = 'pavlovian'
daylist = []

version = 5
doricdatanames = ['AIn-1 - Dem (AOut-1)', 'AIn-1 - Dem (AOut-2)', 'DI--O-1','DI--O-2']
ppddatanames = ['analog_1','analog_2','digital_1','digital_2']
datanames_new = ['405', '470', 'ttl1', 'ttl2']
binsize_interpolation = 10

cs1index = 15
rewardindex = 10
bgdrewardindex = 7
lickindex = 5
window = [0,1000]
windowsize_lick = 3000

cuersp = np.full((len(mouselist),4),np.nan)
rwrsp = np.full((len(mouselist),4),np.nan)
licks = np.full((len(mouselist),4),np.nan)
bgdrwrsp = np.full((len(mouselist),1),np.nan)

for im,mousename in enumerate(mouselist):
    dfffiles, _ = findfiles(os.path.join(directory, mousename, 'pavlovian'), '.p', daylist)
    dfffiles_rr, _ = findfiles(os.path.join(directory, mousename, 'randomrewards'), '.p', daylist)
    probetestidx = [i for i,v in enumerate(dfffiles) if 'probetest' in v]
    if len(probetestidx)>0:
        dfffiles = dfffiles[:probetestidx[0]]
    dfffiles = dfffiles_rr[:1] + dfffiles[:2] + dfffiles[-2:]

    for iD,v in enumerate(dfffiles):
        print(v)
        try:
            matfile, _ = findfiles(os.path.dirname(v),'.mat',[])
            matfile = load_mat(matfile[0])

            dff = load_pickle(v)
            dff = dff[0]

            #if '.doric' in v:
            #    photometryfile = load_doric(v, version, doricdatanames, datanames_new)
            #elif '.ppd' in v:
            #    photometryfile = load_ppd(v, ppddatanames, datanames_new)

            #dff, time = preprocessing(photometryfile, matfile, binsize_interpolation,cs1index)

            if iD==0:
                firstlicktimes = first_event_time_after_reference(matfile['eventlog'], lickindex, bgdrewardindex, 10000)
                rewardtimes = matfile['eventlog'][matfile['eventlog'][:,0]==bgdrewardindex,1]
                dopaminebaseline = calculate_auc(dff['dff'], dff['time'], rewardtimes - np.diff(window), window)
                dopaminerwrsp = np.subtract(calculate_auc(dff['dff'], dff['time'], firstlicktimes, window),dopaminebaseline)

                bgdrwrsp[im] = np.nanmean(dopaminerwrsp/1000)
            else:
                cuetimes = matfile['eventlog'][matfile['eventlog'][:,0]==cs1index,1]
                cuetimes = cuetimes[range(0,len(cuetimes),2)]
                firstlicktimes = first_event_time_after_reference(matfile['eventlog'], lickindex, rewardindex, 10000)
                licktimes = matfile['eventlog'][matfile['eventlog'][:,0]==lickindex,1]

                lickbaseline = [sum(np.logical_and(licktimes>=x-windowsize_lick,licktimes<x)) for x in cuetimes]
                lickcue = [sum(np.logical_and(licktimes>=x,licktimes<x+windowsize_lick))for x in cuetimes]

                dopaminebaseline = calculate_auc(dff['dff'], dff['time'], cuetimes - np.diff(window), window)
                dopaminecuersp = np.subtract(calculate_auc(dff['dff'], dff['time'], cuetimes, window),dopaminebaseline)
                dopaminerwrsp = np.subtract(calculate_auc(dff['dff'], dff['time'], firstlicktimes, window),dopaminebaseline)

                cuersp[im,iD-1] = np.nanmean(dopaminecuersp/1000)
                rwrsp[im,iD-1] = np.nanmean(dopaminerwrsp/1000)
                licks[im,iD-1] = np.nanmean(np.subtract(lickcue,lickbaseline))
        except:
            print('an error occurred')

fig = plt.figure()
subfigs = fig.subfigures(2,1)
for itype in range(0,2):
    (ax1, ax2, ax3) = subfigs.flat[itype].subplots(1,3)
    if itype==0:
        intype = [i for i,v in enumerate(mouselist) if np.logical_and('HT' in v, '8' not in v)]
        ax1.set_title('CS1')
        ax2.set_title('Reward')
        ax3.set_title('Lick')
        ax1.set_ylabel('DAT')
    else:
        intype = [i for i,v in enumerate(mouselist) if np.logical_or('WT' in v,'wt' in v)]
        ax1.set_ylabel('WT')
    [ax1.plot(cuersp[i,:]/rwrsp[i,0], linewidth=0.75) for i in intype]
    [ax2.plot(rwrsp[i,:]/bgdrwrsp[i], linewidth=0.75) for i in intype]
    [ax3.plot(licks[i,:], linewidth=0.75)for i in intype]
   # [ax2.scatter(4,bgdrwrsp[i]/bgdrwrsp[i]) for i in intype]
    ax1.plot(np.nanmean([np.divide(x,y) for x,y in zip(cuersp[intype,:],rwrsp[intype,0])],0),color='k', linewidth=1.5)
    ax2.plot(np.nanmean([np.divide(x,y) for x,y in zip(rwrsp[intype,:],bgdrwrsp[intype])],0),color='k', linewidth=1.5)
    ax3.plot(np.nanmean(licks[intype,:],0), color='k', linewidth=1.5)
    _,p = stat.ttest_rel([cuersp[i,0]/rwrsp[i,0] for i in intype],[cuersp[i,-1]/rwrsp[i,0] for i in intype])
    print(p)
    ax1.set_ylim(-0.2,1.2)
    ax2.set_ylim(-0.2,2.5)
    ax3.set_ylim(-1,17)
    ax1.set_xticks(range(0,4),labels=['1','2','n-1','n'])
    ax2.set_xticks(range(0,4),labels=['1','2','n-1','n'])
    ax3.set_xticks(range(0,4), labels=['1', '2', 'n-1', 'n'])