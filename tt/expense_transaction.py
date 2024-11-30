#!/usr/bin/env python
import datetime
import pprint

from loguru import logger
import mariadb
from pandas import DataFrame
import pandas
import yaml

from tt.db_connection import DBConnection
from tt.db_impl_base import DBImplBase


class ExpenseTransaction():

    def __init__(self):
        self.amount = 0
        self.category0 = None
        self.category1 = None
        self.currency = None
        self.memo0 = None
        self.memo1 = None
        self.source_account = None
        self.target_account = None
        self.transaction_datetime = None  # datetime.datetime

    def __str__(self):
        return f'datetime({self.transaction_datetime}) category0({self.category0}) category1({self.category1}) memo0({self.memo0}) memo1({self.memo1}) amount({self.amount}) currency({self.currency}) source_account({self.source_account}) target_account({self.target_account})'

    def __eq__(self, other):
        if isinstance(other, ExpenseTransaction):
            return self.amount == other.amount \
                and self.category0 == other.category0 \
                and self.category1 == other.category1 \
                and self.currency == other.currency \
                and self.memo0 == other.memo0 \
                and self.memo1 == other.memo1 \
                and self.source_account == other.source_account \
                and self.target_account == other.target_account \
                and self.transaction_datetime == other.transaction_datetime
        return False

    def __hash__(self):
        return hash((self.amount, \
            self.category0, \
            self.category1, \
            self.currency, \
            self.memo0, \
            self.memo1, \
            self.source_account, \
            self.target_account, \
            self.transaction_datetime))


class BankSaladExpenseTransaction():

    def __init__(self):
        self.account = None
        self.amount = 0
        self.category0 = None
        self.category1 = None
        self.currency = None
        self.date = None  # datetime.date
        self.time = None  # datetime.time
        self.type = None
        self.memo0 = None
        self.memo1 = None

    def __str__(self):
        return f'date({self.date}) time({self.time}) type({self.type}) category0({self.category0}) category1({self.category1}) memo0({self.memo0}) amount({self.amount}) currency({self.currency}) account({self.account}) memo1({self.memo1})'


class ExpenseTransactionDBImpl(DBImplBase):

    def __init__(self, db_connection):
        super().__init__(db_connection)
        self.table_name = 'expense_transactions'
        self.core_table_definition = [
            ('transaction_datetime', 'DATETIME', ''),
            ('category0', 'VARCHAR(128)', ''),
            ('category1', 'VARCHAR(128)', ''),
            ('memo0', 'VARCHAR(256)', ''),
            ('amount', 'int', ''),
            ('currency', 'VARCHAR(128)', ''),
            ('source_account', 'VARCHAR(128)', ''),
            ('target_account', 'VARCHAR(128)', ''),
            ('memo1', 'VARCHAR(256)', '')
        ]

    def _get_sql_string_for_table_creation(self):
        sql_string = ''
        sql_string += 'CREATE TABLE IF NOT EXISTS'
        sql_string += ' '
        sql_string += self.table_name
        sql_string += ' '
        sql_string += '(\n'
        sql_string += 'id bigint auto_increment, \n'
        for t in self.core_table_definition:
            sql_string += ' '.join(t) + ',\n'
        sql_string += 'primary key(id)\n'
        sql_string += ')\n'
        sql_string += 'CHARACTER SET \'utf8\';'
        return sql_string

    def _get_sql_string_for_table_deletion(self):
        sql_string = 'DROP TABLE ' + self.table_name + ';'
        return sql_string

    def create_table(self) -> bool:
        sql_string = self._get_sql_string_for_table_creation()
        try:
            cur = self.db_connection.cur()
            cur.execute(sql_string)
        except mariadb.Error as e:
            self.handle_general_sql_execution_error(e, sql_string)
            return False
        return True

    def drop_table(self) -> bool:
        sql_string = self._get_sql_string_for_table_deletion()
        try:
            cur = self.db_connection.cur()
            cur.execute(sql_string)
        except mariadb.Error as e:
            self.handle_general_sql_execution_error(e, sql_string)
            return False
        return True

    def _get_sql_string_for_record_insertion(self, t):
        values = {}
        values['transaction_datetime'] = self.convert_datetime_to_sql_string(t.transaction_datetime)
        values['category0'] = self.escape_sql_string(t.category0)
        values['category1'] = self.escape_sql_string(t.category1)
        values['memo0'] = self.escape_sql_string(t.memo0)
        values['amount'] = t.amount
        values['currency'] = self.escape_sql_string(t.currency)
        values['source_account'] = self.escape_sql_string(t.source_account)
        values['target_account'] = self.escape_sql_string(t.target_account)
        values['memo1'] = self.escape_sql_string(t.memo1)
        sql_string = f'INSERT INTO {self.table_name}'
        sql_string += ' (transaction_datetime, category0, category1, memo0, amount, currency, source_account, target_account, memo1) VALUES ('
        sql_string += f' {values['transaction_datetime']},'
        sql_string += f' {values['category0']},'
        sql_string += f' {values['category1']},'
        sql_string += f' {values['memo0']},'
        sql_string += f' {values['amount']},'
        sql_string += f' {values['currency']},'
        sql_string += f' {values['source_account']},'
        sql_string += f' {values['target_account']},'
        sql_string += f' {values['memo1']}'
        sql_string += ');'
        return sql_string

    def insert_records(self, list_of_transaction: list[ExpenseTransaction]) -> bool:
        cur = self.db_connection.cur()
        for t in list_of_transaction:
            sql_string = self._get_sql_string_for_record_insertion(t)
            try:
                cur.execute(sql_string)
            except mariadb.Error as e:
                self.handle_general_sql_execution_error(e, sql_string)
                return False
        return True

    def get_all(self) -> list[ExpenseTransaction]:
        cur = self.db_connection.cur()
        sql_string = 'SELECT transaction_datetime, category0, category1, memo0, amount, currency, source_account, target_account, memo1 FROM'
        sql_string += ' ' + self.table_name + ';'
        list_of_transaction = []
        try:
            cur.execute(sql_string)
            for (transaction_datetime, category0, category1, memo0, amount, currency, source_account, target_account, memo1) in cur:
                t = ExpenseTransaction()
                t.transaction_datetime = transaction_datetime
                t.category0 = category0
                t.category1 = category1
                t.memo0 = memo0
                t.amount = amount
                t.currency = currency
                t.source_account = source_account
                t.target_account = target_account
                t.memo1 = memo1
                list_of_transaction.append(t)
        except mariadb.Error as e:
            self.handle_general_sql_execution_error(e, sql_string)
            return None
        return list_of_transaction


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
            # 1-indexed. not 0-indexed.
            t.date = row[1].date()
            t.time = row[2]
            t.type = row[3]
            t.category0 = row[4]
            t.category1 = row[5]
            t.memo0 = row[6]
            t.amount = row[7]
            t.currency = row[8]
            t.account = row[9]
            if pandas.isna(row[10]):
                t.memo1 = None
            else:
                t.memo1 = row[10]
            list_of_expense_transaction.append(t)

        return list_of_expense_transaction


class ExpenseTransactionControl():

    def __init__(self, db_connection: DBConnection):
        self.importer = BankSaladExpenseTransactionImporter()
        self.db_impl = ExpenseTransactionDBImpl(db_connection)
        self.conversion_rule = self._load_conversion_rule()

    def import_and_append_from_file(self, input_file_path: str) -> bool:
        list_of_bank_salad_expense_transaction = self.importer.import_from_file(input_file_path)
        if not list_of_bank_salad_expense_transaction:
            return False

        # Convert
        list_of_expense_transaction = self._convert(list_of_bank_salad_expense_transaction, self.conversion_rule)
        if not list_of_expense_transaction:
            return False

        # Create a table if needed. Insert records.
        if not self.db_impl.create_table():
            return False
        list_of_expense_transaction_to_be_appended = self._get_list_of_expense_transaction_to_be_appended(list_of_expense_transaction)
        if not self.db_impl.insert_records(list_of_expense_transaction_to_be_appended):
            return False
        return True

    def _get_list_of_expense_transaction_to_be_appended(self, source_list: list[ExpenseTransaction]) -> list[ExpenseTransaction]:
        target_list = self.db_impl.get_all()
        len_target = len(target_list)
        len_source = len(source_list)
        logger.info(f'The length of target_list is ({len_target})')
        logger.info(f'The length of source_list is ({len_source})')
        set_target = set(target_list)
        set_source = set(source_list)
        # Find element in set_source that are not in set_target
        difference_set = set_source - set_target
        list_to_return = list(difference_set)
        len_of_list_to_return = len(list_to_return)
        logger.info(f'The length of list_to_return is ({len_of_list_to_return})')
        return list_to_return

    def delete(self) -> bool:
        return self.db_impl.drop_table()

    def _load_conversion_rule(self):
        conversion_rule_file_path = './config/conversion_rule.yaml'
        try:
            fp = open(conversion_rule_file_path, 'rb')
            conversion_rule = yaml.safe_load(fp)
            fp.close()
            return conversion_rule
        except IOError as e:
            logger.error('An IO error has been occurred.')
            logger.error(e)
            return None

    def _convert(self, source: list[BankSaladExpenseTransaction], conversion_rule: dict) -> list[ExpenseTransaction]:
        list_of_expense_transaction = []
        for item in source:
            t = ExpenseTransaction()
            t.transaction_datetime = datetime.datetime(year=item.date.year, month=item.date.month, day=item.date.day) \
                + datetime.timedelta(hours=item.time.hour, minutes=item.time.minute, seconds=item.time.second)  # Python datetime.datetime
            t.category0 = self._get_category(conversion_rule, item.category0, item.category1, item.memo0, item.account, item.memo1)
            t.category1 = None  # For future use.
            t.amount = item.amount
            t.currency = item.currency
            t.source_account = item.account
            t.target_account = None
            t.memo0 = item.memo0
            t.memo1 = item.memo1

            list_of_expense_transaction.append(t)

        return list_of_expense_transaction

    def _get_category(self, conversion_rule: dict, src_category0, src_category1, src_memo0, src_account, src_memo1) -> str:
        const_default_category = '카테고리 없음'
        flag_found = False
        for rule in conversion_rule['rules']:
            if (not rule['source']['category0'] or rule['source']['category0'] and rule['source']['category0'] == src_category0) and \
                (not rule['source']['category1'] or rule['source']['category1'] and rule['source']['category1'] == src_category1) and \
                (not rule['source']['memo0'] or rule['source']['memo0'] and rule['source']['memo0'] == src_category1) and \
                (not rule['source']['account'] or rule['source']['account'] and rule['source']['account'] == src_category1) and \
                (not rule['source']['memo1'] or rule['source']['memo1'] and rule['source']['memo1'] == src_category1):
                target_category0 = rule['target']['category0']
                flag_found = True
                break
        if flag_found:
            return target_category0
        return const_default_category
