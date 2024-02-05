# Flywheel HPC Client <!-- omit in toc -->

The HPC Client is a self-service solution that allows Flywheel jobs and gears to run on a High Performance Computing environment. Use on-premise hardware that's already available for highly-concurrent scientific workloads!

### Table of Contents
- [Architecture](#architecture)
- [HPC Types](#hpc-types)
- [Minimum Requirements](#minimum-requirements)
- [Getting Started](#getting-started)
- [FAQs](#faqs)

[![Build Status](https://github.com/flywheel-io/hpc-client/actions/workflows/build.yml/badge.svg)](https://github.com/flywheel-io/hpc-client/actions)

## Architecture

![hpc-client-architecture 20210726](https://user-images.githubusercontent.com/75435671/127048966-af0582f7-10dc-451c-b955-4d5ab50eaf08.png)

## HPC Types

The client, also called Cast, can support several queue mechanisms out of the box. Flywheel, however, currently only
provides support for Slurm. If you require assistance with other schedulers, contact Flywheel.

| Common name              | Code name |
| ------------------------ | --------- |
| IBM spectrum LSF         | `lsf`     |
| Oracle / Sun Grid Engine | `sge`     |
| Slurm                    | `slurm`   |

If your site uses one of these, it may well just need a config file to get running.<br/>
Otherwise, some light python development will be required.

## Minimum Requirements
Reference [this article](https://docs.flywheel.io/hc/en-us/articles/7563372636563) for 
the minimum software and computing requirements of the system where the HPC Client 
will be installed.

## Getting Started

1. Before using Cast, you need to decide how it will run on your cluster.<br/>
[Choose an integration method](doc/1-choose-an-integration-method.md) and keep it in mind for later.
   This sets how frequently Cast with look for, pull, and queue hpc jobs to your HPC from your Flywheel site.

2. It is strongly recommended that you [make a private GitHub repo](doc/2-tracking-changes-privately.md) to track your changes.<br/>
This will make Cast much easier to manage.

3. Perform the [initial cluster setup](doc/3-cluster-install.md). If you are unfamiliar with <br/>
singularity, it is recommended that you read--at a minimum--SingularityCE's [introduction](https://sylabs.io/guides/latest/user-guide/introduction.html) <br/>
   and [quick start](https://sylabs.io/guides/latest/user-guide/quick_start.html) guides.
   
4. [Create an authorization token](doc/singularity_remote_endpoint.md) 
   so Singularity and Flywheel can work with each other.

5. If your queue type is not in the above table, or is sufficiently different, review the guide for [adding a queue type](doc/4-development-guide.md).

6. Collaborate with Flywheel staff to [install the Flywheel engine in your HPC repo](doc/installing_flywheel_engine.md).
   They will also configure the hold engine on your Flywheel site
   to ensure that other engines do not pick up gear jobs that are tagged with "hpc".

7. Complete the integration method you chose in step one.<br/>
   Confirm Cast is running regularly by monitoring `logs/cast.log` and the Flywheel user interface.
   
8. Test and run your first HPC job tests in collaboration with Flywheel. It is recommended
   that you test with MRIQC (non-BIDS version), a gear that's available from Flywheel's [Gear Exchange](https://flywheel.io/gear-exchange/).
   Note: as of 11 May 2022, Flywheel will have to change the rootfs-url (location of where the Docker image resides) for
   any gears installed from the Gear Exchange. For more about how Cast uses a rootfs-url, see Background/Motivation
   of [this article](https://docs.flywheel.io/hc/en-us/articles/4607520806547).

8. Enjoy!

## FAQs
- #### [How do I update the HPC Client to the latest release?](doc/faq_updating_hpc_client.md)
- #### [How do I update my Flywheel engine?](doc/faq_updating_flywheel_engine.md)
- #### [How do I use GPUs on my Slurm Cluster?](doc/faq_use_gpu_on_slurm_cluster.md)
<details>
   <summary><b>How do I set ram and cpu settings for my job?</b></summary>
   Starting in version 2.0.0, the HPC Client will perform the following checks for setting
   ram and cpu settings:
  
   1. Was `scheduler_ram` or `scheduler_cpu` set in the gear config when the Flywheel
      job was launched? If so, use this. The gear must have these as config
      variables to set them. See table below for formatting.
   2. If no setting was found for that specific job, check the `settings/cast.yml` file
      for these variables. Setting this will apply to HPC jobs submitted by the HPC 
      Client. Only step 1. overrides this.
   3. If the setting is still not found, then use the default one set for that specific
      scheduler type (e.g., Slurm). This is hardcoded and should not be changed.
   
      ### Formatting guide for variables 'scheduler_ram' and 'scheduler_cpu'
      | scheduler/cluster | RAM                | CPU                      |
      | ----------------- | ------------------ | ------------------------ |
      | Slurm             | '8G'               | '8'                      |
      | LSF               | 'rusage[mem=4000]' | '1'                      |
      | SGE               | '8G'               | '4-8'   (sets CPU range) |
   
</details>
<details>
    <summary><b>How do I use a custom script template for the jobs submitted to my HPC?</b></summary>
    
The HPC Client creates a shell script (`.sh`) for every job that is submitted to your HPC
through your scheduler (e.g., Slurm). It creates this using a default script template
for the type of scheduler on your HPC. If you would like to use a custom one, you can
do so by using the `script` variable in the `settings/cast.yml` file. It is not recommended
to edit the default templates in the source code (e.g., `src/cluster/slurmpy`)
</details>
<details>
    <summary><b>How do I send my jobs to a specific partition on my HPC?</b></summary>

When you use a custom script template, you can set the partition(s) to which all
your jobs will be sent. For example, if your scheduler is Slurm, you can add the 
following line in your custom script template:

```
    #SBATCH --partition=<partition1_name>,<partition2_name>
```
Example:
```
    #SBATCH --partition=gpu-1,gpu-2
```
    
</details>
<details>
    <summary><b>How do I check my version of the HPC Client?</b></summary>

The version of the HPC Client is in `src/__init__.py` under the variable
`__version__`. This was not available prior to 2.0.0. 
</details>
