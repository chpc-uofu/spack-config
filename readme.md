
- [Spack package manager at CHPC](#spack-package-manager-at-chpc)
  * [Basic information](#basic-information)
  * [Spack installation and setup](#installation-and-setup)
    + [Spack installation and setup](#spack-installation-and-setup)
    + [CHPC custom directory locations](#chpc-custom-directory-locations)
    + [CHPC configuration](#chpc-configuration)
      - [Compiler setup](#compiler-setup)
    + [CHPC Lmod integration](#chpc-lmod-integration)
      - [Configuration modification](#configuration-modification)
      - [Code modification](#code-modification)
      - [Spack generated module hierarchy layout](#spack-generated-module-hierarchy-layout)
      - [Integration into existing Lmod](#integration-into-existing-lmod)
    + [Adding already installed package (installed w/o spack)](#adding-already-installed-package--installed-w-o-spack-)
  * [Basic use](#basic-use)
    + [Source Spack](#source-spack)
    + [Basic installation workflow](#basic-installation-workflow)
      - [Dependencies:](#dependencies-)
      - [Build a package with dependency built with a different compiler:](#build-a-package-with-dependency-built-with-a-differen-compiler-)
      - [External packages (not directly downloadable)](#external-packages--not-directly-downloadable-)
      - [Examples](#examples)
      - [Modifying the spec file](#modifying-the-spec-file)
      - [Adding new version of an existing package](#adding-new-version-of-an-existing-package)
      - [Troubleshooting](#troubleshooting)
      - [Caveats](#caveats)
    + [CPU optimized builds](#cpu-optimized-builds)
    + [User space usage](#user-space-usage)
  * [Things to discuss at CHPC](#things-to-discuss-at-chpc)
    + [Spack vs. easybuild](#spack-vs-easybuild)
  * [Advanced usage](#advanced-usage)
    + [Creating a package definition file](#creating-a-package-definition-file)
    + [Debugging spack](#debugging-spack)
  * [Plan:](#plan-)
  * [Tidbits](#tidbits)
  * [Update instructions](#update-instructions)
  * [Updating/fixing Spack package](#updating/fixing-spack-package)

# Spack package manager at CHPC

## Basic information

- features overview - [http://spack.readthedocs.io/en/latest/features.html](http://spack.readthedocs.io/en/latest/features.html)
- Github repo - [https://github.com/spack/spack](https://github.com/spack/spack)
- documentation - [http://spack.readthedocs.io/en/latest/](http://spack.readthedocs.io/en/latest/)
- tutorial (very useful for learning both basic and more advanced functionality) - [http://spack.readthedocs.io/en/latest/tutorial.html](http://spack.readthedocs.io/en/latest/tutorial.html)
- [tutorial video](https://www.youtube.com/watch?v=RlczUgwFCJg) March 2021 

## Spack installation and setup

### Package installation and setup

Install from Github (may need to version in the future so may need to have own fork)

`git clone https://github.com/spack/spack.git`

Create a module file (see update instructions below), and then load the module, `module load spack`

Alternatively, to explicitly set up the environment, for tcsh:
```
setenv SPACK_ROOT /uufs/chpc.utah.edu/sys/installdir/spack/spack
source $SPACK_ROOT/share/spack/setup-env.csh
setenv PATH $SPACK_ROOT/bin:$PATH
ml use /uufs/chpc.utah.edu/sys/modulefiles/spack/linux-rocky8-x86_64/Core/linux-rocky8-nehalem
```
for bash:
```
export SPACK_ROOT=/uufs/chpc.utah.edu/sys/installdir/spack/spack
source $SPACK_ROOT/share/spack/setup-env.sh
export PATH=$SPACK_ROOT/bin:$PATH
ml use /uufs/chpc.utah.edu/sys/modulefiles/spack/linux-rocky8-x86_64/Core/linux-rocky8-nehalem
```
The last line adds to Lmod modules Spack built programs for the default (lowest common denominator) CPU architecture (lonepeak).

For newer CPU architecture specific builds, also load the following:
```
ml use /uufs/chpc.utah.edu/sys/modulefiles/spack/linux-rocky8-x86_64/Core/$CHPC_ARCH
```
where CHPC_ARCH depends on the machine where one logs in, in particular
- kingspeak - `linux-rocky8-sandybridge`
- notchpeak - `linux-rocky8-skylake_avx512`, `zen`, or `zen2` (for AMD nodes)

### CHPC custom directory locations

`/uufs/chpc.utah.edu/sys/spack` - old root directory for package installation (v. 0.17.2)
`/uufs/chpc.utah.edu/sys/spack/vxxx` - root directory for package installation (>= v. 0.19), vxxx=v019
  see update comment on `.spack-db` for the reason why we had to go with separate root directory for each Spack version

`/uufs/chpc.utah.edu/sys/modulefiles/spack` - Lmod module files

`/scratch/local`, or `~/.spack/stage` - local drive where the build is performed (= need to make sure to build on machine that has it)

`/uufs/chpc.utah.edu/sys/srcdir/spack-cache` - cache for downloaded package sources

`/uufs/chpc.utah.edu/sys/spack/mirror` - locally downloaded package sources (e.g. Amber)

`/uufs/chpc.utah.edu/sys/spack/vxxx/repos` - local repository of package recipes, setup documented in details at [https://spack.readthedocs.io/en/latest/repositories.html#](https://spack.readthedocs.io/en/latest/repositories.html#). Due to potential for syntactical changes in package recipes from version to version, the repo directory needs to be version dependent.

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
To see what configuration options are being used
```
spack config blame config
```

#### External packages

By default Spack builds all the dependencies. Most programs can use some basic system packages, e.g.
```
spack external find perl autoconf automake libtool pkgconf gmake tar openssl flex ncurses bison findutils m4 bash gawk util-macros fontconfig sqlite curl libx11 libxft libxscrnsaver libxext
```
This will go to `$USER/.spack/packages.yaml` which can be then moved to the system-wide `packages.yaml`

#### Compiler setup

Use the `spack compiler find` comand as described at [https://spack.readthedocs.io/en/latest/getting_started.html#compiler-configuration](https://spack.readthedocs.io/en/latest/getting_started.html#compiler-configuration) to add compiler to your user config, and then change it in the global config at `/uufs/chpc.utah.edu/sys/installdir/spack/spack/etc/spack` as well.

Since we have license info for Intel, PGI and Matlab in the `/uufs/chpc.utah.edu/sys/installdir/spack/spack/etc/spack/modules.yaml`, the license info does not need to be put in compilers.yaml. Also, RPATH seems to be added correctly without explicitly being in compilers.yaml.

(go over config files and explain concretization preferences in `packages.yaml`, as per [http://spack.readthedocs.io/en/latest/build_settings.html#concretization-preferences](http://spack.readthedocs.io/en/latest/build_settings.html#concretization-preferences))

As of v 0.17 we install more-less everything except for the system gcc compiler (8.5.0 in Rocky 8) with Spack. This includes the Intel and NVHPC compilers.

For example, to install a new version of the Intel compiler, we install it with Spack and then add it to the Spack's compilers.yaml as follows:
```
spack install intel-oneapi-compilers target=nehalem
```
check if compiler module has been installed in `/uufs/chpc.utah.edu/sys/modulefiles/spack/linux-rocky8-x86_64/Core/linux-rocky8-nehalem`, if not, we may also need to run `spack module lmod refresh intel-oneapi-compilers target=nehalem`.
Then load the module and get Spack to find the compiler:
```
module load intel-oneapi-compilers/2022.2.1
spack compiler find
```
User file (`/uufs/chpc.utah.edu/common/home/hpcapps/.spack/linux/compilers.yaml` will contain the new compiler definitions. This will result in the new compiler being available only to the user, therefore we need to make it available to everyone by copying it out of this file and pasting to `etc/spack/compilers.yaml`.

Also note that as of 2022, intel-oneapi-compilers come with 3 different compiler packages, `intel` for the legacy Intel compilers (icc, icpc, ifort), `oneapi` for the new LLVM based compilers (icx, icpx) and `dpcpp` for the Intel Data Parallel C++ (dpcpp).

### CHPC Lmod integration

In order to use our Core - Compiler - MPI hierarchy, we had to modify both the configuration files, and do a few small changes in the Spack code. 

#### Configuration modification

To get the module names/versions to be consitent with CHPC namings, we had to add the following to `modules.yaml`:
- remove the hash from the module name:
```
    hash_length: 0
```
- create modules only for explicitly installed packages (with `spack install package`), and whitelist the MPIs (currently just Intel MPI):
```
    blacklist_implicits: true
    whitelist:
      - intel-mpi
```
- specify that packages built with the system compiler are the Core packages (no compiler dependency):
```
    core_compilers:
      - 'gcc@8.5.0'
```
- set the hierarchy to MPI:
```
    hierarchy:
      - mpi
```
- use the [projections](https://spack.readthedocs.io/en/latest/module_file_support.html#customize-the-naming-of-modules) to customize the modules hierarchy. Also, add suffix `gpu` to the module name built for GPU (currently just CUDA). Note that the `all` is always evaluated and the rest of the projections have priority top-down, that is, in our case, if we have a CUDA package built with MPI, the `^mpi^cuda` takes precedence over the `^cuda`:
```
    projections:
      all: '{architecture}/{name}/{version}'
      ^mpi^cuda: 'MPI/{architecture}/{compiler.name}/{compiler.version}/{^mpi.name}/{^mpi.version}/{name}/{version}-gpu'
      ^mpi: 'MPI/{architecture}/{compiler.name}/{compiler.version}/{^mpi.name}/{^mpi.version}/{name}/{version}'
      ^cuda: '{architecture}/{name}/{version}-gpu'
```
- add `PACKAGE_ROOT` environment variable:
```
    all:
      environment:
        set:
          '{name}_ROOT': '{prefix}'
```

- to add the `add_property("arch","gpu")`, we modify the template file, `share/spack/templates/modules/modulefile.lua`, to test if `+cuda` variant is on, in the footer of the template:
```
{% if '+cuda' in spec.variants.__str__() %}
add_property("arch","gpu")
{% endif %}
```
Here note that the `spec.variants` is an object that contains all the variants, but we do a pattern match in the full variant string, so need to wrap it around the `__str__()` function.
#### Template modification

The Lmod module template is at `share/spack/templates/modules/modulefile.lua`. Original code for automatic loading of dependencies is:
```
{% block autoloads %}
{% for module in autoload %}
if not isloaded("{{ module }}") then
{% if verbose %}
    LmodMessage("Autoloading {{ module }}")
{% endif %}
    load("{{ module }}")
end
{% endfor %}
{% endblock %}
```
We prefer `depends_on()` since that automatically unloads the dependent modules, so, we change this to:
```
{% block autoloads %}
{% for module in autoload %}
{% if verbose %}
    LmodMessage("Autoloading {{ module }}")
{% endif %}
depends_on("{{ module }}")
{% endfor %}
{% endblock %}
```


#### Code modification

Even with the use of projections, as of ver. 0.16, parts of the path are hard coded, so, we had to make a small change to [lib/spack/spack/modules/lmod.py](https://github.com/spack/spack/blob/develop/lib/spack/spack/modules/lmod.py). The original code builds the module file path at line 244 as:
```
        fullname = os.path.join(
            self.arch_dirname,  # root for lmod files on this architecture
            hierarchy_name,  # relative path
            '.'.join([self.use_name, self.extension])  # file name - use_name = projection
        )   
```

The `hierarchy_name` is what Spack determines based on the `hierarchy` option from `modules.yaml`, and the `self.use.name` is what the projection builds, so for the `^mpi` projection definition, the final path is a concatenation of the two . For example, we end up with a path like this:
```
linux-centos7-x86_64/intel-mpi/2019.8.254-kvtpiwf/intel/19.0.5.281/MPI/intel/19.0.5.281/intel-mpi/2019.8.254/parallel-netcdf/1.12.1.lua
```
while we want
```
linux-centos7-x86_64/MPI/linux-centos7-nehalem/intel/19.0.5.281/intel-mpi/2019.8.254/parallel-netcdf/1.12.1.lua
```

Note also that the compiler/MPI hierarchy allows the module file to be unique without needing another specifier, like the hash, in the MPI/compiler hierarchy that Spack builds using the `mpi` hierarchy option.

Also, the Compiler hierarchy does not seem to be possible to be added via the projections, so, we can not add the `Compiler` string into the hierarchy path. 

To fix these two issues, we modified the Spacks `lmod.py` on line 242 as follows:
```
        # MC remove the hierarchy_name for MPI (hierarchy is done with the projection)
        if "MPI" in self.use_name:
          hierarchy_name = ""
        # MC also add "Compiler" to the path for the Compiler packages
        if "Core" not in parts and "MPI" not in self.use_name:
          # first redo use_name to move the arch forward
          split_use_name = self.use_name.split("/")
          new_use_name = split_use_name[1]+"/"+split_use_name[2]
          hierarchy_name = "Compiler/" + split_use_name[0] + "/" + hierarchy_name
          fullname = os.path.join(
              self.arch_dirname,  # root for lmod files
              hierarchy_name,  # relative path
              '.'.join([new_use_name, self.extension])  # file name - use_name = projection
          )                                             # can't modify self.use_name so need a new var
        else:
          # Compute the absolute path
          fullname = os.path.join(
              self.arch_dirname,  # root for lmod files
              hierarchy_name,  # relative path
              '.'.join([self.use_name, self.extension])  # file name - use_name = projection
          )
```

A more elegant way to fix this would be to modify the hierarchy_name in such a way that it would have the compiler/MPI hierarchy and have the `Compiler` and ```MPI``` path prefixes like the `Core`, but, that would require some more reverse engineering of the code.

One more fix is required to fix the `MODULEPATH` environment variable modification in the MPI module file. This is done in function `unlocked_paths()` at line 411 of file `lmod.py`, by replacing:
```
        return [os.path.join(*parts) for parts in layout.unlocked_paths[None]]
```
with
```
        if layout.unlocked_paths[None]:
          if "mpi" in layout.unlocked_paths[None][0][1]:
            parts=[layout.unlocked_paths[None][0][0],"MPI",str(self.spec.architecture),layout.unlocked_paths[None][0][2],layout.unlocked_paths[None][0][1][0:-8]]
          # and this is for Compilers
          else:
            parts=[layout.unlocked_paths[None][0][0],"Compiler",str(self.spec.architecture),layout.unlocked_paths[None][0][1]]
          print("CHPC custom path:",[os.path.join(*parts)])
          return [os.path.join(*parts)]
        else:
          return [os.path.join(*parts) for parts in layout.unlocked_paths[None]]

```
This changes the Spack generated path (which again ignores the projection) from e.g. `/uufs/chpc.utah.edu/sys/modulefiles/spack/linux-centos7-x86_64/mpich/3.3.2-jtr2h2o/intel/19.0.5.281` to `/uufs/chpc.utah.edu/sys/modulefiles/spack/linux-centos7-x86_64/MPI/intel/19.0.5.281/mpich/3.3.2` by flipping the last two items in the list and removing the hash from the MPI module number.

Again, this is a fairly ugly hack and it remains to be seen if it breaks something somewhere.

##### `spack module lmod loads` modification

`spack module lmod loads --dependencies` can be used to produce a list of `module load` commands for dependencies of a given package. This is especially useful to load Python modules stack. 

Spack does not seem to honor the modules hierarchy in the `module load modulename` output of this command, e.g., we get something like this:
```
ml gcc/8.3.0
spack module lmod loads --dependencies py-mpi4py
filename: /uufs/chpc.utah.edu/sys/modulefiles/spack/linux-centos7-x86_64/Compiler/linux-centos7-nehalem/gcc/8.3.0/intel-mpi/2019.8.254.lua
...
filename: /uufs/chpc.utah.edu/sys/modulefiles/spack/linux-centos7-x86_64/MPI/linux-centos7-nehalem/gcc/8.3.0/intel-mpi/2019.8.254/py-mpi4py/3.0.3.lua
# intel-mpi@2019.8.254%gcc@8.3.0 arch=linux-centos7-nehalem
module load linux-centos7-nehalem/intel-mpi/2019.8.254
...
# py-mpi4py@3.0.3%gcc@8.3.0 arch=linux-centos7-nehalem
module load MPI/linux-centos7-nehalem/gcc/8.3.0/intel-mpi/2019.8.254/py-mpi4py/3.0.3
```
The `filename` is corrected by the above modifications, but, the name of the module, used to load it, still has the old, incorrect, name. We modify this in `/uufs/chpc.utah.edu/sys/installdir/spack/0.16.1/lib/spack/spack/modules` at line 380 by replacing
```
            return writer.layout.use_name
```
with
```
            lastslash = writer.layout.use_name.rfind("/")
            #MC in hierarchical modules, should strip use_name till the 2nd / from the back
            return writer.layout.use_name[writer.layout.use_name.rfind("/",0,lastslash-1)+1:]
```

##### Dependencies modification

When a Spack generated module has a dependency, by default the target is a part of the module name, e.g. ```linux-centos7-nehalem/python/3.8.6```. This has to change to ```python/3.8.6```, which is done in ```common.py``` at ca. line 270, replacing:
```
    def _create_module_list_of(self, what):
        m = self.conf.module
        name = self.conf.name
        return [m.make_layout(x, name).use_name
                for x in getattr(self.conf, what)]
```

with
```
    def _create_module_list_of(self, what):
        m = self.conf.module
        retlist = []
        for x in getattr(self.conf, what):
          orgname = m.make_layout(x).use_name
          myname = re.sub(r'^.*?/', '/', orgname)[1:]
          print("WARNING - changing dependent module from %s to %s"%(orgname,myname))
          retlist.append(myname)
        return retlist
```

#### Spack generated module hierarchy layout

The hierarchy layout is thus as follows:

For Core packages:
```
OS-OSVer/Core/architecture/name/version
```
For Compiler dependent packages packages:
```
OS-OSVer/Compiler/architecture/compiler.name/compiler.version/name/version
```
For MPI dependent packages:
```
OS-OSVer/MPI/architecture/compiler.name/compiler.version/mpi.name/mpi.version/name/version
```

#### Integration into existing Lmod

In our module shell init files, we need to `use` the Spack Lmod module tree:

``` 
ml use /uufs/chpc.utah.edu/sys/modulefiles/spack/linux-rocky8-x86_64/Core/linux-rocky8-nehalem
```
and on Kingspeak and Notchpeak, also add the CPU architecture specific target, e.g for NP Intel nodes:

```ml use /uufs/chpc.utah.edu/sys/modulefiles/spack/linux-centos7-x86_64/Core/linux-rocky8-skylake_avx512```

For compilers - each compiler also needs to load the compiler specific module files, e.g.:
```/uufs/chpc.utah.edu/sys/modulefiles/spack/linux-rocky8-x86_64/Compiler/linux-rocky8-nehalem/intel/2021.1```
and also add cluster specific Compiler modules, e.g.:
```/uufs/chpc.utah.edu/sys/modulefiles/spack/linux-rocky8-x86_64/Compiler/linux-rocky8-skylake_avx512/intel/2021.1```

The first line may get added into the module file when the compiler is installed, but needs to be checked and possibly modified if there is `x86-64` instead of `nehalem`. 
The second, cluster specific line, is still in the works and will need to be added to the module once we get it working.

Same thing for the manually imported MPIs. MPIs installed with Spack should do this automatically with the code hack described above, for that particular CPU architecture (generic Nehalem, Sandybridge (KP) or Skylake (NP)).

If we use the Spack installed compiler to manually compile packages, we also need to add the path where we put the manually built modules into the `MODULEPATH`, e.g. for Intel compiler:
```
-- hand built packages
local mroot = os.getenv("MODULEPATH_ROOT")
local mdir = pathJoin(mroot,"Compiler/intel/2022.2.1")
prepend_path("MODULEPATH",mdir)
```

##### Caveat

`module spider` will not find the Spack built module in the hierarchy if the Compiler and Core module paths are not in the MODULEPATH. But Lmod should be capable of having multiple entries in MODULEPATH-> test if spider cache will make them to be found, https://lmod.readthedocs.io/en/latest/130_spider_cache.html#how-to-test-the-spider-cache-generation-and-usage. 
-> also test if can have different spider caches for different CPU architectures - https://lmod.readthedocs.io/en/latest/130_spider_cache.html#scenario-2-different-computers-owning-different-module-trees

### Adding already installed package (installed w/o spack)

Edit the `packages` config file appropriately:
```
spack config --scope site edit packages
  intel-mkl:
    paths:
      intel-mkl@2018.0.128 arch=linux-centos7-x86_64: /uufs/chpc.utah.edu/sys/installdir/intel/compilers_and_libraries_2018.0.128/linux/mkl
    buildable: False
```
- the `buildable: False` tells Spack to never install this package

In the actual package file, check the `prefix` variable so it maps to our directory structure
```
spack edit intel-mkl
```
Check what dependencies is Spack going to get:
```
spack spec hpl
spack spec hpl%intel
```

Test build the code (if the `prefix` is not correct, the build will crash here)
```spack install hpl```

## Basic use

i.e. build predefined packages

### Load the Spack module

```
module load spack
```
or for a specific version
```
module load spack/0.19
```

### Basic installation workflow
```spack list <package>``` - find if the package is known to Spack

```spack compilers``` - list available compilers (pre-installed as defined in `compilers.yaml` file or installed with Spack)

```spack info <package>``` - information about package versions, variants, dependencies

```spack spec -I <package> <options>``` - see to be installed version/compiler/dependencies

```spack install <package> <options>``` - install the package. NOTE - by default all CPU cores are used so on interactive nodes, use the `-j N` option to limit number of parallel build processes.

Note: By default Spack chooses the CPU microarchitecture where it runs, e.g. ```linux-centos7-sandybridge``` for ```kingspeak```, which may not run on all CHPC nodes. To build a generic CPU package, use the ```target=nehalem``` install option. At this point we almost always use the generic build, i.e.
```spack spec -I <package> <options> target=nehalem``` 
```spack install <package> <options> target=nehalem```

Note: The build files will be by default stored in `/scratch/local/$user/spack-stage`, followed by `~/.spack/stage`, followed by `$TEMPDIR`. To use a different directory, use the `-C` flag, e.g. `spack -C $HOME/spack install <package> <options>`.

```spack find -dlv <package>``` - display installed packages (`-dlv` will print dependencies and build options)

```spack module lmod refresh <package>``` - generate module file for the package that was installed - as of v. 0.19, modules seem to be generated during the install except when the module file is already present. This command will generate the module file even if it's already present (= overwrite the old module file).

#### Dependencies:
`%` - compiler, e.g. `%intel`

`@` - version, e.b. `%intel@2018.0.128`

Most of the packages are built either with the `gcc%8.5.0` RL8 system compiler, and with either `intel-oneapi-mpi@2021.1.1` (newer versions stall on the AMD nodes with some codes) or with the latest `openmpi`.

For example, to build with `intel-oneapi-mpi`:
```
spack install gromacs@2022.3%gcc@8.5.0+cuda+lapack+plumed target=nehalem ^intel-oneapi-mkl ^intel-oneapi-mpi@2021.1.1
```

`openmpi` requires some more options to force use of the UCX middleware that works correctly with InfiniBand:
```
spack spec -I abyss%gcc@8.5.0 target=nehalem ^openmpi%gcc@8.5.0 fabrics=ucx +cxx+internal-hwloc+thread_multiple schedulers=slurm +legacylaunchers ^ucx +mlx5_dv+verbs+ud+dc+rc+cma
```

#### Build a package with dependency built with a different compiler:
```spack install openmpi%pgi ^libpciaccess%gcc```
we don't do this very often, if at all. Example is when perl could not build with NVHPC, so we ended up using the one built with the OS gcc:
```
spack install openmpi@4.1.3%nvhpc@21.5~pmi+cxx target=nehalem fabrics=ucx +internal-hwloc+thread_multiple schedulers=slurm +legacylaunchers ^ucx%gcc@8.5.0 +mlx5-dv+verbs+cm+ud+dc+rc+cma ^perl@5.34.0%gcc@8.5.0
```

#### External packages (not directly downloadable)

Use (mirror)[https://spack.readthedocs.io/en/latest/basic_usage.html#non-downloadable-tarballs].

E.g for Amber:
```
cd /uufs/chpc.utah.edu/sys/spack/mirror/amber
```
download the Amber tarball if it's not there yet, modify the Spack spec file if this particular version is not in it, and then
```
spack spec -I amber@20.20%gcc@8.5.0 +mpi +python target=nehalem ^py-setuptools@57.4.0 ^py-jupyter-client@6.1.12 ^intel-oneapi-mpi@2021.1.1
```

#### Examples
`spack install hpl%intel` - install HPL with default version of Intel compiler and default BLAS (MKL) and MPI (Intel MPI).

`spack install --keep-stage espresso@6.1.0 %intel@2018.0.128 -elpa +mpi +openmp ^intel-mkl threads=openmp` - install Quantum Espresso with Intel compiler, MKL, Intel MPI (default) and threads, and keep the build directory. This is useful for checking how the build was done, especially when something does not work right with the program after it's been built.

#### Troubleshooting
`spack -d <command>`  will print out more detailed information with stack trace of the error - one then can look in the Spack python code and potentially modify it (as hpcapps) to print function arguments that may hint on the problem

`spack help -a` - gives the most generic help

`spack build-env <package> bash` - start a shell with environment that's used to build the package

` spack python` - runs Python with Spack module being loaded, so, one can run Spack functions, e.g. `>>> print(spack.config.get_config('config'))`

#### Caveats

- older versions of the packages may have trouble building with the default (newer) versions of dependencies. Unless older version is required, build the latest version. Spack developers recommend using older compiler versions (e.g. as of Feb 2021, gcc 8 rather than 9 or 10).

- sometimes dependency builds fail. If this happens, try to build the dependency independently. First run `spack spec` on the package you want to build, and find the full spec of the failed package. Then try to `spack install` this failed package with that full spec. E.g., for `py-spyder`, built as `spack install -j2 py-spyder%gcc@8.3.0^cmake@3.18.4^py-ipython@7.3.0^cairo+ft arch=nehalem`, we get `qt` build failure. The `qt` build specs as `py-spyder` requires are `spack -C ~/spack-mcuma install qt@5.14.2%gcc@8.3.0~dbus~debug~examples~framework~gtk+opengl~phonon+shared+sql+ssl+tools+webkit freetype=spack patches=7f34d48d2faaa108dc3fcc47187af1ccd1d37ee0f931b42597b820f03a99864c arch=linux-centos7-nehalem`.

`qt` is a good example of troubleshooting further build failure - the build fails as it is set above. Looking at the error message in the build log file, which is saved during build failures, and which states that Python 2 is required. This is confirmed by web search, and, noting by `spack edit qt` that Python is required by qt: `depends_on("python", when='@5.7.0:', type='build')`. The trouble is that some dependencies (e.g. `glib`) require Python 3 to build and/or run. Therefore need to go over the `spack spec` output to see what these packages are, and see what are the highest versions that dont have Python dependency. Then put these versions as explicit dependencies, e.g.:
```
spack -C ~/spack-mcuma spec qt@5.14.2%gcc@8.3.0~dbus~debug~examples~framework~gtk~opengl~phonon+shared+sql+ssl+tools+webkit freetype=spack patches=7f34d48d2faaa108dc3fcc47187af1ccd1d37ee0f931b42597b820f03a99864c arch=linux-centos7-nehalem ^cmake@3.18.4 ^glib@2.53.1 ^icu4c@60.3 
```

- be careful about rebuilding the failed package with added specs, like compiler flags (`ldflags`, .etc). Spack will try to rebuild all the dependencies

- sometimes during repeated build troubleshooting multiple builds of a package may be created which will conflict when e.g. generate module files. I usually keep only one build, and remove others. First check what is installed, e.g. `spack find -cfdvl qt`. Then uninstall the unwanted ones through a hash, e.g. `spack uninstall /sp26csq`. If there are dependents on this package, Spack will print a warning. This warning usually indicates that this version is the one that you want to keep.

### Modifying the spec file
In general, be careful when editing the spec files so they dont break.

Martin has his own fork of Spack which he used to create pull requests on modified spec files, but, in general we don't do pull request because the changes made are not tested agains different build options so we are not sure if they don't break something else, or the changes are minor enough that they would be expected to be present in a future Spack release.

If the spec file is edited, the original should be kept in the Spack default repo directory (e.g. `/uufs/chpc.utah.edu/sys/installdir/spack/0.19.0/var/spack/repos/builtin/packages`), and a copy of the package should go to one of two locations:

- `/uufs/chpc.utah.edu/sys/spack/vxxx/repos/updated` - when only a new version of a the package has been added
- `/uufs/chpc.utah.edu/sys/spack/vxxx/repos/modified` - when there was further modification of the package, e.g. by adding a new variant, build flag, etc.

Once the package spec has been moved to one of the custom repos, we can edit it either with `spack edit` command or directly with a favorite editor.

`spack edit <package>` will open vi editor with the packages package.py spec file. E.g. `spack edit hpl`.
`env['F90']=spack_fc` - adds environment variable F90 that points to Spacks defined FC compiler, `spack_fc`
`env['FCFLAGS']='-g -O3 -ip'` - adds explicitly defined environment variable

#### Adding new version of an existing package

First get the checksum with `spack checksum <package>`. If new version is not found, see what is the hierarchy of the versions in the URL specified in the `package.py`. This can be specified by `list_url` and `list_depth`, as e.g. in `postgresql` package. This is detailed in [http://spack.readthedocs.io/en/latest/packaging_guide.html#finding-new-versions](http://spack.readthedocs.io/en/latest/packaging_guide.html#finding-new-versions).

For example to add a new version to `cp2k`, first get the package:
```
$ wget https://github.com/cp2k/cp2k/releases/download/v2022.2/cp2k-2022.2.tar.bz2
$ sha256sum cp2k-2022.2.tar.bz2
1a473dea512fe264bb45419f83de432d441f90404f829d89cbc3a03f723b8354  cp2k-2022.2.tar.bz2
```
Then copy the spec:
```
cp -r /uufs/chpc.utah.edu/sys/installdir/spack/0.19.0/var/spack/repos/builtin/packages/cp2k /uufs/chpc.utah.edu/sys/spack/vxxx/repos/modified
```
Then edit the spec to add the new version:
```
spack edit cp2k
```
and there add
```
    version("2022.2", sha256="1a473dea512fe264bb45419f83de432d441f90404f829d89cbc3a03f723b8354")
```
the `sha256` is the checksum we got from the downloaded package.

#### Modifying an existing package

For example, we modified LAMMPS to add new user packages, so, first we copy the original Spack spec to the `modified` directory
```
cp -r /uufs/chpc.utah.edu/sys/installdir/spack/0.19.0/var/spack/repos/builtin/packages/lammps /uufs/chpc.utah.edu/sys/spack/vxxx/repos/modified
```
then we edit the spec file, `spack edit lammps` and change the `supported packages` list as:
```
    # as of Feb22 many packages have changed their names from user-XXX to XXX
    # https://docs.lammps.org/Packages_list.html
    supported_packages = ['adios', 'atc', 'asphere', 'awmpd', 'body', 'bocs',
                          'brownian', 'cg-dna', 'cg-sdk', 'class2', 'colloid',
                          'compress', 'colvars', 'coreshell', 'diffraction',
                          'dipole', 'dpd-basic', 'dpd-meso', 'dpd-react',
                          'dpd-smooth', 'drude', 'eff', 'extra-compute', 'extra-dump',
                          'extra-fix', 'extra-molecule', 'extra-pair', 'fep',
                          'granular', 'h5md', 'interlayer', 'kokkos', 'kspace',
                          'latboltz', 'latte', 'machdyn', 'manifold', 'manybody', 'mc', 'meam',
                          'mesont', 'message', 'mgpt', 'misc', 'ml-iap', 'ml-snap',
                          'mofff', 'molecule', 'mpiio', 'netcdf', 'openmp', 'opt',
                          'orient', 'peri', 'phonon', 'plugin', 'plumed', 'poems',
                          'ptm', 'python', 'qeq', 'qtb', 'reaction', 'reaxff',
                          'replica', 'rigid', 'shock', 'smtbq', 'sph', 'spin', 'srd',
                          'tally', 'uef', 'voronoi', 'yaff']
    # not included packages (ext. dependencies and/or extra parameters):
    # 'gpu', 'intel', 'ml-hdnnp', 'ml-pace', 'ml-quip', 'ml-rann',
    # 'molfile', 'mscg', 'qmmm', 'scafacos', 'vtk'
    # packages explicitly listed as variants: 'kim'
```

Since we did not added all the user packages (omitted ones with extra dependencies or build parameters), we did not push these changes upstream.

### CPU optimized builds

#### Target microarchitectures

Microarchitectures availble through Spack are queried with `[spack arch --known-targets](https://spack.readthedocs.io/en/latest/packaging_guide.html?highlight=target#architecture-specifiers)`. The uarch name can be used as the `target` specifier in the `spack install target=XXX` option. 

The Spack docs also [https://spack.readthedocs.io/en/latest/packaging_guide.html?highlight=target#architecture-specifiers](describe) how this can be used in the package specs to implement uarch specific optimizations.

#### Spack implementation specifics

When the `target` option is used, Spack injects the architecture optimization flags into the builds. While this is not clear from the `spack install --verbose` option, since that outputs the compilation lines as Spack reads them, the actual compilation lines that Spack uses are obtained with the `--debug` option, e.g. `spack --debug install --verbose`. When doing that, two files will be produced in the current directory:
    spack-cc-{NAME}-{HASH}.in.log
    spack-cc-{NAME}-{HASH}.out.log

The in.log files shows the compiler output before the wrapper injects flags. The out.log file shows the compiler output after injecting the flags.

The target detection capability is coming from [archspec](http://github.com/archspec/archspec), Spack library for detecting and reasoning about cpus and compilers. More details are at [this paper](https://tgamblin.github.io/pubs/archspec-canopie-hpc-2020.pdf). In Spack, archspec now lives in [lib/spack/external](https://github.com/spack/spack/tree/develop/lib/spack/external/archspec). And the information it’s using to determine flags is in [this file](https://github.com/spack/spack/blob/develop/lib/spack/external/archspec/json/cpu/microarchitectures.json). That will tell you all the microarchitecture targets that spack knows about, as well as the compilers and compiler flags it associates with them.

Note that at the moment, Spack is only adding options that have to do with the instruction set (e.g., `-march`) and not specific optimization flags (those are left to the packages, the build systems, and user configuration).  The targets are designed to tell us where we can use optimized binaries — they’re currently aimed mainly at ensuring compatibility.

Detailed discussion about this is at [this thread](https://groups.google.com/g/spack/c/2cExxjIvuOI).

### Building programs

#### BLAS libraries and threads

Spack defines `threads=[none,openmp,pthreads,tbb]` to specify thread support in BLAS libraries like `intel-mkl` or `openblas`, with the `threads=none` default. This means that by default the package built with the BLAS dependency will have the BLAS library linked in as sequential, even if `openmp` of this package is specified. To get around this, we need to explicitly list the `threads=openmp` in the BLAS dependency, for example:
```
spack install quantum-espresso+openmp ^intel-mkl threads=openmp
```

### User space usage

It may be a good idea to test if installation of a package works as intended in installing it to home directory before deploying to the `sys` branch. This same approach can be used by an user to extend CHPC installed programs by his/her own.

For this we need to create user Spack configuration that upstreams to the CHPC installation.
1. Create a user Spack directory
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
This will cause Spack to put the built programs and module files to the user directory.

3. Point to CHPC Spack built programs via the `upstream.yaml`:
```
upstreams:
  chpc-instance:
    install_tree: /uufs/chpc.utah.edu/sys/spack
```

Once this is set up, one can check if the package is using the upstream repo by e.g.
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

Because the `gcc/8.3.0` is not the default system compiler module files built this way can be loaded with
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
cp /uufs/chpc.utah.edu/sys/installdir/spack/spack/etc/spack/* etc/spack
```
also diff these files with the files in `etc/spack/default` to see what changes to them were made in the new version and move in the new options/changes.

Since the .spack-db and ~/.spack/cache can be incompatible between versions, modify the following parts of `config.yaml`:
```
  install_tree:
    root: /uufs/chpc.utah.edu/sys/spack/v019
...
  misc_cache: ~/.spack/cache/v019
```

- copy the licenses
```
cp -r /uufs/chpc.utah.edu/sys/installdir/spack/spack/etc/spack/licenses etc/spack
```

- bring in the changes of the Lmod module files generation
```
cd /uufs/chpc.utah.edu/sys/installdir/spack/0.16.1
vim -d lib/spack/spack/modules/lmod.py ../0.16.2/lib/spack/spack/modules
vim -d lib/spack/spack/modules/common.py ../0.16.2/lib/spack/spack/modules
vim -d share/spack/templates/modules/modulefile.lua ../0.16.2/share/spack/templates/modules
```

- by default Spack includes path to all its TCL modules in the setup-env.csh - comment that out:
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

- remove the ```etc/spack/defaults/modules.yaml``` as it gets used over the customized ```etc/spack/modules.yaml```. Verify the correct modules config by ```spack config blame modules```.

- create module file for the new version by copying previous version, and changing the `version` to new version
  also module load and unload, and then check `env` in bash and tcsh, and `declare -f` to see if some new environment variable or shell function has been added to the new Spack version. If so, add them to the `unset` in the module file.

- sometimes Spack updates change `spack` objects hierarchy or syntax, which has a two-fold implication:
1. The `chpc` and `chpc-updated` spack recipes use old incompatible spack object methods, which results in various semi-cryptic errors. As of 0.19 this required us to create a specific repository for the version 0.19. The workaround is to have separate repositories for different Spack versions.
```
spack repo create /uufs/chpc.utah.edu/sys/spack/v019/repos/updated
spack repo add /uufs/chpc.utah.edu/sys/spack/v019/repos/updated
spack repo create /uufs/chpc.utah.edu/sys/spack/v019/repos/modified
spack repo add /uufs/chpc.utah.edu/sys/spack/v019/repos/modified
```
2. The Spack database in `/uufs/chpc.utah.edu/sys/spack/.spack-db` points to repositories (also called namespaces) which are incompatible in #1, causing further errors. The workaround is to move away the old .spack-db and create a new one, though this necessitates to re-build all the dependent packages.

## Updating/fixing Spack package

When you feel like the fix you did to a Spack package may benefit the whole community, submit it as a pull request.

First, make a fork of Spack and clone it to your workstation:
1. Fork the [https://github.com/spack/spack](https://github.com/spack/spack) into your github page.
2. Clone it to your workstation
```
git clone https://github.com/mcuma/spack
```

Now you are ready to make the change you want and create the pull request:
1. Create a new branch in your Spack cloned repo
```
git checkout -b packagename-my-fix
```
2. Modify the package spec that you are fixing
3. Commit the change and push it to the GitHub
```
git commit -am "Meaningful description of the change"
git push origin packagename-my-fix
```
4. On the GitHub page, create the new pull request from the new branch that you have just pushed.

The Spack pull request workflow is that first it needs to be reviewed by a person that has write access to the Spack repo. Then Continuous Integration scripts will run to check the change. They are faily strict with syntax and style of the Python code so be aware of that. Once the CI tests pass, it is up to the maintainer to accept the pull request. Sometime they take time to do that.
