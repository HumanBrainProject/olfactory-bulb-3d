#!/bin/bash

#SBATCH --account=proj16
#SBATCH --partition=prod_p2
#SBATCH --time=02:00:00

#SBATCH --nodes=1
#SBATCH --constraint=volta
#SBATCH --gres=gpu:1
##SBATCH --ntasks-per-node=16

#SBATCH --cpus-per-task=2
#SBATCH --exclusive
#SBATCH --mem=0

# Stop on error
#set -e

# =============================================================================
# SIMULATION PARAMETERS TO EDIT
# =============================================================================

BASE_DIR=$(pwd)
INSTALL_DIR=$BASE_DIR/install
SOURCE_DIR=$BASE_DIR/sources

export HOC_LIBRARY_PATH=$BASE_DIR/sim
. $SOURCE_DIR/venv/bin/activate
PYTHONPATH_INIT=$PYTHONPATH

#Change this according to the desired runtime of the benchmark
export SIM_TIME=1050

# =============================================================================
#export CUDA_MPS_LOG_DIRECTORY=$(pwd)
nvidia-cuda-mps-control -d # Start the daemon

# Enter the channel benchmark directory
cd $BASE_DIR/sim

#echo "----------------- NEURON SIM (CPU) ----------------"
#export PYTHONPATH=$INSTALL_DIR/nrn_cnrn_cpu_mod2c/lib/python:$PYTHONPATH_INIT
#rm 0_nrn_gpu_.log 0_nrn_gpu_.spk
#srun dplace $INSTALL_DIR/nrn_cnrn_cpu_mod2c/special/x86_64/special -mpi -python bulb3dtest.py $SIM_TIME 0 0 0_nrn_gpu 2>&1 | tee 0_nrn_gpu_.log
# Sort the spikes
#cat 0_nrn_gpu.spikes* | sort -k 1n,1n -k 2n,2n > 0_nrn_gpu_.spk
#rm 0_nrn_gpu.*
#rm -rf __pycache__

echo "----------------- CoreNEURON SIM (GPU_MOD2C) ----------------"
export PYTHONPATH=$INSTALL_DIR/nrn_cnrn_gpu_mod2c/lib/python:$PYTHONPATH_INIT
rm 1_nrn_cnrn_gpu_mod2c_.log 1_nrn_cnrn_gpu_mod2c_.spk
rm -rf coredat
srun dplace $INSTALL_DIR/nrn_cnrn_gpu_mod2c/special/x86_64/special -mpi -python bulb3dtest.py $SIM_TIME 1 1 1_nrn_cnrn_gpu_mod2c 2>&1 | tee 1_nrn_cnrn_gpu_mod2c_.log
# Sort the spikes
cat 1_nrn_cnrn_gpu_mod2c.spikes* | sort -k 1n,1n -k 2n,2n > 1_nrn_cnrn_gpu_mod2c_.spk
rm 1_nrn_cnrn_gpu_mod2c.*
rm -rf __pycache__

#echo "----------------- CoreNEURON SIM File Mode (GPU_MOD2C) ----------------"
#export PYTHONPATH=$INSTALL_DIR/nrn_cnrn_gpu_mod2c/lib/python:$PYTHONPATH_INIT
#rm 1_cnrn_gpu_mod2c_.log 1_cnrn_gpu_mod2c_.spk
#srun -n 8 dplace $INSTALL_DIR/nrn_cnrn_gpu_mod2c/special/x86_64/special-core -d coredat --gpu --mpi -e $SIM_TIME --voltage=1000 --cell-permute=2 2>&1 | tee 1_cnrn_gpu_mod2c_.log
## Sort the spikes
#cat out.dat | sort -k 1n,1n -k 2n,2n > 1_cnrn_gpu_mod2c_.spk
#rm out.dat
#exit
#echo "----------------- CoreNEURON SIM File Mode (GPU_NMODL) ----------------"
#export PYTHONPATH=$INSTALL_DIR/nrn_cnrn_gpu_nmodl/lib/python:$PYTHONPATH_INIT
#rm 2_nrn_cnrn_gpu_nmodl_.log 2_nrn_cnrn_gpu_nmodl_.spk
#srun dplace $INSTALL_DIR/nrn_cnrn_gpu_nmodl/special/x86_64/special -mpi -python bulb3dtest.py $SIM_TIME 1 1 2_nrn_cnrn_gpu_nmodl 2>&1 | tee 2_nrn_cnrn_gpu_nmodl_.log
#srun -n 8 dplace $INSTALL_DIR/nrn_cnrn_gpu_nmodl/special/x86_64/special-core -d coredat --gpu --mpi -e $SIM_TIME --voltage=1000 --cell-permute=2 2>&1 | tee 2_cnrn_gpu_nmodl_.log
# Sort the spikes
#cat 2_cnrn_gpu_nmodl.spikes* | sort -k 1n,1n -k 2n,2n > 2_cnrn_gpu_nmodl_.spk
#rm 2_cnrn_gpu_nmodl.*
#rm -rf __pycache__

#echo quit | nvidia-cuda-mps-control
exit
# =============================================================================

echo "---------------------------------------------"
echo "-------------- Compare Spikes ---------------"
echo "---------------------------------------------"

DIFF=$(diff 0_nrn_gpu_.spk 1_nrn_cnrn_gpu_mod2c_.spk)
if [ "$DIFF" != "" ] 
then
    echo "0_nrn_gpu_.spk 1_nrn_cnrn_gpu_mod2c_.spk are not the same"
else
    echo "0_nrn_gpu_.spk 1_nrn_cnrn_gpu_mod2c_.spk are the same"
fi

DIFF=$(diff 0_nrn_gpu_.spk 2_nrn_cnrn_gpu_nmodl_.spk)
if [ "$DIFF" != "" ] 
then
    echo "0_nrn_gpu_.spk 2_nrn_cnrn_gpu_nmodl_.spk are not the same"
else
    echo "0_nrn_gpu_.spk 2_nrn_cnrn_gpu_nmodl_.spk are the same"
fi

# =============================================================================

echo "---------------------------------------------"
echo "----------------- SIM STATS -----------------"
echo "---------------------------------------------"

echo "----------------- NEURON SIM STATS (CPU) ----------------"
grep "Solver time : " 0_nrn_gpu_.log
echo "----------------- CoreNEURON SIM (GPU_MOD2C) STATS ----------------"
grep "Solver Time : " 1_nrn_cnrn_gpu_mod2c_.log
echo "----------------- CoreNEURON SIM (GPU_NMODL) STATS ----------------"
grep "Solver Time : " 2_cnrn_gpu_nmodl_.log

echo "---------------------------------------------"
echo "---------------------------------------------"
