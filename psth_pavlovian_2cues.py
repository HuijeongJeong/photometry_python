import functions.load as fnl
import functions.plot as fnp
import matplotlib.pyplot as plt
import os.path

# parameters to load data
# the structure of data folder: directory>mousename>foldername>Day
directory = 'D:/OneDrive - UCSF/Huijeong'
#directory = 'D:/OneDrive - University of California, San Francisco/Huijeong'
mouselist = ['HJ_FP_datHT_stGtACR_M3']                                          # list of mousename
foldername = 'pavlovian'                                                        # foldername under mousename folder - to describe task
daylist = []                                                                   # If you specify daylist, it will only produce plot for that days. If it is empty, it will run all days available

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
    dfffiles, _ = fnl.findfiles(os.path.join(directory, mousename, foldername), '.p', daylist)
    idx = [i for i, v in enumerate(dfffiles) if 'optotest' in v]
    dfffiles = [dfffiles[i] for i in idx]

    for iD,v in enumerate(dfffiles):
        print(v)
        psthfiles, _ = fnl.findfiles(os.path.dirname(dfffiles[iD]), '.png',[])
        #if sum([f=='psth.png' for f in [os.path.basename(x) for x in psthfiles]]) >0:
        #    continue

        matfile, _ = fnl.findfiles(os.path.dirname(dfffiles[iD]), '.mat', [])
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
        matfile = fnl.load_mat(matfile)

        filepath = os.path.dirname(v)

        dff = fnl.load_pickle(v)
        dff = dff[0]

        eventtime = matfile['eventlog'][:,1]
        eventindexseries = matfile['eventlog'][:,0]
        cuetimes = eventtime[eventindexseries==cs1index]
        #cuetimes = cuetimes[range(0,len(cuetimes),2)]

        fig = plt.figure()
        subfigs = fig.subfigures(2,1)

        fnp.plot_signal(dff['dff'],dff['time'],eventtime,eventindexseries,[cuetimes],window,resolution_signal,clr,['Trials','dF/F (%)'],subfigs.flat[0],0)
        fnp.plot_events(eventtime,eventindexseries,lickindex,[cuetimes],window,binsize,resolution,clr,['Trials','Lick rate (Hz)'],subfigs.flat[1])
        fig.savefig(os.path.join(filepath,'psth.png'))