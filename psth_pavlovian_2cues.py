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
mouselist = ['HJ_FP_datHT_stGtACR_M2']
foldername = 'pavlovian'
daylist = []
version = 5

doricdatanames = ['AIn-1 - Dem (AOut-1)', 'AIn-1 - Dem (AOut-2)', 'DI--O-1','DI--O-2']
ppddatanames = ['analog_1','analog_2','digital_1','digital_2']
datanames_new = ['405', '470', 'ttl1', 'ttl2']

binsize_interpolation = 10 # if binsize_interpolation is zero, not doing interpolation

lickindex = 5
cs1index = 15

window = [-2000,10000]
binsize = 10
resolution_signal = 0
resolution = 5
clr = ['black']

for mousename in mouselist:
    photometryfiles = fl.findfiles(directory, mousename, ['.doric', '.ppd'], foldername, daylist)
    matfiles = fl.findfiles(directory, mousename, '.mat', foldername, daylist)

    photometryfiles = photometryfiles[-1:]
    matfiles = matfiles[-1:]
    for iD,v in enumerate(photometryfiles):
        print(v)
        if '.doric' in v:
            photometryfile = fl.load_doric(v, version, doricdatanames, datanames_new)
        elif '.ppd' in v:
            photometryfile = fl.load_ppd(v, ppddatanames, datanames_new)
        matfile = fl.load_mat(matfiles[iD])
        filepath = os.path.dirname(matfiles[iD])

        dff, time = fpt.preprocessing(photometryfile, matfile, binsize_interpolation,cs1index)

        cuetimes = matfile['eventlog'][matfile['eventlog'][:,0]==cs1index,1]
        cuetimes = cuetimes[range(0,len(cuetimes),2)]

        fig = plt.figure()
        subfigs = fig.subfigures(3,1)

        fp.plot_signal(dff,time,matfile['eventlog'],[cuetimes],window,resolution_signal,clr,['Trials','dF/F (%)'],subfigs.flat[0])
        fp.plot_events(matfile['eventlog'],lickindex,[cuetimes],window,binsize,resolution,clr,['Trials','Lick rate (Hz)'],subfigs.flat[1])
        fig.savefig(os.path.join(filepath,'psth.png'))