import os
import os.path as op
from glob import glob
from nipype.interfaces.dcm2nii import Dcm2niix
import shutil
import pandas as pd
from pydeface.utils import deface_image
import numpy as np
import argparse
import json
import nibabel as nib


def sort_series(task_dirs):
    series_id = [op.basename(x).split('-')[0] for x in task_dirs]
    series_id_sorted = np.sort(series_id)
    series_id_loc = np.searchsorted(series_id_sorted, series_id)
    task_dirs = [task_dirs[x] for x in series_id_loc]
    return task_dirs


def dicom_converter(out_dir=None, source_dir=None, filename=None):
    converter = Dcm2niix()
    converter.inputs.bids_format = True
    converter.inputs.anon_bids = True
    converter.inputs.compress = 'y'
    converter.inputs.output_dir = out_dir
    converter.inputs.source_dir = source_dir
    converter.inputs.out_filename = filename
    converter.run()

def json_slicer(filename=None, trs=None):
    json_fn = '{0}.json'.format(filename)
    with open(json_fn, 'r') as fo:
        js_data = json.load(fo)

    img_info = nib.load('{0}.nii.gz'.format(filename))
    if img_info.shape[3] == trs:
        js_data['NumberOfVolumesDiscardedByScanner'] = 5
    else:
        js_data['NumberOfVolumesDiscardedByScanner'] = 0

    with open(json_fn, 'w') as fo:
        json.dump(js_data, fo, sort_keys=True, indent=4)


def get_parser():
    parser = argparse.ArgumentParser(description='This script will convert a single subject to BIDS format.')
    parser.add_argument('-w', '--workdir', required=False, dest='work_dir',
                        help='Path to working directory.')
    parser.add_argument('-b', '--bidsdir', required=False, dest='bids_dir',
                        help='Path to output directory.')
    parser.add_argument('-d', '--dicomdir', required=False, dest='raw_dir',
                        help='Path to dicom directory.')
    parser.add_argument('-s', '--sub', required=False, dest='sub',
                        help='Subject ID.')
    return parser


def main(argv=None):

    args = get_parser().parse_args(argv)

    raw_dir = args.raw_dir
    bids_dir = args.bids_dir
    work_dir = args.work_dir
    sub = args.sub

    sess = sorted(os.listdir(op.join(raw_dir, sub)))

    for i, ses in enumerate(sess):

        anat_dir = op.join(bids_dir, 'sub-{subject}'.format(subject=sub), 'ses-{session}'.format(session=i+1), 'anat')
        os.makedirs(anat_dir)

        t1s = sorted(glob(op.join(raw_dir, sub, ses, '*PU:3D_T1_Sag-Structural*')))
        if not t1s:
            t1s = sorted(glob(op.join(raw_dir, sub, ses, '*3D_T1_Sag-Structural*')))
        for j, t1 in enumerate(t1s):
            t1_fn = 'sub-{subject}_ses-{session}_run-{run}_T1w'.format(subject=sub, session=i+1, run=j+1)
            shutil.copytree(t1, op.join(work_dir, 'tmp'))
            dicom_converter(out_dir=anat_dir, source_dir=op.join(work_dir, 'tmp'), filename=t1_fn)
            shutil.rmtree(op.join(work_dir, 'tmp'))
            deface_image(infile=op.join(anat_dir, '{0}.nii.gz'.format(t1_fn)),
                         outfile=op.join(anat_dir, '{0}.nii.gz'.format(t1_fn)),
                         force=True,
                         forcecleanup=True,
                         verbose=False)

        func_dir = op.join(bids_dir, 'sub-{subject}'.format(subject=sub), 'ses-{session}'.format(session=i+1), 'func')
        os.makedirs(func_dir)

        task_dict = {'FCI': 'fci', 'RETR': 'retr', 'REAS': 'reas', 'Resting_State': 'rest'}
        tr_dict = {'FCI': 167, 'RETR': 173, 'REAS': 210, 'Resting_State': 360}

        for task in list(task_dict.keys()):

            task_dirs = glob(op.join(raw_dir, sub, ses, '*{task}*'.format(task=task)))
            task_dirs = sort_series(task_dirs)

            for j, task_dir in enumerate(task_dirs):
                task_fn = 'sub-{subject}_ses-{session}_task-{task}_run-{run}_bold'.format(subject=sub, session=i+1, task=task_dict[task], run=j+1)
                dicom_converter(out_dir=func_dir, source_dir=task_dir, filename=task_fn)
                json_slicer(filename=op.join(func_dir, task_fn), trs=tr_dict[task])


if __name__ == '__main__':
    main()
