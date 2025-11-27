import os
import sys

from loguru import logger
import yaml


class AutomatedTextImporterControl:
    def __init__(self):
        from tt.constants import Constants
        self.config_dir_path = Constants.config_dir_path
        self.input_data_dir_path = Constants.input_data_dir_path
        self.output_data_dir_path = Constants.output_data_dir_path
        self.local_config = None

    def load_local_config(self) -> None:
        local_config_file_name = "automated_text_importer_config.yaml"
        local_config_file_path = os.path.join(self.config_dir_path, local_config_file_name)
        if not os.path.exists(local_config_file_path):
            logger.error(f"The automated text importer configuration file does not exist: {local_config_file_path}")
            sys.exit(-1)
        self.local_config = self._read_yaml_based_config(local_config_file_path)

    def import_all_transactions(self) -> None:
        file_and_meta_list = self._find_files()
        if file_and_meta_list:
            self._import_transactions_from_local_file_system(file_and_meta_list)

    def _read_yaml_based_config(self, config_file_path: str) -> dict:
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

    def _import_transactions_from_local_file_system(self) -> bool:
        """Import transaction from local file system.

        Returns:
            bool: True if import is successful, False otherwise.
        """
        return False

    def _find_files(self) -> list[tuple[str, dict]]:
        """Find files to import from the local file system.

        Returns:
            list[tuple[str, dict]]: A list of tuples containing file paths and metadata.
        """
        return []
