# Using GPUs for Gear Execution on a Slurm Cluster <!-- omit from toc -->

- [Configuration](#configuration)
  - [Slurm Configuration](#slurm-configuration)
    - [slurm.conf](#slurmconf)
    - [gres.conf](#gresconf)
  - [Updating the fw-cast settings](#updating-the-fw-cast-settings)
- [Gear Execution](#gear-execution)
  - [Potential Problems](#potential-problems)

## Configuration

Both Slurm and fw-cast must be configured appropriately to enable GPU execution of gears
on a Slurm Cluster.

### Slurm Configuration

To execute gears on GPU nodes of a Slurm cluster, Slurm must be configured
correctly. Your system administrator will most likely configure these settings. Below
are examples of how a working configuration was set. If you don't see something like
these settings on the nodes of the Slurm Cluster, it is likely that it is not set up
for GPU execution.

Detailed instructions for configuring Slurm can be found at [https://slurm.schedmd.com/](https://slurm.schedmd.com/).
Including a [Slurm Configuration Tool](https://slurm.schedmd.com/configurator.html).

#### slurm.conf

The [`slurm.conf`](https://slurm.schedmd.com/slurm.conf.html) file is typically found in
`/etc/slurm/`. Below is an example for a node definition that enables GPUs to be
scheduled.

```conf
NodeName=scien-hpc-gpu Gres=gpu:tesla:1 CPUs=4 Boards=1 SocketsPerBoard=1 CoresPerSocket=2 ThreadsPerCore=2 RealMemory=14978
```

The Generic RESource (GRES) flag (`Gres=gpu:tesla:1`) must be present to indicate the
resource type (e.g. "gpu"), the resource class (e.g. "tesla"), and the number of resources present
("1"). Execution on more than one GPU per node has not yet been explored.

If desired, the remainder of the node configuration (e.g. CPUs, RealMemory) can be interrogated by
the following command:

```bash
slurmd -C
```

#### gres.conf

The [Generic RESource (GRES)](https://slurm.schedmd.com/gres.conf.html) configuration,
`gres.conf`, needs to have an entry for each resource named in `slurm.conf`.

```conf
NodeName=scien-hpc-gpu Name=gpu Type=tesla File=/dev/nvidia0
```

Here `File=/dev/nvidia0` is a reference to the device that the GPU is mounted on.

### Updating the fw-cast settings

It is recommended that you replace the `script` section of your `settings/cast.yml` file
with the `script` section of the `examples/settings/gpu_cast.yml` file. This is also
shown below.

```yaml
  script: |+
   #!/bin/bash
   #SBATCH --job-name=fw-{{job.fw_id}}
   #SBATCH --ntasks=1
   #SBATCH --cpus-per-task={{job.cpu}}
   #SBATCH --mem-per-cpu={{job.ram}}
   {% if job.gpu %}#SBATCH --gpus-per-node={{job.gpu}}{% endif %}
   #SBATCH --output {{script_log_path}}
  
   set -euo pipefail
  
   source "{{cast_path}}/settings/credentials.sh"
   cd "{{engine_run_path}}"
  
   set -x
   srun ./engine run --single-job {{job.fw_id}}
```

## Gear Execution

With the rest of the workflow configured, adding a `gpu` tag (in addition to the
`hpc` tag) to the launch of the gear will schedule a GPU to execute the gear on the
Slurm cluster.

### Potential Problems

- Without the `gpu` tag present on gear launch any node meeting the criteria will be
  scheduled.
- If the `cast.yml` does not have the line with `--gpus-per-node` only CPU nodes will
  be scheduled.
- If GPU nodes are not available on the cluster, the job will be put in a waiting state
  until one is.
