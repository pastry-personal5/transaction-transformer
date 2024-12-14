# test_expense_transaction.py
import unittest
from unittest.mock import MagicMock, patch
import datetime

import pandas as pd

from tt import *
from tt.expense_transaction import ExpenseTransaction


class TestExpenseTransaction(unittest.TestCase):

    def test_equality_same_attributes(self):
        transaction1 = ExpenseTransaction()
        transaction2 = ExpenseTransaction()
        transaction1.amount = 100
        transaction2.amount = 100
        transaction1.category0 = "Food"
        transaction2.category0 = "Food"
        transaction1.transaction_datetime = datetime.datetime.now()
        transaction2.transaction_datetime = transaction1.transaction_datetime
        transaction1.user_identifier = "user123"
        transaction2.user_identifier = "user123"

        self.assertEqual(transaction1, transaction2)

    def test_equality_different_attributes(self):
        transaction1 = ExpenseTransaction()
        transaction2 = ExpenseTransaction()
        transaction1.amount = 100
        transaction2.amount = 200  # Different amount
        transaction1.category0 = "Food"
        transaction2.category0 = "Travel"

        self.assertNotEqual(transaction1, transaction2)

    def test_equality_and_hash_same_attributes_while_ignoring_several_fields_0000(self):
        transaction1 = ExpenseTransaction()
        transaction2 = ExpenseTransaction()
        transaction1.amount = 100
        transaction2.amount = 100
        transaction1.category0 = "Food"
        transaction2.category0 = "Travel"
        transaction1.category0 = "Chinese Food"
        transaction2.category0 = "Chinese Food"
        transaction1.memo0 = "Memo0"
        transaction2.memo0 = "Memo0"
        transaction1.memo1 = "Memo1"
        transaction2.memo1 = "Memo1"
        transaction1.transaction_datetime = datetime.datetime.now()
        transaction2.transaction_datetime = transaction1.transaction_datetime
        transaction1.user_identifier = "user123"
        transaction2.user_identifier = "user123"

        self.assertEqual(transaction1, transaction2)
        self.assertEqual(hash(transaction1), hash(transaction2))

    def test_equality_ans_hash_same_attributes_while_ignoring_several_fields_0001(self):
        transaction1 = ExpenseTransaction()
        transaction2 = ExpenseTransaction()
        transaction1.amount = 100
        transaction2.amount = 100
        transaction1.category0 = "Food"
        transaction2.category0 = "Food"
        transaction1.category0 = "Chinese Food"
        transaction2.category0 = "French Food"
        transaction1.memo0 = "Memo0"
        transaction2.memo0 = "Memo0"
        transaction1.memo1 = "Memo1"
        transaction2.memo1 = "Memo1"
        transaction1.transaction_datetime = datetime.datetime.now()
        transaction2.transaction_datetime = transaction1.transaction_datetime
        transaction1.user_identifier = "user123"
        transaction2.user_identifier = "user123"

        self.assertEqual(transaction1, transaction2)
        self.assertEqual(hash(transaction1), hash(transaction2))

    def test_equality_and_hash_same_attributes_while_ignoring_several_fields_0002(self):
        transaction1 = ExpenseTransaction()
        transaction2 = ExpenseTransaction()
        transaction1.amount = 100
        transaction2.amount = 100
        transaction1.category0 = "Food"
        transaction2.category0 = "Food"
        transaction1.category0 = "Chinese Food"
        transaction2.category0 = "Chinese Food"
        transaction1.memo0 = "Memo0"
        transaction2.memo0 = "Memo0x"
        transaction1.memo1 = "Memo1"
        transaction2.memo1 = "Memo1"
        transaction1.transaction_datetime = datetime.datetime.now()
        transaction2.transaction_datetime = transaction1.transaction_datetime
        transaction1.user_identifier = "user123"
        transaction2.user_identifier = "user123"

        self.assertEqual(transaction1, transaction2)
        self.assertEqual(hash(transaction1), hash(transaction2))

    def test_equality_and_hash_same_attributes_while_ignoring_several_fields_0003(self):
        transaction1 = ExpenseTransaction()
        transaction2 = ExpenseTransaction()
        transaction1.amount = 100
        transaction2.amount = 100
        transaction1.category0 = "Food"
        transaction2.category0 = "Food"
        transaction1.category0 = "Chinese Food"
        transaction2.category0 = "Chinese Food"
        transaction1.memo0 = "Memo0"
        transaction2.memo0 = "Memo0"
        transaction1.memo1 = "Memo1"
        transaction2.memo1 = "Memo1x"
        transaction1.transaction_datetime = datetime.datetime.now()
        transaction2.transaction_datetime = transaction1.transaction_datetime
        transaction1.user_identifier = "user123"
        transaction2.user_identifier = "user123"

        self.assertEqual(transaction1, transaction2)
        self.assertEqual(hash(transaction1), hash(transaction2))

    def test_hash_same_attributes(self):
        transaction1 = ExpenseTransaction()
        transaction2 = ExpenseTransaction()
        transaction1.amount = 100
        transaction2.amount = 100
        transaction1.category0 = "Food"
        transaction2.category0 = "Food"
        transaction1.transaction_datetime = datetime.datetime.now()
        transaction2.transaction_datetime = transaction1.transaction_datetime
        transaction1.user_identifier = "user123"
        transaction2.user_identifier = "user123"

        self.assertEqual(hash(transaction1), hash(transaction2))

    def test_hash_different_attributes(self):
        transaction1 = ExpenseTransaction()
        transaction2 = ExpenseTransaction()
        transaction1.amount = 100
        transaction2.amount = 200  # Different amount
        transaction1.category0 = "Food"
        transaction2.category0 = "Travel"

        self.assertNotEqual(hash(transaction1), hash(transaction2))

    def test_string_representation(self):
        transaction = ExpenseTransaction()
        transaction.amount = 150
        transaction.category0 = "Groceries"
        transaction.transaction_datetime = datetime.datetime(2023, 12, 1, 15, 30)
        transaction.user_identifier = "user123"
        expected_str = (
            "datetime(2023-12-01 15:30:00) "
            "category0(Groceries) category1(None) memo0(None) memo1(None) "
            "amount(150) currency(None) source_account(None) target_account(None) "
            "user_identifier(user123)"
        )
        self.assertEqual(str(transaction), expected_str)


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
