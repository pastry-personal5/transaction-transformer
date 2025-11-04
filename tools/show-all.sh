#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE_DIR="${SCRIPT_DIR}"/..

uv run "${BASE_DIR}"/tools/show_euc_kr_doc.py "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2020-5417-5299.csv
uv run "${BASE_DIR}"/tools/show_euc_kr_doc.py "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2021-5417-5299.csv
uv run "${BASE_DIR}"/tools/show_euc_kr_doc.py "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2022-5417-5299.csv
uv run "${BASE_DIR}"/tools/show_euc_kr_doc.py "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2023-5417-5299.csv
uv run "${BASE_DIR}"/tools/show_euc_kr_doc.py "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2024-5417-5299.csv
uv run "${BASE_DIR}"/tools/show_euc_kr_doc.py "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2025-5417-5299.csv
