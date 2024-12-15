import sys
from urllib.parse import quote

from loguru import logger
import sqlalchemy
from sqlalchemy.engine.url import URL

import mariadb


class DBConnection():

    def __init__(self, global_config_ir):
        self.alchemy_conn = None
        self.conn = None
        self.database_name = 'finance'
        self.engine = None  # An SQLAlchemy engine.
        self.global_config_ir = global_config_ir

    def do_initial_setup(self):
        self.connect()
        self.use_database()

    def connect(self):
        assert self.global_config_ir is not None
        host = self.global_config_ir['mariadb']['host']
        port = self.global_config_ir['mariadb']['port']  # Integer
        user = self.global_config_ir['mariadb']['user']
        password = self.global_config_ir['mariadb']['password']
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
        encoded_password = quote(password)
        connection_string = f'mariadb+mariadbconnector://{user}:{encoded_password}@{host}:{port}/{self.database_name}'
        self.engine = sqlalchemy.create_engine(connection_string, echo=True)
        self.alchemy_conn = self.engine.connect()

    def use_database(self):
        database_name = self.database_name
        cur = self.cur()
        sql_string = 'USE' + ' ' + database_name
        try:
            cur.execute(sql_string)
        except mariadb.Error as e:
            logger.error(f'Error: {e}')
            sys.exit(-1)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()
        self.conn = None

    def cur(self):
        assert self.conn is not None
        return self.conn.cursor()
