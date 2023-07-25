#Upgrading the HPC Client

##Purpose
The HPC Client will receive upgrades with enhancements and fixes. This document describes
the process for upgrading the source code for your HPC Client. For additional 
instructions when upgrading to a specific version, see [this section below](#Additional-notes-for-upgrading-to-specific-versions).

##Instructions
Since your local copy of the HPC Client contains credentials, it was not possible to 
simply "fork" the HPC Client repository. This process will upgrade the source code (
in the `src` directory, formerly `code`) of your HPC Client repo. This will also update
all other directories except `settings`. It is highly recommended that you track your 
`settings` directory by ensuring that it is *__not__* in your `.gitignore` file.  Additionally,
it is recommended that you do not change the `src` directory, or you will have to 
manually resolve any conflicts.

1. To ensure a smooth upgrade, reserve a few hours to upgrade your HPC Client. Stop any
   jobs from being submitted by the HPC Client, and verify that all previous jobs submitted
   by the HPC Client have been completed. 
2. Pause the integration method so it stops running `settings/start-cast.sh`. For 
   example, if Cron was used, use the command `crontab -e`, comment out the 
   `start-cast.sh` line, and save the changes to the file.
3. Ensure you are in your main/master branch (e.g., `git checkout master`) and that 
   you have committed and pushed any local changes to your __private__, remote repository.
4. Set the HPC Client repository as an upstream repository and disable pushing to it by 
   adding an invalid URL
   ```
   git remote add upstream https://github.com/flywheel-io/hpc-client.git
   git config remote.upstream.pushurl "NEVER GONNA PUSH YOU UP"
   ```
5. Create and checkout a new branch from your main/master branch; for tracking, include 
   the version number in the name.
   ```
   git checkout -b ver_<HPC-Client-version>
   ```
   Example:
   ```
   git checkout -b ver_2.0.0
   ```
6. Pull the HPC Client upstream repository you created to your new branch.
   ```
   git pull upstream
   ```
7. If you get any conflicts (i.e., got the error message `Automatic merge failed; fix 
   conflicts and then commit the result.`), you will have to manually resolve these. 
   [Follow these instructions](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-using-the-command-line) 
   to do this through the command line. This should not be an issue if you did not make
   changes to the `src` code document. Note: to quickly make edits in the command line,
   it is recommended that you learn keyboard shortcuts for selecting mutliple lines and 
   deleting them (e.g., if using Nano as the text editor, use 
   <kbd>ctrl</kbd> + <kbd>shift</kbd> + <kbd>6</kbd> and <kbd>ctrl</kbd> + <kbd>k</kbd>).
8. Restart the integration method you paused (from step 1.).
9. Test a gear, like mriqc, on your HPC and ensure the HPC Client creates and submits 
   the job. You can monitor casting logs from the HPC Client with 
   `tail -f fw-cast/logs/cast.log`. If the gear completes on your HPC without any issues,
   then the update was successful. If you encounter any issues, please contact Flywheel
   staff by either submitting a ticket or emailing suppport@flywheel.io
10. Push the local changes of your branch to remote branch.
   




##Additional notes for upgrading to specific versions
### 2.0.0
1. The `code` folder was renamed to `src` because it can cause issues with Python to 
   prevent conflicts with the inherent `code` module in Python. After pulling from the 
   HPC Client upstream repo, you may have to use `git rm code/cluster/common.py` to 
   resolve changes. Only this file should be troublesome.
2. 