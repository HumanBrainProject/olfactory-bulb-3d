## How to run this model on Marconi100

#### Installing NEURON+CoreNEURON

NEURON+CoreNEURON has been already installed at below location on Marconi100:

```
/m100_work/Pra18_4575_0/software/gpu/install
```

We can use this installation for execution on Marconi100. If you want to re-build it from source, see the instructions at the end of this README file.

#### Download Model

Let's clone olfactory bulb model repository from GitHub:

```
git clone https://github.com/HumanBrainProject/olfactory-bulb-3d.git
cd olfactory-bulb-3d/sim
```

#### Building Special

We can now build the model `nrnivmodl -coreneuron ` command. Make sure to change path of `nrnivmodl` if you have installed NEURON from source.

```
module load profile/advanced
module load pgi/19.10--binary gnu/8.4.0 cuda/10.1
module load spectrum_mpi/10.3.1--binary boost/1.72.0--spectrum_mpi--10.3.1--binary
module load cmake/3.17.1

export PGI_LOCALRC=/m100_work/Pra18_4575_0/software/gpu/pgi/localrc
export OMPI_CXX=pgc++
export OMPI_CC=pgcc
export CC=mpicc
export CXX=mpicxx

/m100_work/Pra18_4575_0/software/gpu/install/bin/nrnivmodl -coreneuron .
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

module load profile/advanced
module load pgi/19.10--binary gnu/8.4.0 cuda/10.1
module load spectrum_mpi/10.3.1--binary boost/1.72.0--spectrum_mpi--10.3.1--binary

export PYTHONPATH=/m100_work/Pra18_4575_0/software/gpu/install/lib64/python/:$PYTHONPATH

# gpu run with coreneuron
mpirun ./special_wrapper.ppc64 -python -mpi bulb3dtest.py --tstop=1050 --coreneuron --gpu
```

Note that we are using `special_wrapper.ppc64` instead of `ppc64le/special` as a binary to launch. This is because [MPS](https://docs.nvidia.com/deploy/pdf/CUDA_Multi_Process_Service_Overview.pdf) service is currently not enabled on Marconi100. Using wrapper script, we start the MPS service before launching an application.


### Installing NEURON+CoreNEURON from Source

NEURON+CoreNEURON has been already installed in below location:

```
/m100_work/Pra18_4575_0/software/gpu/install
```

Use above installation unless you want to build everything from scratch. In order to do so, you can use following script:

```
module load profile/advanced
module load pgi/19.10--binary gnu/8.4.0 cuda/10.1
module load spectrum_mpi/10.3.1--binary boost/1.72.0--spectrum_mpi--10.3.1--binary
module load cmake/3.17.1

export PGI_LOCALRC=/m100_work/Pra18_4575_0/software/gpu/pgi/localr
export OMPI_CXX=pgc++
export OMPI_CC=pgcc
export CC=mpicc
export CXX=mpicxx

git clone https://github.com/neuronsimulator/nrn.git

mkdir -p nrn/build && cd nrn/build
#git checkout 6f4ae452d771521ddaa357bb2ed8eb33c3f4a2d0

# cmake, make and make install
cmake .. -DCMAKE_INSTALL_PREFIX=$HOME/install \
	-DNRN_ENABLE_INTERVIEWS=OFF \
	-DNRN_ENABLE_RX3D=OFF \
	-DNRN_ENABLE_CORENEURON=ON \
	-DPYTHON_EXECUTABLE=`which python` \
	-DCORENRN_ENABLE_MPI=ON \
	-DCORENRN_ENABLE_OPENMP=OFF \
	-DCORENRN_ENABLE_GPU=ON \
	-DNRN_ENABLE_BINARY_SPECIAL=ON \
	-DNRN_ENABLE_SHARED=OFF \
	-DNRN_ENABLE_INTERNAL_READLINE=ON
make -j8
make install
```
