#!/bin/bash

set -euo pipefail

# ENVIRONMENT SETUP
# ideally there should be a pre-built docker image
# this would be deployed to a container where the code cloned
# and run.
# having this allows standardization of things like "the environment python code
# runs in". 
# your container setup would not use these next commands, this is a minimal
# setup to run on the host machine without changing anything about the host
# system's python install
python3 -m venv venv
source venv/bin/activate

# INSTALL DEPENDENCIES
# your docker image should already have pythonX.Y installed and pip available
# -U pip will ensure pip is updated, as well as confirming the ability to reach
# out over the network as necessary
# your organization may layout requirements.txt files differently; a search
# for all *requirements.txt files might be a general approach
# this is the format I use as it is the last annoying when using tab complete
pip install -U pip && pip install --no-cache-dir -r requirements.txt -r tests/requirements.txt

# RUN TESTS
# these commands are ran in the repo's directory. For instance
# $ git clone git@github.com:deerlord/openweatherapi
# $ cd openweatherapi
# now these commands can run as expected
flake8 --max-line-length=88 openweathermap tests
mypy openweathermap tests
pytest tests
