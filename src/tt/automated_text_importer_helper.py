import datetime
import os
import sys
from pathlib import Path

import yaml
from loguru import logger

from tt.simple_transaction import SimpleTransaction


class AutomatedTextImporterHelper():

    @staticmethod
    def show_all_candidate_files() -> None:
        from tt.constants import Constants
        input_data_dir_path = Constants.input_data_dir_path
        module_config = AutomatedTextImporterHelper.load_module_config()
        securities_firm_ids = module_config.get("securities_firm_id", [])
        for securities_firm_id in securities_firm_ids:
            input_data_directory_path = os.path.join(input_data_dir_path, f"{securities_firm_id}-exported-transactions")
            logger.info(f"Checking for {securities_firm_id} transaction candidate files in: {input_data_directory_path}")
            for path in Path(input_data_directory_path).glob("*.csv"):
                logger.info(f"Found {securities_firm_id} transaction candidate file: {path} as {os.path.basename(path)}")
                input_file = open(path, newline="", encoding="euc-kr")

                sys.stdout.buffer.write((f"{os.path.basename(path)}").encode("utf-8"))
                sys.stdout.buffer.write(("\n").encode("utf-8"))
                for line in input_file.readlines():
                    sys.stdout.buffer.write(line.strip().encode("utf-8"))
                    sys.stdout.buffer.write(("\n").encode("utf-8"))
                sys.stdout.buffer.write(("---\n").encode("utf-8"))

                input_file.close()

    @staticmethod
    def load_module_config() -> dict:
        module_config_file_name = "automated_text_importer_config.yaml"
        from tt.constants import Constants
        config_dir_path = Constants.config_dir_path
        module_config_file_path = os.path.join(config_dir_path, module_config_file_name)
        if not os.path.exists(module_config_file_path):
            logger.error(f"The automated text importer configuration file does not exist: {module_config_file_path}")
            sys.exit(-1)
        return AutomatedTextImporterHelper.read_yaml_based_config(module_config_file_path)

    @staticmethod
    def read_yaml_based_config(config_file_path: str) -> dict:
        config_to_return = {}
        try:
            config_file = open(config_file_path, "rb")
            config = yaml.safe_load(config_file)
            if config is not None:
                config_to_return = config.copy()
            config_file.close()
        except IOError as e:
            logger.error(f"IOError: {e}")
            logger.error("A configuration file path was: %s" % config_file_path)
            return None
        return config_to_return

    @staticmethod
    # This function merges two lists of |SimpleTransactions| objects. It's based on date-by-date iteration.
    # Note: Performance-wise, this function can be improved a lot.
    def merge_simple_transactions(
        first: list[SimpleTransaction], second: list[SimpleTransaction]
    ) -> list[SimpleTransaction]:
        merged = []
        len_first = len(first)
        len_second = len(second)
        if len_second == 0:
            return first
        if second[0].open_date < first[0].open_date:
            return AutomatedTextImporterHelper.merge_simple_transactions(second, first)
        i = 0
        j = 0
        current_date = first[0].open_date
        transactions_of_current_date = None
        ending_date = datetime.date.today()
        while current_date <= ending_date:
            transactions_of_current_date = []
            while i < len_first:
                f = first[i]
                f_date = f.open_date
                if f_date > current_date:
                    break
                transactions_of_current_date.append(f)
                i += 1
            while j < len_second:
                s = second[j]
                s_date = s.open_date
                if s_date > current_date:
                    break
                transactions_of_current_date.append(s)
                j += 1
            AutomatedTextImporterHelper.append_transactions_of_current_date(merged, transactions_of_current_date)
            current_date += datetime.timedelta(days=1)

        return merged

    @staticmethod
    def append_transactions_of_current_date(
        list_of_simple_transactions: list, transactions_of_current_date: list
    ):
        for t in transactions_of_current_date:
            if (
                t.transaction_type
                == SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_DELETION
            ):
                list_of_simple_transactions.append(t)
        for t in transactions_of_current_date:
            if (
                t.transaction_type
                == SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_INSERTION
            ):
                list_of_simple_transactions.append(t)
        for t in transactions_of_current_date:
            if t.transaction_type == SimpleTransaction.SimpleTransactionTypeEnum.TYPE_BUY:
                list_of_simple_transactions.append(t)
        for t in transactions_of_current_date:
            if (
                t.transaction_type
                == SimpleTransaction.SimpleTransactionTypeEnum.TYPE_INBOUND_TRANSFER_RESULTED_FROM_EVENT
            ):
                list_of_simple_transactions.append(t)
        for t in transactions_of_current_date:
            if t.transaction_type == SimpleTransaction.SimpleTransactionTypeEnum.TYPE_SELL:
                list_of_simple_transactions.append(t)
