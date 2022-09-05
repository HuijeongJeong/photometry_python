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

#@register_class('LabMetaDataExtension',name)
#class LabMetaDataExtension()


import numpy as np
# import pyodbc

def find_files(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


recording_area = 'NAcc'
sensor = 'dLight1.3b'
experimenter = 'Joey'

doric_channel_description = ['405', '470', 'TTL']
doric_channel_name = ['AIn-1 - Dem (AOut-1)','AIn-1 - Dem (AOut-2)','DI/O-2']

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

