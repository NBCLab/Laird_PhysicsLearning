proj_dir='/home/data/nbc/Laird_PhysicsLearning'

deriv=3dTproject_denoise_acompcor_csfwm+12mo+0.35mm

if [ ! -d $proj_dir/dset/derivatives/$deriv/ ]; then
    mkdir -p $proj_dir/dset/derivatives/$deriv/
fi

subs=$(dir $proj_dir/dset/derivatives/fmriprep-1.5.0/)
for tmpsub in $subs; do
    echo $tmpsub
    if [[ $tmpsub == sub-* ]]; then

      sess=$(dir $proj_dir/dset/derivatives/fmriprep-1.5.0/$tmpsub/fmriprep/$tmpsub/)
      for tmpses in $sess; do
          echo $tmpses
          if [[ $tmpses == ses-* ]]; then

            if [ ! -d $proj_dir/dset/derivatives/$deriv/$tmpsub/$tmpses ]; then
                sbatch -J $tmpsub-$tmpses-3dtproject-denoise -e $proj_dir/code/err/$tmpsub-$tmpses-3dtproject-denoise -o $proj_dir/code/out/$tmpsub-$tmpses-3dtproject-denoise -c 1 --qos pq_nbc -p investor --account iacc_nbc --wrap="python3 $proj_dir/code/3dTproject_denoise.py -b $proj_dir/dset -w /scratch/$USER/$tmpsub-$tmpses-3dTproject-denoise --sub $tmpsub --ses $tmpses --deriv $deriv"
            fi

          fi
      done
    fi
done
