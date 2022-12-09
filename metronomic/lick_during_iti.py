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
mousenumber = ['M2','M3','M4','M6','M7','F1','F2']
mouselist = ['HJ-FP-'+i for i in mousenumber]
daystart = [16,12,13,7,6,7,13]
dayend = [28,23,31,18,19,18,23]

# event indices
cs1index = 15
cs2index = 16
rewardindex = 10
lickindex = 5

boutthreshold = 1

lickboutlength = {}
lickonsetauc = {}
lickoffsetauc = {}
psthlickonset = {}
psthlickoffset = {}
prioranticpatorylick = {}
priorconsummatorylick = {}

cm = 1 / 2.54
##
for im, mousename in enumerate(mouselist):
    # load DANDI url of an animal
    url, path = fnl.load_dandi_url(dandiset_id, mousename,range(daystart[im],dayend[im]+1))

    lickboutlength[mousename] = {}
    lickonsetauc[mousename] = {}
    lickoffsetauc[mousename] = {}
    psthlickonset[mousename] = {}
    psthlickoffset[mousename] = {}
    prioranticpatorylick[mousename] = {}
    priorconsummatorylick[mousename] = {}

    fig = plt.figure(figsize=(25 * cm, 15 * cm))

    subfigs = fig.subfigures(6,5)
    subfigs = subfigs.flat

    for i,v in enumerate(url):
        if i>=20:
            break
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

            firstlicktime = fnp.first_event_time_after_reference(eventtime,eventindexseries,lickindex,rewardindex,5)
            cuetime = eventtime[np.logical_or(eventindexseries==cs1index,eventindexseries==cs2index)]
            rwtime = eventtime[eventindexseries==rewardindex]

            lickbout = []
            for ibout,boutstart in enumerate([i for i,v in enumerate(lickboutidx) if v==1]):
                boutend = [i for i,v in enumerate(lickboutidx) if np.logical_and(v==3,i>boutstart)]
                if len(boutend)==0:
                    break
                lickbout.append(licktime[boutstart:boutend[0]+1])
            consumboutidx = [False if len(firstlicktime[firstlicktime>=y[0]])==0 else
                             True if firstlicktime[firstlicktime>=y[0]][0] in y else False for y in lickbout]
            trialidx = [np.any([True if np.any(np.logical_and(x>=y,x<=z)) else False for y,z in zip(cuetime,rwtime)]) for x in lickbout]
            dff = results['dff']['data']
            time = results['dff']['timestamps']

            anticipatorylick = fnp.calculate_numevents(eventtime, eventindexseries, lickindex, cuetime, [0,3])
            consumbouts = [x for x,y in zip(lickbout,consumboutidx) if y]

            for ianal in range(0,2):
                (ax1, ax2) = subfigs[i+15*ianal].subplots(2, 2)
                if ianal==0: # iti lick bout analysis
                    inanal = ~np.logical_or(consumboutidx,trialidx)
                    label = 'iti'
                else:
                    inanal = trialidx
                    label = 'anticipatory'
                lickboutiti = [x for x,y in zip(lickbout,inanal) if y]
                nbout = len(lickboutiti)

                if i==0:
                    ax1[0].set_title(label)
                    lickonsetauc[mousename][label] = []
                    lickoffsetauc[mousename][label] = []
                    psthlickonset[mousename][label] = []
                    psthlickoffset[mousename][label] = []
                    lickboutlength[mousename][label] = []
                    prioranticpatorylick[mousename][label] = []
                    priorconsummatorylick[mousename][label] = []
                if nbout==0:
                    lickboutlength[mousename][label].append([np.nan])
                    lickonsetauc[mousename][label].append([np.nan])
                    lickoffsetauc[mousename][label].append([np.nan])
                    psthlickonset[mousename][label].append([np.nan])
                    psthlickoffset[mousename][label].append([np.nan])
                    prioranticpatorylick[mousename][label].append([np.nan])
                    priorconsummatorylick[mousename][label].append([np.nan])
                    continue

                lickboutanticipatory =  [0 if len(z)==0 else z[0] for z in [[y for x,y in zip(reversed(cuetime),reversed(anticipatorylick)) if x<a[0]] for a in lickboutiti]]
       #             [next(y for x,y in zip(reversed(cuetime),reversed(anticipatorylick)) if x<z[0]) for z in lickboutiti]
                lickboutconsummatory =  [0 if len(z)==0 else z[0] for z in [[len(x) for x in reversed(consumbouts) if x[-1]<y[0]] for y in lickboutiti]]

                prioranticpatorylick[mousename][label].append(lickboutanticipatory)
                priorconsummatorylick[mousename][label].append(lickboutconsummatory)

                lickboutlength_temp = [x[-1] - x[0] for x in lickboutiti]
                lickboutlength[mousename][label].append(lickboutlength_temp)

                lickbaselineauc = fnp.calculate_auc(dff, time, [x[0] for x in lickboutiti], [-1, -0.5])
                lickonsetauc[mousename][label].append(np.subtract(fnp.calculate_auc(dff, time, [x[0] for x in lickboutiti],
                                                                                    [0, 0.5]),lickbaselineauc))
                lickoffsetauc[mousename][label].append(np.subtract(fnp.calculate_auc(dff, time, [x[-1] for x in lickboutiti],
                                                                                     [0, 0.5]),lickbaselineauc))

                psthlickonset_temp, psthmeanlickonset, _, psthtimeonset = fnp.align_signal_to_reference(dff, time, eventtime, eventindexseries,
                                                          [x[0] for x in lickboutiti], [-2,5],0, [-1.5,-0.5])
                psthlickoffset_temp, psthmeanlickoffset, _, psthtimeoffset = fnp.align_signal_to_reference(dff, time, eventtime, eventindexseries,
                                                                          [x[-1] for x in lickboutiti], [-5, 2], 0,
                                                                          [[-1.5-x, -0.5-x] for x in lickboutlength[mousename][label][i]])

                psthlickonset[mousename][label].append(psthlickonset_temp)
                psthlickoffset[mousename][label].append(psthlickoffset_temp)

                if ianal==0:
                    sortidx = np.argsort(lickboutlength[mousename][label][i])

                    psthlickonset_temp = [psthlickonset_temp[x] for x in sortidx]
                    psthlickoffset_temp = [psthlickoffset_temp[x] for x in sortidx]
                    lickboutlength_temp = [lickboutlength_temp[x] for x in sortidx]

                ax1[0].imshow(psthlickonset_temp, extent=[psthtimeonset[0], psthtimeonset[-1],1,len(lickboutiti)],aspect='auto')
                ax1[1].imshow(psthlickoffset_temp, extent=[psthtimeoffset[0], psthtimeoffset[-1], 1, len(lickboutiti)], aspect='auto')
                ax1[0].scatter(lickboutlength_temp,range(nbout,0,-1),1,'red',edgecolors='none')
                ax1[1].scatter([-x for x in lickboutlength_temp],range(nbout,0,-1),1,'red',edgecolors='none')
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
    fig.savefig('pavlovian_session_lick_psth_' + mousename, bbox_inches='tight')
    plt.close('all')

cm = 1/2.54
for ianal in range(0,3):
    fig = plt.figure(figsize=(60*cm,25*cm))
    for im, mousename in enumerate(mouselist):
        if ianal == 0:
            lick = prioranticpatorylick[mousename]['iti']
            label = 'anticipatory'
            xlim = [-1,20]
        elif ianal == 1:
            lick = priorconsummatorylick[mousename]['iti']
            label = 'consummatory'
            xlim = [-1,50]
        else:
            lick = [[np.nan if np.logical_or(xx==0,yy==0) else xx/yy for xx,yy in zip(x,y)] for x,y in zip(prioranticpatorylick[mousename]['iti'],priorconsummatorylick[mousename]['iti'])]
            label = 'anticipatory_consummatory'
            xlim = [-1,5]
        for i,data in enumerate(lickonsetauc[mousename]['iti']):
            plt.subplot(len(mouselist), 20, 20 * im + i + 1)
            plt.scatter(lick[i],data,1,color='k')
            plt.xlim(xlim)
            axes = plt.gca()
            if i==0:
                ylimit = axes.get_ylim()
                axes.set_ylabel(mousename + '\nauc(onset)')
            else:
                axes.set_yticklabels([])
            if im == len(mouselist) - 1:
                if i == 0:
                    axes.set_xlabel(label+' lick')
            else:
                axes.set_xticklabels([])
    fig.savefig('pavlovian_lickonsetauc_'+label, bbox_inches='tight')

fig = plt.figure(figsize=(30*cm,15*cm))
for ianal in range(0,3):
    for im, mousename in enumerate(mouselist):
        if ianal == 0:
            lick = prioranticpatorylick[mousename]['iti']
            label = 'anticipatory'
            xlim = [-1,10]
        elif ianal == 1:
            lick = priorconsummatorylick[mousename]['iti']
            label = 'consummatory'
            xlim = [-1,50]
        else:
            lick = [[np.nan if np.logical_or(xx==0,yy==0) else xx/yy for xx,yy in zip(x,y)] for x,y in zip(prioranticpatorylick[mousename]['iti'],priorconsummatorylick[mousename]['iti'])]
            label = 'anticipatory_consummatory'
            xlim = [-1,2]
        plt.subplot(3,len(mouselist),im+ianal*len(mouselist)+1)
        plt.scatter([np.nanmean(x) for x in lick],[np.nanmean(x) for x in lickonsetauc[mousename]['iti']],1,color='k')
        plt.ylim([-1,1])
plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.5, hspace=0.5)
fig.savefig('pavlovian_lickonsetauc_sessionave', bbox_inches='tight')


for i in range(0,2):
    if i==0:
        auc = lickonsetauc
        figname = 'lickonset'
    else:
        auc = lickoffsetauc
        figname = 'lickoffset'
    fig = plt.figure(figsize=(30*cm,20*cm))
    for im,mousename in enumerate(mouselist):
        for i,data in enumerate(auc[mousename]['iti']):
            plt.subplot(len(mouselist),12,12*im+i+1)
            plt.scatter(lickboutlength[mousename]['iti'][i],data,1,color='k')
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
    fig.savefig('pavlovian_scatter_'+figname+'_boutlength',bbox_inches='tight')
    plt.close('all')


fig = plt.figure(figsize=(50*cm,20*cm))
axes = fig.subplots(2,6)
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

        for iday in range(0,6):
            popdata = [np.squeeze(np.nanmean(i,1)) for i in [psth[x]['iti'][iday:iday+1] for x in mouselist]]
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

fig.savefig('pavlovian_average_oversession',bbox_inches='tight')

