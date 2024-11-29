# test_expense_transaction.py
import unittest
from unittest.mock import MagicMock, patch
import datetime

import pandas as pd

from tt import *

class TestExpenseTransactionDBImpl(unittest.TestCase):

    def setUp(self):
        self.mock_db_connection = MagicMock(spec=DBConnection)
        self.db_impl = ExpenseTransactionDBImpl(self.mock_db_connection)

    def test_create_table_success(self):
        cur_mock = MagicMock()
        self.mock_db_connection.cur.return_value = cur_mock
        cur_mock.execute.return_value = None

        result = self.db_impl.create_table()
        self.assertTrue(result)
        cur_mock.execute.assert_called_once()


class TestExpenseTransactionControl(unittest.TestCase):

    def setUp(self):
        self.mock_db_connection = MagicMock(spec=DBConnection)
        self.control = ExpenseTransactionControl(self.mock_db_connection)

    def test_conversion(self):
        mock_transaction = BankSaladExpenseTransaction()
        mock_transaction.date = datetime.date(2024, 1, 1)
        mock_transaction.time = datetime.time(12, 30)
        mock_transaction.category0 = 'Food'
        mock_transaction.memo0 = 'Test'
        mock_transaction.amount = 100
        mock_transaction.currency = 'USD'
        mock_transaction.account = 'Bank Account'

        result = self.control._convert([mock_transaction], {'rules': []})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].amount, 100)
        self.assertEqual(result[0].category0, '카테고리 없음')

if __name__ == '__main__':
    unittest.main()
