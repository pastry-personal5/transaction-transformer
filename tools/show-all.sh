#!/usr/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE_DIR="${SCRIPT_DIR}"/..

python "${BASE_DIR}"/tools/show-euc-kr-doc.py "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2020-5417-5299.csv
python "${BASE_DIR}"/tools/show-euc-kr-doc.py "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2021-5417-5299.csv
python "${BASE_DIR}"/tools/show-euc-kr-doc.py "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2022-5417-5299.csv
python "${BASE_DIR}"/tools/show-euc-kr-doc.py "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2023-5417-5299.csv
python "${BASE_DIR}"/tools/show-euc-kr-doc.py "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2024-5417-5299.csv
