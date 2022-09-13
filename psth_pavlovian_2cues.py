from functions.load import *
from functions.plot import *
from functions.photometry import *
import matplotlib.pyplot as plt
import os.path

#directory = 'D:/OneDrive - UCSF/Huijeong'
directory = 'D:/OneDrive - University of California, San Francisco/Huijeong'
mouselist = ['HJ_FP_datHT_stGtACR_M5']
foldername = 'pavlovian'
daylist = [8]
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
    photometryfiles = findfiles(directory, mousename, ['.doric', '.ppd'], foldername, daylist)
    matfiles = findfiles(directory, mousename, '.mat', foldername, daylist)

    for iD,v in enumerate(photometryfiles):
        print(v)
        if '.doric' in v:
            photometryfile = load_doric(v, version, doricdatanames, datanames_new)
        elif '.ppd' in v:
            photometryfile = load_ppd(v, ppddatanames, datanames_new)
        matfile = load_mat(matfiles[iD])
        filepath = os.path.dirname(matfiles[iD])

        dff, time = preprocessing(photometryfile, matfile, binsize_interpolation,cs1index)

        cuetimes = matfile['eventlog'][matfile['eventlog'][:,0]==cs1index,1]
        cuetimes = cuetimes[range(0,len(cuetimes),2)]

        fig = plt.figure()
        subfigs = fig.subfigures(2,1)
        if foldername=='probetest':
            plot_signal(dff, time, matfile['eventlog'], [cuetimes], window, resolution_signal, clr,['Trials', 'dF/F (%)'], subfigs.flat[0])
        else:
            plot_signal(dff,time,matfile['eventlog'],[cuetimes],window,resolution_signal,clr,['Trials','dF/F (%)'],subfigs.flat[0])
            plot_events(matfile['eventlog'], lickindex, [cuetimes], window, binsize, resolution, clr, ['Trials', 'Lick rate (Hz)'], subfigs.flat[1])

        fig.savefig(os.path.join(filepath,'psth.png'))