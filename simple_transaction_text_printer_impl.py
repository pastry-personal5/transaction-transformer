from simple_transaction import SimpleTransaction
from text_printer_impl_base import TextPrinterImplBase

class SimpleTransactionTextPrinterImpl(TextPrinterImplBase):

    def __init__(self):
        pass

    def print_all(self, list_of_simple_transaction: list[SimpleTransaction]) -> None:
        for t in list_of_simple_transaction:
            print(t)
