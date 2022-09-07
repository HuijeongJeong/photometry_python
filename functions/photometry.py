def calculate_dff(data_405,data_470,time,window,binsize_interpolation):
    # if binsize_interpolation is zero, not doing interpolation
    import numpy as np
    inwindow = (time>=window[0]) & (time<=window[1])
    coef = np.polyfit(data_405[inwindow],data_470[inwindow],1)
    fitted_405 = np.polyval(coef,data_405)
    dff = (data_470-fitted_405)*100/fitted_405

    if binsize_interpolation>0:
        import scipy.interpolate as interpolate
        f = interpolate.interp1d(time,dff)
        newtime = np.arange(time[0], time[-1], binsize_interpolation)
        newdata = f(newtime)
        dff = newdata
        time = newtime
    return dff, time

def synchronize_timestamps(photometryfile,matfile,ttl2matindex):
    import numpy as np
    start_doric = [i+1 for i, v in enumerate(np.diff(photometryfile['ttl1'])) if v==1]
    end_doric = [i for i, v in enumerate(np.diff(photometryfile['ttl1'])) if v==-1]
    window_doric = start_doric+end_doric
    window_doric = photometryfile['time'][window_doric]

    window_mat = [0, matfile['eventlog'][matfile['eventlog'][:,0]==0,1][0]]

    if len(window_doric)!=2 or len(window_mat)!=2:
        ref_doric = [i+1 for i,v in enumerate(np.diff(photometryfile['ttl2'])) if v==1]
        ref_mat = matfile['eventlog'][matfile['eventlog'][:,0]==ttl2matindex,1]
        if len(ref_doric)<len(ref_mat):
            if len(start_doric)==0:
                ref_mat = ref_mat[-len(ref_doric):]
            elif len(end_doric)==0:
                ref_mat = ref_mat[:len(ref_doric)]
        window_doric = [ref_doric[0], ref_doric[-1]]
        window_doric = photometryfile['time'][window_doric]
        window_mat = [ref_mat[0], ref_mat[-1]]


    newtime = (photometryfile['time'] - window_doric[0]) * np.diff(window_mat) / np.diff(window_doric) + window_mat[0]

    return newtime

def preprocessing(photometryfile,matfile,binsize_interpolation,ttl2matindex):
    mat_endtime = matfile['eventlog'][matfile['eventlog'][:,0]==0,1][0]
    photometryfile['time'] = synchronize_timestamps(photometryfile,matfile,ttl2matindex)
    dff,time = calculate_dff(photometryfile['405'], photometryfile['470'], photometryfile['time'], [0, mat_endtime], binsize_interpolation)
    return dff, time
