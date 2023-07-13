# Updating your HPC's Flywheel engine binary file
Version: 1.0.0

## Purpose
When a Flywheel site is updated, sometimes Flywheel engines will also be updated, but 
it does not happen for every *site* release.  If you have integrated your Flywheel site 
with your HPC, it is recommended to update the Flywheel engine binary file when a new 
engine is released. Please contact Flywheel staff to get an updated Flywheel engine.

## Instructions
1. Ensure you are logged in to your HPC login/head node as the user that is set up to
  launch Flywheel jobs through the HPC Client.
   

2. `cd` into the engine binary directory `cd ~/fw-cast/logs/temp`. Note: if you named your HPC Client repo 
   something else, then use that instead of `fw-cast`.
   

3. Copy the latest engine binary file into this directory. If you're using secure copy in
   your terminal, you can open a new terminal window to access your files locally and use 
   the following to copy the file from your local computer to the HPC node:
   ```
   scp <path_to_updated_engine_binary_file≥ <username>@<hostname>:<path_to_engine_folder>
   ```
   Example:
   ```
   scp "/Users/jesusavila/Downloads/engine.16.18.0-plat-764-signe-urls-streaming-uploads-rc.0" jiavila@scien-hpc:/home/jiavila/fw-cast/logs/temp/
   ```
   

4. To verify it copied correctly, use `ls -lah` in the login/head node terminal. You
   should see something like the following:
    ```
    total 54M
    drwxrwxr-x 2 jiavila      jiavila 4.0K Jul  5 23:58 .
    drwxrwxr-x 5 jiavila      jiavila 4.0K Jul  5 22:09 ..
    lrwxrwxrwx 1 root         root      27 Oct 14  2022 engine -> engine--2022-10-11--16.12.2
    -rwxr-xr-x 1 pablovelasco root     16M Oct 11  2022 engine--2022-10-11--16.12.2
    -rw-r--r-- 1 jiavila      jiavila  18M Jul  6 00:01 engine.16.18.0-plat-764-signe-urls-streaming-uploads-rc.0
    lrwxrwxrwx 1 jiavila      jiavila    9 Nov 22  2021 log.json -> /dev/null
    ```
   
5. Ensure the new engine binary file is executable:

   ```
   chmod +x <updated_engine_binary_file>
   ```
   Example:
   ```
   chmod +x engine.16.18.0-plat-764-signe-urls-streaming-uploads-rc.0
   ```

6. Update the symbolic link to the updated engine binary file:
   ```
   ln -sf <updated_engine_binary_file>
   ```
   Example:
   ```
   ln -sf engine.16.18.0-plat-764-signe-urls-streaming-uploads-rc.0 engine
   ```
   
7. Verify that the updated engine binary file is being linked and that the file is 
    executable with `ls -lah`. You should see something like the following:
   ```
    total 54M
    drwxrwxr-x 2 jiavila      jiavila 4.0K Jul  6 00:14 .
    drwxrwxr-x 5 jiavila      jiavila 4.0K Jul  5 22:09 ..
    lrwxrwxrwx 1 jiavila      jiavila   57 Jul  6 00:14 engine -> engine.16.18.0-plat-764-signe-urls-streaming-uploads-rc.0
    -rwxr-xr-x 1 pablovelasco root     16M Oct 11  2022 engine--2022-10-11--16.12.2
    -rwxr-xr-x 1 jiavila      jiavila  18M Jul  6 00:01 engine.16.18.0-plat-764-signe-urls-streaming-uploads-rc.0
    lrwxrwxrwx 1 jiavila      jiavila    9 Nov 22  2021 log.json -> /dev/null
   ```