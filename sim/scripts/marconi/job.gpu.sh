#!/bin/bash
#SBATCH -A Pra18_4575_0
#SBATCH -p m100_usr_prod
#SBATCH --time 00:60:00
#SBATCH --ntasks-per-node=16
#SBATCH --gres=gpu:4
#SBATCH --job-name=coreneuron_gpu_test

##SBATCH --nodes=2
##SBATCH --output=coreneuron-gpu-%j.out

module load profile/advanced
module load pgi/19.10--binary gnu/8.4.0 cuda/10.1 spectrum_mpi/10.3.1--binary
export PYTHONPATH=/m100_work/Pra18_4575_0/kumbhar/software/install/lib64/python/:$PYTHONPATH

# gpu run with coreneuron
mpirun ./special_wrapper -python -mpi bulb3dtest.py

mkdir -p gpu
mv bulb3dtest-*.txt gpu/
mv bulb3dtest.spike* gpu/
