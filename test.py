import functions_load as fl
import functions_plot as fp
import functions_photometry as fpt
import matplotlib.pyplot as plt
import numpy as np

directory = 'D:/OneDrive - University of California, San Francisco/Huijeong'
mousename = 'HJ_FP_datWT_stGtACR_F1'
daylist = []

doricfiles = fl.findfiles(directory, mousename, '.doric', daylist)
matfiles = fl.findfiles(directory, mousename, '.mat', daylist)
version = 5
doricdatanames = ['AIn-1 - Dem (AOut-1)', 'AIn-1 - Dem (AOut-2)', 'DI--O-1','DI--O-2']
doricdatanames_new = ['405', '470', 'ttl1', 'ttl2']

iD = 0
doricfile = fl.load_doric(doricfiles[iD], version, doricdatanames, doricdatanames_new)
matfile = fl.load_mat(matfiles[iD])

binsize_interpolation = 100/1000 # if binsize_interpolation is zero, not doing interpolation
dff, time = fpt.preprocessing(doricfile, matfile, binsize_interpolation)

eventindex = 5
referenceindex = [7]
window = [-2000,5000]
binsize = 10
resolution_signal = 0
resolution = 5
clr = ['blue']
ylabels_signal = ['Trials','dF/F (%)']
ylabels = ['Trials','Lick rate (Hz)']

fig = plt.figure()
subfigs = fig.subfigures(2,1)
fp.plot_signal(dff,time,matfile['eventlog'],referenceindex,window,resolution_signal,clr,ylabels_signal,subfigs.flat[0])
fp.plot_events(matfile['eventlog'],eventindex,referenceindex,window,binsize,resolution,clr,ylabels,subfigs.flat[1])
plt.show()
