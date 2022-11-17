from functions.load import *
from functions.plot import *
from functions.photometry import *
import matplotlib.pyplot as plt
import os.path

# parameters to load data
# the structure of data folder: directory>mousename>foldername>Day
directory = 'D:/OneDrive - University of California, San Francisco/Huijeong'
foldername = 'pavlovian'
daylist = [5,6]


mouselist = ['HJ_FP_datHT_stGtACR_M1','HJ_FP_datHT_stGtACR_M2','HJ_FP_datHT_stGtACR_M4','HJ_FP_datHT_stGtACR_M6']     # list of mousename
foldername = 'randomrewards'
daylist = []                            # If you specify daylist, it will only produce plot for that days. If it is empty, it will run all days available

# parameters for photometry data
version = 5                                                                             # version of doric software; for the future when we update software version
doricdatanames = ['AIn-1 - Dem (AOut-1)', 'AIn-1 - Dem (AOut-2)', 'DI--O-1','DI--O-2']  # data name saved in doric file (version 5)
ppddatanames = ['analog_1','analog_2','digital_1','digital_2']                          # data name saved in ppd file
datanames_new = ['405', '470', 'ttl1', 'ttl2']                                          # new data name for new photometry data structure
binsize_interpolation = 10                                                              # interpolation bin size for photometry data; if it is zero, not doing interpolation

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
    dfffiles, _ = findfiles(os.path.join(directory, mousename, foldername), '.p', daylist)

    for iD,v in enumerate(dfffiles):
        print(v)

        matfile, _ = findfiles(os.path.dirname(v), '.mat', [])
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
        matfile = load_mat(matfile)

        dff = load_pickle(v)
        dff = dff[0]

        # find first lick time after reward delivery
        firstlicktimes = first_event_time_after_reference(matfile['eventlog'], lickindex, rewardindex, 10000)

        # plot figure
        fig = plt.figure()
        subfigs = fig.subfigures(2,1)
        plot_signal(dff['dff'],dff['time'],matfile['eventlog'],[firstlicktimes],window,resolution_signal,clr,['Trials','dF/F (%)'],subfigs.flat[0])
        plot_events(matfile['eventlog'],lickindex,[firstlicktimes],window,binsize,resolution,clr,['Trials','Lick rate (Hz)'],subfigs.flat[1])
        fig.savefig(os.path.join(filepath,'psth_'+str(iD)+'.png'))