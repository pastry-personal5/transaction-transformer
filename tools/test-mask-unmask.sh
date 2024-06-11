#!/usr/bin/bash
set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE_DIR="${SCRIPT_DIR}"/..

python "${BASE_DIR}"/tools/mask.py --config "${BASE_DIR}"/tests/mask/config_for_testing.yaml --function unmask
echo
cat "${BASE_DIR}"/tests/mask/test_0000.txt
echo
cat "${BASE_DIR}"/tests/mask/test_0001.txt
python "${BASE_DIR}"/tools/mask.py --config "${BASE_DIR}"/tests/mask/config_for_testing.yaml --function mask
echo
cat "${BASE_DIR}"/tests/mask/test_0000.txt
echo
cat "${BASE_DIR}"/tests/mask/test_0001.txt
