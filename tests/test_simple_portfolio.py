import unittest
from datetime import date

import tt
from tt.simple_portfolio import SimplePortfolio
from tt.simple_transaction import SimpleTransaction


class TestSimplePortfolio(unittest.TestCase):
    def setUp(self):
        self.portfolio = SimplePortfolio()

    def test_record_buy(self):
        transaction = SimpleTransaction('AAPL', SimpleTransaction.SimpleTransactionTypeEnum.TYPE_BUY, 10, 150.0, date(2024, 6, 11), 0.0)
        self.portfolio.record_buy(transaction)
        self.assertEqual(self.portfolio.p['AAPL']['amount'], 10)
        self.assertEqual(self.portfolio.p['AAPL']['open_price'], 150.0)

    def test_record_sell(self):
        transaction = SimpleTransaction('AAPL', SimpleTransaction.SimpleTransactionTypeEnum.TYPE_BUY, 10, 150.0, date(2024, 6, 11), 0.0)
        self.portfolio.record_buy(transaction)
        transaction = SimpleTransaction('AAPL', SimpleTransaction.SimpleTransactionTypeEnum.TYPE_SELL, 5, 155.0, date(2024, 6, 12), 0.0)
        self.portfolio.record_sell(transaction)
        self.assertEqual(self.portfolio.p['AAPL']['amount'], 5)

    def test_record_stock_split_merge_insertion(self):
        transaction = SimpleTransaction('AAPL', SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_INSERTION, 2, 140.0, date(2024, 6, 13), 0.0)
        self.portfolio.record_stock_split_merge_insertion(transaction)
        self.assertEqual(self.portfolio.p['AAPL']['amount'], 2)
        self.assertEqual(self.portfolio.p['AAPL']['open_price'], 140.0)

    def test_record_stock_split_merge_deletion(self):
        transaction = SimpleTransaction('AAPL', SimpleTransaction.SimpleTransactionTypeEnum.TYPE_BUY, 10, 150.0, date(2024, 6, 11), 0.0)
        self.portfolio.record_buy(transaction)
        transaction = SimpleTransaction('AAPL', SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_DELETION, 5, 160.0, date(2024, 6, 14), 0.0)
        self.portfolio.record_stock_split_merge_deletion(transaction)
        self.assertEqual(self.portfolio.p['AAPL']['amount'], 5)


if __name__ == '__main__':
    unittest.main()
