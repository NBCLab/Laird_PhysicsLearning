# Remember to load singularity 3 and activate an environment
proj_dir=/home/data/nbc/Laird_PhysicsLearning
wkdir=/scratch/miriedel

#module load glibc/2.14
#module load slurm

if [ ! -d $proj_dir/dset/derivatives/fmriprep-1.5.0/ ]; then
    mkdir -p $proj_dir/dset/derivatives/fmriprep-1.5.0/
fi

subs=$(dir $proj_dir/dset/)
nprocs=2

for tmpsub in $subs; do
  if [[ $tmpsub == sub-* ]]; then
      if [ ! -d $proj_dir/dset/derivatives/fmriprep-1.5.0/$tmpsub ]; then

          echo $tmpsub
          while [ $(squeue -u $USER | wc -l) -gt 40 ]; do
              sleep 30m
          done
          sbatch -J $tmpsub-func-proc -e $proj_dir/code/err/$tmpsub-func-proc -o $proj_dir/code/out/$tmpsub-func-proc -n $nprocs --qos pq_nbc -p centos7 --account iacc_nbc --wrap="python3 $proj_dir/code/fmriprep.py -b $proj_dir/dset -w $wkdir/$tmpsub-func-proc --sub $tmpsub --n_procs $nprocs"
      fi
  fi
done
