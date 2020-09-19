WIP

### How to run this model

Make sure you have neuron with Python3 installed (or neuron module loaded). You can then compile mod files as:

```
cd sim
nrnivmodl .
```

Once `special` is created, you can run test model as:

```
mpirun -n 4 ./x86_64/special -python -mpi bulb3dtest.py
```

If you are running on HPC system then typical job script looks like:


```
#!/bin/bash
#SBATCH --account=projX
#SBATCH --partition=partition_name
#SBATCH --time 06:00:00

#SBATCH --ntasks-per-node=64
#SBATCH --nodes=2

# load modules here
module load neuron python
module load profile/advanced

mpirun ./x86_64/special -python -mpi bulb3dtest.py
```
