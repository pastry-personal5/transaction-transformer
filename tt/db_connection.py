import sys

from loguru import logger

import mariadb


class DBConnection():

    def __init__(self, global_config_ir):
        self.conn = None
        self.global_config_ir = global_config_ir

    def connect(self):
        assert self.global_config_ir is not None
        host = self.global_config_ir['mariadb_exporter']['host']
        port = self.global_config_ir['mariadb_exporter']['port']  # Integer
        user = self.global_config_ir['mariadb_exporter']['user']
        password = self.global_config_ir['mariadb_exporter']['password']
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
