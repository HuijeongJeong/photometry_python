import functions.load as fnl
import functions.plot as fnp
import matplotlib.pyplot as plt
import os.path

# parameters to load data
# the structure of data folder: directory>mousename>foldername>Day
directory = 'D:/OneDrive - UCSF/Huijeong'
foldername = 'pavlovian'
daylist = [5,6]


mouselist = ['HJ_FP_datHT_stGtACR_M1','HJ_FP_datHT_stGtACR_M2','HJ_FP_datHT_stGtACR_M4','HJ_FP_datHT_stGtACR_M6']     # list of mousename
foldername = 'randomrewards'
daylist = []                            # If you specify daylist, it will only produce plot for that days. If it is empty, it will run all days available

# event index
lickindex = 5
rewardindex = 7

# parameters for plot
window = [-2000,10000]                  # time window for plot
binsize = 10                            # bin size for lick psth
resolution_signal = 0                   # convolution resolution for photometry data
resolution = 5                          # convolution resolution for lick; sigma = binsize*resolution
clr = ['black']

for mousename in mouselist:
    dfffiles, _ = fnl.findfiles(os.path.join(directory, mousename, foldername), '.p', daylist)

    for iD,v in enumerate(dfffiles):
        print(v)

        matfile, _ = fnl.findfiles(os.path.dirname(v), '.mat', [])
        if len(matfile) == 0:
            print('no event file!')
            continue
        elif len(matfile) > 1:
            print('there are more than one event file.\n')
            print(matfile)
            matfileidx = input('please specify the correct one or enter none if you want to skip.\n')
            if matfileidx == 'none':
                continue
            else:
                matfile = matfile[int(matfileidx)]
        else:
            matfile = matfile[0]
        filepath = os.path.dirname(matfile)
        matfile = fnl.load_mat(matfile)

        dff = fnl.load_pickle(v)
        dff = dff[0]

        # find first lick time after reward delivery
        eventtime = matfile['eventlog'][:,1]
        eventindexseries = matfile['eventlog'][:,0]
        firstlicktimes = fnp.first_event_time_after_reference(eventtime,eventindexseries, lickindex, rewardindex, 10000)

        # plot figure
        fig = plt.figure()
        subfigs = fig.subfigures(2,1)
        fnp.plot_signal(dff['dff'],dff['time'],eventtime,eventindexseries,[firstlicktimes],window,resolution_signal,clr,['Trials','dF/F (%)'],subfigs.flat[0],0)
        fnp.plot_events(eventtime,eventindexseries,lickindex,[firstlicktimes],window,binsize,resolution,clr,['Trials','Lick rate (Hz)'],subfigs.flat[1])
        fig.savefig(os.path.join(filepath,'psth_'+str(iD)+'.png'))