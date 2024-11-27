from loguru import logger

from simple_transaction import SimpleTransaction


class SimplePortfolio():

    p = {}

    def __init__(self):
        self.p = {}

    def __str__(self):
        to_return = ''
        for item in self.p.items():
            symbol = item['symbol']
            amount = item['amount']
            open_price = item['open_price']
            open_date = item['open_date']
            to_return += f'symbol({symbol}) amount({amount}) open_price({open_price}) open_date({open_date})'
            to_return += '\n'
        return to_return

    def record_buy(self, transaction: SimpleTransaction):
        symbol = transaction.symbol
        amount = transaction.amount
        open_price = transaction.open_price
        open_date = transaction.open_date

        if symbol in self.p:
            prev_amount = self.p[symbol]['amount']
            prev_open_price = self.p[symbol]['open_price']
            self.p[symbol]['amount'] += amount  # float
            if prev_amount == 0:
                self.p[symbol]['open_price'] = open_price
            elif (prev_amount + amount) != 0:
                self.p[symbol]['open_price'] = \
                    ((prev_open_price * prev_amount) + (open_price * amount)) \
                    / (prev_amount + amount)  # float
            else:
                logger.warning(f'For symbol ({symbol}), amount is zero now.')

        else:
            self.p[symbol] = {}
            self.p[symbol]['amount'] = amount  # float
            self.p[symbol]['open_price'] = open_price  # float
            self.p[symbol]['open_date'] = open_date  # datetime.date

    def record_sell(self, transaction: SimpleTransaction):
        symbol = transaction.symbol
        amount = transaction.amount
        open_price = transaction.open_price
        open_date = transaction.open_date

        if symbol in self.p:
            self.p[symbol]['amount'] -= amount  # float
        else:
            self.p[symbol] = {}
            self.p[symbol]['amount'] = amount  # float
            self.p[symbol]['open_price'] = open_price  # float
            self.p[symbol]['open_date'] = open_date  # datetime.date

    def record_stock_split_merge_insertion(self, transaction: SimpleTransaction):
        symbol = transaction.symbol
        amount = transaction.amount
        open_price = transaction.open_price
        open_date = transaction.open_date

        if symbol in self.p:
            self.p[symbol]['amount'] += amount  # float
            self.p[symbol]['open_price'] = open_price  # float
        else:
            self.p[symbol] = {}
            self.p[symbol]['amount'] = amount  # float
            self.p[symbol]['open_price'] = open_price  # float
            self.p[symbol]['open_date'] = open_date  # datetime.date

    def record_stock_split_merge_deletion(self, transaction: SimpleTransaction):
        symbol = transaction.symbol
        amount = transaction.amount
        open_price = transaction.open_price
        open_date = transaction.open_date

        if symbol in self.p:
            self.p[symbol]['amount'] -= amount  # float
        else:
            self.p[symbol] = {}
            self.p[symbol]['amount'] = amount  # float
            self.p[symbol]['open_price'] = open_price  # float
            self.p[symbol]['open_date'] = open_date  # datetime.date

    def record(self, transaction: SimpleTransaction):
        if transaction.transaction_type == SimpleTransaction.SimpleTransactionTypeEnum.TYPE_BUY:
            self.record_buy(transaction)
        elif transaction.transaction_type == SimpleTransaction.SimpleTransactionTypeEnum.TYPE_SELL:
            self.record_sell(transaction)
        elif transaction.transaction_type == SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_INSERTION:
            self.record_stock_split_merge_insertion(transaction)
        elif transaction.transaction_type == SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_DELETION:
            self.record_stock_split_merge_deletion(transaction)
