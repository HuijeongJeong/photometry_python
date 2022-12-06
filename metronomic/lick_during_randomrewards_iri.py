import functions.load as fnl
import functions.plot as fnp
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stat

# name spaces for namlab nwb extension
namespaces = ["C:\\Users\\Huijeong Jeong\\PycharmProjects\\photometry\\ndx-photometry-namlab.namespace.yaml",
              "C:\\Users\\Huijeong Jeong\\PycharmProjects\\photometry\\ndx-eventlog-namlab.namespace.yaml"]

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

boutthreshold = 1

lickboutlength = {}
lickonsetauc = {}
lickoffsetauc = {}
psthlickonset = {}
psthlickoffset = {}

cm = 1 / 2.54
##
for im, mousename in enumerate(mouselist):
    # load DANDI url of an animal
    url, path = fnl.load_dandi_url(dandiset_id, mousename,range(1,daylist[im]+1))

    lickboutlength[mousename] = []
    lickonsetauc[mousename] = []
    lickoffsetauc[mousename] = []
    psthlickonset[mousename] = []
    psthlickoffset[mousename] = []

    fig = plt.figure(figsize=(25 * cm, 15 * cm))

    subfigs = fig.subfigures(3,5)
    subfigs = subfigs.flat

    for i,v in enumerate(url):
        print(path[i])
        (ax1,ax2) = subfigs[i].subplots(2,2)
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
            consumboutidx = [False if len(firstlicktime[firstlicktime>=y[0]])==0 else
                             True if firstlicktime[firstlicktime>=y[0]][0] in y else False for y in lickbout]
            lickboutiti = [x for x,y in zip(lickbout,consumboutidx) if y is False]
            nbout = len(lickboutiti)

            lickboutlength[mousename].append([x[-1] - x[0] for x in lickboutiti])

            dff = results['dff']['data']
            time = results['dff']['timestamps']
            lickbaselineauc = fnp.calculate_auc(dff, time, [x[0] for x in lickboutiti], [-1, -0.5])
            lickonsetauc[mousename].append(np.subtract(fnp.calculate_auc(dff, time, [x[0] for x in lickboutiti], [0, 0.5]),lickbaselineauc))
            lickoffsetauc[mousename].append(np.subtract(fnp.calculate_auc(dff, time, [x[-1] for x in lickboutiti], [0, 0.5]),lickbaselineauc))

            psthlickonset_temp, psthmeanlickonset, _, psthtimeonset = fnp.align_signal_to_reference(dff, time, eventtime, eventindexseries,
                                                          [x[0] for x in lickboutiti], [-2,5],0, [-1.5,-0.5])
            psthlickoffset_temp, psthmeanlickoffset, _, psthtimeoffset = fnp.align_signal_to_reference(dff, time, eventtime, eventindexseries,
                                                                          [x[-1] for x in lickboutiti], [-5, 2], 0,
                                                                          [[-1.5-x, -0.5-x] for x in lickboutlength[mousename][i]])
            psthlickonset[mousename].append(psthlickonset_temp)
            psthlickoffset[mousename].append(psthlickoffset_temp)

            sortidx = np.argsort(lickboutlength[mousename][i])

            psthlickonset_sorted = [psthlickonset_temp[x] for x in sortidx]
            psthlickoffset_sorted = [psthlickoffset_temp[x] for x in sortidx]

            ax1[0].imshow(psthlickonset_sorted, extent=[psthtimeonset[0], psthtimeonset[-1],1,len(lickboutiti)],aspect='auto')
            ax1[1].imshow(psthlickoffset_sorted, extent=[psthtimeoffset[0], psthtimeoffset[-1], 1, len(lickboutiti)], aspect='auto')
            ax1[0].scatter([lickboutlength[mousename][i][x] for x in sortidx],range(nbout,0,-1),1,'red',edgecolors='none')
            ax1[1].scatter([-lickboutlength[mousename][i][x] for x in sortidx],range(nbout,0,-1),1,'red',edgecolors='none')
            ax2[0].plot(psthtimeonset,psthmeanlickonset)
            ax2[1].plot(psthtimeoffset,psthmeanlickoffset)
            ax2[0].plot([0,0],[-2.5,2.5],'k:')
            ax2[1].plot([0, 0], [-2.5, 2.5], 'k:')
            ax1[0].set_xlim([-2, 5])
            ax2[0].set_xlim([-2, 5])
            ax1[1].set_xlim([-5, 2])
            ax2[1].set_xlim([-5, 2])
            ax2[0].set_ylim([-2.5, 2.5])
            ax2[1].set_ylim([-2.5, 2.5])
            ax1[1].set_yticklabels([])
            ax2[1].set_yticklabels([])
            ax1[0].set_xticklabels([])
            ax1[1].set_xticklabels([])
            if i<len(url)-5:
                ax2[0].set_xticklabels([])
                ax2[1].set_xticklabels([])
            else:
                ax2[0].set_xlabel('time from\n bout onset (s)')
                ax2[1].set_xlabel('time form\n bout offset (s)')
            plt.show()
            plt.pause(1)
        except:
            i
    fig.savefig('session_lick_psth_' + mousename, bbox_inches='tight')
    plt.close('all')

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
for i in range(0,2):
    if i==0:
        auc = lickonsetauc
        figname = 'lickonset'
    else:
        auc = lickoffsetauc
        figname = 'lickoffset'
    fig = plt.figure(figsize=(30*cm,20*cm))
    for im,mousename in enumerate(mouselist):
        for i,data in enumerate(auc[mousename]):
            plt.subplot(len(mouselist),12,12*im+i+1)
            plt.scatter(lickboutlength[mousename][i],data,1,color='k')
            plt.plot([0,10],[0,0],'r:')
            axes = plt.gca()
            if i==0:
                ylimit = axes.get_ylim()
                axes.set_ylabel(mousename+'\nauc(onset)')
            else:
                axes.set_yticklabels([])
            plt.ylim([x*1.5 for x in ylimit])
            plt.xlim([0,10])
            if im==len(mouselist)-1:
                if i==0:
                    axes.set_xlabel('Bout length (s)')
            else:
                axes.set_xticklabels([])
    fig.savefig('scatter_'+figname+'_boutlength',bbox_inches='tight')
    plt.close('all')


fig = plt.figure(figsize=(30*cm,20*cm))
axes = fig.subplots(2,4)
try:
    for idata in range(0,2):
        if idata==0:
            psth = psthlickonset
            time = psthtimeonset
            xlabel = 'Time from bout onset (s)'
        else:
            psth = psthlickoffset
            time = psthtimeoffset
            xlabel = 'Time from bout offset (s)'

        for iday in range(0,4):
            popdata = [np.squeeze(np.nanmean(i,1)) for i in [psth[x][iday:iday+1] for x in mouselist]]
            [axes[idata][iday].plot(time,i,color='grey',linewidth=0.5) for i in popdata]
            axes[idata][iday].plot(time,np.mean(popdata,0),color='black',linewidth=1)
            axes[idata][iday].set_ylim([-3,1.5])
            axes[idata][iday].plot([0,0],[-3,1.5],'k:')
            if idata==0:
                axes[idata][iday].set_title('session #'+str(iday+1))
            if iday==0:
                axes[idata][iday].set_ylabel('Norm. df/f')
                axes[idata][iday].set_xlabel(xlabel)
            else:
                axes[idata][iday].set_yticklabels([])
except:
    idata

fig.savefig('average_oversession',bbox_inches='tight')

