import sys

from loguru import logger

import mariadb

class DBImplBase():

    def __init__(self, conn, cur):
        self.conn = conn
        self.cur = cur

    def handle_general_sql_execution_error(self, exception_object, sql_string):
        logger.error(f'Error executing the SQL. Error was: {exception_object}')
        logger.error(f'Error executing the SQL. SQL was: {sql_string}')
        sys.exit(1)

    def escape_sql_string(self, value: str) -> str:
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
