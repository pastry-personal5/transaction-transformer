import pprint
from typing import Tuple

import yaml
from loguru import logger


class SymbolConfigElement:

    def __init__(self):
        self.original_namespace = None
        self.original_symbol = None
        self.legit_namespace = None
        self.legit_symbol = None

    def __eq__(self, other):
        if isinstance(other, SymbolConfigElement):
            return (
                self.original_namespace == other.original_namespace
                and self.original_symbol == other.original_symbol
                and self.legit_namespace == other.legit_namespace
                and self.legit_symbol == other.legit_symbol
            )
        return False

    def __hash__(self):
        return hash((self.original_namespace, self.original_symbol, self.legit_namespace, self.legit_symbol))

    def __str__(self):
        return f"namespace({self.original_namespace}) symbol({self.original_symbol}) legit_namespace({self.legit_namespace}) legit_symbol({self.legit_symbol})"

class SymbolConfig:

    def __init__(self):
        self.symbol_config_elements = []

    def __str__(self):
        to_return = ""
        for item in self.symbol_config_elements:
            to_return += pprint.pformat(str(item))
            to_return += "\n"
        return to_return

    def get_namespace_and_symbol_by_raw_input(self, original_namespace: str, original_symbol: str) -> tuple[str, str]:
        for item in self.symbol_config_elements:
            if item.original_namespace == original_namespace and item.original_symbol == original_symbol:
                return (item.legit_namespace, item.legit_symbol)
        raise ValueError(f"Symbol not found for original_namespace: {original_namespace}, original_symbol: {original_symbol}")

    def get_original_namespace_and_symbol(self, original_namespace: str, legit_symbol: str) -> tuple[str, str]:
        for item in self.symbol_config_elements:
            if item.original_namespace == original_namespace and item.legit_symbol == legit_symbol:
                return (item.original_namespace, item.original_symbol)
        raise ValueError(f"Original symbol not found for namespace: {original_namespace}, legit_symbol: {legit_symbol}")

class SymbolConfigControl:

    def __init__(self):
        self.symbol_config = SymbolConfig()

    def import_from_file(self, symbol_config_file_path: str) -> Tuple[bool, SymbolConfig | None]:
        logger.info(f"Importing symbol configuration from file: {symbol_config_file_path} ...")
        symbol_config = self._build_symbol_config(symbol_config_file_path)
        if symbol_config is not None:
            self.symbol_config = symbol_config
            return (True, self.symbol_config)
        else:
            return (False, None)

    def _build_symbol_config(self, symbol_config_file_path: str) -> SymbolConfig:
        symbol_config = SymbolConfig()
        try:
            with open(symbol_config_file_path, "rb") as config_file:
                config = yaml.safe_load(config_file)
        except IOError as e:
            logger.error(f"IOError: {e}")
            logger.error("A configuration file path was: %s" % symbol_config_file_path)
            return None
        except yaml.YAMLError as e:
            logger.error(f"YAMLError: {e}")
            logger.error("A configuration file path was: %s" % symbol_config_file_path)
            return None

        if config is None:
            return symbol_config

        if not isinstance(config, list):
            logger.error("Symbol config must be a list.")
            logger.error("A configuration file path was: %s" % symbol_config_file_path)
            return None

        for item in config:
            if not isinstance(item, dict):
                logger.error("Each symbol config entry must be a mapping.")
                logger.error("A configuration file path was: %s" % symbol_config_file_path)
                return None
            symbol_config_element = SymbolConfigElement()
            symbol_config_element.original_namespace = item.get("original_namespace", None)
            symbol_config_element.original_symbol = item.get("original_symbol", None)
            symbol_config_element.legit_namespace = item.get("legit_namespace", None)
            symbol_config_element.legit_symbol = item.get("legit_symbol", None)
            symbol_config.symbol_config_elements.append(symbol_config_element)
        return symbol_config
