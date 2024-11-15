"""
This module exports transactions to a mariaDB instance.
"""
import sys

from loguru import logger

import mariadb


class SimpleMariaDBExporter():

    global_configuration = None
    conn = None

    def __init__(self, global_configuration):
        self.global_configuration = global_configuration

    def connect(self):
        assert self.global_configuration is not None
        host = self.global_configuration['mariadb_exporter']['host']
        port = self.global_configuration['mariadb_exporter']['port']  # Integer
        user = self.global_configuration['mariadb_exporter']['user']
        password = self.global_configuration['mariadb_exporter']['password']
        try:
            self.conn = mariadb.connect(
                host=host,
                port=port,
                user=user,
                password=password
            )
            self.conn.autocommit = True
        except mariadb.Error as e:
            logger.error(f'Error connecting to the database: {e}')
            sys.exit(-1)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()
        self.conn = None

    def get_cursor(self):
        assert self.conn is not None
        return self.conn.cursor()

    def handle_general_sql_execution_error(self, exception_object, sql_string):
        logger.error(f'Error executing the SQL. Error was: {exception_object}')
        logger.error(f'Error executing the SQL. SQL was: {sql_string}')
        sys.exit(1)

    def delete_all_records_from_simple_transactions_table(self, cur):
        try:
            sql_string = 'DELETE FROM simple_transactions'
            cur.execute(sql_string)
        except mariadb.Error as e:
            self.handle_general_sql_execution_error(e, sql_string)

    def get_sql_value_string(self, src):
        return f'\'{src}\''

    def export_all(self, list_of_simple_transactions):

        self.connect()
        cur = self.get_cursor()

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

        self.delete_all_records_from_simple_transactions_table(cur)

        for transaction in list_of_simple_transactions:
            try:
                open_date = self.get_sql_value_string(transaction.open_date)
                symbol = self.get_sql_value_string(transaction.symbol)
                transaction_type = self.get_sql_value_string(transaction.get_transaction_type_string())
                sql_string = f'INSERT INTO simple_transactions \n' \
                    f'(amount, commission, open_date, open_price, symbol, transaction_type) \n' \
                    f'VALUES \n' \
                    f'({transaction.amount}, {transaction.commission}, {open_date}, {transaction.open_price}, {symbol}, {transaction_type}) \n'
                cur.execute(sql_string)
            except mariadb.Error as e:
                self.handle_general_sql_execution_error(e, sql_string)

        self.commit()
        self.close()
