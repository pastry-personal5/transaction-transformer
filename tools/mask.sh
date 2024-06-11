#!/usr/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE_DIR="${SCRIPT_DIR}"/..

python "${BASE_DIR}"/tools/mask.py --config "${BASE_DIR}"/config/mask.yaml --function=mask
