#!/bin/bash

python3.8 -m venv venv
source venv/bin/activate
pip install -U pip && pip install -r requirements.txt -r tests/requirements.txt
flake8
mypy
pytest tests/
