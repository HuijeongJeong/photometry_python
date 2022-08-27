from datetime import datetime
# from dateutil.tz import tzlocal


from pynwb import NWBFile, TimeSeries, get_class, load_namespaces
from pynwb.file import Subject, LabMetaData
from pynwb.behavior import BehavioralEvents
from pynwb.spec import NWBDatasetSpec, NWBNamespaceBuilder, NWBGroupSpec

# import matplotlib.pyplot as plt
import os
import fnmatch
import pandas as pd
import scipy.io as sio

name = 'ndx-namboodiri-metadata'
ns_path = 'C://Users//Huijeong Jeong//ndx-namboodiri-metadata//spec//ndx-namboodiri-metadata.namespace.yaml'
load_namespaces(ns_path)

@register_class('LabMetaDataExtension',name)
class LabMetaDataExtension()


import numpy as np
# import pyodbc

def find_files(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


# photometry_rig_number = 1
# photometry_manufacturer = 'doric'
recording_area = 'NAcc'
# recording_coordinate = [1.3,-1.4,-4.2] #AP, ML, DV (mm)
sensor = 'dLight1.3b'
experimenter = 'Joey'

doric_channel_description = ['405', '470', 'TTL']
doric_channel_name = ['AIn-1 - Dem (AOut-1)','AIn-1 - Dem (AOut-2)','DI/O-2']
# imaging_rate = 120000. #Hz

path = 'D:\OneDrive - University of California, San Francisco\Huijeong'
session_file = find_files('sessions.csv',path)
session_data = pd.read_csv(session_file[0])

animal_name = 'HJ_FP_M9'
animal_idx = [i for i, x in enumerate(session_data['Animal ID']==animal_name) if x]
date_surgery = datetime.strptime(session_data['Date'][animal_idx[0]],'%m/%d/%y')
date_birth = datetime.strptime(session_data['DOB'][animal_idx[0]],'%m/%d/%y')

behavior_files = find_files('*.mat',path+'\\'+animal_name)
photometry_files = find_files('*.csv',path+'\\'+animal_name)

subject = Subject(
    subject_id = session_data['Serial Number'][animal_idx[0]],
    age = 'P'+str((date_surgery-date_birth).days)+'D',
    description = animal_name,
    genotype = session_data['Genotype'][animal_idx[0]],
    weight = session_data['Weight (g)'][animal_idx[0]],
    species = 'mouse',
    sex = session_data['Sex'][animal_idx[0]],
    date_of_birth = date_birth,
    strain = 'C57BL/6J'
)

iF = 0
file_create_time = os.path.getctime(photometry_files[iF].replace('.csv','.doric'))
file_create_time = datetime.fromtimestamp(file_create_time)

behavior_data = sio.loadmat(behavior_files[iF])
parameter_names = behavior_data['params'].dtype.names
parameters = behavior_data['params'].tolist()[0][0]
params = {}
for index, value in enumerate(parameter_names):
    params[value] = parameters[index].tolist()[0]

nwbfile = NWBFile(
    session_description = os.path.split(photometry_files[iF])[0].split('\\')[-2],
    #task description
    identifier = 'photometry-'+recording_area+'-'+sensor+'-'+animal_name,
    #recording method, recording area, sensor,animal name
    session_start_time = file_create_time, # time when doric file was saved
    session_id = os.path.split(photometry_files[iF])[0].split('\\')[-1],
    experimenter = experimenter,
    lab = 'Namboodiri lab',
    institution = 'University of California, San Francisco'
)

# device = nwbfile.create_device(
#     name = 'photometry',
#     description = 'photometry'+str(photometry_rig_number),
#     manufacturer = photometry_manufacturer
# )

photometry_data = pd.read_csv(photometry_files[iF])
for iCh in range(len(doric_channel_description)):
    if iCh==len(doric_channel_description)-1:
        name = doric_channel_description[iCh]
    else:
        name = doric_channel_description[iCh]+'nm'
    time_series = TimeSeries(
        name = name,
        data = photometry_data[doric_channel_name[iCh]].tolist(),
        unit = 'mV',
        timestamps = photometry_data['Time(s)'].tolist()
    )
    nwbfile.add_acquisition(time_series)

behavior_module = nwbfile.create_processing_module(
    name = 'behavior',
    description = 'processed behavior data'
)

eventlog = behavior_data['eventlog']
time_series = TimeSeries(
    name = 'eventlog',
    data = eventlog[:,1:],
    timestamps = eventlog[:,0],
    description = 'column1,event code; column2,nonsolenoid flag',
    unit = 'ms'
)
eventlog = BehavioralEvents(time_series=time_series, name = 'EventLog')
behavior_module.add(eventlog)


# with NWBHDF5IO('behavior_data.nwb')

# imaging_plane = nwbfile.create_imaging_plane(
#     name = 'ImagingPlane',
#     optical_channel = optical_channel,
#     imaging_rate = imaging_rate,
#     description = recording_area,
#     device = device,
#     excitation_lambda = optical_emission,
#     indicator = sensor,
#     location = recording_area,
#     grid_spacing= [np.nan],
#     grid_spacing_unit= 'none',
#     origin_coords= recording_coordinate,
#     origin_coords_unit= 'micrometer'
# )
#
# rt_region = ps.create_roi_table_region(
#     region=[0, 1],
#     description='the first of two ROIs'
# )
#
# photometry_module = nwbfile.create_processing_module(
#     name='photometry',
#     description='photometry data'
# )
#
# img_seg = ImageSegmentation()
#
# ps = img_seg.create_plane_segmentation(
#     name='PlaneSegmentation',
#     description='photometry data does not need plan segmentation',
#     imaging_plane=imaging_plane,
# )
# photometry_module.add(img_seg)
#
# rt_channel = ps.create_roi_table_region(
#     region=[0, 1],
#     description='two different channels' #405nm and 470nm
# )


# img_seg = ImageSegmentation()
# ps = img_seg.create_plane_segmentation(
#     name='PlaneSegmentation',
#     description='output from segmenting my favorite imaging plane',
#     imaging_plane=imaging_plane,
# )
#
# ps = img_seg.create_plane_segmentation(
#     name='PlaneSegmentation',
#     description='output from segmenting my favorite imaging plane',
#     imaging_plane=imaging_plane,
#     reference_images=image_series1  # optional
# )
#
# ophys_module.add(img_seg)
#
# data = pd.read_csv(photometry_file[iF])
#
#
#
# nwbfile.ophys.RoiResponseSeries(
#     name = recording_method+'data',
#     data = data[['AIn-1 - Dem (AOut-1)','AIn-1 - Dem (AOut-2)']],
#     unit = 'mV',
#     roi =
# )