import importlib.util
import tempfile
import textwrap
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "tt" / "symbol_config.py"
MODULE_SPEC = importlib.util.spec_from_file_location("tt_symbol_config", MODULE_PATH)
SYMBOL_CONFIG_MODULE = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(SYMBOL_CONFIG_MODULE)

SymbolConfigControl = SYMBOL_CONFIG_MODULE.SymbolConfigControl
SymbolConfigElement = SYMBOL_CONFIG_MODULE.SymbolConfigElement


class TestSymbolConfigControl(unittest.TestCase):

    def _write_temp_file(self, content: str) -> str:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "symbol_config.yaml"
        path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
        return str(path)

    def test_import_from_file_loads_valid_config(self):
        path = self._write_temp_file(
            """
            - original_namespace: meritz
              original_symbol: IVV.AX
              legit_namespace: NYSEARCA
              legit_symbol: IVV
            - original_namespace: kiwoom
              original_symbol: BRKb
              legit_namespace: NYSE
              legit_symbol: BRK.B
            """
        )
        control = SymbolConfigControl()

        result, symbol_config = control.import_from_file(path)

        self.assertTrue(result)
        self.assertIs(symbol_config, control.symbol_config)
        self.assertEqual(len(symbol_config.symbol_config_elements), 2)

        first_item = symbol_config.symbol_config_elements[0]
        self.assertEqual(first_item.original_namespace, "meritz")
        self.assertEqual(first_item.original_symbol, "IVV.AX")
        self.assertEqual(first_item.legit_namespace, "NYSEARCA")
        self.assertEqual(first_item.legit_symbol, "IVV")

    def test_import_from_file_returns_empty_config_for_empty_yaml(self):
        path = self._write_temp_file("")
        control = SymbolConfigControl()

        result, symbol_config = control.import_from_file(path)

        self.assertTrue(result)
        self.assertIs(symbol_config, control.symbol_config)
        self.assertEqual(symbol_config.symbol_config_elements, [])

    def test_import_from_file_rejects_invalid_yaml(self):
        path = self._write_temp_file(
            """
            - original_namespace: meritz
              original_symbol: [broken
            """
        )
        control = SymbolConfigControl()

        result, symbol_config = control.import_from_file(path)

        self.assertFalse(result)
        self.assertIsNone(symbol_config)
        self.assertEqual(control.symbol_config.symbol_config_elements, [])

    def test_import_from_file_rejects_non_list_top_level(self):
        path = self._write_temp_file(
            """
            original_namespace: meritz
            original_symbol: IVV.AX
            """
        )
        control = SymbolConfigControl()

        result, symbol_config = control.import_from_file(path)

        self.assertFalse(result)
        self.assertIsNone(symbol_config)
        self.assertEqual(control.symbol_config.symbol_config_elements, [])

    def test_import_from_file_rejects_non_mapping_entry(self):
        path = self._write_temp_file(
            """
            - original_namespace: meritz
              original_symbol: IVV.AX
              legit_namespace: NYSEARCA
              legit_symbol: IVV
            - not-a-mapping
            """
        )
        control = SymbolConfigControl()

        result, symbol_config = control.import_from_file(path)

        self.assertFalse(result)
        self.assertIsNone(symbol_config)
        self.assertEqual(control.symbol_config.symbol_config_elements, [])

    def test_get_namespace_and_symbol_by_raw_input_returns_match(self):
        path = self._write_temp_file(
            """
            - original_namespace: kiwoom
              original_symbol: BRKb
              legit_namespace: NYSE
              legit_symbol: BRK.B
            """
        )
        control = SymbolConfigControl()
        result, symbol_config = control.import_from_file(path)

        self.assertTrue(result)
        self.assertEqual(
            symbol_config.get_namespace_and_symbol_by_raw_input("kiwoom", "BRKb"),
            ("NYSE", "BRK.B"),
        )

    def test_get_original_namespace_and_symbol_returns_match(self):
        path = self._write_temp_file(
            """
            - original_namespace: investing_dot_com
              original_symbol: BRK.B
              legit_namespace: NYSE
              legit_symbol: BRK.B
            """
        )
        control = SymbolConfigControl()
        result, symbol_config = control.import_from_file(path)

        self.assertTrue(result)
        self.assertEqual(
            symbol_config.get_original_namespace_and_symbol("investing_dot_com", "BRK.B"),
            ("investing_dot_com", "BRK.B"),
        )


class TestSymbolConfigElement(unittest.TestCase):

    def test_equality_and_hash(self):
        lhs = SymbolConfigElement()
        lhs.original_namespace = "meritz"
        lhs.original_symbol = "IVV.AX"
        lhs.legit_namespace = "NYSEARCA"
        lhs.legit_symbol = "IVV"

        rhs = SymbolConfigElement()
        rhs.original_namespace = "meritz"
        rhs.original_symbol = "IVV.AX"
        rhs.legit_namespace = "NYSEARCA"
        rhs.legit_symbol = "IVV"

        self.assertEqual(lhs, rhs)
        self.assertEqual(hash(lhs), hash(rhs))


if __name__ == "__main__":
    unittest.main()
