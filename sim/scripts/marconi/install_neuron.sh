set -e
cwd=`pwd`

module load profile/advanced
module load pgi/19.10--binary gnu/8.4.0 cuda/10.1
module load spectrum_mpi/10.3.1--binary boost/1.72.0--spectrum_mpi--10.3.1--binary
module load cmake/3.17.1

export PGI_LOCALRC=`pwd`/localrc
export OMPI_CXX=pgc++
export OMPI_CC=pgcc
export CC=mpicc
export CXX=mpicxx

[[ -d nrn ]] || git clone https://github.com/neuronsimulator/nrn.git

mkdir -p nrn/build && cd nrn/build
cmake .. -DCMAKE_INSTALL_PREFIX=$cwd/install -DNRN_ENABLE_INTERVIEWS=OFF -DNRN_ENABLE_RX3D=OFF -DNRN_ENABLE_CORENEURON=ON -DPYTHON_EXECUTABLE=`which python` -DCORENRN_ENABLE_MPI=ON -DCORENRN_ENABLE_OPENMP=OFF -DCORENRN_ENABLE_GPU=ON -DNRN_ENABLE_BINARY_SPECIAL=ON -DNRN_ENABLE_SHARED=OFF -DNRN_ENABLE_INTERNAL_READLINE=ON
make -j8
make install
