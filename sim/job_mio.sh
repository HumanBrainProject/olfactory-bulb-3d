#!/bin/bash
#SBATCH --output=job.out
#SBATCH --error=job.err
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=36
#SBATCH --account=HBP_CDP21_it_1
#SBATCH --time=2:00:00
#SBATCH --mem=60000
#SBATCH --partition=gll_usr_prod
##SBATCH --qos=knl_qos_bprod
##SBATCH --qos=qos_prio
#SBATCH --mail-type=END
#SBATCH --mail-user=emiliano.spera@pa.ibf.cnr.it
##SBATCH --constraint=cache

module load intel/pe-xe-2018--binary
module load intelmpi/2018--binary
module load python/2.7.12

echo "# Add Neuron and IV to path variable" >> ~/.bashrc
echo 'export PATH="$HOME/neuron/nrn/x86_64/bin:$PATH"' >> ~/.bashrc
echo 'export PATH="$HOME/neuron/iv/x86_64/bin:$PATH"' >> ~/.bashrc

source ~/.bashrc

cd /gpfs/work/HBP_CDP21_it_1/Emiliano/modeldb-bulb3d/sim
mpirun nrniv -mpi -python bulb3dtest.py
