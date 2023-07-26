# Upgrading the HPC Client

## Purpose
The HPC Client will receive upgrades with enhancements and fixes. This document describes
the process for upgrading the source code for your HPC Client. Please read [Additional 
Notes for Upgrading to Specific Versions](#additional-notes-for-upgrading-to-specific-versions) 
__before__ upgrading to that version.

## Instructions
Since your local copy of the HPC Client contains credentials, it was not possible to 
simply "fork" the HPC Client repository. This process will upgrade the source code (
in the `src` directory, formerly `code`) of your HPC Client repo. This will also update
all other directories except `settings`. It is highly recommended that you track your 
`settings` directory by ensuring that it is *__not__* in your `.gitignore` file.  Additionally,
it is recommended, if possible, that you do not change any directories except `settings`,
or you will have to manually resolve any conflicts.

1. To ensure a smooth upgrade, reserve a few hours to upgrade your HPC Client. Stop any
   jobs from being submitted by the HPC Client, and verify that all previous jobs submitted
   by the HPC Client have been completed. 
2. Pause the integration method so it stops running `settings/start-cast.sh`. For 
   example, if Cron was used, use the command `crontab -e`, comment out the 
   `start-cast.sh` line, and save the changes to the file.
3. `cd` into your `fw-cast` repo. Ensure you are in your main/master branch 
   (e.g., `git checkout master`). Check the status with `git status`.   Commit and push
   any local changes to your __private__, remote repository.
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
   it is recommended that you learn keyboard shortcuts for selecting multiple lines and 
   deleting them (e.g., if using Nano as the text editor, use 
   <kbd>ctrl</kbd> + <kbd>shift</kbd> + <kbd>6</kbd> and <kbd>ctrl</kbd> + <kbd>k</kbd>).
8. Restart the integration method you paused (from step 1.). Monitor casting logs from 
   the HPC Client with the following: 
   ```
   tail -f fw-cast/logs/cast.log
   ```
   If HPC Client successfully runs, yous hould get something like the following:
   ```
   07-25 21:35:02 DBUG Looking for jobs to cast...
   07-25 21:35:02 DBUG Found 0 jobs in 151 ms.
   07-25 21:35:02 INFO No jobs to handle. Runtime: 413 ms.
   ```
9. Test a gear, like mriqc, on your HPC and ensure the HPC Client creates and submits 
   the job. If the gear completes on your HPC without any issues,
   then the update was successful. Regardless, commit and push your local changes to 
   your remote branch.
   Example:
   ```
   git add .
   git commit -m "merge 2.0.0 updates"
   git push --set-upstream origin ver_2.0.0
   ```
   
10. If you encounter any issues, please contact Flywheel staff by either submitting a 
    ticket or emailing suppport@flywheel.io  If not, then create a pull request/merge 
    request to your main/master branch, review it, merge it, checkout your local 
    repository to main/master, then pull these changes. The update is now complete.
   
    
## Additional notes for upgrading to specific versions
### 2.0.0
- The `code` folder was renamed to `src` to prevent conflicts with the inherent `code` 
  module in Python. The following are changes that must get fixed to handle this 
  renaming. Both of these should be done after pulling from the HPC Client upstream 
  repo (step 6.).
   - Use `git rm code/cluster/common.py` to resolve conflicts with this file. If this 
     file does not appear in the uncommitted portion when you type `git status`, then 
     you can skip this part.
  - Since the `settings` folder does not get updated, we have to change the source folder 
    from `code` to `src` in `settings/start-cast.sh` You need only change the `cd` line. 
    It should look like the following after edits:
    ```
    # This time limit may need to be adjusted based on the speed of your system.
    cd src
    ```