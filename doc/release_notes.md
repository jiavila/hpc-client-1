# Release Notes

## 2.0.0
__Fix__:

- Fixes cluster/scheduler accessing slurm ram and cpu incorrectly from the Flywheel job 
  config ([issue 11](https://github.com/flywheel-io/hpc-client/issues/11)). It now uses 
  `scheduler_ram` and `scheduler_cpu` parameters from the gear config.
  
- Fixes default `cast.yml` variable `script`; it was not setting the correct job number.

- Change source code folder name from `code` to `src` to prevent collision with default
  Python `code` module.

__Enhancement__:

- Set ram and cpu settings in Flywheel gear job using `scheduler_ram` and `scheduler_cpu` variables.
  If no setting was found for that specific job, check `settings/cast.yml`. If none, then
  use default settings.

- Add FAQ section to readme.md

- Add docs for updating Flywheel engine.

- Add docs for updating HPC Client.

- Add docs for contributing.

- Add dev testing along with pre-commit and flak8.