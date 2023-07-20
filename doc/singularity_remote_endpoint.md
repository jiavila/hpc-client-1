# Flywheel HPC Singularity API key configuration
Version 1.0.2

## Purpose
Singularity/Apptainer needs to establish a remote endpoint with your Flywheel instance's
Docker repository so that it can pull container images to your HPC system.

## Instructions
### Create a remote endpoint to your site's Docker registry
Use the command below to login and set up a token for your site's Docker registry. It 
will prompt you for a password; enter the associated Flywheel API Key ([create one](https://docs.flywheel.io/hc/en-us/articles/16302604562963) 
if you haven't already).

Note: This user will be the only one that pulls Docker images from your Flywheel site through
Singularity/Apptainer. It is recommended that a new Flywheel admin user be created that 
is not tied to an individual at your institution/company.
```
singularity remote login --username <flywheel_user_email> docker://<your_flywheel_site_url>
```

Example:
```
singularity remote login --username support@flywheel.io docker://ga.ce.flywheel.io
```

You should see something like the following if the login was succesful:
```
INFO:    Token stored in /home/<user>/.singularity/remote.yaml
```

You should also be able to see the new remote endpoint with `singularity remote list`,
under the "Authenticated Logins" section.

### Secure the docker json file (Recommended)
As is mentioned in [Singularity/Apptainer documentation](https://apptainer.org/user-docs/master/endpoint.html#managing-oci-registries),
the token is stored in the home directory of the user you selected to set up the remote
endpoint. It is typically stored in `~/.singularity/docker-config.json` 
(or `~/.apptainer/docker-config.json`). It is recommended that the permissions for this 
file be changed so that only certain users can access it. Here are several 
options and considerations for each.

#### Only one user has read & write access
After the HPC Client submits the HPC job through the scheduler (e.g., Slurm), the 
Flywheel engine will use credentials from the `~/fw-cast/settings/credentials.sh` file 
to get the *Flywheel* job from your Flywheel site. It wil run it locally on your HPC. 
Singularity/Apptainer still needs, however, a user to pull the Docker image from your 
Flywheel site.

By default, the user that submits the job to your HPC scheduler is the one that 
periodically runs the `~/fw-cast/settings/start-cast.sh` file (with the integration 
method you chose). This user must have access to the `docker-config.json` file. If it is
the same user, then you can just do the following:

`chmod 0600 ~/.singularity/docker-config.json`

#### Several users have access (Future feature, not implemented yet)
In future HPC Client releases, there will be an option for different users to submit the
scheduler job. With this configuration, HPC resources can be tracked for the user or 
group that creates the Flywheel job (and subsequent scheduler job). If configuring this,
then all users that submit the scheduler job to the HPC must be able to read the 
`docker-config.json` file. To give read/write access to the file owner and read 
permission to a group of users, you can use the following:
```
chmod 0640 ~/.singularity/docker-config.json
```