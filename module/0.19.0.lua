-- -*- lua -*-
-- 
local version = "0.19.0"

help(
[[
This module loads the Spack package manager environment
]])

whatis("Name: Spack")
whatis("Version: " .. version)
whatis("Category: package manager")
whatis("Keywords: System, package manager")
whatis("URL: https://spack.readthedocs.io")
whatis("Installed on 11/22/2022")


-- PATH & MANPATH
local base = pathJoin("/uufs/chpc.utah.edu/sys/installdir",myModuleName(), version)

setenv("SPACK_ROOT",base)
prepend_path("PATH",pathJoin(base,"bin"))

-- For loading module we source the setup_env script

-- local mycmd="source " .. base .. "/share/spack/setup-env."..myShellType()
-- io.stderr:write("cmd:  ",mycmd,"\n")
execute{cmd="source " .. base .. "/share/spack/setup-env."..myShellType(),modeA={"load"}}

-- For unloading manually remove the variable set by the setup_env
-- could also do "conda deactivate; " but that should be part of independent VE module
if (myShellType() == "csh") then
-- csh sets these environment variables and aliases
  cmd = "unalias _spack_pathadd; unalias spack; unalias spacktivate; " ..
        "unset _spack_share_dir; unset _spack_source_file; unsetenv SPACK_PYTHON;" ..
        "unset _sp_tcl_roots; unset _sp_sys_type; unset _sp_lmod_roots; unset _sp_compatible_sys_types;"
  execute{cmd=cmd, modeA={"unload"}}
end
if (myShellType() == "sh") then
-- bash sets shell functions and aliases
  cmd = "unalias spacktivate; " ..
        "unset -f __spack_shell_wrapper; unset -f spack; " ..
        "unset -f _all_packages; unset -f _all_resource_hashes;" ..
        "unset -f _config_sections; unset -f _environments;" ..
        "unset -f _extensions; unset -f _installed_compilers;" ..
        "unset -f _installed_packages; unset -f _keys;" ..
        "unset -f _mirrors; unset -f _pretty_print;" ..
        "unset -f _providers; unset -f _repos;" ..
        "unset -f _sp_multi_pathadd; unset -f _subcommands;" ..
        "unset -f _test_vars; unset -f _tests;" ..
        "unset -f _bash_completion_spack;" ..
        "unset -f _spack;" ..
        "unset -f _spack_activate;" ..
        "unset -f _spack_add;" ..
        "unset -f _spack_analyze;" ..
        "unset -f _spack_analyze_list_analyzers;" ..
        "unset -f _spack_analyze_run;" ..
        "unset -f _spack_arch;" ..
        "unset -f _spack_audit;" ..
        "unset -f _spack_audit_configs;" ..
        "unset -f _spack_audit_list;" ..
        "unset -f _spack_audit_packages;" ..
        "unset -f _spack_audit_packages_https;" ..
        "unset -f _spack_blame;" ..
        "unset -f _spack_bootstrap;" ..
        "unset -f _spack_bootstrap_disable;" ..
        "unset -f _spack_bootstrap_enable;" ..
        "unset -f _spack_bootstrap_list;" ..
        "unset -f _spack_bootstrap_reset;" ..
        "unset -f _spack_bootstrap_root;" ..
        "unset -f _spack_bootstrap_trust;" ..
        "unset -f _spack_bootstrap_untrust;" ..
        "unset -f _spack_build_env;" ..
        "unset -f _spack_buildcache;" ..
        "unset -f _spack_buildcache_check;" ..
        "unset -f _spack_buildcache_copy;" ..
        "unset -f _spack_buildcache_create;" ..
        "unset -f _spack_buildcache_download;" ..
        "unset -f _spack_buildcache_get_buildcache_name;" ..
        "unset -f _spack_buildcache_install;" ..
        "unset -f _spack_buildcache_keys;" ..
        "unset -f _spack_buildcache_list;" ..
        "unset -f _spack_buildcache_preview;" ..
        "unset -f _spack_buildcache_save_specfile;" ..
        "unset -f _spack_buildcache_sync;" ..
        "unset -f _spack_buildcache_update_index;" ..
        "unset -f _spack_cd;" ..
        "unset -f _spack_checksum;" ..
        "unset -f _spack_ci;" ..
        "unset -f _spack_ci_generate;" ..
        "unset -f _spack_ci_rebuild;" ..
        "unset -f _spack_ci_rebuild_index;" ..
        "unset -f _spack_ci_reproduce_build;" ..
        "unset -f _spack_clean;" ..
        "unset -f _spack_clone;" ..
        "unset -f _spack_commands;" ..
        "unset -f _spack_compiler;" ..
        "unset -f _spack_compiler_add;" ..
        "unset -f _spack_compiler_find;" ..
        "unset -f _spack_compiler_info;" ..
        "unset -f _spack_compiler_list;" ..
        "unset -f _spack_compiler_remove;" ..
        "unset -f _spack_compiler_rm;" ..
        "unset -f _spack_compilers;" ..
        "unset -f _spack_completions;" ..
        "unset -f _spack_concretize;" ..
        "unset -f _spack_config;" ..
        "unset -f _spack_config_add;" ..
        "unset -f _spack_config_blame;" ..
        "unset -f _spack_config_edit;" ..
        "unset -f _spack_config_get;" ..
        "unset -f _spack_config_list;" ..
        "unset -f _spack_config_prefer_upstream;" ..
        "unset -f _spack_config_remove;" ..
        "unset -f _spack_config_revert;" ..
        "unset -f _spack_config_rm;" ..
        "unset -f _spack_config_update;" ..
        "unset -f _spack_containerize;" ..
        "unset -f _spack_create;" ..
        "unset -f _spack_deactivate;" ..
        "unset -f _spack_debug;" ..
        "unset -f _spack_debug_create_db_tarball;" ..
        "unset -f _spack_debug_report;" ..
        "unset -f _spack_dependencies;" ..
        "unset -f _spack_dependents;" ..
        "unset -f _spack_deprecate;" ..
        "unset -f _spack_determine_shell;" ..
        "unset -f _spack_dev_build;" ..
        "unset -f _spack_develop;" ..
        "unset -f _spack_diff;" ..
        "unset -f _spack_docs;"
  cmd1= "unset -f _spack_edit;" ..
        "unset -f _spack_env;" ..
        "unset -f _spack_env_activate;" ..
        "unset -f _spack_env_create;" ..
        "unset -f _spack_env_deactivate;" ..
        "unset -f _spack_env_list;" ..
        "unset -f _spack_env_loads;" ..
        "unset -f _spack_env_ls;" ..
        "unset -f _spack_env_remove;" ..
        "unset -f _spack_env_revert;" ..
        "unset -f _spack_env_rm;" ..
        "unset -f _spack_env_st;" ..
        "unset -f _spack_env_status;" ..
        "unset -f _spack_env_update;" ..
        "unset -f _spack_env_view;" ..
        "unset -f _spack_extensions;" ..
        "unset -f _spack_external;" ..
        "unset -f _spack_external_find;" ..
        "unset -f _spack_external_list;" ..
        "unset -f _spack_fetch;" ..
        "unset -f _spack_find;" ..
        "unset -f _spack_flake8;" ..
        "unset -f _spack_fn_exists;" ..
        "unset -f _spack_gc;" ..
        "unset -f _spack_gpg;" ..
        "unset -f _spack_gpg_create;" ..
        "unset -f _spack_gpg_export;" ..
        "unset -f _spack_gpg_init;" ..
        "unset -f _spack_gpg_list;" ..
        "unset -f _spack_gpg_publish;" ..
        "unset -f _spack_gpg_sign;" ..
        "unset -f _spack_gpg_trust;" ..
        "unset -f _spack_gpg_untrust;" ..
        "unset -f _spack_gpg_verify;" ..
        "unset -f _spack_graph;" ..
        "unset -f _spack_help;" ..
        "unset -f _spack_info;" ..
        "unset -f _spack_install;" ..
        "unset -f _spack_license;" ..
        "unset -f _spack_license_list_files;" ..
        "unset -f _spack_license_update_copyright_year;" ..
        "unset -f _spack_license_verify;" ..
        "unset -f _spack_list;" ..
        "unset -f _spack_load;" ..
        "unset -f _spack_location;" ..
        "unset -f _spack_log_parse;" ..
        "unset -f _spack_maintainers;" ..
        "unset -f _spack_mark;" ..
        "unset -f _spack_mirror;" ..
        "unset -f _spack_mirror_add;" ..
        "unset -f _spack_mirror_create;" ..
        "unset -f _spack_mirror_destroy;" ..
        "unset -f _spack_mirror_list;" ..
        "unset -f _spack_mirror_remove;" ..
        "unset -f _spack_mirror_rm;" ..
        "unset -f _spack_mirror_set_url;" ..
        "unset -f _spack_module;" ..
        "unset -f _spack_module_lmod;" ..
        "unset -f _spack_module_lmod_find;" ..
        "unset -f _spack_module_lmod_loads;" ..
        "unset -f _spack_module_lmod_refresh;" ..
        "unset -f _spack_module_lmod_rm;" ..
        "unset -f _spack_module_lmod_setdefault;" ..
        "unset -f _spack_module_tcl;" ..
        "unset -f _spack_module_tcl_find;" ..
        "unset -f _spack_module_tcl_loads;" ..
        "unset -f _spack_module_tcl_refresh;" ..
        "unset -f _spack_module_tcl_rm;" ..
        "unset -f _spack_monitor;" ..
        "unset -f _spack_patch;" ..
        "unset -f _spack_pathadd;" ..
        "unset -f _spack_pkg;" ..
        "unset -f _spack_pkg_add;" ..
        "unset -f _spack_pkg_added;" ..
        "unset -f _spack_pkg_changed;" ..
        "unset -f _spack_pkg_diff;" ..
        "unset -f _spack_pkg_list;" ..
        "unset -f _spack_pkg_removed;" ..
        "unset -f _spack_providers;" ..
        "unset -f _spack_pydoc;" ..
        "unset -f _spack_python;" ..
        "unset -f _spack_reindex;" ..
        "unset -f _spack_remove;" ..
        "unset -f _spack_repo;" ..
        "unset -f _spack_repo_add;" ..
        "unset -f _spack_repo_create;" ..
        "unset -f _spack_repo_list;" ..
        "unset -f _spack_repo_remove;" ..
        "unset -f _spack_repo_rm;" ..
        "unset -f _spack_resource;" ..
        "unset -f _spack_resource_list;" ..
        "unset -f _spack_resource_show;" ..
        "unset -f _spack_restage;" ..
        "unset -f _spack_rm;" ..
        "unset -f _spack_shell_wrapper;" ..
        "unset -f _spack_solve;" ..
        "unset -f _spack_spec;" ..
        "unset -f _spack_stage;" ..
        "unset -f _spack_style;" ..
        "unset -f _spack_tags;" ..
        "unset -f _spack_test;" ..
        "unset -f _spack_test_env;" ..
        "unset -f _spack_test_find;" ..
        "unset -f _spack_test_list;" ..
        "unset -f _spack_test_remove;" ..
        "unset -f _spack_test_results;" ..
        "unset -f _spack_test_run;" ..
        "unset -f _spack_test_status;" ..
        "unset -f _spack_tutorial;" ..
        "unset -f _spack_undevelop;" ..
        "unset -f _spack_uninstall;" ..
        "unset -f _spack_unit_test;" ..
        "unset -f _spack_unload;" ..
        "unset -f _spack_url;" ..
        "unset -f _spack_url_list;" ..
        "unset -f _spack_url_parse;" ..
        "unset -f _spack_url_stats;" ..
        "unset -f _spack_url_summary;" ..
        "unset -f _spack_verify;" ..
        "unset -f _spack_versions;" ..
        "unset -f _spack_view;" ..
        "unset -f _spack_view_add;" ..
        "unset -f _spack_view_check;" ..
        "unset -f _spack_view_copy;" ..
        "unset -f _spack_view_hard;" ..
        "unset -f _spack_view_hardlink;" ..
        "unset -f _spack_view_relocate;" ..
        "unset -f _spack_view_remove;" ..
        "unset -f _spack_view_rm;" ..
        "unset -f _spack_view_soft;" ..
        "unset -f _spack_view_statlink;" ..
        "unset -f _spack_view_status;" ..
        "unset -f _spack_view_symlink;" ..
        "unset -f _spack_bootstrap_add;" ..
        "unset -f _spack_bootstrap_mirror;" ..
        "unset -f _spack_bootstrap_now;" ..
        "unset -f _spack_bootstrap_remove;" ..
        "unset -f _spack_bootstrap_status;" ..
        "unset -f _spack_change;" ..
        "unset -f _spack_env_depfile;" ..
        "unset -f _spack_external_read_cray_manifest;" ..
        "unset -f _spack_make_installer;" ..
        "unset -f _spack_module_tcl_setdefault;" ..
        "unset -f _spack_pkg_hash;" ..
        "unset -f _spack_pkg_source;" ..
        "unset -f SPACK_TESTS;" ..
        "unset SPACK_PYTHON;" ..
        "unset -f _spacktivate;"
        
  -- split into 2 strings as Lua complains when string is too long
  execute{cmd=cmd, modeA={"unload"}}
  execute{cmd=cmd1, modeA={"unload"}}
end
