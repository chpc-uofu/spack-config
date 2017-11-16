# Spack package manager at CHPC

## Basic information

- features overview - [http://spack.readthedocs.io/en/latest/features.html](http://spack.readthedocs.io/en/latest/features.html)
- Github repo - [https://github.com/spack/spack](https://github.com/spack/spack)
- documentation - [http://spack.readthedocs.io/en/latest/](http://spack.readthedocs.io/en/latest/)
- tutorial (very useful for learning both basic and more advanced functionality) - [http://spack.readthedocs.io/en/latest/tutorial.html](http://spack.readthedocs.io/en/latest/tutorial.html)

## Installation and setup

### CHPC custom configuration (to be confirmed)

```/uufs/chpc.utah.edu/sys/spack``` - root directory for package installation
```/uufs/chpc.utah.edu/sys/modulefiles/spack``` - Lmod module files
```/scratch/local``` - local drive where the build is performed (= need to make sure to build on machine that has it)


### Package installation and setup

Install from Github (may need to version in the future so may need to have own fork)
```git clone https://github.com/spack/spack.git```

Basic setup (to be put to hpcapps .tcshrc)
```
setenv SPACK_ROOT /uufs/chpc.utah.edu/sys/installdir/spack/spack
source $SPACK_ROOT/share/spack/setup-env.csh
```

### CHPC configuration

All configuration files (and package definition files) are in YAML format so pay attention to indentation, etc.
First basic configuration (paths, ...):
```
cp etc/spack/defaults/config.yaml etc/spack/
spack config --scope site edit config
```
Then based on Argonne configs:
```
spack config --scope site edit compilers
spack config --scope site edit modules
spack config --scope site edit packages
```
check with
```
spack config get config
```
Compilers defined are the latest Intel (2018.0), PGI (17.10), stock gcc (4.8.5) and gcc(5.4.0). More can be added, or perhaps easier built with Spack.

(go over config files and explain concretization preferences in ```packages.yaml```, as per [http://spack.readthedocs.io/en/latest/build_settings.html#concretization-preferences](http://spack.readthedocs.io/en/latest/build_settings.html#concretization-preferences))

Other preinstalled packages that have been included into Spack (list may grow in the future):
- Intel MPI
- Intel MKL

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

### Adding already installed package (installed w/o spack)

Edit the ```packages``` config file appropriately:
```
spack config --scope site edit packages
  intel-mkl:
    paths:
      intel-mkl@2018.0.128 arch=linux-centos7-x86_64: /uufs/chpc.utah.edu/sys/installdir/intel/compilers_and_libraries_2018.0.128/linux/mkl
    buildable: False
```
- the ```buildable: False``` tells Spack to never install this package

In the actual package file, check the ```prefix``` variable so it maps to our directory structure
```
spack edit intel-mkl
```
Check what dependencies is Spack going to get:
```
spack spec hpl
spack spec hpl %intel
```

Test build the code (if the ```prefix``` is not correct, the build will crash here)
```spack install hpl```

## Basic use

i.e. build predefined packages

### Source Spack

if not done in .tcshrc
```
setenv SPACK_ROOT /uufs/chpc.utah.edu/sys/installdir/spack/spack
source $SPACK_ROOT/share/spack/setup-env.csh
```

### Basic installation workflow
```spack list <package>``` - find if the package is known to Spack
```spack spec <package> <options>``` - see to be installed version/compiler/dependencies
```spack install <package> <options>``` - install the package
```spack find -dl <package>``` - display installed packages (```-dl``` will print version details)

Dependencies:
```%``` - compiler, e.g. ```%intel```
```@``` - version, e.b. ```%intel@2018.0.128```
