-- -*- lua -*-
-- 
local version = "0.19.2"

help(
[[
This module loads the Spack package manager environment
]])

whatis("Name: Spack")
whatis("Version: " .. version)
whatis("Category: package manager")
whatis("Keywords: System, package manager")
whatis("URL: https://spack.readthedocs.io")
whatis("Installed on 04/12/2023")

-- PATH & MANPATH
local base = pathJoin("/uufs/chpc.utah.edu/sys/installdir",myModuleName(), version)
setenv("SPACK_ROOT",base)
prepend_path("PATH",pathJoin(base,"bin"))

-- For loading module we source the setup_env script
if (myShellType() == "csh") then
-- source_sh() does not work with Spack's setup-env.csh
  execute{cmd="source " .. base .. "/share/spack/setup-env."..myShellType(),modeA={"load"}}
-- csh sets these environment variables and aliases
  cmd = "unalias _spack_pathadd; unalias spack; unalias spacktivate; " ..
        "unsetenv SPACK_PYTHON;" ..
        "unset _sp_compatible_sys_types; unset _sp_lmod_roots; unset _sp_sys_type; unset _sp_tcl_roots;" ..
        "unset _spack_share_dir; unset _spack_source_file;" ..
        "unset tcl_root; unset tcl_roots;" 
  execute{cmd=cmd, modeA={"unload"}}

else
  local mycmd= base .. "/share/spack/setup-env."..myShellType()
  --io.stderr:write("cmd:  ",mycmd,"\n")
  source_sh("bash", mycmd)
end

