## How to run this model on Marconi100

### Installing NEURON+CoreNEURON from Source

First we need to build NEURON with CoreNEURON support. In order to do so, you can use following script:

```console
module load profile/base
module load profile/advanced
module load hpc-sdk/2021--binary gnu/8.4.0 cuda/11.0
module load spectrum_mpi/10.3.1--binary boost/1.72.0--spectrum_mpi--10.3.1--binary
module load cmake/3.20.0 python/3.8.2

export OMPI_CXX=nvc++
export OMPI_CC=nvc
export CC=mpicc
export CXX=mpicxx

git clone https://github.com/neuronsimulator/nrn.git

mkdir -p nrn/build && cd nrn/build

# cmake, make and make install
cmake .. -DCMAKE_INSTALL_PREFIX=$HOME/install \
	-DNRN_ENABLE_INTERVIEWS=OFF \
	-DNRN_ENABLE_RX3D=OFF \
	-DNRN_ENABLE_CORENEURON=ON \
	-DPYTHON_EXECUTABLE=`which python` \
	-DCORENRN_ENABLE_MPI=ON \
	-DCORENRN_ENABLE_OPENMP=OFF \
	-DCORENRN_ENABLE_GPU=ON
make -j8
make install
```

Note that above mentioned modules (from May 2022) might change in the future. So make sure to change them if necessary.

#### Download Model

Let's clone olfactory bulb model repository from GitHub. For now, we have to use `2to3` branch which has Python 3 support:

```
git clone https://github.com/HumanBrainProject/olfactory-bulb-3d.git
cd olfactory-bulb-3d/sim
git checkout 2to3
```

#### Building Special

We can now build the model `nrnivmodl -coreneuron ` command. Make sure to change path of `nrnivmodl` if you have installed NEURON from source.

```
module load profile/base
module load profile/advanced
module load hpc-sdk/2021--binary gnu/8.4.0 cuda/11.0
module load spectrum_mpi/10.3.1--binary boost/1.72.0--spectrum_mpi--10.3.1--binary
module load cmake/3.20.0 python/3.8.2

export OMPI_CXX=nvc++
export OMPI_CC=nvc
export CC=mpicc
export CXX=mpicxx

$HOME/install/bin/nrnivmodl -coreneuron .
```

If there are no errors, `special` with CoreNEURON support will be built.

#### Running model on GPU

We are now ready to run model. To enable GPU support via CoreNEURON, you can pass the following command line argument to `bulb3dtest.py`:

```
--coreneuron --gpu
```

Also, if you are benchmarking model then make sure to select larger test case i.e. changing `runsim.build_part_model` in in `bulb3dtest.py`.

We can now submit the job to the cluster using following job script:

```
#!/bin/bash
#SBATCH -A Pra18_4575_0
#SBATCH -p m100_usr_prod
#SBATCH --time 00:60:00
#SBATCH --job-name=coreneuron_gpu_test
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --gres=gpu:4

module load profile/base
module load profile/advanced
module load hpc-sdk/2021--binary gnu/8.4.0 cuda/11.0
module load spectrum_mpi/10.3.1--binary boost/1.72.0--spectrum_mpi--10.3.1--binary
module load cmake/3.20.0 python/3.8.2

export PYTHONPATH=$HOME/install/lib/python/:$PYTHONPATH

# gpu run with coreneuron
mpirun ./special_wrapper.ppc64 -python -mpi bulb3dtest.py --tstop=1050 --coreneuron --gpu
```

Note that we are using `special_wrapper.ppc64` instead of `ppc64le/special` as a binary to launch. This is because [MPS](https://docs.nvidia.com/deploy/pdf/CUDA_Multi_Process_Service_Overview.pdf) service is currently not enabled on Marconi100. Using wrapper script, we start the MPS service before launching an application.

