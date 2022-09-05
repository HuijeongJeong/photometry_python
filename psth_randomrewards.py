import functions_load as fl
import functions_plot as fp
import functions_photometry as fpt
import matplotlib.pyplot as plt
import os.path
import numpy as np

directory = 'D:/OneDrive - UCSF/Huijeong'
#directory = 'D:/OneDrive - University of California, San Francisco/Huijeong'
#mouselist = ['HJ_FP_datHT_stGtACR_M1','HJ_FP_datWT_stGtACR_F1','HJ_FP_WT_stGtACR_F1','HJ_FP_WT_stGtACR_F2',
#             'HJ_FP_WT_stGtACR_M1','HJ_FP_WT_stGtACR_M2','HJ_FP_WT_stGtACR_M3']
mouselist = ['HJ_FP_datHT_stGtACR_M4']
foldername = 'randomrewards'
daylist = []
version = 5

doricdatanames = ['AIn-1 - Dem (AOut-1)', 'AIn-1 - Dem (AOut-2)', 'DI--O-1','DI--O-2']
ppddatanames = ['analog_1','analog_2','digital_1','digital_2']
datanames_new = ['405', '470', 'ttl1', 'ttl2']

binsize_interpolation = 10 # if binsize_interpolation is zero, not doing interpolation

lickindex = 5
rewardindex = 7

window = [-2000,10000]
binsize = 10
resolution_signal = 0
resolution = 5
clr = ['black']

for mousename in mouselist:
    photometryfiles = fl.findfiles(directory, mousename, ['.doric', '.ppd'], foldername, daylist)
    matfiles = fl.findfiles(directory, mousename, '.mat', foldername, daylist)

    for iD,v in enumerate(photometryfiles):
        print(v)
        if '.doric' in v:
            photometryfile = fl.load_doric(v, version, doricdatanames, datanames_new)
        elif '.ppd' in v:
            photometryfile = fl.load_ppd(v, ppddatanames, datanames_new)
        matfile = fl.load_mat(matfiles[iD])
        filepath = os.path.dirname(matfiles[iD])

        dff, time = fpt.preprocessing(photometryfile, matfile, binsize_interpolation,rewardindex)

        firstlicktimes = fp.first_event_time_after_reference(matfile['eventlog'], lickindex, rewardindex, 10000)

        fig = plt.figure()
        subfigs = fig.subfigures(3,1)

        fp.plot_signal(dff,time,matfile['eventlog'],[firstlicktimes],window,resolution_signal,clr,['Trials','dF/F (%)'],subfigs.flat[0])
        fp.plot_events(matfile['eventlog'],lickindex,[firstlicktimes],window,binsize,resolution,clr,['Trials','Lick rate (Hz)'],subfigs.flat[1])
        fig.savefig(os.path.join(filepath,'psth_'+str(iD)+'.png'))