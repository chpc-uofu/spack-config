# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import collections
import itertools
import os.path
import posixpath
from typing import Any, Dict  # novm

import llnl.util.lang as lang

import spack.compilers
import spack.config
import spack.error
import spack.repo
import spack.spec
import spack.tengine as tengine
import spack.util.environment

from .common import BaseConfiguration, BaseContext, BaseFileLayout, BaseModuleFileWriter

import re

#: lmod specific part of the configuration
def configuration(module_set_name):
    config_path = "modules:%s:lmod" % module_set_name
    config = spack.config.get(config_path, {})
    return config


# Caches the configuration {spec_hash: configuration}
configuration_registry = {}  # type: Dict[str, Any]


def make_configuration(spec, module_set_name):
    """Returns the lmod configuration for spec"""
    key = (spec.dag_hash(), module_set_name)
    try:
        return configuration_registry[key]
    except KeyError:
        return configuration_registry.setdefault(key, LmodConfiguration(spec, module_set_name))


def make_layout(spec, module_set_name):
    """Returns the layout information for spec"""
    conf = make_configuration(spec, module_set_name)
    return LmodFileLayout(conf)


def make_context(spec, module_set_name):
    """Returns the context information for spec"""
    conf = make_configuration(spec, module_set_name)
    return LmodContext(conf)


def guess_core_compilers(name, store=False):
    """Guesses the list of core compilers installed in the system.

    Args:
        store (bool): if True writes the core compilers to the
            modules.yaml configuration file

    Returns:
        List of core compilers, if found, or None
    """
    core_compilers = []
    for compiler_config in spack.compilers.all_compilers_config():
        try:
            compiler = compiler_config["compiler"]
            # A compiler is considered to be a core compiler if any of the
            # C, C++ or Fortran compilers reside in a system directory
            is_system_compiler = any(
                os.path.dirname(x) in spack.util.environment.system_dirs
                for x in compiler["paths"].values()
                if x is not None
            )
            if is_system_compiler:
                core_compilers.append(str(compiler["spec"]))
        except (KeyError, TypeError, AttributeError):
            continue

    if store and core_compilers:
        # If we asked to store core compilers, update the entry
        # in the default modify scope (i.e. within the directory hierarchy
        # of Spack itself)
        modules_cfg = spack.config.get(
            "modules:" + name, {}, scope=spack.config.default_modify_scope()
        )
        modules_cfg.setdefault("lmod", {})["core_compilers"] = core_compilers
        spack.config.set("modules:" + name, modules_cfg, scope=spack.config.default_modify_scope())

    return core_compilers or None


class LmodConfiguration(BaseConfiguration):
    """Configuration class for lmod module files."""

    # Note: Posixpath is used here as well as below as opposed to
    # os.path.join due to spack.spec.Spec.format
    # requiring forward slash path seperators at this stage
    default_projections = {"all": posixpath.join("{name}", "{version}")}

    @property
    def core_compilers(self):
        """Returns the list of "Core" compilers

        Raises:
            CoreCompilersNotFoundError: if the key was not
                specified in the configuration file or the sequence
                is empty
        """
        value = configuration(self.name).get("core_compilers") or guess_core_compilers(
            self.name, store=True
        )

        if not value:
            msg = 'the key "core_compilers" must be set in modules.yaml'
            raise CoreCompilersNotFoundError(msg)
        return value

    @property
    def core_specs(self):
        """Returns the list of "Core" specs"""
        return configuration(self.name).get("core_specs", [])

    @property
    def hierarchy_tokens(self):
        """Returns the list of tokens that are part of the modulefile
        hierarchy. 'compiler' is always present.
        """
        tokens = configuration(self.name).get("hierarchy", [])

        # Check if all the tokens in the hierarchy are virtual specs.
        # If not warn the user and raise an error.
        not_virtual = [t for t in tokens if t != "compiler" and not spack.repo.path.is_virtual(t)]
        if not_virtual:
            msg = "Non-virtual specs in 'hierarchy' list for lmod: {0}\n"
            msg += "Please check the 'modules.yaml' configuration files"
            msg = msg.format(", ".join(not_virtual))
            raise NonVirtualInHierarchyError(msg)

        # Append 'compiler' which is always implied
        tokens.append("compiler")

        # Deduplicate tokens in case duplicates have been coded
        tokens = list(lang.dedupe(tokens))

        return tokens

    @property
    def requires(self):
        """Returns a dictionary mapping all the requirements of this spec
        to the actual provider. 'compiler' is always present among the
        requirements.
        """
        # If it's a core_spec, lie and say it requires a core compiler
        if any(self.spec.satisfies(core_spec) for core_spec in self.core_specs):
            return {"compiler": self.core_compilers[0]}

        # Keep track of the requirements that this package has in terms
        # of virtual packages that participate in the hierarchical structure
        requirements = {"compiler": self.spec.compiler}
        # For each virtual dependency in the hierarchy
        for x in self.hierarchy_tokens:
            # If I depend on it
            if x in self.spec and not self.spec.package.provides(x):
                requirements[x] = self.spec[x]  # record the actual provider
        return requirements

    @property
    def provides(self):
        """Returns a dictionary mapping all the services provided by this
        spec to the spec itself.
        """
        provides = {}

        # Treat the 'compiler' case in a special way, as compilers are not
        # virtual dependencies in spack

        # If it is in the list of supported compilers family -> compiler
        if self.spec.name in spack.compilers.supported_compilers():
            provides["compiler"] = spack.spec.CompilerSpec(str(self.spec))
        elif self.spec.name in spack.compilers.package_name_to_compiler_name:
            # If it is the package for a supported compiler, but of a different name
            cname = spack.compilers.package_name_to_compiler_name[self.spec.name]
            provides["compiler"] = spack.spec.CompilerSpec("%s@%s" % (cname, self.spec.version))

        # All the other tokens in the hierarchy must be virtual dependencies
        for x in self.hierarchy_tokens:
            if self.spec.package.provides(x):
                provides[x] = self.spec[x]
        return provides

    @property
    def available(self):
        """Returns a dictionary of the services that are currently
        available.
        """
        available = {}
        # What is available is what I require plus what I provide.
        # 'compiler' is the only key that may be overridden.
        available.update(self.requires)
        available.update(self.provides)
        return available

    @property
    def missing(self):
        """Returns the list of tokens that are not available."""
        return [x for x in self.hierarchy_tokens if x not in self.available]


class LmodFileLayout(BaseFileLayout):
    """File layout for lmod module files."""

    #: file extension of lua module files
    extension = "lua"

    @property
    def arch_dirname(self):
        """Returns the root folder for THIS architecture"""
        # Architecture sub-folder
        arch_folder_conf = spack.config.get("modules:%s:arch_folder" % self.conf.name, True)
        if arch_folder_conf:
            # include an arch specific folder between root and filename
            arch_folder = "-".join(
                [str(self.spec.platform), str(self.spec.os), str(self.spec.target.family)]
            )
            return os.path.join(self.dirname(), arch_folder)
        return self.dirname()

    @property
    def filename(self):
        """Returns the filename for the current module file"""

        # Get the list of requirements and build an **ordered**
        # list of the path parts
        requires = self.conf.requires
        hierarchy = self.conf.hierarchy_tokens
        path_parts = lambda x: self.token_to_path(x, requires[x])
        parts = [path_parts(x) for x in hierarchy if x in requires]

        # My relative path if just a join of all the parts
        hierarchy_name = os.path.join(*parts)

#       # Compute the absolute path
#       fullname = os.path.join(
#           self.arch_dirname,  # root for lmod files on this architecture
#           hierarchy_name,  # relative path
#           ".".join([self.use_name, self.extension]),  # file name
#       )
        #print("org self.use_name ", self.use_name)
        #print("hierarchy_name ", hierarchy_name)

        # MC in order to be able to modify the module path with projections, need to 
        # MC remove the hierarchy_name for MPI (hierarchy is done with the projection)
        if "MPI" in self.use_name:
          hierarchy_name = ""
        # MC also add "Compiler" to the path for the Compiler packages
        if "Core" not in parts and "MPI" not in self.use_name:
          # first redo use_name to move the arch forward
          # split_use_name = self.use_name.split("/")
          # change in 0.17.0
          # new_use_name = split_use_name[1]+"/"+split_use_name[2]
          #new_use_name = self.use_name
          #hierarchy_name = "Compiler/" + hierarchy_name
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
        # MC self.use_name includes the uarch which we include elsewhere - remove
        if "Core" in parts:
          orgname = self.use_name
#          setattr(self, "use_name",re.sub(r'^.*?/', '/', orgname)[1:])
          self._use_name = re.sub(r'^.*?/', '/', orgname)[1:]

        #print("self.arch_dirname ", self.arch_dirname)
        #print("hierarchy_name ", hierarchy_name)
        #print("self.use_name ", self.use_name)
        #print("self.extension ", self.extension)
        #print("fullname ", fullname)
        #print("spec: ",self.spec)
        #print("spec vars: ",self.spec.__dict__)
        #print("spec _dependents: ",self.spec._dependents)
        #print("spec _dependencies: ",self.spec._dependencies)
        #print("spec.variants: ",self.spec.variants)
        #print("type(spec.variants): ",type(self.spec.variants))
        return fullname

    def token_to_path(self, name, value):
        """Transforms a hierarchy token into the corresponding path part.

        Args:
            name (str): name of the service in the hierarchy
            value: actual provider of the service

        Returns:
            str: part of the path associated with the service
        """
        # General format for the path part
        path_part_fmt = os.path.join("{token.name}", "{token.version}")

        # If we are dealing with a core compiler, return 'Core'
        core_compilers = self.conf.core_compilers
        if name == "compiler" and str(value) in core_compilers:
            return "Core"

        # CompilerSpec does not have an hash, as we are not allowed to
        # use different flavors of the same compiler
        if name == "compiler":
            return path_part_fmt.format(token=value)

        # In case the hierarchy token refers to a virtual provider
        # we need to append an hash to the version to distinguish
        # among flavors of the same library (e.g. openblas~openmp vs.
        # openblas+openmp)
        path = path_part_fmt.format(token=value)
        path = "-".join([path, value.dag_hash(length=7)])
        return path

    @property
    def available_path_parts(self):
        """List of path parts that are currently available. Needed to
        construct the file name.
        """
        # List of available services
        available = self.conf.available
        # List of services that are part of the hierarchy
        hierarchy = self.conf.hierarchy_tokens
        # Tokenize each part that is both in the hierarchy and available
        parts = [self.token_to_path(x, available[x]) for x in hierarchy if x in available]
        return parts

    @property
    def unlocked_paths(self):
        """Returns a dictionary mapping conditions to a list of unlocked
        paths.

        The paths that are unconditionally unlocked are under the
        key 'None'. The other keys represent the list of services you need
        loaded to unlock the corresponding paths.
        """

        unlocked = collections.defaultdict(list)

        # Get the list of services we require and we provide
        requires_key = list(self.conf.requires)
        provides_key = list(self.conf.provides)

        # A compiler is always required. To avoid duplication pop the
        # 'compiler' item from required if we also **provide** one
        if "compiler" in provides_key:
            requires_key.remove("compiler")

        # Compute the unique combinations of the services we provide
        combinations = []
        for ii in range(len(provides_key)):
            combinations += itertools.combinations(provides_key, ii + 1)

        # Attach the services required to each combination
        to_be_processed = [x + tuple(requires_key) for x in combinations]

        # Compute the paths that are unconditionally added
        # and append them to the dictionary (key = None)
        available_combination = []
        for item in to_be_processed:
            hierarchy = self.conf.hierarchy_tokens
            available = self.conf.available
            ac = [x for x in hierarchy if x in item]
            available_combination.append(tuple(ac))
            parts = [self.token_to_path(x, available[x]) for x in ac]
            unlocked[None].append(tuple([self.arch_dirname] + parts))

        # Deduplicate the list
        unlocked[None] = list(lang.dedupe(unlocked[None]))

        # Compute the combination of missing requirements: this will lead to
        # paths that are unlocked conditionally
        missing = self.conf.missing

        missing_combinations = []
        for ii in range(len(missing)):
            missing_combinations += itertools.combinations(missing, ii + 1)

        # Attach the services required to each combination
        for m in missing_combinations:
            to_be_processed = [m + x for x in available_combination]
            for item in to_be_processed:
                hierarchy = self.conf.hierarchy_tokens
                available = self.conf.available
                token2path = lambda x: self.token_to_path(x, available[x])
                parts = []
                for x in hierarchy:
                    if x not in item:
                        continue
                    value = token2path(x) if x in available else x
                    parts.append(value)
                unlocked[m].append(tuple([self.arch_dirname] + parts))
            # Deduplicate the list
            unlocked[m] = list(lang.dedupe(unlocked[m]))
        return unlocked


class LmodContext(BaseContext):
    """Context class for lmod module files."""

    @tengine.context_property
    def has_modulepath_modifications(self):
        """True if this module modifies MODULEPATH, False otherwise."""
        return bool(self.conf.provides)

    @tengine.context_property
    def has_conditional_modifications(self):
        """True if this module modifies MODULEPATH conditionally to the
        presence of other services in the environment, False otherwise.
        """
        # In general we have conditional modifications if we have modifications
        # and we are not providing **only** a compiler
        provides = self.conf.provides
        provide_compiler_only = "compiler" in provides and len(provides) == 1
        has_modifications = self.has_modulepath_modifications
        return has_modifications and not provide_compiler_only

    @tengine.context_property
    def name_part(self):
        """Name of this provider."""
        return self.spec.name

    @tengine.context_property
    def version_part(self):
        """Version of this provider."""
        s = self.spec
        return "-".join([str(s.version), s.dag_hash(length=7)])

    @tengine.context_property
    def provides(self):
        """Returns the dictionary of provided services."""
        return self.conf.provides

    @tengine.context_property
    def missing(self):
        """Returns a list of missing services."""
        return self.conf.missing

    @tengine.context_property
    def unlocked_paths(self):
        """Returns the list of paths that are unlocked unconditionally."""
        layout = make_layout(self.spec, self.conf.name)
#        return [os.path.join(*parts) for parts in layout.unlocked_paths[None]]
        ##print("layout: ",dir(layout),layout.use_name)
        #print("all unlocked paths ",layout.unlocked_paths)
        #MC Here we join paths of the "unlocked_paths", as:
        #MC [('/uufs/chpc.utah.edu/sys/modulefiles/spack/linux-centos7-x86_64', 'mpich/3.3.2-jtr2h2o', 'intel/19.0.5.281')]
        #MC So far, this only seems to work for MPI, so, hard code our MPI path hierarchy
        if layout.unlocked_paths[None]:
          #print("old path:",[os.path.join(*parts) for parts in layout.unlocked_paths[None]])
          #print("spec.arch:",self.spec.architecture)
          # need to flip the last and last but one path, and remove hash from the now last path
          #print("if unlocked paths ",layout.unlocked_paths[None][0][1][0:-8])
          #if "mpi" in layout.unlocked_paths[None][0][1]:
          #need to list all the MPI providers - would be better to call the equivalent of 'mpi providers mpi'
          mpis=('mpich','mvapich2','openmpi','intel-mpi','intel-oneapi-mpi','hpcx-mpi','fujitsu-mpi','spectrum-mpi')
          if any(s in layout.unlocked_paths[None][0][1] for s in mpis):
            parts=[layout.unlocked_paths[None][0][0],"MPI",str(self.spec.architecture),layout.unlocked_paths[None][0][2],layout.unlocked_paths[None][0][1][0:-8]]
          # and this is for Compilers
          else:
            parts=[layout.unlocked_paths[None][0][0],"Compiler",str(self.spec.architecture),layout.unlocked_paths[None][0][1]]
          #print("parts:",parts)
          print("CHPC custom path:",[os.path.join(*parts)])
          return [os.path.join(*parts)]
        else:
          return [os.path.join(*parts) for parts in layout.unlocked_paths[None]]

    @tengine.context_property
    def conditionally_unlocked_paths(self):
        """Returns the list of paths that are unlocked conditionally.
        Each item in the list is a tuple with the structure (condition, path).
        """
        layout = make_layout(self.spec, self.conf.name)
        value = []
        conditional_paths = layout.unlocked_paths
        conditional_paths.pop(None)
        for services_needed, list_of_path_parts in conditional_paths.items():
            condition = " and ".join([x + "_name" for x in services_needed])
            for parts in list_of_path_parts:

                def manipulate_path(token):
                    if token in self.conf.hierarchy_tokens:
                        return "{0}_name, {0}_version".format(token)
                    return '"' + token + '"'

                path = ", ".join([manipulate_path(x) for x in parts])

                value.append((condition, path))
        return value


class LmodModulefileWriter(BaseModuleFileWriter):
    """Writer class for lmod module files."""

    default_template = posixpath.join("modules", "modulefile.lua")


class CoreCompilersNotFoundError(spack.error.SpackError, KeyError):
    """Error raised if the key 'core_compilers' has not been specified
    in the configuration file.
    """


class NonVirtualInHierarchyError(spack.error.SpackError, TypeError):
    """Error raised if non-virtual specs are used as hierarchy tokens in
    the lmod section of 'modules.yaml'.
    """
