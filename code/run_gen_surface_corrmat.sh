proj_dir='/home/data/nbc/Laird_PhysicsLearning'

deriv=gradient-analysis

if [ ! -d $proj_dir/dset/derivatives/$deriv/ ]; then
    mkdir -p $proj_dir/dset/derivatives/$deriv/
fi

subs=$(dir $proj_dir/dset/derivatives/3dTproject_denoise_acompcor_csfwm+12mo+0.35mm/)
for tmpsub in $subs; do
    echo $tmpsub
    if [[ $tmpsub == sub-* ]]; then

      sess=$(dir $proj_dir/dset/derivatives/3dTproject_denoise_acompcor_csfwm+12mo+0.35mm/$tmpsub/fmriprep/$tmpsub/)
      for tmpses in $sess; do
          echo $tmpses
          if [[ $tmpses == ses-* ]]; then

            if [ ! -d $proj_dir/dset/derivatives/$deriv/$tmpsub/$tmpses ]; then
                sbatch -J $tmpsub-$tmpses-gen_surface_corrmat -e $proj_dir/code/err/$tmpsub-$tmpses-gen_surface_corrmat -o $proj_dir/code/out/$tmpsub-$tmpses-gen_surface_corrmat -c 1 --qos pq_nbc -p investor --account iacc_nbc --wrap="python3 $proj_dir/code/gen_surface_corrmat.py -b $proj_dir/dset --sub $tmpsub --ses $tmpses --deriv $deriv"
                exit
            fi

          fi
      done
    fi
done
