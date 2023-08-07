# Contributing

## Setting up dev environment
After creating a fork of the HPC Client repo and cloning it locally, perform the steps 
below in the command line. 

1. Install a python 3 environment (e.g., with `miniconda`). Python 3.8 is recommended.
2. Install pipenv in the source Python environment with 
   ```
   python -m pip install pipenv
   ```
3. Change the directory with 
   ```
   cd src
   ```
4. Install the pipenv developer virtual environment with
   ```
   python -m pipenv install -d
   ```
5. Activate the virtual environment with
   ```
   pipenv shell
   ```
   You check the path to the python execute file with 
   ```
   which python
   ```
   . It should print something like the following: `/Users/<user>/.local/share/virtualenvs/src_code-LEKyUmPy/bin/python
    `
6. Check that pytest was successfully installed by running pytest with and install pre-commit
   ```
   cd ..
   pytest
   pre-commit install
   ```
   
### Pycharm
If using Pycharm as your IDE, follow these additional instructions to reference the 
python environment you just created.

1. Update interpreter.
    1. Copy path to python executable you printed with `which python`.
    1. Go to `Settings -> Project -> Python Interpreter -> Settings Gear Icon -> Add... -> Virtualenv Environment -> Existing Environment -> ...` 
    3. Paste the python executable path in the folders textbox.
    2. Click `OK -> OK` to apply settings.
2. Set source root so that module references work correctly.
	1. Go to `Settings -> Project -> Project Structure`
	2. Click `src` folder. Near the top, mark as `Sources` folder. Click OK.

## Dependency management

This gear uses [`pipenv`](https://pipenv.pypa.io/en/latest/) to manage dependencies and
develop.

### Dependencies

Dependencies are listed in the `src/Pipfile`.

#### Managing dependencies
After activating the shel environment, you can use the commands below to manage packages.
To use these commands, the working directory should be `src` (i.e., `cd src`).

* Adding: Use `pipenv install <package_name> [-d]` (optional: `-d` is for dev)
* Removing: Use `pipenv uninstall <package_name> [-d]`
* Updating: Use `pipenv update <package_name>` or `pipenv update` to update all deps.
  * Update dry run: `--dry-run`

## Linting and Testing

Local linting and testing scripts are managed through
[`pre-commit`](https://pre-commit.com/). Pre-commit allows running hooks which
can be defined locally, or in other repositories. Default hooks to run on each
commit:

* flake8: Style guide enforcement
* pytest: Runs pytest and requires coverage

These hooks will all run automatically on commit, but can also be run manually
or just be disabled.

### pre-commit usage

* Run hooks manually:
  * Run on all files: `pre-commit run -a`
  * Run on certain files: `pre-commit run --files test/*`
* Update (e.g. clean and install) hooks: `pre-commit clean && pre-commit install`
* Disable all hooks: `pre-commit uninstall`
* Enable all hooks: `pre-commit install`
* Skip a hook on commit: `SKIP=<hook-name> git commit`
* Skip all hooks on commit: `git commit --no-verify`

## Adding a contribution

Every contribution should be associated with a ticket on the GEAR JIRA board, or be a
hotfix (for Flywheel internal development). You should contribute by creating a branch 
titled with either `hotfix-<hotfix_name` or `GEAR-<gear_num>-<description>`. For now, 
other branch names will be accepted, but soon branch names will be rejected if they 
don't follow this pattern.

After pushing local changes to your forked repo, you can create a pull request back to 
the HPC Client repo through the github UI.

### Merge requests

The merge request should contain at least two things:

1. Your relevant change
2. Update the corresponding entry under `docs/release_notes.md`

Adding the release notes does two things:

1. It makes it easier for the reviewer to identify what relevant changes they should
expect and look for in the MR, and
2. It makes it easier to create a release.

#### Populating release notes

For example, if the cocde is currently on version `0.2.1` and you are working on a
bugfix under the branch GEAR-999-my-bugfix. When you create a merge request against
`main`, you should add a section to `doc/release_notes.md` such as the following:

```markdown
## 0.2.2
__FIX__:
* Fixed my-bug, see [GEAR-999](https://flywheelio.atlassian.net/browse/GEAR-999)

```

Where the rest of the file contains release notes for previous versions.