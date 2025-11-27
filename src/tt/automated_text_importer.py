import os
from pathlib import Path
import pprint
import sys
from typing import Tuple, List

from loguru import logger
import yaml

from tt.meritz_text_importer import MeritzTextImporter
from tt.shinhan_text_importer import ShinhanTextImporter
from tt.automated_text_importer_base import AutomatedTextImporterBase
from tt.kiwoom_text_importer import KiwoomTextImporter
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
            try:
                (result, concatenated_file_meta) = importer.concat_and_cleanup_local_files_if_needed()
                if result and concatenated_file_meta:
                    (result, list_of_simple_transactions) = importer.import_transactions(concatenated_file_meta)
                    if result:
                        logger.info(f"Successfully imported transactions for {securities_firm_id}")
                        # @FIXME(dennis.oh) Merge all transactions from different securities firms.
                        return (result, list_of_simple_transactions)
                    else:
                        logger.error(f"Failed to import transactions for {securities_firm_id}")
            except Exception as e:
                logger.error(f"Error importing transactions for {securities_firm_id}: {e}")
                continue
            index += 1
        return (True, merged)
