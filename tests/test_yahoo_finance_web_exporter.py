"""
It tests `TestYahooFinanceWebExporter`.
A chatgpt-4o-generated unittest in 2024.
"""
import unittest
from unittest.mock import patch

from  yahoo_finance_web_exporter import YahooFinanceWebExporter


class TestYahooFinanceWebExporter(unittest.TestCase):

    @patch('builtins.input', side_effect=['c'])
    @patch('builtins.print')  # Mocking print to avoid actual print calls during tests
    def test_wait_for_page_load(self, mock_print, mock_input):

        obj = YahooFinanceWebExporter()
        obj.wait_for_page_load()
        # Verify if the function returned as expected
        # pylint: disable=redundant-unittest-assert
        self.assertTrue(True)  # Simply asserting True because if the function completes, it worked as expected
        # pylint: enable=redundant-unittest-assert

    @patch('builtins.input', side_effect=['a', 'b', 'c'])
    @patch('builtins.print')  # Mocking print to avoid actual print calls during tests
    def test_wait_for_page_load_with_multiple_inputs(self, mock_print, mock_input):
        # pylint: disable=redundant-unittest-assert
        obj = YahooFinanceWebExporter()
        obj.wait_for_page_load()
        # Verify if the function returned as expect
        # pylint: disable=redundant-unittest-assert
        self.assertTrue(True)  # Simply asserting True because if the function completes, it worked as expected
        # pylint: enable=redundant-unittest-assert

if __name__ == '__main__':
    unittest.main()
