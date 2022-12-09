import functions.load as fnl
import functions.plot as fnp
import numpy as np
import os


# name spaces for namlab nwb extension
namespaces = ["D:\\github\\namlab\\anccr-matlab\\nwbextension\\ndx-photometry-namlab.namespace.yaml",
              "D:\\github\\namlab\\anccr-matlab\\nwbextension\\ndx-eventlog-namlab.namespace.yaml"]

# DANDI set id
dandiset_id = '000351'

# animal list
firstcohort = ['M2','M3','M4','M6','M7','F1','F2']
secondcohort = ['F1']
thirdcohort = ['F1','F2','F3','M1','M2','M3']
mouselist = ['HJ-FP-'+i for i in firstcohort] + ['HJ-FP-datWT-stGtACR-'+i for i in secondcohort]\
            + ['HJ-FP-WT-stGtACR-'+i for i in thirdcohort]

firstpavlovianday = [16,12,13,7,6,7,13,2,2,2,2,2,2,2]

# event indices
csindex = [15,16]
rewardindex = 10
bgdrewardindex = 7
lickindex = 5

dopamine_reward = np.full((len(mouselist),6),np.nan)
dopamine_cue = np.full((len(mouselist),6,2),np.nan)
lick_cue = np.full((len(mouselist),6,2),np.nan)

for im,mousename in enumerate(mouselist):
    # load DANDI url of an animal
    url, path = fnl.load_dandi_url(dandiset_id, mousename,[1]+list(range(firstpavlovianday[im],firstpavlovianday[im]+5)))

    # use first random reward and first five conditioning sessions
    for i,v in enumerate(url):
        print(path[i])
        # load eventlog and dff from nwb file
        results, _ = fnl.load_nwb(v, namespaces, [('a', 'eventlog'), ('p', 'photometry', 'dff')])
        eventtime = results['eventlog']['eventtime']
        eventindex = results['eventlog']['eventindex']
        if i==0:
            firstlicktimes = fnp.first_event_time_after_reference(eventindex,eventtime, lickindex,bgdrewardindex, 3)
            out = np.logical_or(np.diff([np.nan]+firstlicktimes.tolist())<5, np.isnan(firstlicktimes))
            dopamine_baseline = np.nanmean(fnp.calculate_auc(results['dff']['data'], results['dff']['timestamps'],
                                                             [x for x,y in zip(firstlicktimes,out) if not y],[-2,-0.5]))
            dopamine_reward[im,i] = np.nanmean(fnp.calculate_auc(results['dff']['data'], results['dff']['timestamps'],
                                                           [x for x,y in zip(firstlicktimes,out) if not y],[-0.5,1])) - dopamine_baseline
        else:
            firstlicktimes = fnp.first_event_time_after_reference(eventindex,eventtime, lickindex,rewardindex, 3)
            cuetimes = results['eventlog']['eventtime'][[x in csindex for x in results['eventlog']['eventindex']]]
            cueidx = results['eventlog']['eventindex'][[x in csindex for x in results['eventlog']['eventindex']]]
            rewardidx = results['eventlog']['nonsolenoidflag'][results['eventlog']['eventindex']==rewardindex]
            if len(cueidx)>len(rewardidx):
                cueidx = cueidx[:len(rewardidx)]
                cuetimes = cuetimes[:len(rewardidx)]
            csplus = np.unique(cueidx[rewardidx==1])

            dopamine_baseline = np.nanmean(fnp.calculate_auc(results['dff']['data'], results['dff']['timestamps'],
                                                             cuetimes,[-1, 0]))
            dopamine_cue[im,i,0] = np.nanmean(fnp.calculate_auc(results['dff']['data'], results['dff']['timestamps'],
                                                                  cuetimes[cueidx==csplus],[0, 1])) - dopamine_baseline
            dopamine_cue[im, i, 1] = np.nanmean(fnp.calculate_auc(results['dff']['data'], results['dff']['timestamps'],
                                                                  cuetimes[cueidx != csplus],[0, 1])) - dopamine_baseline
            dopamine_reward[im, i] = np.nanmean(fnp.calculate_auc(results['dff']['data'], results['dff']['timestamps'],
                                                                  firstlicktimes[cueidx==csplus],[0, 1])) - dopamine_baseline

            lick_baseline = np.nanmean(fnp.calculate_numevents(results['eventlog']['eventtime'],results['eventlog']['eventindex'],
                                                    lickindex,csindex,[-1,0]))
            lick_cue[im,i,0] = np.nanmean(fnp.calculate_numevents(results['eventlog']['eventtime'], results['eventlog']['eventindex'],
                                                    lickindex, int(csplus), [0, 3]))/3-lick_baseline
            lick_cue[im,i,1] = np.nanmean(fnp.calculate_numevents(results['eventlog']['eventtime'], results['eventlog']['eventindex'],
                                                    lickindex, [x for x in csindex if x is not int(csplus)][0], [0, 3]))/3-lick_baseline


lick_cue