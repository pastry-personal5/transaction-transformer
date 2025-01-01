import datetime
from enum import Enum


class SimpleTransaction():

    CORE_FIELD_LENGTH = 7  # The length of items - account, amount, open_date, etc.
    NUMBER_OF_TYPES = 6  # Number of types. It includes the type 'other.'

    class SimpleTransactionTypeEnum(Enum):
        # Constants
        TYPE_OTHER = 0
        TYPE_SELL = 1
        TYPE_BUY = 2
        TYPE_STOCK_SPLIT_MERGE_INSERTION = 3
        TYPE_STOCK_SPLIT_MERGE_DELETION = 4
        TYPE_INBOUND_TRANSFER_RESULTED_FROM_EVENT = 5

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
        array_of_transaction_type = [self.SimpleTransactionTypeEnum.TYPE_SELL,
                                     self.SimpleTransactionTypeEnum.TYPE_BUY,
                                     self.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_INSERTION,
                                     self.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_DELETION,
                                     self.SimpleTransactionTypeEnum.TYPE_INBOUND_TRANSFER_RESULTED_FROM_EVENT,
                                     ]
        array_of_transaction_type_string = [
            'SELL',
            'BUY',
            'STOCK_SPLIT_MERGE_INSERTION',
            'STOCK_SPLIT_MERGE_DELETION',
            'INBOUND_TRANSFER_RESULTED_FROM_EVENT',
        ]
        assert SimpleTransaction.NUMBER_OF_TYPES - 1 == len(array_of_transaction_type)
        assert len(array_of_transaction_type) == len(array_of_transaction_type_string)

        try:
            targetIndex = array_of_transaction_type.index(self.transaction_type)
            type_as_string = array_of_transaction_type_string[targetIndex]
        except ValueError:
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
        elif transaction_type_string == 'INBOUND_TRANSFER_RESULTED_FROM_EVENT':
            return SimpleTransaction.SimpleTransactionTypeEnum.TYPE_INBOUND_TRANSFER_RESULTED_FROM_EVENT
        elif transaction_type_string == 'OTHER':
            return SimpleTransaction.SimpleTransactionTypeEnum.TYPE_OTHER
