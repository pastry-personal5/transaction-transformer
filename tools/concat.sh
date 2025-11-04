#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE_DIR="${SCRIPT_DIR}"/..

# 5417-5299
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2020-5417-5299.csv > "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-5417-5299.csv
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2021-5417-5299.csv >> "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-5417-5299.csv
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2022-5417-5299.csv >> "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-5417-5299.csv
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2023-5417-5299.csv >> "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-5417-5299.csv
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2024-5417-5299.csv >> "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-5417-5299.csv
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2025-5417-5299.csv >> "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-5417-5299.csv

uv run  "${BASE_DIR}"/tools/cleanup_kiwoom_data.py --file "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-5417-5299.csv


# 3021-6825
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2023-3021-6825.csv > "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-3021-6825.csv
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2024-3021-6825.csv >> "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-3021-6825.csv

uv run  "${BASE_DIR}"/tools/cleanup_kiwoom_data.py --file "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-3021-6825.csv

# 3480-4607
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2023-3480-4607.csv > "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-3480-4607.csv
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2024-3480-4607.csv >> "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-3480-4607.csv

uv run  "${BASE_DIR}"/tools/cleanup_kiwoom_data.py --file "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-3480-4607.csv
