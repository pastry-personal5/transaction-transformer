#!/usr/bin/env python
import datetime
import pprint

from loguru import logger
from pandas import DataFrame
import pandas

from db_connection import DBConnection
from db_impl_base import DBImplBase


class ExpenseTransaction():

    def __init__(self):
        self.datetime = None  # datetime.datetime
        self.type = None
        self.category0 = None
        self.memo0 = None
        self.memo1 = None
        self.amount = 0
        self.currency = None
        self.source_account = None
        self.target_account = None


class BankSaladExpenseTransaction():

    def __init__(self):
        self.date = None  # datetime.date
        self.time = None  # datetime.time
        self.type = None
        self.category0 = None
        self.category1 = None
        self.memo0 = None
        self.amount = 0
        self.currency = None
        self.account = None
        self.memo1 = None


class BankSaladExpenseTransactionDBImpl(DBImplBase):

    def __init__(self, db_connection):
        super().__init__(db_connection)
        self.table_name = 'bank_salad_expense_transactions'
        self.core_table_definition = [
            ('datetime', 'DATETIME', ''),
            ('type', 'VARCHAR(128)', ''),
            ('category0', 'VARCHAR(128)', ''),
            ('category1', 'VARCHAR(128)', ''),
            ('memo0', 'VARCHAR(128)', ''),
            ('amount', 'int', ''),
            ('currency', 'VARCHAR(128)', ''),
            ('account', 'VARCHAR(128)', ''),
            ('memo1', 'VARCHAR(128)', '')
        ]

    def _get_sql_string_for_table_creation(self):
        sql_string = ''
        sql_string += 'CREATE TABLE IF NOT EXISTS'
        sql_string += ' '
        sql_string += self.table_name
        sql_string += ' '
        sql_string += '(\n'
        sql_string += 'transaction_id int auto_increment, \n'
        for t in self.core_table_definition:
            sql_string += ' '.join(t(0), t(1), t(2)) + ',\n'
        sql_string += 'primary key(transaction_id)\n'
        sql_string += ')\n'
        return sql_string

    def create_table(self) -> bool:
        sql_string = self._get_sql_string_for_table_creation()
        try:
            self.cur.execute(sql_string)
        except mariadb.Error as e:
            self.handle_general_sql_execution_error(e, sql_string)
            return False
        return True


class BankSaladExpenseTransactionImporter():

    def __init__(self):
        pass

    def import_from_file(self, input_file_path: str) -> list[BankSaladExpenseTransaction]:
        logger.info(f'Try to import from a file path ({input_file_path})...')
        try:
            fp = open(input_file_path, 'rb')
            # One is going to pass it as an integer also as an index 0(0-indexed).
            # That means the second sheet.
            # Its original name MAY be '가계부 내역' in Korean.
            const_sheet_name = 1
            # Read an Excel file into a pandas DataFrame.
            # Also, read the row 0(0-indexed) to use for the column labels of the parsed DataFrame.
            df = pandas.read_excel(fp, sheet_name=const_sheet_name)
            logger.info(pprint.pformat(df.info()))
            fp.close()
        except IOError as e:
            logger.error('An IO error has been occurred.')
            logger.error(e)
            return None
        return self._bulid_expense_transaction(df)

    def _bulid_expense_transaction(self, df: DataFrame) -> list[BankSaladExpenseTransaction]:
        list_of_expense_transaction = []
        for row in df.itertuples(index=True, name=None):
            t = BankSaladExpenseTransaction()
            t.date = row[1].date()
            t.time = row[2]
            t.type = row[3]
            t.category0 = row[4]
            t.category1 = row[5]
            t.memo0 = row[6]
            t.amount = row[7]
            t.currency = row[8]
            t.account = row[9]
            t.memo1 = row[10]
            list_of_expense_transaction.append(t)

        return list_of_expense_transaction


class BankSaladExpenseTransactionControl():

    def __init__(self, db_connection: DBConnection):
        self.bank_salad_expense_transaction_importer = BankSaladExpenseTransactionImporter()
        self.bank_salad_expense_transaction_db_impl = BankSaladExpenseTransactionDBImpl(db_connection)

    def import_and_insert_from_file(self, input_file_path: str) -> bool:
        list_of_bank_salad_expense_transaction = self.bank_salad_expense_transaction_importer.import_from_file(input_file_path)
        if not list_of_bank_salad_expense_transaction:
            return False
        if not self.bank_salad_expense_transaction_db_impl.create_table():
            return False
        # @TODO(dennis.oh) insert records...


def main():
    # @TODO(dennis.oh) Remove main.
    input_file_path = './data/2024-11-14.xlsx'
    i = BankSaladExpenseTransactionImporter()
    list_of_expense_transaction = i.import_from_file(input_file_path)


if __name__ == '__main__':
    main()
