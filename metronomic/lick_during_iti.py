import functions.load as fnl
import functions.plot as fnp
import functions.general as fng
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stat
import pandas as pd
import os

# name spaces for namlab nwb extension
namespaces = [os.path.join(os.path.dirname(os.getcwd()),'ndx-photometry-namlab.namespace.yaml'),
              os.path.join(os.path.dirname(os.getcwd()),'ndx-eventlog-namlab.namespace.yaml')]

# DANDI set id
dandiset_id = '000351'

# animal list
mousenumber = ['M2','M3','M4','M6','M7','M8','F1','F2']
mouselist = ['HJ-FP-'+i for i in mousenumber]
daylist = [11,7,8,6,5,8,5,8]

# event indices
cs1index = 15
randomrewardindex = 7
lickindex = 5

boutthreshold = 0.5

lickboutlength = {}
lickonsetauc = {}
lickoffsetauc = {}

##
for im, mousename in enumerate(mouselist):
    # load DANDI url of an animal
    url, path = fnl.load_dandi_url(dandiset_id, mousename,range(1,daylist[im]+1))

    lickboutlength[mousename] = []
    lickonsetauc[mousename] = []
    lickoffsetauc[mousename] = []
    for i,v in enumerate(url):
        print(path[i])
        # load eventlog and dff from nwb file
        try:
            results, _ = fnl.load_nwb(v, namespaces, [('a', 'eventlog'), ('p', 'photometry', 'dff')])
            eventtime = results['eventlog']['eventtime']
            eventindexseries = results['eventlog']['eventindex']
            licktime = eventtime[eventindexseries==lickindex]

            lickdiff = np.diff(np.append(0,licktime))
            lickboutidx = np.squeeze(np.empty((len(lickdiff),1))*np.nan)
            lickboutidx[lickdiff>=boutthreshold] = 1 # lick bout onset
            lickboutidx[np.append(lickdiff[1:],0)>=boutthreshold] = 3 # lick bout offset
            lickboutidx[np.isnan(lickboutidx)] = 2
            lickboutidx = [int(x) for x in lickboutidx]

            firstlicktime = fnp.first_event_time_after_reference(eventtime,eventindexseries,lickindex,randomrewardindex,5)
            lickbout = []
            for ibout,boutstart in enumerate([i for i,v in enumerate(lickboutidx) if v==1]):
                boutend = [i for i,v in enumerate(lickboutidx) if np.logical_and(v==3,i>boutstart)]
                if len(boutend)==0:
                    break
                lickbout.append(licktime[boutstart:boutend[0]+1])
            consumboutidx = [False if len(firstlicktime[firstlicktime>y[0]])==0 else
                             True if firstlicktime[firstlicktime>y[0]][0] in y else False for y in lickbout]
            lickboutiti = [x for x,y in zip(lickbout,consumboutidx) if y is False]

            lickboutlength[mousename].append([x[-1] - x[0] for x in lickboutiti])

            dff = results['dff']['data']
            time = results['dff']['timestamps']
            lickbaselineauc = fnp.calculate_auc(dff, time, [x[0] for x in lickboutiti], [-0.5, 0])
            lickonsetauc[mousename].append(np.subtract(fnp.calculate_auc(dff, time, [x[0] for x in lickboutiti], [0, 0.5]),lickbaselineauc))
            lickoffsetauc[mousename].append(np.subtract(fnp.calculate_auc(dff, time, [x[-1] for x in lickboutiti], [0, 0.5]),lickbaselineauc))

            psthlickonset, psthmeanlickonset, _, psthtimeonset = fnp.align_signal_to_reference(dff, time, eventtime, eventindexseries,
                                                          [x[0] for x in lickboutiti], [-2,5],0, [-1,-0.5])
            psthlickoffset, psthmeanlickoffset, _, psthtimeoffset = fnp.align_signal_to_reference(dff, time, eventtime, eventindexseries,
                                                                          [x[-1] for x in lickboutiti], [-5, 2], 0,
                                                                          [[-1-x, -0.5-x] for x in lickboutlength[mousename][i]])
            sortidx = np.argsort(lickboutlength[mousename][i])
            psthlickonset_sorted = [psthlickonset[x] for x in sortidx]
            psthlickoffset_sorted = [psthlickoffset[x] for x in sortidx]

            fig = plt.figure()
            (ax1, ax2) = fig.subplots(2, 2)
            ax1[0].imshow(psthlickonset_sorted, extent=[psthtimeonset[0], psthtimeonset[-1],1,len(lickboutiti)],aspect='auto')
            ax1[1].imshow(psthlickoffset_sorted, extent=[psthtimeoffset[0], psthtimeoffset[-1], 1, len(lickboutiti)], aspect='auto')
            ax2[0].plot(psthtimeonset,psthmeanlickonset)
            ax2[1].plot(psthtimeoffset,psthmeanlickoffset)
            ax1[0].set_xlim([-2, 5])
            ax2[0].set_xlim([-2, 5])
            ax1[1].set_xlim([-5, 2])
            ax2[1].set_xlim([-5, 2])
            ax2[0].set_ylim([-2.5, 1.5])
            ax2[1].set_ylim([-2.5, 1.5])
            fig.savefig('session_lick_psth_'+mousename+str(i), bbox_inches='tight')
            plt.close('all')

        except:
            i

ronset = {}
ponset = {}
for mousename in mouselist:
    a = [stat.pearsonr([i for i,v in zip(x,y) if not np.isnan(v)],
                     [i for i in y if not np.isnan(i)]) for x,y in zip(lickboutlength[mousename],lickonsetauc[mousename])]
    ronset[mousename] = [x[0] for x in a]
    ponset[mousename] = [x[1] for x in a]
    plt.plot(ronset[mousename])
plt.show()
plt.pause(1)

cm = 1/2.54
fig = plt.figure(figsize=(30*cm,20*cm))
for im,mousename in enumerate(mouselist):
    for i,data in enumerate(lickonsetauc[mousename]):
        plt.subplot(len(mouselist),12,12*im+i+1)
        plt.scatter(lickboutlength[mousename][i],data,1,color='k')
        axes = plt.gca()
        if i==0:
            ylimit = axes.get_ylim()
        plt.ylim([x*1.5 for x in ylimit])
fig.savefig('scatter_lickonset_boutlength',bbox_inches='tight')

for mousename in mouselist:
    plt.plot([np.nanmean(x) for x in lickoffsetauc[mousename]])