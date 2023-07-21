#!/usr/bin/env bash
set -euo pipefail
unset CDPATH; cd "$( dirname "${BASH_SOURCE[0]}" )/.."; cd "$(pwd -P)"
set -x

# This script checks the project for correct formatting.

cd src

python -m flake8 --config .flake8 .
