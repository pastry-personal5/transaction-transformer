from abc import abstractmethod
import os
from pathlib import Path
import re
from typing import Tuple

from loguru import logger

from tt.automated_text_importer_base import AutomatedTextImporterBase
from tt.simple_transaction import SimpleTransaction


class AutomatedTextImporterBaseImpl(AutomatedTextImporterBase):

    def __init__(self):
        self.securities_firm_id = None

    @abstractmethod
    def import_transactions(self, concatenated_file_meta: list[tuple[str, str]]) -> Tuple[bool, list[SimpleTransaction]]:
        """
        Subclasses must implement this method to import transactions from the provided concatenated files.
        """
        pass

    # Implemented method
    def concat_and_cleanup_local_files_if_needed(self) -> tuple[bool, list[tuple[str, str]] | None]:
        """
        Concatenate local files if needed.
        Do the cleansing on input data, if needed.
        """
        concatenated_file_meta = self._concat_files_if_needed()
        if concatenated_file_meta:
            self._cleanup_files(concatenated_file_meta)
            return (True, concatenated_file_meta)
        else:
            return (False, None)

    def _build_input_data_directory_path(self, securities_firm_id: str) -> str:
        from tt.constants import Constants
        input_data_dir_path = Constants.input_data_dir_path
        input_data_directory_path = os.path.join(input_data_dir_path, f"{securities_firm_id}-exported-transactions")
        return input_data_directory_path

    def _concat_files_if_needed(self) -> None:
        input_data_dir_path = self._build_input_data_directory_path(self.securities_firm_id)
        logger.info(f"Checking for transaction candidate files in: {input_data_dir_path}")
        files = []
        for path in Path(input_data_dir_path).glob("year-*.csv"):
            logger.info(f"Found transaction candidate file: {path}")
            files.append(os.path.basename(path))

        files.sort()

        account_set = set()
        for name in files:
            match = re.match(r"year-(\d{4})-(.*)\.csv", name)
            if match:
                account_set.add(match.group(2))
            else:
                logger.warning(f"Filename does not match expected pattern: {name}")
                continue
        account_and_file_map = {}
        for account in account_set:
            account_and_file_map[account] = []
            for name in files:
                if f"-{account}." in name:
                    account_and_file_map[account].append(name)
        concatenated_file_meta = []
        for account in account_set:
            concatenated_file_path = os.path.join(input_data_dir_path, f"latest-{account}.csv")
            with open(concatenated_file_path, "w", encoding="euc-kr") as concatenated_file:
                for name in account_and_file_map[account]:
                    file_path = os.path.join(input_data_dir_path, name)
                    with open(file_path, "r", encoding="euc-kr") as input_file:
                        lines = input_file.readlines()
                        if len(lines) > 0:
                            # Skip header line for all but the first file
                            start_index = 1 if name != account_and_file_map[account][0] else 0
                            for line in lines[start_index:]:
                                concatenated_file.write(line)
                    logger.info(f"Processed file: {os.path.basename(file_path)}")
            logger.info(f"Created concatenated file: {os.path.basename(concatenated_file_path)}")
            concatenated_file_meta.append((concatenated_file_path, account))
        return concatenated_file_meta

    def _cleanup_files(self, concatenated_file_meta: list[tuple[str, str]]) -> None:
        """
        Subclasses may override this method to implement file cleanup logic.
        """
        pass
