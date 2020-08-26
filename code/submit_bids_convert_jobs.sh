raw_dir=/home/data/nbc/DICOM/ALAI_NSF_14-007
bids_dir=/home/data/nbc/Laird_PhysicsLearning
work_dir=/scratch/miriedel

if [ ! -d $bids_dir/code/err ]; then
  mkdir -p $bids_dir/code/err
fi
if [ ! -d $bids_dir/code/out ]; then
  mkdir -p $bids_dir/code/out
fi

echo "participant_id" > $bids_dir/dset/participants.tsv

dir_ignore=(DicomFileLists.py F_14_007_321 PILOT1 PILOT2 PILOT3 PILOT4 PILOT5 summary)

subs=$(dir $raw_dir)

for sub in $subs; do

  #skip the bad folders grabbed by the dir command
  proc=1
  for tmp_dir in ${dir_ignore[@]}; do
    if [[ "$tmp_dir" == "$sub" ]]; then
      proc=0
      break
    fi
  done
  if [ $proc -eq 0 ]; then
    continue
  fi
  echo $sub
  echo "sub-$sub" >> $bids_dir/dset/participants.tsv

  sbatch -J bids_convert_$sub \
         -e $bids_dir/code/err/$sub \
         -o $bids_dir/code/out/$sub \
         -n 1 \
         --qos pq_nbc \
         --account iacc_nbc \
         -p investor \
         --wrap="python $bids_dir/code/bids_convert.py --workdir $work_dir/$sub --bidsdir $bids_dir/dset --dicomdir $raw_dir --sub $sub"
done
