import datetime
from enum import Enum


class SimpleTransaction():

    CORE_FIELD_LENGTH = 7  # The length of items - account, amount, open_date, etc.

    class SimpleTransactionTypeEnum(Enum):
        # Constants
        TYPE_SELL = 0
        TYPE_BUY = 1
        TYPE_STOCK_SPLIT_MERGE_INSERTION = 2
        TYPE_STOCK_SPLIT_MERGE_DELETION = 3
        TYPE_OTHER = 4


    def __init__(self, symbol='', transaction_type=SimpleTransactionTypeEnum.TYPE_BUY, amount=0.0, open_price=0.0, open_date=datetime.date(1970, 1, 1), commission=0.0):
        self.account = ''  # string
        self.amount = amount  # float
        self.commission = commission  # float
        self.open_date = open_date  # Python datetime.date
        self.open_price = open_price  # float
        self.symbol = symbol  # string
        self.transaction_type = transaction_type  # SimpleTransactionTypeEnum

    def __str__(self):
        transaction_type_as_string = self.get_transaction_type_string()
        return f'symbol({self.symbol}) transaction_type({transaction_type_as_string}) open_price({self.open_price}) amount({self.amount}) commission({self.commission}) open_date({self.open_date})'

    def get_transaction_type_string(self):
        if self.transaction_type == self.SimpleTransactionTypeEnum.TYPE_SELL:
            type_as_string = 'SELL'
        elif self.transaction_type == self.SimpleTransactionTypeEnum.TYPE_BUY:
            type_as_string = 'BUY'
        elif self.transaction_type == self.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_INSERTION:
            type_as_string = 'STOCK_SPLIT_MERGE_INSERTION'
        elif self.transaction_type == self.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_DELETION:
            type_as_string = 'STOCK_SPLIT_MERGE_DELETION'
        else:
            type_as_string = 'OTHER'
        return type_as_string

    @staticmethod
    def get_transaction_type_from_string(transaction_type_string: str) -> SimpleTransactionTypeEnum:
        if transaction_type_string == 'SELL':
            return SimpleTransaction.SimpleTransactionTypeEnum.TYPE_SELL
        elif transaction_type_string == 'BUY':
            return SimpleTransaction.SimpleTransactionTypeEnum.TYPE_BUY
        elif transaction_type_string == 'STOCK_SPLIT_MERGE_INSERTION':
            return SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_INSERTION
        elif transaction_type_string == 'STOCK_SPLIT_MERGE_DELETION':
            return SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_DELETION
        elif transaction_type_string == 'OTHER':
            return SimpleTransaction.SimpleTransactionTypeEnum.TYPE_OTHER
