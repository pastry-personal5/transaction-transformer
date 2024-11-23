import datetime

from loguru import logger
import mariadb

from db_connection import DBConnection
from simple_transaction import SimpleTransaction


class SimpleTransactionDBImpl():

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

    def __init__(self):
        pass

    def get_all_records(self, db_connection: DBConnection) -> list[SimpleTransaction]:
        list_of_simple_transaction_records = []
        cur = db_connection.get_cursor()
        sql_string = 'USE finance'
        cur.execute(sql_string)
        sql_string = 'SELECT amount, commission, open_date, open_price, symbol, transaction_type FROM simple_transactions'
        cur.execute(sql_string)
        for (amount, commission, open_date, open_price, symbol, transaction_type_as_str) in cur:
            transaction_type = SimpleTransaction.get_transaction_type_from_string(transaction_type_as_str)
            t = SimpleTransaction(symbol, transaction_type, amount, open_price, open_date, commission)
            list_of_simple_transaction_records.append(t)

        return list_of_simple_transaction_records

    def get_records_with_filter(self, db_connection: DBConnection, simple_transaction_filter: SimpleTransactionFilter) -> list[SimpleTransaction]:
        where_clause_str = self._get_where_clause(simple_transaction_filter)
        list_of_simple_transaction_records = []
        cur = db_connection.get_cursor()
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
                    str_to_return += self._escape_sql_string(value_given)
                else:
                    str_to_return += value_given
                if index != len_filters - 1:
                    str_to_return += ' AND'
                index += 1
        return str_to_return

    def _escape_sql_string(self, value: str) -> str:
        """
        Escapes special characters in a string for safe use in an SQL query for MariaDB.
        * @author: chatgpt-4.

        Args:
            value (str): The string to escape.

        Returns:
            str: The escaped string, safe for inclusion in SQL.
        """
        if value is None:
            return 'NULL'

        # Replace special characters with escaped versions
        escaped_value = (
            value.replace('\\', '\\\\').replace('\'', '\\\'').replace('"', '\\"').replace('\0', '\\0')
        )

        # Wrap in quotes for SQL compatibility
        return f'\'{escaped_value}\''
