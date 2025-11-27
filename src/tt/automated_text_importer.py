import pprint
from typing import List, Tuple

from loguru import logger

from tt.automated_text_importer_base import AutomatedTextImporterBase
from tt.automated_text_importer_helper import AutomatedTextImporterHelper
from tt.kiwoom_text_importer import KiwoomTextImporter
from tt.meritz_text_importer import MeritzTextImporter
from tt.shinhan_text_importer import ShinhanTextImporter
from tt.simple_transaction import SimpleTransaction


class AutomatedTextImporterFactory:
    @staticmethod
    def create_importer(importer_type: str) -> AutomatedTextImporterBase | None:
        if importer_type == "kiwoom":
            return KiwoomTextImporter()
        elif importer_type == "shinhan":
            return ShinhanTextImporter()
        elif importer_type == "meritz":
            return MeritzTextImporter()
        else:
            logger.error(f"Unknown importer type: {importer_type}")
            return None


class AutomatedTextImporterControl:
    def __init__(self):
        from tt.constants import Constants
        self.config_dir_path = Constants.config_dir_path
        self.input_data_dir_path = Constants.input_data_dir_path
        self.output_data_dir_path = Constants.output_data_dir_path
        self.module_config = None

    def load_module_config(self) -> None:
        self.module_config = AutomatedTextImporterHelper.load_module_config()

    def import_all_transactions(self) -> Tuple[bool, List[SimpleTransaction]]:
        return self._import_transactions_from_local_file_system()

    def _import_transactions_from_local_file_system(self) -> Tuple[bool, List[SimpleTransaction]]:
        """Import transaction from local file system.

        Returns:
            bool: True if import is successful, False otherwise.
        """
        merged = []
        index = 0
        for securities_firm_id in self.module_config.get("securities_firm_id", []):
            importer = AutomatedTextImporterFactory.create_importer(securities_firm_id)
            if importer is None:
                logger.warning(f"Failed to create importer for id: {securities_firm_id}")
                continue

            (result, concatenated_file_meta) = importer.concat_and_cleanup_local_files_if_needed()
            if result and concatenated_file_meta:
                (result, list_of_simple_transactions) = importer.import_transactions(concatenated_file_meta)
                if result:
                    logger.info(f"Successfully imported transactions for {securities_firm_id}")
                    if index == 0:
                        merged = list_of_simple_transactions.copy()
                    else:
                        merged = AutomatedTextImporterHelper.merge_simple_transactions(merged, list_of_simple_transactions)
                    logger.info(f"Total imported transactions so far: {len(merged)}")
                else:
                    logger.error(f"Failed to import transactions for {securities_firm_id}")

            index += 1
        return (True, merged)
