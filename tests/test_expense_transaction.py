# test_expense_transaction.py
import unittest
from unittest.mock import MagicMock, patch
import datetime

import pandas as pd

from tt import *
from tt.expense_transaction import ExpenseTransaction


class TestExpenseTransaction(unittest.TestCase):

    def setUp(self):
        """Initialize test instances of ExpenseTransaction."""
        self.transaction1 = ExpenseTransaction()
        self.transaction1.amount = 100
        self.transaction1.currency = "USD"
        self.transaction1.source_account = "Account1"
        self.transaction1.target_account = "Account2"
        self.transaction1.transaction_datetime = datetime.datetime(2024, 2, 15, 12, 0, 0)
        self.transaction1.user_identifier = "User123"

        self.transaction2 = ExpenseTransaction()
        self.transaction2.amount = 100
        self.transaction2.currency = "USD"
        self.transaction2.source_account = "Account1"
        self.transaction2.target_account = "Account2"
        self.transaction2.transaction_datetime = datetime.datetime(2024, 2, 15, 12, 0, 0)
        self.transaction2.user_identifier = "User123"

        self.transaction_different = ExpenseTransaction()
        self.transaction_different.amount = 200  # Different amount
        self.transaction_different.currency = "EUR"
        self.transaction_different.source_account = "AccountX"
        self.transaction_different.target_account = "AccountY"
        self.transaction_different.transaction_datetime = datetime.datetime(2024, 2, 16, 14, 0, 0)
        self.transaction_different.user_identifier = "User456"

    def test_initialization(self):
        """Test if ExpenseTransaction initializes with default values."""
        default_transaction = ExpenseTransaction()
        self.assertEqual(default_transaction.amount, 0)
        self.assertIsNone(default_transaction.currency)
        self.assertIsNone(default_transaction.transaction_datetime)

    def test_str_method(self):
        """Test __str__ method for proper string representation."""
        expected_str = (
            "transaction_datetime(2024-02-15 12:00:00) category0(None) category1(None) "
            "memo0(None) memo1(None) amount(100) currency(USD) "
            "source_account(Account1) target_account(Account2) user_identifier(User123)"
        )
        self.assertEqual(str(self.transaction1), expected_str)

    def test_equality(self):
        """Test __eq__ method for equality comparison."""
        self.assertEqual(self.transaction1, self.transaction2)  # Same values, should be equal
        self.assertNotEqual(self.transaction1, self.transaction_different)  # Different values, should not be equal

    def test_hash_method(self):
        """Test __hash__ method to ensure consistent hashing."""
        self.assertEqual(hash(self.transaction1), hash(self.transaction2))
        self.assertNotEqual(hash(self.transaction1), hash(self.transaction_different))


class TestExpenseTransactionDBImpl(unittest.TestCase):

    def setUp(self):
        self.mock_db_connection = MagicMock(spec=DBConnection)
        self.db_impl = ExpenseTransactionDBImpl(self.mock_db_connection)

    @patch.object(DBImplBase, "_is_table_in_database")  # Mock method in the class
    @patch.object(ExpenseTransaction.__table__, "create")  # Mock table creation
    def test_create_table(self, mock_create, mock_is_table_in_db):
        # Create a mock DBConnection object
        mock_db_connection = MagicMock(spec=DBConnection)

        # Initialize DBImplBase with the mock DBConnection
        db_impl = DBImplBase(mock_db_connection)

        # Case 1: Table already exists -> should return False
        mock_is_table_in_db.return_value = True
        self.assertFalse(self.db_impl.create_table())
        mock_create.assert_not_called()  # Ensure create() wasn't called

        self.db_impl.db_connection.engine = None

        # Case 2: Table does not exist -> should create and return True
        mock_is_table_in_db.return_value = False
        self.assertTrue(self.db_impl.create_table())
        mock_create.assert_called_once_with(self.db_impl.db_connection.engine)  # Ensure create() was called


class TestExpenseTransactionControl(unittest.TestCase):

    def setUp(self):
        self.mock_db_connection = MagicMock(spec=DBConnection)
        self.control = ExpenseTransactionControl(self.mock_db_connection)

    def test_conversion(self):
        mock_transaction = BankSaladExpenseTransaction()
        mock_transaction.date = datetime.date(2024, 1, 1)
        mock_transaction.time = datetime.time(12, 30)
        mock_transaction.category0 = "Food"
        mock_transaction.memo0 = "Test"
        mock_transaction.amount = 100
        mock_transaction.currency = "USD"
        mock_transaction.account = "Bank Account"

        result = self.control._convert([mock_transaction], {"rules": []})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].amount, 100)
        self.assertEqual(result[0].category0, "카테고리 없음")


if __name__ == "__main__":
    unittest.main()
