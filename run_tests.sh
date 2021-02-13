#!/bin/bash

set -euo pipefail

python3 -m venv venv
source venv/bin/activate
pip install -U pip && pip install --no-cache-dir -r requirements.txt -r tests/requirements.txt
flake8 --max-line-length=88 openweathermap tests
mypy openweathermap tests
pytest tests
