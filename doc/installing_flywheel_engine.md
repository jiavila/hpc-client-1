# HPC Client: Flywheel Engine Installation
Version: 1.0.1

## Purpose
The HPC Client is a self-service solution that allows Flywheel jobs and gears to run in a
High Performance Computing environment. It uses on-premise hardware that's already available
for highly-concurrent scientific workloads. When the HPC Client creates an HPC job through
your scheduler (e.g., Slurm), it needs a Flywheel engine to run Flywheel jobs. In addition,
the engine needs access to your Flywheel site to pull/push Flywheel jobs. You will need 
your site's drone secret for this. Please contact Flywheel staff 
(e.g., support@flywheel.io) so that they can provide you the latest Flywheel engine 
binary file and your site's drone secret.

## Instructions
### Drone secret
Once this key is provided to you by Flywheel staff in a secure way, copy and paste this 
into the environment variable `SCITRAN_CORE_DRONE_SECRET` in the 
`~/fw-cast/settings/credentials.sh` file. That variable should already exist in that file; 
only your key is missing. It should look like the following:
```
export SCITRAN_CORE_DRONE_SECRET="<your-credentials>"
```

### Flywheel engine binary file
1. After receiving the engine binary file from the Flywheel Team 
   (e.g., engine--2021-05-20--15.5.1) and setting up your HPC Client repo, place the 
   binary file in the following directory:
    ```
    ~/fw-cast/logs/temp.
    ```
2. Create a symlink to the engine binary file so they can be updated in the future without 
   disturbing jobs in flight. Make sure your working directory is the temp directory 
   where the engine file was just stored.
   ```
   ln -s <engine_binaries_name> engine
   ```
   You can check if the link was created with ls -lah, which will show something like the 
   following:
   ```
   engine -> engine--2021-05-20--15.5.1
   ```
3. Ensure the engine binary is executable with the command
   ```
   chmod +x <engine_binaries_name>
   ```
