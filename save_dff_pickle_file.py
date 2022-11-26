import functions.load as fnl
import functions.photometry as fnp
import os
import pickle

directory = 'D:\OneDrive - University of California, San Francisco\Huijeong'
dathetlist = ['M2','M3','M4','M5','M6','M7']
datwtlist = ['F1']
wtlist = ['F1','F2','F3','M1','M2','M3']
mouselist = ['HJ_FP_datHT_stGtACR_'+i for i in dathetlist] + ['HJ_FP_datWT_stGtACR_'+i for i in datwtlist]\
            + ['HJ_FP_WT_stGtACR_'+i for i in wtlist]
foldername = 'pavlovian'
daylist = [6]

version = 5
doricdatanames = ['AIn-1 - Dem (AOut-1)', 'AIn-1 - Dem (AOut-2)', 'DI--O-1','DI--O-2'] # what saved in doric raw file
ppddatanames = ['analog_1','analog_2','digital_1','digital_2'] # what saved in pyphotometry raw file
# what we will generally call - 405nm (isosbestic), 470nm (actual signal), ttl1 (session onset/offset),
# ttl2 (cue or reward time - it depends on task type eg., it is reward time in randomreward task, but it is cue time in most other tasks)
datanames_new = ['405', '470', 'ttl1', 'ttl2']
# binsize of final dff; unit in ms; this is for making all photometry files
# (the one with decimation or not, the one from doric or pyphotomtry) to have same binsize
binsize_interpolation = 10

# this is event index of your ttl2 - need to be changed according to task
cs1index = 15

for im,mousename in enumerate(mouselist):
    photometryfiles, _ = fnl.findfiles(os.path.join(directory,mousename,foldername), ['.doric', '.ppd'], daylist)
    for iD,v in enumerate(photometryfiles):
        print(v)
        try:
            # load matlab task file
            matfile, _ = fnl.findfiles(os.path.dirname(v),'.mat',[])
            matfile = fnl.load_mat(matfile[0])

            # load photometry file
            if '.doric' in v: # the one from doric system
                photometryfile = fnl.load_doric(v, version, doricdatanames, datanames_new)
            elif '.ppd' in v: # the one from pyphotometry system
                photometryfile = fnl.load_ppd(v, ppddatanames, datanames_new)

            # saving pickle file that has dff and synchronized timestamps
            dff, time = fnp.preprocessing(photometryfile, matfile, binsize_interpolation,cs1index)
            data = {'dff':dff,'time':time}
            pickle.dump(data, open(os.path.join(os.path.dirname(v),mousename+'_dff.p'),'wb'))

        except:
            print('an error occurred')
