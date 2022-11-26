def calculate_dff(data_405,data_470,time,window,binsize_interpolation):
    # if binsize_interpolation is zero, not doing interpolation
    import numpy as np
    # only use the data within window (task time) for calculating coefficient
    # this is to cut out some initial part with non-linear decrease of fluorescence
    inwindow = (time>=window[0]) & (time<=window[1])
    # fit 405 signal to 470, and find coefficients
    coef = np.polyfit(data_405[inwindow],data_470[inwindow],1)
    # calculated fitted 405
    fitted_405 = np.polyval(coef,data_405)
    # subtract fitted 405 from 470 and then divide it by fitted 405 - this is dff
    dff = (data_470-fitted_405)*100/fitted_405

    # if binsize_interpolation is larger than 0, interpolate dff with desired bin size
    if binsize_interpolation>0:
        import scipy.interpolate as interpolate
        f = interpolate.interp1d(time,dff)
        newtime = np.arange(time[0], time[-1], binsize_interpolation)
        newdata = f(newtime)
        dff = newdata
        time = newtime
    return dff, time

def synchronize_timestamps(photometryfile,matfile,ttl2matindex):
    # synchronizing timestmaps of photometry file to the timestamps of mat file
    import numpy as np

    # find photometry window - only use timepoints during the session on
    start_pf = [i+1 for i, v in enumerate(np.diff(photometryfile['ttl1'])) if v==1]
    end_pf = [i for i, v in enumerate(np.diff(photometryfile['ttl1'])) if v==-1]
    window_pf= start_pf+end_pf
    window_pf = photometryfile['time'][window_pf]

    window_mat = [0, matfile['eventlog'][matfile['eventlog'][:,0]==0,1][0]]

    # when there's some error...
    # like photometry file doesn't have onset and offset of session in ttl1 or session end time is missing in mat file
    # use ttl2 to sync timestamps
    if len(window_pf)!=2 or np.diff(window_mat)==0:
        ref_doric = [i+1 for i,v in enumerate(np.diff(photometryfile['ttl2'])) if v==1]
        ref_mat = matfile['eventlog'][matfile['eventlog'][:,0]==ttl2matindex,1]
        if len(ref_doric)<len(ref_mat):
            if len(start_pf)==0:
                ref_mat = ref_mat[-len(ref_doric):]
            elif len(end_pf)==0:
                ref_mat = ref_mat[:len(ref_doric)]
        window_pf = [ref_doric[0], ref_doric[-1]]
        window_pf = photometryfile['time'][window_pf]
        window_mat = [ref_mat[0], ref_mat[-1]]

    # this is new synchronized timestamps of photometry file
    newtime = (photometryfile['time'] - window_pf[0]) * np.diff(window_mat) / np.diff(window_pf) + window_mat[0]

    return newtime

def preprocessing(photometryfile,matfile,binsize_interpolation,ttl2matindex):
    # this function synchronize timestamps and calculate dff
    # session end time recorded in mat file
    mat_endtime = matfile['eventlog'][matfile['eventlog'][:,0]==0,1][0]
    if mat_endtime==0: # when there's a error..
        mat_endtime = matfile['eventlog'][matfile['eventlog'][:,0]==ttl2matindex,1][-1]

    # save synchronized timestamps of photometry file
    photometryfile['time'] = synchronize_timestamps(photometryfile,matfile,ttl2matindex)

    # calculate dff
    dff,time = calculate_dff(photometryfile['405'], photometryfile['470'], photometryfile['time'], [0, mat_endtime], binsize_interpolation)
    return dff, time
