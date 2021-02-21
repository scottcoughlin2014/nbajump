# DJANGO Fanduel NBA Jumpball

## Install
We recommend creating an anaconda virtual environment. That way you can also automatically set the `DJANGO_SETTINGS_MODULE` environmnetal variable correctly upon activation and unset upon deactivation
```
conda create --name fanduel_nba_jumpball django python=3.8 --yes
conda activate fanduel_nba_jumpball
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
mkdir -p $CONDA_PREFIX/etc/conda/deactivate.d
echo \#\!/bin/sh > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo export DJANGO_SETTINGS_MODULE=jumpnba.dev_settings >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo \#\!/bin/sh > $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
echo unset DJANGO_SETTINGS_MODULE >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
```
Then deactivate and reactivate the environment

## Initialize and fill database
We have provided all of the needed commands in `src`. So just run
```
bash src
```
