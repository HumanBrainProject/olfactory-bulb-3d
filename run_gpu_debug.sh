#!/bin/bash

#SBATCH --account=proj16
#SBATCH --partition=prod_p2
#SBATCH --time=08:00:00

#SBATCH --nodes=1
#SBATCH --constraint=volta
#SBATCH --gres=gpu:4

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

#export GPUS="1 2 4"
export GPUS="1"
# =============================================================================
#export CUDA_MPS_LOG_DIRECTORY=$(pwd)
nvidia-cuda-mps-control -d # Start the daemon

# Enter the channel benchmark directory
cd $BASE_DIR/sim

echo "----------------- NEURON SIM (CPU) Debug Build ----------------"
export PYTHONPATH=$INSTALL_DIR/nrn_cnrn_gpu_mod2c_debug/lib/python:$PYTHONPATH_INIT
rm 0_nrn_gpu_.log 0_nrn_gpu_.spk
srun dplace $INSTALL_DIR/nrn_cnrn_gpu_mod2c_debug/special/x86_64/special -mpi -python bulb3dtest.py $SIM_TIME 0 0 0_nrn_gpu_debug 2>&1 | tee 0_nrn_gpu_debug_.log
# Sort the spikes
cat 0_nrn_gpu_debug.spikes* | sort -k 1n,1n -k 2n,2n > 0_nrn_gpu_debug_.spk
rm 0_nrn_gpu_debug.*
rm -rf __pycache__

for NUM_GPU in $GPUS; 
do
    echo "----------------- CoreNEURON SIM (GPU_MOD2C) $NUM_GPU GPUs Debug Build ----------------"
    export PYTHONPATH=$INSTALL_DIR/nrn_cnrn_gpu_mod2c_debug/lib/python:$PYTHONPATH_INIT
    rm 1_nrn_cnrn_gpu_mod2c_debug_${NUM_GPU}_.log 1_nrn_cnrn_gpu_mod2c_debug_${NUM_GPU}_.spk
    rm -rf coredat
    srun --gres=gpu:${NUM_GPU} dplace $INSTALL_DIR/nrn_cnrn_gpu_mod2c_debug/special/x86_64/special -mpi -python bulb3dtest.py $SIM_TIME 1 1 1_nrn_cnrn_gpu_mod2c_debug_${NUM_GPU} 2>&1 | tee 1_nrn_cnrn_gpu_mod2c_debug_${NUM_GPU}_.log
    # Sort the spikes
    cat 1_nrn_cnrn_gpu_mod2c_debug_${NUM_GPU}.spikes* | sort -k 1n,1n -k 2n,2n > 1_nrn_cnrn_gpu_mod2c_debug_${NUM_GPU}_.spk
    rm 1_nrn_cnrn_gpu_mod2c_debug_${NUM_GPU}.*
    rm -rf __pycache__
done

echo quit | nvidia-cuda-mps-control
# =============================================================================

echo "---------------------------------------------"
echo "-------------- Compare Spikes ---------------"
echo "---------------------------------------------"

for NUM_GPU in $GPUS;
do
    DIFF=$(diff 0_nrn_gpu_debug_.spk 1_nrn_cnrn_gpu_mod2c_debug_${NUM_GPU}_.spk)
    if [ "$DIFF" != "" ] 
    then
        echo "0_nrn_gpu_debug_.spk 1_nrn_cnrn_gpu_mod2c_debug_${NUM_GPU}_.spk are not the same"
    else
        echo "0_nrn_gpu_debug_.spk 1_nrn_cnrn_gpu_mod2c_debug_${NUM_GPU}_.spk are the same"
    fi
done

# =============================================================================

echo "---------------------------------------------"
echo "----------------- SIM STATS -----------------"
echo "---------------------------------------------"

echo "----------------- NEURON SIM STATS (CPU) ----------------"
grep "Solver time : " 0_nrn_gpu_debug_.log
for NUM_GPU in $GPUS;
do
    echo "----------------- CoreNEURON SIM (GPU_MOD2C) STATS $NUM_GPU GPUs ----------------"
    grep "Solver Time : " 1_nrn_cnrn_gpu_mod2c_debug_${NUM_GPU}_.log
done

echo "---------------------------------------------"
echo "---------------------------------------------"
