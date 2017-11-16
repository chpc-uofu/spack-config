# Spack package manager at CHPC

## Basic information

- features overview - [http://spack.readthedocs.io/en/latest/features.html](http://spack.readthedocs.io/en/latest/features.html)
- Github repo - [https://github.com/spack/spack](https://github.com/spack/spack)
- documentation - [http://spack.readthedocs.io/en/latest/](http://spack.readthedocs.io/en/latest/)
- tutorial (very useful for learning both basic and more advanced functionality) - [http://spack.readthedocs.io/en/latest/tutorial.html](http://spack.readthedocs.io/en/latest/tutorial.html)

## Installation and setup

### CHPC custom configuration (to be confirmed)

### Package installation and setup

Install from Github (may need to version in the future so may need to have own fork)
```git clone https://github.com/spack/spack.git```

Basic setup (to be put to hpcapps .tcshrc)
```
setenv SPACK_ROOT /uufs/chpc.utah.edu/sys/installdir/spack/spack
source $SPACK_ROOT/share/spack/setup-env.csh
```

### CHPC configuration
```
cp etc/spack/defaults/config.yaml etc/spack/
spack config --scope site edit config
```
based on Argonne configs
```
spack config --scope site edit compilers
spack config --scope site edit modules
spack config --scope site edit packages
```
check with
```
spack config get config
```

### CHPC Lmod integration
In our module shell init files, we also need to ```use``` the Spack Lmod module tree:
``` ml use /uufs/chpc.utah.edu/sys/modulefiles/spack/linux-centos7-x86_64/Core```

For compilers - each compiler also needs to load the compiler specific module files, e.g.:
```/uufs/chpc.utah.edu/sys/modulefiles/spack/linux-centos7-x86_64/intel/2018.0.128```
Now emulate this as:
```
ml intel/18
ml use /uufs/chpc.utah.edu/sys/modulefiles/spack/linux-centos7-x86_64/intel/2018.0.128
```

Since we are using Spack's Intel MPI package definition, the IMPI path is set up correctly when loading ```intel-mpi``` module from the Spack module tree.

For gcc, things are a bit different. gcc compiler modules equal to ```Core```, which contains intel-mpi, which sets the module path to IMPI.
(had to fix intel-mpi module as it is for some reason doing ml() and module())




