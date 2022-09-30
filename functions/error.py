def merge_multiple_eventlogs(mousename,directory,foldername,daylist,ttl2matindex):
    import functions.load as load
    import os.path
    import numpy as np
    from scipy.io import savemat

    def time(matfile):
        return int(matfile.split('.mat')[0][-6:])

    version = 5
    doricdatanames = ['AIn-1 - Dem (AOut-1)', 'AIn-1 - Dem (AOut-2)', 'DI--O-1','DI--O-2']
    ppddatanames = ['analog_1','analog_2','digital_1','digital_2']
    datanames_new = ['405', '470', 'ttl1', 'ttl2']

    photometryfiles,_ = load.findfiles(directory, mousename, ['.doric', '.ppd'], foldername, daylist)
    matfiles,_ = load.findfiles(directory, mousename, '.mat', foldername, daylist)
    matfiles = sorted(matfiles,key=time)

    if '.doric' in photometryfiles[0]:
        photometryfile = load.load_doric(photometryfiles[0], version, doricdatanames, datanames_new)
    elif '.ppd' in photometryfiles[0]:
        photometryfile = load.load_ppd(photometryfiles[0], ppddatanames, datanames_new)

    i = 0
    matfile = load.load_mat(matfiles[i])
    ref_doric = [i + 1 for i, v in enumerate(np.diff(photometryfile['ttl2'])) if v == 1]
    ref_mat = matfile['eventlog'][matfile['eventlog'][:, 0] == ttl2matindex, 1]
    window_mat = [ref_mat[0], ref_mat[-1]]
    window_doric = [ref_doric[0], ref_doric[len(ref_mat)-1]]
    window_doric = photometryfile['time'][window_doric]
    newtime = (photometryfile['time'] - window_doric[0]) * np.diff(window_mat) / np.diff(window_doric) + window_mat[0]
    neweventlog = matfile['eventlog']
    params = matfile['params']

    for i,v in enumerate(matfiles[1:]):
        start_doric = [ii + 1 for ii, vv in enumerate(np.diff(photometryfile['ttl1'])) if vv == 1]
        end_doric = [ii for ii, vv in enumerate(np.diff(photometryfile['ttl1'])) if vv == -1]
        matfile = load.load_mat(v)
        window_doric = [start_doric[i+1], end_doric[i+1]]
        window_doric = newtime[window_doric]
        window_mat = [0, matfile['eventlog'][matfile['eventlog'][:, 0] == 0, 1][0]]
        matfile['eventlog'][:,1] = matfile['eventlog'][:,1]*np.diff(window_doric)/np.diff(window_mat) + window_doric[0]
        neweventlog = np.append(neweventlog,matfile['eventlog'],axis=0)

    mdic = {'eventlog':neweventlog, 'params':params}
    savemat(os.path.join(os.path.dirname(matfiles[0]),'fixed_'+mousename+matfiles[-1].split(mousename)[-1]),mdic)
