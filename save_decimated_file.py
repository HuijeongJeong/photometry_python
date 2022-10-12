from functions.load import *
from functions.photometry import *
import os
import pickle

directory = 'D:\OneDrive - University of California, San Francisco\Huijeong'
dathetlist = ['M2','M3','M4','M5','M6','M7']
datwtlist = ['F1']
wtlist = ['F1','F2','F3','M1','M2','M3']
#mouselist = ['HJ_FP_datHT_stGtACR_'+i for i in dathetlist] + ['HJ_FP_datWT_stGtACR_'+i for i in datwtlist]\
#            + ['HJ_FP_WT_stGtACR_'+i for i in wtlist]
mouselist = ['HJ_FP_WT_stGtACR_M3']
foldername = 'pavlovian'
daylist = [6]

version = 5
doricdatanames = ['AIn-1 - Dem (AOut-1)', 'AIn-1 - Dem (AOut-2)', 'DI--O-1','DI--O-2']
ppddatanames = ['analog_1','analog_2','digital_1','digital_2']
datanames_new = ['405', '470', 'ttl1', 'ttl2']
binsize_interpolation = 10

cs1index = 15

for im,mousename in enumerate(mouselist):
    photometryfiles, _ = findfiles(os.path.join(directory,mousename,foldername), ['.doric', '.ppd'], daylist)
    #idx = [i for i,v in enumerate(photometryfiles) if 'optotest' in v]
    #photometryfiles = [photometryfiles[i] for i in idx]
    for iD,v in enumerate(photometryfiles):
        print(v)
        try:
            matfile, _ = findfiles(os.path.dirname(v),'.mat',[])
            matfile = load_mat(matfile[0])

            if '.doric' in v:
                photometryfile = load_doric(v, version, doricdatanames, datanames_new)
            elif '.ppd' in v:
                photometryfile = load_ppd(v, ppddatanames, datanames_new)

            dff, time = preprocessing(photometryfile, matfile, binsize_interpolation,cs1index)
            data = {'dff':dff,'time':time}
            pickle.dump(data, open(os.path.join(os.path.dirname(v),mousename+'_dff.p'),'wb'))

        except:
            print('an error occurred')
