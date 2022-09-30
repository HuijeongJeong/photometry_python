def flatten(lst):
    a = [item for sublist in lst for item in sublist]
    return a

def movmean(lst,n,step,dim):
    import numpy as np
    if dim == 0:
        a = [[np.nanmean(lst[np.arange(0, n) + i, j]) for i in range(0, len(lst) - step + 1, step)]
             for j in range(0, np.size(lst, 1))]
    elif dim == 1:
        a = [[np.nanmean(lst[j,np.arange(0,n)+i]) for i in range(0,len(lst)-step+1,step)]
             for j in range(0, np.size(lst, 0))]
    return a

def peaksearch(lst,threshold,option):
    import numpy as np
    if len(threshold) == 1:
        threshold = np.repeat(threshold, len(lst))

    peakidx = [[i for i, v in enumerate(lst[j]) if v > threshold[j]] for j in range(0, np.size(lst, 0))]
    peakval = [[v for i, v in enumerate(lst[j]) if v > threshold[j]] for j in range(0, np.size(lst, 0))]

    if option != 'nan':
        if option == 'max':
            tempidx = [np.argmax(x) for x in peakval]
        elif option == 'first':
            tempidx = np.repeat(0, len(lst))
        elif option == 'last':
            tempidx = np.repeat(-1, len(lst))
        peakidx = [x[y] for x, y in zip(peakidx, tempidx)]
        peakval = [x[y] for x, y in zip(peakval, tempidx)]

    return peakidx, peakval

