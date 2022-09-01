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

def synchronize_timestamps(doricfile,matfile):
    import numpy as np
    window_doric = [i for i, v in enumerate(np.diff(doricfile['ttl1'])) if (v==1) | (v==-1)]
    window_doric[0] = window_doric[0]+1
    window_doric = doricfile['time'][window_doric]

    window_mat = [0, matfile['eventlog'][matfile['eventlog'][:,0]==0,1][0]]

    newtime = (doricfile['time']-window_doric[0])*np.diff(window_mat)/np.diff(window_doric)
    return newtime

def preprocessing(doricfile,matfile,binsize_interpolation):
    mat_endtime = matfile['eventlog'][matfile['eventlog'][:,0]==0,1][0]
    doricfile['time'] = synchronize_timestamps(doricfile,matfile)
    dff,time = calculate_dff(doricfile['405'], doricfile['470'], doricfile['time'], [0, mat_endtime], binsize_interpolation)
    return dff, time
