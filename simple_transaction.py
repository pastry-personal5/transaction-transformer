import datetime


class SimpleTransaction():
    # Constants
    TYPE_SELL = 0
    TYPE_BUY = 1
    TYPE_STOCK_SPLIT_MERGE_INSERTION = 2
    TYPE_STOCK_SPLIT_MERGE_DELETION = 3

    account = ''  # string
    amount = 0  # float
    commission = 0  # float
    open_date = None  # Python datetime.date
    open_price = 0  # float
    symbol = ''
    transaction_type = TYPE_SELL  # It's either |TYPE_SELL| or |TYPE_BUY|.

    def __init__(self, symbol='', transaction_type=TYPE_BUY, amount=0.0, open_price=0.0, open_date=datetime.date(1970, 1, 1), commission=0.0):
        self.symbol = symbol
        self.transaction_type = transaction_type
        self.amount = amount
        self.open_price = open_price
        self.open_date = open_date
        self.commission = commission

    def __str__(self):
        transaction_type_as_string = self.get_transaction_type_string()
        return f'symbol({self.symbol}) transaction_type({transaction_type_as_string}) open_price({self.open_price}) amount({self.amount}) commission({self.commission}) open_date({self.open_date})'

    def get_transaction_type_string(self):
        if self.transaction_type == self.TYPE_SELL:
            type_as_string = 'SELL'
        elif self.transaction_type == self.TYPE_BUY:
            type_as_string = 'BUY'
        elif self.transaction_type == self.TYPE_STOCK_SPLIT_MERGE_INSERTION:
            type_as_string = 'TYPE_STOCK_SPLIT_MERGE_INSERTION'
        elif self.transaction_type == self.TYPE_STOCK_SPLIT_MERGE_DELETION:
            type_as_string = 'TYPE_STOCK_SPLIT_MERGE_DELETION'
        else:
            type_as_string = 'OTHER'
        return type_as_string
