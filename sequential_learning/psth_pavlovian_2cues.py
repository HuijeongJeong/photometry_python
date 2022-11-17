from functions.load import *
from functions.plot import *
from functions.photometry import *
import matplotlib.pyplot as plt
import os.path

# parameters to load data
# the structure of data folder: directory>mousename>foldername>Day
#directory = 'D:/OneDrive - UCSF/Huijeong'
directory = 'D:/OneDrive - University of California, San Francisco/Huijeong'
mouselist = ['HJ_FP_datHT_stGtACR_M3']                                          # list of mousename
foldername = 'pavlovian'                                                        # foldername under mousename folder - to describe task
daylist = []                                                                   # If you specify daylist, it will only produce plot for that days. If it is empty, it will run all days available

# parameters for photometry data
version = 5                                                                             # version of doric software; for the future when we update software version
doricdatanames = ['AIn-1 - Dem (AOut-1)', 'AIn-1 - Dem (AOut-2)', 'DI--O-1','DI--O-2']  # data name saved in doric file (version 5)
ppddatanames = ['analog_1','analog_2','digital_1','digital_2']                          # data name saved in ppd file
datanames_new = ['405', '470', 'ttl1', 'ttl2']                                          # new data name for new photometry data structure
binsize_interpolation = 10                                                              # interpolation bin size for photometry data; if it is zero, not doing interpolation

# event index
lickindex = 5
cs1index = 15

# parameters for plot
window = [-2000,10000]                                                          # time window for plot
binsize = 10                                                                    # bin size for lick psth
resolution_signal = 0                                                           # convoluting resolution for photometry data
resolution = 5                                                                  # convolution resolution for lick; sigma = binsize*resolution
clr = ['black']

for mousename in mouselist:
    dfffiles, _ = findfiles(os.path.join(directory, mousename, foldername), '.p', daylist)
    idx = [i for i, v in enumerate(dfffiles) if 'optotest' in v]
    dfffiles = [dfffiles[i] for i in idx]

    for iD,v in enumerate(dfffiles):
        print(v)
        psthfiles, _ = findfiles(os.path.dirname(dfffiles[iD]), '.png',[])
        if sum([f=='psth.png' for f in [os.path.basename(x) for x in psthfiles]]) >0:
            continue

        matfile, _ = findfiles(os.path.dirname(dfffiles[iD]), '.mat', [])
        if len(matfile)==0:
            print('no event file!')
            continue
        elif len(matfile)>1:
            print('there are more than one event file.\n')
            print(matfile)
            matfileidx = input('please specify the correct one or enter none if you want to skip.\n')
            if matfileidx=='none':
                continue
            else:
                matfile = matfile[int(matfileidx)]
        else:
            matfile = matfile[0]
        filepath = os.path.dirname(matfile)
        matfile = load_mat(matfile)

        filepath = os.path.dirname(v)

        dff = load_pickle(v)
        dff = dff[0]

        cuetimes = matfile['eventlog'][matfile['eventlog'][:,0]==cs1index,1]
        #cuetimes = cuetimes[range(0,len(cuetimes),2)]

        fig = plt.figure()
        subfigs = fig.subfigures(2,1)

        plot_signal(dff['dff'],dff['time'],matfile['eventlog'],[cuetimes],window,resolution_signal,clr,['Trials','dF/F (%)'],subfigs.flat[0])
        plot_events(matfile['eventlog'],lickindex,[cuetimes],window,binsize,resolution,clr,['Trials','Lick rate (Hz)'],subfigs.flat[1])
        fig.savefig(os.path.join(filepath,'psth.png'))