module load profile/advanced
module load pgi/19.10--binary gnu/8.4.0 cuda/10.1 spectrum_mpi/10.3.1--binary

export PGI_LOCALRC=`pwd`/localrc
export OMPI_CXX=pgc++
export OMPI_CC=pgcc
export CC=mpicc
export CXX=mpicxx

NRN_INSTALL=/m100_work/Pra18_4575_0/kumbhar/software/install

$NRN_INSTALL/bin/nrnivmodl-core .
$NRN_INSTALL/bin/nrnivmodl -incflags "-acc" -loadflags "-acc -rdynamic -lrt -Wl,--whole-archive -Lppc64le/ -lcorenrnmech -L$NRN_INSTALL/lib -lcoreneuron -lcudacoreneuron  -Wl,--no-whole-archive $CUDA_LIB/libcudart_static.a" .
