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

3. In `~/.spack`, put an user `config.yaml` which is the same as the one in `/uufs/chpc.utah.edu/sys/installdir/spack/spack/etc/spack`, i.e.
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
4. Create a new file `~/.spack/modules.yaml` and there put:
```
modules:
  default:
    roots:
      lmod: $HOME/spack/local/modules
```
This will cause Spack to put the built programs and module files to the user directory `$HOME/spack/local/builds` and `$HOME/spack/local/modules`.

Note: To make the Spack generated module files available, one needs to `module use $HOME/spack/local/modules/Core/linux-rocky8-nehalem`

4.  To import the CHPC Spack built programs, create a new file `~/.spack/upstreams.yaml`:
```
upstreams:
  chpc-instance:
    install_tree: /uufs/chpc.utah.edu/sys/spack/v019
```

## Activating CHPC installed Spack

Load the Spack module:
```
module load spack
```

This needs to be done every time one uses Spack in a fresh terminal (like using any other module).

## Checking that all is good

When this is set up, one can check if the package is using the upstream repo by e.g.
```
$ spack spec -I octave target=nehalem
Input spec
--------------------------------
 -   octave arch=None-None-nehalem

Concretized
--------------------------------
 -   octave@7.3.0%gcc@8.5.0~arpack+bz2~curl~fftw~fltk~fontconfig~freetype~gl2ps~glpk~gnuplot~hdf5~jdk~llvm~magick~opengl~qhull~qrupdate~qscintilla~qt+readline~suitesparse~zlib build_system=autotools arch=linux-rocky8-nehalem
[^]      ^bzip2@1.0.6%gcc@8.5.0~debug~pic+shared build_system=generic arch=linux-rocky8-x86_64
[^]      ^intel-mkl@2020.4.304%gcc@8.5.0~ilp64+shared build_system=generic threads=none arch=linux-rocky8-nehalem
[^]          ^cpio@2.12%gcc@8.5.0 build_system=autotools arch=linux-rocky8-x86_64
 -       ^pcre@8.45%gcc@8.5.0~jit+multibyte+utf build_system=autotools arch=linux-rocky8-nehalem
[^]      ^pkgconf@1.4.2%gcc@8.5.0 build_system=autotools arch=linux-rocky8-x86_64
 -       ^readline@8.1.2%gcc@8.5.0 build_system=autotools arch=linux-rocky8-nehalem
[^]          ^ncurses@6.1.20180224%gcc@8.5.0~symlinks+termlib abi=6 build_system=autotools arch=linux-rocky8-x86_64
 -       ^texinfo@6.5%gcc@8.5.0 build_system=autotools patches=12f6edb,1732115 arch=linux-rocky8-x86_64

```
The `[^]` denotes packages used from upstream, `[-]` packages that are missing in the upstream.

Now we can build the new program which will then store the build in `$HOME/spack/local/builds`
```
spack install octave~readline target=nehalem
```

Because the system default `gcc/8.5.0` module does not have the user modules path, we need to add it with `module use`.
```
module load gcc/8.5.0
module use $HOME/spack/local/modules/linux-rocky8-x86_64/Core
```

NOTE: You can put the configure files to other directory than `~/.spack`, but then you will need to point to this directory with the `-C` option of the `spack` commands. More details on precendence of config file locations is [here](https://spack.readthedocs.io/en/latest/configuration.html#scope-precedence).

### Basic installation workflow

See part of the main [readme.md](readme.md#basic-installation-workflow)
