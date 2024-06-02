SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE_DIR=${SCRIPT_DIR}/..

python ${BASE_DIR}/tools/show-euc-kr-doc.py ${BASE_DIR}/data/kiwoom-exported-transactions/year-2020-<YOUR_ACCOUNT_0000_HERE>.csv
python ${BASE_DIR}/tools/show-euc-kr-doc.py ${BASE_DIR}/data/kiwoom-exported-transactions/year-2021-<YOUR_ACCOUNT_0000_HERE>.csv
python ${BASE_DIR}/tools/show-euc-kr-doc.py ${BASE_DIR}/data/kiwoom-exported-transactions/year-2022-<YOUR_ACCOUNT_0000_HERE>.csv
python ${BASE_DIR}/tools/show-euc-kr-doc.py ${BASE_DIR}/data/kiwoom-exported-transactions/year-2023-<YOUR_ACCOUNT_0000_HERE>.csv
python ${BASE_DIR}/tools/show-euc-kr-doc.py ${BASE_DIR}/data/kiwoom-exported-transactions/year-2024-<YOUR_ACCOUNT_0000_HERE>.csv
