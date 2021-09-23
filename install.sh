#!/bin/bash

# stop on error
set -e

# build and install directories
export BASE_DIR=$(pwd)
export SOURCE_DIR=$BASE_DIR/sources
export BUILD_DIR=$BASE_DIR/build
export INSTALL_DIR=$BASE_DIR/install
mkdir -p $SOURCE_DIR $INSTALL_DIR

# Re-install -> Do not delete x86_64
# To re-install provide just an arbitrary arguement
if [ $# -eq 0 ]
then
    REINSTALL=0
else
    REINSTALL=1
fi

# =============================================================================
# 1. Setting source & build dependencies
# =============================================================================

# Modules to load typically on the cluster environment
# TODO: change the modules based on your environment
setup_modules() {
    printf "\n----------------- SETTING MODULES --------------\n"
    module purge
    module load unstable
    module load cmake git flex bison python-dev hpe-mpi
}

# TODO Adjust compiler loading according to your system

load_gcc() {
    module load gcc
    export CC=$(which gcc)
    export CXX=$(which g++)
}

unload_gcc() {
    module unload gcc
    unset CC
    unset CXX
}

load_intel() {
    module load intel
    export CC=$(which icc)
    export CXX=$(which icpc)
}

unload_intel() {
    module unload intel
    unset CC
    unset CXX
}

load_pgi_cuda() {
    module load gcc nvhpc/21.2 cuda/11.0.2
    export CC=$(which pgcc)
    export CXX=$(which pgc++)
}

unload_pgi_cuda() {
    module unload gcc nvhpc/21.2 cuda/11.0.2
    unset CC
    unset CXX
}

# =============================================================================
# NO NEED TO EDIT BELLOW HERE
# =============================================================================

# Clone neuron repository
setup_source() {
    printf "\n----------------- CLONING REPO --------------\n"
    [[ -d $SOURCE_DIR/nrn ]] || git clone --recursive https://github.com/neuronsimulator/nrn.git $SOURCE_DIR/nrn
}

# Install python packages if not exist in standard environment
setup_python_packages() {
    printf "\n----------------- SETUP PYTHON PACKAGES --------------\n"
    [[ -d $SOURCE_DIR/venv ]] || python3 -mvenv $SOURCE_DIR/venv
    . $SOURCE_DIR/venv/bin/activate
    pip3 install Jinja2 PyYAML pytest "sympy<1.6"
}

# =============================================================================
# 2. Installing base software
# =============================================================================

# Install NMODL which is used for translating DSL to C++ code. This could be built with GNU
# toolchain as this is used as source-to-source compiler.
install_nmodl() {
    printf "\n----------------- INSTALL NMODL --------------\n"
    load_gcc
    mkdir -p $BUILD_DIR/nmodl && pushd $BUILD_DIR/nmodl
    cmake $SOURCE_DIR/nrn/external/coreneuron/external/nmodl \
        -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR/NMODL \
        -DPYTHON_EXECUTABLE=$(which python3) \
        -DCMAKE_CXX_COMPILER=$CXX \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo
    make -j && make install
    popd
    unload_gcc
}

# =============================================================================
# 3. Installing simulation engine
# =============================================================================

install_nrn_cnrn_cpu_mod2c() {
    printf "\n----------------- INSTALL NEURON+CORENEURON+MOD2C (CPU) --------------\n"
    load_intel
    mkdir -p $BUILD_DIR/nrn_cnrn_cpu_mod2c && pushd $BUILD_DIR/nrn_cnrn_cpu_mod2c
    cmake $SOURCE_DIR/nrn \
        -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR/nrn_cnrn_cpu_mod2c \
        -DNRN_ENABLE_INTERVIEWS=OFF \
        -DNRN_ENABLE_RX3D=OFF \
        -DNRN_ENABLE_MPI=ON \
        -DCORENRN_ENABLE_OPENMP=OFF \
        -DNRN_ENABLE_CORENEURON=ON \
        -DCORENRN_ENABLE_GPU=OFF \
        -DCORENRN_ENABLE_NMODL=OFF \
        -DNRN_ENABLE_PYTHON=ON \
        -DPYTHON_EXECUTABLE=$(which python3) \
        -DNRN_ENABLE_TESTS=OFF \
        -DCORENRN_ENABLE_UNIT_TESTS=OFF \
        -DCMAKE_C_COMPILER=$CC \
        -DCMAKE_CXX_COMPILER=$CXX \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo
    make -j && make install
    popd
    unload_intel
}

install_nrn_cnrn_cpu_mod2c_debug() {
    printf "\n----------------- INSTALL NEURON+CORENEURON+MOD2C (CPU) --------------\n"
    load_intel
    mkdir -p $BUILD_DIR/nrn_cnrn_cpu_mod2c_debug && pushd $BUILD_DIR/nrn_cnrn_cpu_mod2c_debug
    cmake $SOURCE_DIR/nrn \
        -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR/nrn_cnrn_cpu_mod2c_debug \
        -DNRN_ENABLE_INTERVIEWS=OFF \
        -DNRN_ENABLE_RX3D=OFF \
        -DNRN_ENABLE_MPI=ON \
        -DCORENRN_ENABLE_OPENMP=OFF \
        -DNRN_ENABLE_CORENEURON=ON \
        -DCORENRN_ENABLE_GPU=OFF \
        -DCORENRN_ENABLE_NMODL=OFF \
        -DNRN_ENABLE_PYTHON=ON \
        -DPYTHON_EXECUTABLE=$(which python3) \
        -DNRN_ENABLE_TESTS=OFF \
        -DCORENRN_ENABLE_UNIT_TESTS=OFF \
        -DCMAKE_C_COMPILER=$CC \
        -DCMAKE_CXX_COMPILER=$CXX \
        -DCMAKE_BUILD_TYPE=Debug
    make -j && make install
    popd
    unload_intel
}

install_nrn_cnrn_cpu_nmodl() {
    printf "\n----------------- INSTALL NEURON+CORENEURON+NMODL (CPU) --------------\n"
    load_intel
    mkdir -p $BUILD_DIR/nrn_cnrn_cpu_nmodl && pushd $BUILD_DIR/nrn_cnrn_cpu_nmodl
    cmake $SOURCE_DIR/nrn \
        -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR/nrn_cnrn_cpu_nmodl \
        -DNRN_ENABLE_INTERVIEWS=OFF \
        -DNRN_ENABLE_RX3D=OFF \
        -DNRN_ENABLE_MPI=ON \
        -DCORENRN_ENABLE_OPENMP=OFF \
        -DNRN_ENABLE_CORENEURON=ON \
        -DCORENRN_ENABLE_GPU=OFF \
        -DCORENRN_ENABLE_NMODL=ON \
        -DCORENRN_NMODL_DIR=$INSTALL_DIR/NMODL \
        -DNRN_ENABLE_PYTHON=ON \
        -DPYTHON_EXECUTABLE=$(which python3) \
        -DNRN_ENABLE_TESTS=OFF \
        -DCORENRN_ENABLE_UNIT_TESTS=OFF \
        -DCMAKE_C_COMPILER=$CC \
        -DCMAKE_CXX_COMPILER=$CXX \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo
    make -j && make install
    popd
    unload_intel
}

install_nrn_cnrn_cpu_nmodl_sympy() {
    printf "\n----------------- INSTALL NEURON+CORENEURON+NMODL (CPU) --------------\n"
    load_intel
    mkdir -p $BUILD_DIR/nrn_cnrn_cpu_nmodl_sympy && pushd $BUILD_DIR/nrn_cnrn_cpu_nmodl_sympy
    cmake $SOURCE_DIR/nrn \
        -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR/nrn_cnrn_cpu_nmodl_sympy \
        -DNRN_ENABLE_INTERVIEWS=OFF \
        -DNRN_ENABLE_RX3D=OFF \
        -DNRN_ENABLE_MPI=ON \
        -DCORENRN_ENABLE_OPENMP=OFF \
        -DNRN_ENABLE_CORENEURON=ON \
        -DCORENRN_ENABLE_GPU=OFF \
        -DCORENRN_ENABLE_NMODL=ON \
        -DCORENRN_NMODL_DIR=$INSTALL_DIR/NMODL \
        -DCORENRN_NMODL_FLAGS="sympy --analytic" \
        -DNRN_ENABLE_PYTHON=ON \
        -DPYTHON_EXECUTABLE=$(which python3) \
        -DNRN_ENABLE_TESTS=OFF \
        -DCORENRN_ENABLE_UNIT_TESTS=OFF \
        -DCMAKE_C_COMPILER=$CC \
        -DCMAKE_CXX_COMPILER=$CXX \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo
    make -j && make install
    popd
    unload_intel
}

install_nrn_cnrn_gpu_mod2c() {
    printf "\n----------------- INSTALL NEURON+CORENEURON+MOD2C (GPU) --------------\n"
    load_pgi_cuda
    mkdir -p $BUILD_DIR/nrn_cnrn_gpu_mod2c && pushd $BUILD_DIR/nrn_cnrn_gpu_mod2c
    cmake $SOURCE_DIR/nrn \
        -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR/nrn_cnrn_gpu_mod2c \
        -DNRN_ENABLE_INTERVIEWS=OFF \
        -DNRN_ENABLE_RX3D=OFF \
        -DNRN_ENABLE_MPI=ON \
        -DCORENRN_ENABLE_OPENMP=OFF \
        -DNRN_ENABLE_CORENEURON=ON \
        -DCORENRN_ENABLE_GPU=ON \
        -DCORENRN_ENABLE_NMODL=OFF \
        -DNRN_ENABLE_PYTHON=ON \
        -DPYTHON_EXECUTABLE=$(which python3) \
        -DNRN_ENABLE_TESTS=OFF \
        -DCORENRN_ENABLE_UNIT_TESTS=OFF \
        -DCMAKE_C_COMPILER=$CC \
        -DCMAKE_CXX_COMPILER=$CXX \
        -DCMAKE_CUDA_COMPILER=nvcc \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo
    make -j && make install
    popd
    unload_pgi_cuda
}

install_nrn_cnrn_gpu_mod2c_debug() {
    printf "\n----------------- INSTALL NEURON+CORENEURON+MOD2C DEBUG (GPU) --------------\n"
    load_pgi_cuda
    mkdir -p $BUILD_DIR/nrn_cnrn_gpu_mod2c_debug && pushd $BUILD_DIR/nrn_cnrn_gpu_mod2c_debug
    cmake $SOURCE_DIR/nrn \
        -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR/nrn_cnrn_gpu_mod2c_debug \
        -DNRN_ENABLE_INTERVIEWS=OFF \
        -DNRN_ENABLE_RX3D=OFF \
        -DNRN_ENABLE_MPI=ON \
        -DCORENRN_ENABLE_OPENMP=OFF \
        -DNRN_ENABLE_CORENEURON=ON \
        -DCORENRN_ENABLE_GPU=ON \
        -DCORENRN_ENABLE_NMODL=OFF \
        -DNRN_ENABLE_PYTHON=ON \
        -DPYTHON_EXECUTABLE=$(which python3) \
        -DNRN_ENABLE_TESTS=OFF \
        -DCORENRN_ENABLE_UNIT_TESTS=OFF \
        -DCMAKE_C_COMPILER=$CC \
        -DCMAKE_CXX_COMPILER=$CXX \
        -DCMAKE_CUDA_COMPILER=nvcc \
        -DCMAKE_BUILD_TYPE=Debug
    make -j && make install
    popd
    unload_pgi_cuda
}

install_nrn_cnrn_gpu_nmodl() {
    printf "\n----------------- INSTALL NEURON+CORENEURON+NMODL (GPU) --------------\n"
    load_pgi_cuda
    mkdir -p $BUILD_DIR/nrn_cnrn_gpu_nmodl && pushd $BUILD_DIR/nrn_cnrn_gpu_nmodl
    cmake $SOURCE_DIR/nrn \
        -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR/nrn_cnrn_gpu_nmodl \
        -DNRN_ENABLE_INTERVIEWS=OFF \
        -DNRN_ENABLE_RX3D=OFF \
        -DNRN_ENABLE_MPI=ON \
        -DCORENRN_ENABLE_OPENMP=OFF \
        -DNRN_ENABLE_CORENEURON=ON \
        -DCORENRN_ENABLE_GPU=ON \
        -DCORENRN_ENABLE_NMODL=ON \
        -DCORENRN_NMODL_DIR=$INSTALL_DIR/NMODL \
        -DNRN_ENABLE_PYTHON=ON \
        -DPYTHON_EXECUTABLE=$(which python3) \
        -DNRN_ENABLE_TESTS=OFF \
        -DCORENRN_ENABLE_UNIT_TESTS=OFF \
        -DCMAKE_C_COMPILER=$CC \
        -DCMAKE_CXX_COMPILER=$CXX \
        -DCMAKE_CUDA_COMPILER=nvcc \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo
    make -j && make install
    popd
    unload_pgi_cuda
}

install_nrn_cnrn_gpu_nmodl_sympy() {
    printf "\n----------------- INSTALL NEURON+CORENEURON+NMODL+SYMPY (GPU) --------------\n"
    load_pgi_cuda
    mkdir -p $BUILD_DIR/nrn_cnrn_gpu_nmodl_sympy && pushd $BUILD_DIR/nrn_cnrn_gpu_nmodl_sympy
    cmake $SOURCE_DIR/nrn \
        -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR/nrn_cnrn_gpu_nmodl_sympy \
        -DNRN_ENABLE_INTERVIEWS=OFF \
        -DNRN_ENABLE_RX3D=OFF \
        -DNRN_ENABLE_MPI=ON \
        -DCORENRN_ENABLE_OPENMP=OFF \
        -DNRN_ENABLE_CORENEURON=ON \
        -DCORENRN_ENABLE_GPU=ON \
        -DCORENRN_ENABLE_NMODL=ON \
        -DCORENRN_NMODL_DIR=$INSTALL_DIR/NMODL \
        -DCORENRN_NMODL_FLAGS="sympy --analytic" \
        -DNRN_ENABLE_PYTHON=ON \
        -DPYTHON_EXECUTABLE=$(which python3) \
        -DNRN_ENABLE_TESTS=OFF \
        -DCORENRN_ENABLE_UNIT_TESTS=OFF \
        -DCMAKE_C_COMPILER=$CC \
        -DCMAKE_CXX_COMPILER=$CXX \
        -DCMAKE_CUDA_COMPILER=nvcc \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo
    make -j && make install
    popd
    unload_pgi_cuda
}

# Provide the BUILD_TYPE as argument
run_nrnivmodl() {
    BUILD_TYPE=$1
    mkdir -p $INSTALL_DIR/$BUILD_TYPE/special && pushd $INSTALL_DIR/$BUILD_TYPE/special
    # Delete any executables from previous runs
    if [ $REINSTALL == 0 ]
    then
        rm -rf x86_64
    fi
    # Run nrnivmodl-core to generate the CoreNEURON library
    ../bin/nrnivmodl -coreneuron $BASE_DIR/sim
    popd
}

# 1. Setting source & build dependencies
setup_source
setup_modules
setup_python_packages

# 2. Installing base software
install_nmodl

# 3. Installing simulation engine
install_nrn_cnrn_cpu_mod2c
install_nrn_cnrn_cpu_nmodl
install_nrn_cnrn_cpu_nmodl_sympy
install_nrn_cnrn_gpu_mod2c
install_nrn_cnrn_gpu_mod2c_debug
install_nrn_cnrn_gpu_nmodl
install_nrn_cnrn_gpu_nmodl_sympy

# 4. Generate library
run_nrnivmodl nrn_cnrn_cpu_mod2c
run_nrnivmodl nrn_cnrn_cpu_nmodl
run_nrnivmodl nrn_cnrn_cpu_nmodl_sympy
run_nrnivmodl nrn_cnrn_gpu_mod2c
run_nrnivmodl nrn_cnrn_gpu_mod2c_debug
run_nrnivmodl nrn_cnrn_gpu_nmodl
run_nrnivmodl nrn_cnrn_gpu_nmodl_sympy
