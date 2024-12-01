import datetime
import sys

from loguru import logger
import mariadb

from tt.db_connection import DBConnection

class DBImplBase():

    def __init__(self, db_connection: DBConnection):
        self.const_default_table_charset = 'utf8mb4'
        self.db_connection = db_connection

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

    def convert_datetime_to_sql_string(self, dt: datetime) -> str:
        """Convert a Python datetime object to an SQL string for insertion.

        Args:
            dt (datetime): The datetime object to convert.

        Returns:
            str: Formatted SQL datetime string or 'NULL' if input is None.
        """
        if dt is None:
            return 'NULL'

        return f'\'{dt.strftime('%Y-%m-%d %H:%M:%S')}\''
