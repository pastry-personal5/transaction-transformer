import datetime

from loguru import logger
import mariadb


from tt.db_connection import DBConnection
from tt.db_impl_base import DBImplBase
from tt.simple_transaction import SimpleTransaction


class SimpleTransactionDBImpl(DBImplBase):

    class SimpleTransactionFilter():

        def __init__(self):
            self.flag_filter_by = {}
            self.flag_filter_by['account'] = False
            self.flag_filter_by['amount'] = False
            self.flag_filter_by['commission'] = False
            self.flag_filter_by['open_date'] = False
            self.flag_filter_by['open_price'] = False
            self.flag_filter_by['symbol'] = False
            self.flag_filter_by['transaction_type'] = False

            assert len(self.flag_filter_by) == SimpleTransaction.CORE_FIELD_LENGTH

            self.flag_sql_escaping_needed = {}
            self.flag_sql_escaping_needed['account'] = True
            self.flag_sql_escaping_needed['amount'] = True
            self.flag_sql_escaping_needed['commission'] = True
            self.flag_sql_escaping_needed['open_date'] = True
            self.flag_sql_escaping_needed['open_price'] = True
            self.flag_sql_escaping_needed['symbol'] = True
            self.flag_sql_escaping_needed['transaction_type'] = True

            self.value_dict = {}

            assert len(self.flag_sql_escaping_needed) == SimpleTransaction.CORE_FIELD_LENGTH

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def get_all_records(self) -> list[SimpleTransaction]:
        list_of_simple_transaction_records = []
        cur = self.db_connection.cur()
        sql_string = 'USE finance'
        cur.execute(sql_string)
        sql_string = 'SELECT amount, commission, open_date, open_price, symbol, transaction_type FROM simple_transactions'
        cur.execute(sql_string)
        for (amount, commission, open_date, open_price, symbol, transaction_type_as_str) in cur:
            transaction_type = SimpleTransaction.get_transaction_type_from_string(transaction_type_as_str)
            t = SimpleTransaction(symbol, transaction_type, amount, open_price, open_date, commission)
            list_of_simple_transaction_records.append(t)

        return list_of_simple_transaction_records

    def get_records_with_filter(self, simple_transaction_filter: SimpleTransactionFilter) -> list[SimpleTransaction]:
        where_clause_str = self._get_where_clause(simple_transaction_filter)
        list_of_simple_transaction_records = []
        cur = self.db_connection.cur()
        sql_string = 'USE finance'
        cur.execute(sql_string)
        sql_string = 'SELECT amount, commission, open_date, open_price, symbol, transaction_type FROM simple_transactions'
        if len(where_clause_str) > 0:
            sql_string += ' ' + where_clause_str
        cur.execute(sql_string)
        for (amount, commission, open_date, open_price, symbol, transaction_type_as_str) in cur:
            transaction_type = SimpleTransaction.get_transaction_type_from_string(transaction_type_as_str)
            t = SimpleTransaction(symbol, transaction_type, amount, open_price, open_date, commission)
            list_of_simple_transaction_records.append(t)

        return list_of_simple_transaction_records

    def _get_where_clause(self, simple_transaction_filter: SimpleTransactionFilter) -> str:
        flag_is_there_any_true_flag = False
        len_filters = 0
        for key, value in simple_transaction_filter.flag_filter_by.items():
            if value is True:
                flag_is_there_any_true_flag = True
                len_filters += 1

        if not flag_is_there_any_true_flag:
            return ''

        str_to_return = 'WHERE'
        index = 0
        for key, value in simple_transaction_filter.flag_filter_by.items():
            if value is True:
                str_to_return += ' '
                str_to_return += key
                str_to_return += '='
                value_given = simple_transaction_filter.value_dict[key]
                if simple_transaction_filter.flag_sql_escaping_needed[key] is True:
                    str_to_return += self.escape_sql_string(value_given)
                else:
                    str_to_return += value_given
                if index != len_filters - 1:
                    str_to_return += ' AND'
                index += 1
        return str_to_return

    def delete_all_records_from_simple_transactions_table(self):
        cur = self.db_connection.cur()
        try:
            sql_string = 'DELETE FROM simple_transactions;'
            cur.execute(sql_string)
        except mariadb.Error as e:
            self.handle_general_sql_execution_error(e, sql_string)

    def export_all(self, list_of_simple_transactions):

        cur = self.db_connection.cur()

        try:
            sql_string = 'CREATE DATABASE IF NOT EXISTS finance;'
            cur.execute(sql_string)
            sql_string = 'USE finance;'
            cur.execute(sql_string)
            sql_string = 'CREATE TABLE IF NOT EXISTS simple_transactions(\n' \
                'transaction_id int auto_increment,\n' \
                'amount float,\n' \
                'commission float,\n' \
                'open_date date,\n' \
                'open_price float,\n' \
                'symbol varchar(512) not null,\n' \
                'transaction_type varchar(512) not null,\n' \
                'primary key(transaction_id)\n' \
                ');\n'
            cur.execute(sql_string)
        except mariadb.Error as e:
            self.handle_general_sql_execution_error(e, sql_string)

        self.delete_all_records_from_simple_transactions_table()

        for transaction in list_of_simple_transactions:
            try:
                open_date = self.escape_sql_string(transaction.open_date.strftime('%Y-%m-%d'))
                symbol = self.escape_sql_string(transaction.symbol)
                transaction_type = self.escape_sql_string(transaction.get_transaction_type_string())
                sql_string = f'INSERT INTO simple_transactions \n' \
                    f'(amount, commission, open_date, open_price, symbol, transaction_type) \n' \
                    f'VALUES \n' \
                    f'({transaction.amount}, {transaction.commission}, {open_date}, {transaction.open_price}, {symbol}, {transaction_type}) \n'
                cur.execute(sql_string)
            except mariadb.Error as e:
                self.handle_general_sql_execution_error(e, sql_string)
