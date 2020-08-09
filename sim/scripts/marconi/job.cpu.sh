#!/bin/bash
#SBATCH -A Pra18_4575_0
#SBATCH -p m100_usr_prod
#SBATCH --time 00:60:00
#SBATCH --ntasks-per-node=64
#SBATCH --job-name=neuron_cpu_test

##SBATCH --nodes=2
##SBATCH --output=neuron-cpu-%j.out

module load profile/advanced
module load pgi/19.10--binary gnu/8.4.0 cuda/10.1 spectrum_mpi/10.3.1--binary
export PYTHONPATH=/m100_work/Pra18_4575_0/kumbhar/software/install/lib64/python/:$PYTHONPATH

# cpu run with neuron
mpirun ./special_wrapper -python -mpi bulb3dtest.py

# move the results to cpu
mkdir -p cpu
mv bulb3dtest-*.txt cpu/
mv bulb3dtest.spike* cpu/
