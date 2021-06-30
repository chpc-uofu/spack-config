# Spack package manager at CHPC - guide for users

- [User space usage](#user-space-usage)
- [Setting up user-based Spack](#setting-up-user-based-spack)
  * [User Spack configuration](#user-spack-configuration)
  * [Activating CHPC installed Spack](#activating-chpc-installed-spack)
  * [Checking that all is good](#checking-that-all-is-good)
- [Basic installation workflow](#basic-installation-workflow)

# User space usage

User can build their own packages leveraging CHPC Spack installed packages, which will both save time and user disk space. To leverage this option, one has to either run CHPC installed Spack or install his/her own, and set the CHPC Spack installed packages as upstream.

# Setting up user-based Spack

## User Spack configuration

To run spack in user space, one needs to tell it where to write all its files (typically users home directory), and configure to use the CHPC upstream repository. This needs to be done only once.

1. Create a user Spack directory. Whis is where all user built packages and modules go:
```mkdir -p $HOME/spack/local```

2. If not already created, make a `~/.spack` directory where the configuration files go:
```mkdir -p $HOME/.spack```

2. In `~/.spack`, put an user `config.yaml` which is the same as the one in `/uufs/chpc.utah.edu/sys/installdir/spack/spack/etc/spack`, i.e.
```cp /uufs/chpc.utah.edu/sys/installdir/spack/spack/etc/spack/config.yaml ~/.spack```

And then modify the following in this file:
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

3.  To import the CHPC Spack built programs, create a new file `~/.spack/upstreams.yaml`:
```
upstreams:
  chpc-instance:
    install_tree: /uufs/chpc.utah.edu/sys/spack
```

## Activating CHPC installed Spack

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

## Checking that all is good

When this is set up, one can check if the package is using the upstream repo by e.g.
```
$ spack spec -I octave target=nehalem
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
spack install octave target=nehalem
```

Because the `gcc/8.3.0` is not the default system compiler module files built this way can be made active with
```
module load gcc/8.3.0
module use $HOME/spack/local/modules/linux-centos7-x86_64/Compiler/linux-centos7-nehalem/gcc/8.3.0
```

NOTE: You can put the configure files to other directory than `~/.spack`, but then you will need to point to this directory with the `-C` option of the `spack` commands. More details on precendence of config file locations is [here](https://spack.readthedocs.io/en/latest/configuration.html#scope-precedence).

### Basic installation workflow

See part of the main [readme.md](readme.md#basic-installation-workflow)
