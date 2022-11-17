from functions.load import *
from functions.plot import *
import matplotlib.pyplot as plt
import os.path



plt.rcParams['axes.titlesize'] = 10
plt.rcParams['axes.labelsize'] = 8
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 8
plt.rcParams['legend.labelspacing'] = 0.2
plt.rcParams['axes.labelpad'] = 2
plt.rcParams['axes.linewidth'] = 0.35
plt.rcParams['xtick.major.size'] = 1
plt.rcParams['xtick.major.width'] = 0.35
plt.rcParams['xtick.major.pad'] = 3
plt.rcParams['ytick.major.size'] = 1
plt.rcParams['ytick.major.width'] = 0.35
plt.rcParams['ytick.major.pad'] = 2
plt.rcParams['lines.scale_dashes'] = False
plt.rcParams['lines.dashed_pattern'] = (2, 1)
plt.rcParams['font.sans-serif'] = ['Helvetica']
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['text.color'] = 'k'

cm = 1/2.54

# parameters to load data
# the structure of data folder: directory>mousename>foldername>Day
directory = 'D:/OneDrive - University of California, San Francisco/Huijeong'
mouselist = ['HJ_FP_datHT_stGtACR_M8']                                          # list of mousename
foldername = 'pavlovian'                                                        # foldername under mousename folder - to describe task
daylist = [2]                                                                   # If you specify daylist, it will only produce plot for that days. If it is empty, it will run all days available

# event index
lickindex = 5
cs1index = 15

# parameters for plot
window = [-2000,10000]                                                          # time window for plot
binsize = 10                                                                    # bin size for lick psth
resolution_signal = 2                                                           # convoluting resolution for photometry data
resolution = 5                                                                  # convolution resolution for lick; sigma = binsize*resolution
clr = ['black']

for mousename in mouselist:
    dfffiles, _ = findfiles(os.path.join(directory, mousename, foldername), '.p', daylist)

    for iD,v in enumerate(dfffiles):
        print(v)
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
        cuetimes = cuetimes[range(0,100,2)]
        fig = plt.figure(figsize=(4.2*cm,3.2*cm))
        subfigs = fig.subfigures(1,2)

        ax1, ax2, im = plot_signal(dff['dff'],dff['time'],matfile['eventlog'],[cuetimes],window,resolution_signal,clr,['Trial','DF/F (%)'],subfigs.flat[1],1)
        ax1.plot([1.5, 1.5],[0, 50],'k:',linewidth=0.35)
        ax1.plot([3, 3],[0, 50],'k:',linewidth=0.35)
        ax2.plot([1.5, 1.5], [-1.5, 1.5], 'k:', linewidth=0.35)
        ax2.plot([3, 3], [-1.5, 1.5], 'k:', linewidth=0.35)
        ax1.set_yticks([1, 50])
        ax2.set_yticks([-1, 0, 1])
        im.set_clim([-1, 1])
        ax1.set_xticks([0,3,6,9],[])
        ax2.set_xticks([0,3,6,9])
        ax2.set_ylim([-1.5,1])

        ax3, ax4 = plot_events(matfile['eventlog'],lickindex,[cuetimes],window,50,2,clr,['Trial','Lick (Hz)'],subfigs.flat[0])
        ax3.plot([1.5, 1.5], [0, 50], 'k:', linewidth=0.35)
        ax3.plot([3, 3], [0, 50], 'k:', linewidth=0.35)
        ax4.plot([1.5, 1.5], [-1,10], 'k:', linewidth=0.35)
        ax4.plot([3, 3], [-1,10], 'k:', linewidth=0.35)
        ax3.set_yticks([1, 50])
        ax4.set_yticks([0,5,10])
        ax3.set_xticks([0, 3, 6, 9], [])
        ax4.set_xticks([0, 3, 6, 9])
        fig.savefig(os.path.dirname(directory)+'//figures\manuscript\dopamine_contingency//revision//example_psth_m8.pdf',bbox_inches='tight')
