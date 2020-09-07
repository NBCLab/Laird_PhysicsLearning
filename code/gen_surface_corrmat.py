"""
Based on
https://github.com/BIDS-Apps/example/blob/aa0d4808974d79c9fbe54d56d3b47bb2cf4e0a0d/run.py
"""
import os
import os.path as op
import argparse
import nibabel as nib
import numpy as np
from nilearn import plotting
import matplotlib.pyplot as plt
import pickle
from nilearn.connectome import ConnectivityMeasure
from nilearn import surface
from nilearn.datasets import fetch_surf_fsaverage
from nilearn.masking import compute_background_mask
from glob import glob


def get_parser():
    parser = argparse.ArgumentParser(description='This script will generate axials, surface medial and surface lateral view images with the specified overlay.')
    parser.add_argument('-b', required=False, dest='dset',
                        help='BIDS directory')
    parser.add_argument('--sub', required=False, dest='sub',
                        help='Subject ID')
    parser.add_argument('--ses', required=False, dest='ses',
                        help='Session ID')
    parser.add_argument('--deriv', required=False, dest='deriv',
                        help='Output derivative name.')
    return parser


def main(argv=None):

    args = get_parser().parse_args(argv)

    output_dir = op.join(args.dset, 'derivatives', args.deriv, args.sub, args.ses)
    os.makedirs(output_dir, exist_ok = True)

    nii_files = glob(op.join(args.dset, 'derivatives', '3dTproject_denoise_acompcor_csfwm+12mo+0.35mm', args.sub, args.ses, '*.nii.gz'))

    for tmp_nii_file in nii_files:
        print(tmp_nii_file)
        imgs = nib.load(tmp_nii_file)

        fsaverage = fetch_surf_fsaverage(mesh='fsaverage5')

        mask = compute_background_mask(imgs)
        surf_lh = surface.vol_to_surf(imgs, fsaverage.pial_left, radius=24, interpolation='nearest', kind='ball', n_samples=None, mask_img=mask)
        surf_rh = surface.vol_to_surf(imgs, fsaverage.pial_right, radius=24, interpolation='nearest', kind='ball', n_samples=None, mask_img=mask)

        time_series = np.transpose(np.vstack((surf_lh, surf_rh)))
        correlation = ConnectivityMeasure(kind='correlation')
        time_series = correlation.fit_transform([time_series])[0]
        plotting.plot_matrix(time_series, figure=(10, 8))
        plt.savefig(op.join(output_dir, '{0}-correlation_matrix.png'.format(op.basename(tmp_nii_file).split('.')[0])))
        plt.close()
        with open(op.join(output_dir, '{0}-correlation_matrix.pkl'.format(op.basename(tmp_nii_file).split('.')[0])), 'wb') as fo:
            pickle.dump(time_series, fo)


if __name__ == '__main__':
    main()
