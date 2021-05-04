# Spack package manager at CHPC - guide for users

- [User space usage](#user-space-usage)

# User space usage

User can build their own packages leveraging CHPC Spack installed packages, which will both save time and user disk space. To leverage this option, one has to either run CHPC installed Spack or install his/her own, and set the CHPC Spack installed packages as upstream.

## Activating up CHPC installed Spack

For the tcsh shell:
```
setenv SPACK_ROOT /uufs/chpc.utah.edu/sys/installdir/spack/spack
source $SPACK_ROOT/share/spack/setup-env.csh
setenv PATH $SPACK_ROOT/bin:$PATH
```
for bash shell:
```
export SPACK_ROOT=/uufs/chpc.utah.edu/sys/installdir/spack/spack
source $SPACK_ROOT/share/spack/setup-env.sh
export PATH=$SPACK_ROOT/bin:$PATH
```

This needs to be done every time one uses Spack, so, it may be useful to place it in `custom.csh` or `custom.sh`.

## Configuring Spack to for user repository with CHPC upstream

1. Create a user Spack directory. Whis is where all user Spack related files go, including user Spack configuration and user built packages:
```mkdir -p $HOME/spack/local```

2. In this directory put an user `config.yaml` which is the same as the one in `/uufs/chpc.utah.edu/sys/installdir/spack/spack/etc/spack`, except:
```
  install_tree:
    projections:
      all: ${ARCHITECTURE}/${COMPILERNAME}-${COMPILERVER}/${PACKAGE}-${VERSION}-${HASH}
    root: $HOME/spack/local/builds
  template_dirs:
  - $HOME/spack/local/templates
  module_roots:
    lmod: $HOME/spack/local/modules
```
This will cause Spack to put the built programs and module files to the user directory `$HOME/spack/local/builds` and `$HOME/spack/local/modules`.

Note: To make the Spack generated module files available, one needs to `module use $HOME/spack/local/modules`

3. Point to CHPC Spack built programs via the `upstream.yaml`:
```
upstreams:
  chpc-instance:
    install_tree: /uufs/chpc.utah.edu/sys/spack
```

These three steps need to be done only once.

### Checking that all is good

When this is set up, one can check if the package is using the upstream repo by e.g.
```
$ spack -C $HOME/spack/local spec -I octave target=nehalem
Input spec
--------------------------------
 -   octave arch=linux-None-nehalem

Concretized
--------------------------------
[-]  octave@6.2.0%gcc@8.3.0~arpack~curl~fftw~fltk~fontconfig~freetype~gl2ps~glpk~gnuplot~hdf5~jdk~llvm~magick~opengl~qhull~qrupdate~qscintilla~qt+readline~suitesparse~zlib arch=linux-centos7-nehalem
[^]      ^intel-mkl@2020.3.279%gcc@8.3.0~ilp64+shared threads=none arch=linux-centos7-nehalem
[^]          ^cpio@2.13%gcc@8.3.0 arch=linux-centos7-nehalem
[^]      ^pcre@8.44%gcc@8.3.0~jit+multibyte+utf arch=linux-centos7-nehalem
[^]      ^pkgconf@1.7.3%gcc@8.3.0 arch=linux-centos7-nehalem
[^]      ^readline@8.0%gcc@8.3.0 arch=linux-centos7-nehalem
[^]          ^ncurses@6.2%gcc@8.3.0~symlinks+termlib arch=linux-centos7-nehalem
```
The `[^]` denotes packages used from upstream, `[-]` packages that are missing in the upstream.

Now we can build the new program which will then store the build in `$HOME/spack/local/builds`
```
spack -C $HOME/spack/local spec octave target=nehalem
```

Because the `gcc/8.3.0` is not the default system compiler module files built this way can be made active with
```
module load gcc/8.3.0
module use $HOME/spack/local/modules/linux-centos7-x86_64/Compiler/linux-centos7-nehalem/gcc/8.3.0
```

NOTE: You can also put the user `config.yaml` and `upstream.yaml` to `~/.spack`, which will make it default for any user interaction, thus not requiring the `-C` option with the `spack` commands. More details on precendence of config file locations is [here](https://spack.readthedocs.io/en/latest/configuration.html#scope-precedence).

## Things to discuss at CHPC
- install dir and local drive for building, module files location
- Lmod integration (module use for the Spack generated modules)
- consider allowing only one compiler (spack modules set CC, CXX, ...)
- consider bash as shell for hpcapps
- policy in locating and loading Python modules
- platform specific settings/install tree - no need to specific sys branch for different architectures (x84, ppc64)


### Spack vs. easybuild
- spack has stronger dependency model (DAG), uninstall
- easier to use by user feedback
- power users can fairly easily use it for their own package building

## Advanced usage

I.e. installing a package that is not defined yet

### Creating a package definition file

- follow the package creation tutorial [http://spack.readthedocs.io/en/latest/tutorial_packaging.html](http://spack.readthedocs.io/en/latest/tutorial_packaging.html) if stuck.
- create basic YAML definition file that needs to be further filled in
 `spack create <package url>`
- edit the file and fill in whats needed
```spack edit <package>```
- find a package that is similar to what you are trying to install to get further ideas on what to do, based on the build specifics
-- autoconf, cmake, make, ...

### Debugging spack

I.e. figuring out where build or other errors come from

1. Run Spack inside Python
- source spack
- get into Python with `spack python`
- run Spack functions, e.g. `>>> print(spack.config.get_config('config'))` 

2. Put temporary print statements into the Spack code


## Plan:
- go over the ANL config and test - DONE
- test implementation in installdir - DONE
- local customizations, such as installdir and local scratch - DONE
 - ANL has /soft/spack - we can have /uufs/chpc.utah.edu/sys/spack
- local preinstalled software - mainly - PART
- prototype installdir structure, modules (module use for the spack built tree) - DONE
- apps to try (unless there is an explicit need)
 -- hpl - DONE
 -- check difference between intel, intel-parallel-studio, intel-mpi -> use pre-installed intel, intel-mpi, no intel-parallel-studio as it puts everything in one module
 -- when building look at how dependencies are being built (e.g. mpi, fftw)
- check package files
 -- lammps, matlab, pgi, namd, nwchem, espresso (QE)
- describe workflow on github
 -- installing existing package version - DONE
 -- installing new version of an existing package (including github pull request)
- things to decide/discuss in the future 
 -- python and R - Spack has separate package definitions for individual Python and R libraries
- package files to create - WRF, Amber
- webpage documentation for enabling power users to build codes on their own
- more preinstalled packages - Matlab, IDL
- Python specifics
 - make sure numpy, etc, are built with MKL - current py-numpy spec is confusing


## Tidbits

Local package repos
 var/spack/repos/builtin

Tidbits
 - use RPATH
 - generate modulefiles
 - - and ~ do the same thing - ~ may expand to user name in which case use - instead
 - can use find through dependencies, flags, etc
 - spack find -pe -- lists the location of the installed packages
   -- can change the root location, but spack will maintain the tree structure
 - make version dependencies
   ^openmpi@1.4: - use version higher than, inclusive (python slices)
   ^mpi@2 - spec constraint (MPI spec > 2.0)
 - extensions - Python packages - 
  -- they also have module files for each python package - may work better for us
 - while installing, can pres "v" for verbose output


- GPU - depend("cuda")

spack build cache -h - what is in binary cache

 - location of the packages to install
 -- etc/spack/defaults/config.yaml - never edit - git versioned
   -> $SPACK_ROOT - path to spack install that we're using
  -> $SPACK_ROOT/etc/spack/config.yaml 
  -> install_tree
 - can edit config files, e.g. 
    spack config edit compilers
     -- that edits the user specific config 
    spack config --scope defaults edit config
     -- that edits global config
 - compilers can be specified through modules in the config file - may be better for us
 - use distro packages
    zlib:
    paths:
      zlib@1.2.8%gcc@5.4.0 arch=linux-ubuntu16.04-x86_64: /usr
    buildable: False
  -> link version/arch to /usr and tell spack to never build it (even for different compiler)
  -> probably want to set some to this
  - limit # of threads to build package (default max cores)
   - just use -j xx in the spack instal, or in config file
   config:
     build_jobs: 4
 - in the config file use local mirror if it's available


Creating package names
 -- quick creation - will create basic YAML definition file that needs to be further filled in
 ```spack create <package url>```
 
## Update instructions

- wget the version you want in ```/uufs/chpc.utah.edu/sys/installdir/spack/``` and move to the right version
```
wget https://github.com/spack/spack/releases/download/v0.16.1/spack-0.16.1.tar.gz
tar xfz spack-0.16.1.tar.gz
mv spack-0.16.1 0.16.1
cd 0.16.1
```

- copy config files from the previous version
```
cp -r /uufs/chpc.utah.edu/sys/installdir/spack/spack/etc/spack/* etc/spack
```

- bring in the changes of the Lmod module files generation
```
cd /uufs/chpc.utah.edu/sys/installdir/spack/0.16.1
vim -d lib/spack/spack/modules/lmod.py ../0.16.0/lib/spack/spack/modules
```


- by default Spack includes path to all its lmod modules in the setup-env.csh - comment that out:
```/uufs/chpc.utah.edu/sys/installdir/spack/0.16.1/share/spack/setup-env.csh```
```
# Set up module search paths in the user environment
# MC comment out TCL path being added to MODULEPATH
#set tcl_roots = `echo $_sp_tcl_roots:q | sed 's/:/ /g'`
#set compatible_sys_types = `echo $_sp_compatible_sys_types:q | sed 's/:/ /g'`
#foreach tcl_root ($tcl_roots:q)
#    foreach systype ($compatible_sys_types:q)
#        _spack_pathadd MODULEPATH "$tcl_root/$systype"
#    end
#end
```
Similar will need to be done for the other shell init scripts, e.g. ```setup-env.sh```.
