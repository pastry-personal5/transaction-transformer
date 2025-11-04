from loguru import logger
import mariadb

class BootstrapControl:

    def __init__(self):
        pass

    def bootstrap(sel, db_connection) -> None:
        database_name = db_connection.database_name
        cursor = db_connection.conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        db_connection.conn.commit()
        cursor.close()
