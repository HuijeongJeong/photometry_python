import os
from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, export_spec

def main():
    ns_builder = NWBNamespaceBuilder(
        doc='type for storing metadata for Namboodiri lab',
        name='ndx-namboodiri-metadata',
        version='0.1.0',
        author=['Huijeong Jeong'],
        contact=['huijeong.jeong00@gmail.com']
    )

    ns_builder.include_type('LabMetaData', namespace='core')

    LabMetaDataExtension = NWBGroupSpec(
        doc='type for storing metadata for Namboodiri lab',
        neurodata_type_def='LabMetaDataExtension',
        neurodata_type_inc='LabMetaData',
    )

    ParamsExtension = NWBGroupSpec(
        doc='type for storing task parameters',
        neurodata_type_def='ParamsExtension',
        neurodata_type_inc='LabMetaData',
    )

    param_attr = [('numtrials', 'int'), ('CSfreq', 'int'), ('CSsolenoid', 'int'),
                ('CSprob', 'int'), ('CSopentime', 'int'), ('CSdur', 'int'),
                ('CS_t_fxd', 'int'), ('CSpulse', 'bool'), ('CSspeaker', 'int'),
                ('golickreq', 'bool'), ('golicktube', 'int'),
                ('CSsignal', 'int'), ('meanITI', 'int'),('maxITI','int'),
                ('minITI', 'int'), ('intervaldistribution', 'text'),
                ('mindelaybgdtocue', 'int'), ('mindelayfxdtobgd','int'), ('experimentmode','int'),
                ('trialbytrialbgdsolenoidflag', 'bool'), ('totPoisssolenoid', 'int'),
                ('reqlicknum', 'int'), ('licksolenoid', 'int'),('lickprob','int'),
                ('lickopentime', 'int'), ('delaytoreward', 'int'),('delaytolick','int'),
                ('minrewards', 'int'), ('signaltolickreq', 'int'), ('soundsignalpulse', 'bool'),
                ('soundfreq', 'int'),('sounddur', 'int'), ('lickspeaker', 'int'),
                ('laserlatency', 'int'), ('laserduration','int'), ('randlaserflag','bool'),
                ('laserpulseperiod', 'int'), ('laserpulseoffperiod', 'int'),('lasertrialbytrialflag','bool'),
                ('maxdelaycuetovacuum', 'int'), ('CSlight', 'int'), ('variableratioflag', 'bool'),
                ('variableintervalflag','bool'),('licklight', 'int'), ('CS1lasercheck', 'bool'),
                ('CS2lasercheck', 'bool'), ('CS3lasercheck','bool'), ('CS4lasercheck','bool'),
                ('fixedsidecheck', 'bool'), ('Rewardlasercheck', 'bool'), ('CSrampmaxdelay', 'int'),
                ('CSrampexp', 'int'), ('CSincrease', 'int'),
                ('delaybetweensoundandlight', 'int'), ('CSsecondcue', 'int'), ('CSsecondcuefreq', 'int'),
                ('CSsecondcuespeaker', 'int'), ('CSsecondcuelight', 'int')]
    for attr in param_attr:
        ParamsExtension.add_attribute(
            name=attr[0],
            doc='params information',
            dtype=attr[1],
            required=False
        )

    LabMetaDataExtension.add_group(
        name='params',
        neurodata_type_inc='ParamsExtension',
        doc='type for storing task parameters',
    )

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','ndx-namboodiri-metadata', 'spec'))
    export_spec(ns_builder, [LabMetaDataExtension,ParamsExtension], output_dir)

if __name__ == "__main__":
    main()