from tt.db_connection import DBConnection
from tt.stock_split import StockSplitControl


class FactDataControl:

    def __init__(self, db_connection: DBConnection):
        self.stock_split_control = StockSplitControl(db_connection)

    def bootstrap(self):
        self.stock_split_control.bootstrap()
