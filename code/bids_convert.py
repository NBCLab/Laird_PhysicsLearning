import os
import os.path as op
from glob import glob
from nipype.interfaces.dcm2nii import Dcm2niix
import shutil
import pandas as pd
from pydeface.utils import deface_image

raw_dir = '/home/data/nbc/DICOM/ALAI_NSF_14-007'
bids_dir = '/home/data/nbc/Laird_PhysicsLearning/dset'
work_dir = '/scratch/miriedel'

dir_ignore = ['DicomFileLists.py', 'F_14_007_321', 'PILOT1', 'PILOT2', 'PILOT3', 'PILOT4', 'PILOT5', 'summary']
subs = os.listdir(raw_dir)
subs = sorted([x for x in subs if x not in dir_ignore])
participant_id = ['sub-{0}'.format(sub) for sub in subs]
participants_df = pd.DataFrame()
participants_df['participant_id'] = participant_id
participants_df.to_csv(op.join(bids_dir, 'participants.tsv'), sep='\t', index=False)

converter = Dcm2niix()
converter.inputs.bids_format = True
converter.inputs.anon_bids = True
converter.inputs.compress = 'y'

for sub in subs:
    sess = sorted(os.listdir(op.join(raw_dir, sub)))

    for i, ses in enumerate(sess):

        anat_dir = op.join(bids_dir, 'sub-{subject}'.format(subject=sub), 'ses-{session}'.format(session=i), 'anat')
        os.makedirs(anat_dir)
        converter.inputs.output_dir = anat_dir

        t1s = sorted(glob(op.join(raw_dir, sub, ses, '*PU:3D_T1_Sag-Structural*')))
        if not t1s:
            t1s = sorted(glob(op.join(raw_dir, sub, ses, '*3D_T1_Sag-Structural*')))
        for j, t1 in enumerate(t1s):
            shutil.copytree(t1, op.join(work_dir, 'tmp'))
            t1_fn = 'sub-{subject}_ses-{session}_run-{run}_T1w'.format(subject=sub, session=i, run=j)
            converter.inputs.source_dir = op.join(work_dir, 'tmp')
            converter.inputs.out_filename = t1_fn
            converter.run()
            shutil.rmtree(op.join(work_dir, 'tmp'))
            deface_image(infile=op.join(anat_dir, '{0}.nii.gz'.format(t1_fn)),
                         outfile=op.join(anat_dir, '{0}.nii.gz'.format(t1_fn)),
                         force=True,
                         forcecleanup=True,
                         verbose=False)

        func_dir = op.join(bids_dir, 'sub-{subject}'.format(subject=sub), 'ses-{session}'.format(session=i), 'func')
        os.makedirs(func_dir)
        converter.inputs.output_dir = func_dir

        fcis = sorted(glob(op.join(raw_dir, sub, ses, '*FCI*')))
        for j, fci in enumerate(fcis):
            fci_fn = 'sub-{subject}_ses-{session}_task-fci_run-{run}_bold'.format(subject=sub, session=i, run=j)
            converter.inputs.source_dir = fci
            converter.inputs.out_filename = fci_fn
            converter.run()

        retrs = sorted(glob(op.join(raw_dir, sub, ses, '*RETR*')))
        for j, retr in enumerate(retrs):
            retr_fn = 'sub-{subject}_ses-{session}_task-retr_run-{run}_bold'.format(subject=sub, session=i, run=j)
            converter.inputs.source_dir = retr
            converter.inputs.out_filename = retr_fn
            converter.run()

        reass = sorted(glob(op.join(raw_dir, sub, ses, '*REAS*')))
        for j, reas in enumerate(reass):
            reas_fn = 'sub-{subject}_ses-{session}_task-reas_run-{run}_bold'.format(subject=sub, session=i, run=j)
            converter.inputs.source_dir = reas
            converter.inputs.out_filename = reas_fn
            converter.run()

        rests = sorted(glob(op.join(raw_dir, sub, ses, '*Resting_State*')))
        for j, rest in enumerate(rests):
            rest_fn = 'sub-{subject}_ses-{session}_task-rest_run-{run}_bold'.format(subject=sub, session=i, run=j)
            converter.inputs.source_dir = rest
            converter.inputs.out_filename = rest_fn
            converter.run()
