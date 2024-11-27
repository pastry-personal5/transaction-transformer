#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE_DIR="${SCRIPT_DIR}"/..

# <YOUR_ACCOUNT_0000_HERE>
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2020-<YOUR_ACCOUNT_0000_HERE>.csv > "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-<YOUR_ACCOUNT_0000_HERE>.csv
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2021-<YOUR_ACCOUNT_0000_HERE>.csv >> "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-<YOUR_ACCOUNT_0000_HERE>.csv
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2022-<YOUR_ACCOUNT_0000_HERE>.csv >> "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-<YOUR_ACCOUNT_0000_HERE>.csv
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2023-<YOUR_ACCOUNT_0000_HERE>.csv >> "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-<YOUR_ACCOUNT_0000_HERE>.csv
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2024-<YOUR_ACCOUNT_0000_HERE>.csv >> "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-<YOUR_ACCOUNT_0000_HERE>.csv

python "${BASE_DIR}"/tools/cleanup_kiwoom_data.py --file "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-<YOUR_ACCOUNT_0000_HERE>.csv


# <YOUR_ACCOUNT_0001_HERE>
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2023-<YOUR_ACCOUNT_0001_HERE>.csv > "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-<YOUR_ACCOUNT_0001_HERE>.csv
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2024-<YOUR_ACCOUNT_0001_HERE>.csv >> "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-<YOUR_ACCOUNT_0001_HERE>.csv

python "${BASE_DIR}"/tools/cleanup_kiwoom_data.py --file "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-<YOUR_ACCOUNT_0001_HERE>.csv

# <YOUR_ACCOUNT_0002_HERE>
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2023-<YOUR_ACCOUNT_0002_HERE>.csv > "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-<YOUR_ACCOUNT_0002_HERE>.csv
cat "${BASE_DIR}"/data/kiwoom-exported-transactions/year-2024-<YOUR_ACCOUNT_0002_HERE>.csv >> "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-<YOUR_ACCOUNT_0002_HERE>.csv

python "${BASE_DIR}"/tools/cleanup_kiwoom_data.py --file "${BASE_DIR}"/data/kiwoom-exported-transactions/latest-<YOUR_ACCOUNT_0002_HERE>.csv
