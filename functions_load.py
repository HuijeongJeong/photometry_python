def findfiles(directory,mousename,fileformat,daylist):
	import os
	def days(doricfile):
		return int(os.path.dirname(doricfile).split('Day')[-1])

	files = [os.path.join(root, name)
			 for root, dirs, files in os.walk(os.path.join(directory, mousename))
			 for name in files
			 if name.endswith(fileformat)]
	files = sorted(files, key=days)

	if len(daylist)>0:
		outdaylist = [i for i,v in enumerate(days) if v not in daylist]
		files.remove(outdaylist)

	return files


def load_mat(filename):
	import numpy as np
	from scipy.io import loadmat, matlab

	"""
    This function should be called instead of direct scipy.io.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    """

	def _check_vars(d):
		"""
        Checks if entries in dictionary are mat-objects. If yes
        todict is called to change them to nested dictionaries
        """
		for key in d:
			if isinstance(d[key], matlab.mat_struct):
				d[key] = _todict(d[key])
			elif isinstance(d[key], np.ndarray):
				d[key] = _toarray(d[key])
		return d

	def _todict(matobj):
		"""
        A recursive function which constructs from matobjects nested dictionaries
        """
		d = {}
		for strg in matobj._fieldnames:
			elem = matobj.__dict__[strg]
			if isinstance(elem, matlab.mat_struct):
				d[strg] = _todict(elem)
			elif isinstance(elem, np.ndarray):\
				d[strg] = _toarray(elem)
			else:
				d[strg] = elem
		return d
	def _toarray(ndarray):
		"""
        A recursive function which constructs ndarray from cellarrays
        (which are loaded as numpy ndarrays), recursing into the elements
        if they contain matobjects.
        """
		if ndarray.dtype != 'float64':
			elem_list = []
			for sub_elem in ndarray:
				if isinstance(sub_elem, matlab.mat_struct):
					elem_list.append(_todict(sub_elem))
				elif isinstance(sub_elem, np.ndarray):
					elem_list.append(_toarray(sub_elem))
				else:
					elem_list.append(sub_elem)
			return np.array(elem_list)
		else:
			return ndarray

	data = loadmat(filename, struct_as_record=False, squeeze_me=True)
	return _check_vars(data)

def load_doric(filename,version,datanames,datanames_new):
	import h5py
	import numpy as np

	def ish5dataset(item):
		return isinstance(item, h5py.Dataset)

	def h5getDatasetR(item, leading=''):
		r = []
		for key in item:
			# First have to check if the next layer is a dataset or not
			firstkey = list(item[key].keys())[0]
			if ish5dataset(item[key][firstkey]):
				r = r + [{'Name': leading + '_' + key, 'Data':
					[{'Name': k, 'Data': np.array(item[key][k]),
					  'DataInfo': {atrib: item[key][k].attrs[atrib] for atrib in item[key][k].attrs}} for k in
					 item[key]]}]
			else:
				r = r + h5getDatasetR(item[key], leading + '_' + key)

		return r

	# Extact Data from a doric file
	def ExtractDataAcquisition(filename, version):
		# version: doric neuroscience studio version
		output = {}
		with h5py.File(filename, 'r') as h:
			# print(filename)
			if version == 5:
				return h5getDatasetR(h['Traces'], filename)
			elif version == 6:
				return h5getDatasetR(h['DataAcquisition'], filename)

	doricfile = [data["Data"][0] for data in ExtractDataAcquisition(filename,version)]
	data = {}
	if version == 5:
		data['time'] = [data["Data"] for data in doricfile if data["Name"] == 'Console_time(s)'][0]
	for i, v in enumerate(datanames):
		if version == 5:
			data[datanames_new[i]] = [data["Data"] for data in doricfile if data["Name"] == v][0]

	return data