import unittest
import datetime

from tt.simple_transaction import SimpleTransaction


class TestSimpleTransaction(unittest.TestCase):

    def test_initialization(self):
        transaction = SimpleTransaction(
            symbol='AAPL',
            transaction_type=SimpleTransaction.SimpleTransactionTypeEnum.TYPE_BUY,
            amount=100.0,
            open_price=150.0,
            open_date=datetime.date(2023, 6, 12),
            commission=10.0
        )
        self.assertEqual(transaction.symbol, 'AAPL')
        self.assertEqual(transaction.transaction_type, SimpleTransaction.SimpleTransactionTypeEnum.TYPE_BUY)
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.open_price, 150.0)
        self.assertEqual(transaction.open_date, datetime.date(2023, 6, 12))
        self.assertEqual(transaction.commission, 10.0)

    def test_default_initialization(self):
        transaction = SimpleTransaction()
        self.assertEqual(transaction.symbol, '')
        self.assertEqual(transaction.transaction_type, SimpleTransaction.SimpleTransactionTypeEnum.TYPE_BUY)
        self.assertEqual(transaction.amount, 0.0)
        self.assertEqual(transaction.open_price, 0.0)
        self.assertEqual(transaction.open_date, datetime.date(1970, 1, 1))
        self.assertEqual(transaction.commission, 0.0)

    def test_transaction_type_string(self):
        transaction_sell = SimpleTransaction(transaction_type=SimpleTransaction.SimpleTransactionTypeEnum.TYPE_SELL)
        self.assertEqual(transaction_sell.get_transaction_type_string(), 'SELL')

        transaction_buy = SimpleTransaction(transaction_type=SimpleTransaction.SimpleTransactionTypeEnum.TYPE_BUY)
        self.assertEqual(transaction_buy.get_transaction_type_string(), 'BUY')

        transaction_split_insertion = SimpleTransaction(transaction_type=SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_INSERTION)
        self.assertEqual(transaction_split_insertion.get_transaction_type_string(), 'STOCK_SPLIT_MERGE_INSERTION')

        transaction_split_deletion = SimpleTransaction(transaction_type=SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_DELETION)
        self.assertEqual(transaction_split_deletion.get_transaction_type_string(), 'STOCK_SPLIT_MERGE_DELETION')

        transaction_other = SimpleTransaction(transaction_type=99)
        self.assertEqual(transaction_other.get_transaction_type_string(), 'OTHER')

    def test_str(self):
        transaction = SimpleTransaction(
            symbol='AAPL',
            transaction_type=SimpleTransaction.SimpleTransactionTypeEnum.TYPE_BUY,
            amount=100.0,
            open_price=150.0,
            open_date=datetime.date(2023, 6, 12),
            commission=10.0
        )
        self.assertEqual(str(transaction), 'symbol(AAPL) transaction_type(BUY) open_price(150.0) amount(100.0) commission(10.0) open_date(2023-06-12)')


if __name__ == '__main__':
    unittest.main()
