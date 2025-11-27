#!/usr/bin/env python

import os

from loguru import logger
import pandas
import sqlalchemy
from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base

from tt.db_connection import DBConnection
from tt.db_impl_base import DBImplBase


Base = declarative_base()  # An sqlalchemy's base class.


class StockSplit(Base):

    __tablename__ = "stock_splits"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
    }
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    denominator = sqlalchemy.Column(sqlalchemy.Integer)
    event_date = sqlalchemy.Column(sqlalchemy.Date)  # Local time for each region
    numerator = sqlalchemy.Column(sqlalchemy.Integer)
    symbol = sqlalchemy.Column(sqlalchemy.String(128))
    symbol_namespace = sqlalchemy.Column(sqlalchemy.String(128))

    CORE_FIELD_LENGTH = 5  # The length of items - event_date, symbol, etc.

    def __init__(self):
        self.denominator = 0
        self.event_date = None
        self.numerator = 0
        self.symbol = None
        self.symbol_namespace = None

    def __str__(self):
        return f"event_date({self.event_date}) symbol({self.symbol}) numerator({self.numerator}) denominator({self.denominator}) symbol_namespace({self.symbol_namespace})"

    def __eq__(self, other):
        """
        `__eq__` tests equality.
        # @Warning Please note that `__eq__` function is customized one. Several are ignored, intentionally.
        """
        if isinstance(other, StockSplit):
            return (
                self.event_date == other.event_date
                and self.symbol == other.symbol
                and self.denominator == other.denominator
                and self.numerator == other.numerator
                and self.symbol_namespace == other.symbol_namespace
            )
        return False

    def __hash__(self):
        """
        `__hash__` returns a unique hash of an object.
        @Warning Please note that `__eq__` function is customized one. Several fields are ignored, intentionally.
        """
        return hash(
            (
                self.event_date,
                self.symbol,
                self.denominator,
                self.numerator,
                self.symbol_namespace,
            )
        )


class StockSplitDBImpl(DBImplBase):

    def __init__(self, db_connection):
        super().__init__(db_connection)

    def create_table(self) -> bool:
        if self._is_table_in_database(StockSplit.__tablename__):
            return False
        StockSplit.__table__.create(self.db_connection.engine)
        return True

    def drop_table(self) -> bool:
        if not self._is_table_in_database(StockSplit.__tablename__):
            return False
        StockSplit.__table__.drop(self.db_connection.engine)
        return True

    def insert_records(self, list_of_stock_split: list[StockSplit]) -> bool:
        session = self._get_session()
        try:
            session.add_all(list_of_stock_split)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error during record insertion: {e}")
            return False
        finally:
            # The finally block still executes before the function actually returns.
            # The finally block still executes, even if return is called inside the except.
            session.close()

    def get_all_filtered_by_symbol_and_symbol_namespace(
        self, symbol: str, symbol_namespace
    ) -> list[StockSplit]:
        try:
            with self._get_session() as session:
                return (
                    session.query(StockSplit)
                    .filter(StockSplit.symbol == symbol)
                    .filter(StockSplit.symbol_namespace == symbol_namespace)
                    .order_by(asc(StockSplit.event_date))
                    .all()
                )
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching records: {e}")
            return []

    def get_all(self) -> list[StockSplit]:
        try:
            with self._get_session() as session:
                return session.query(StockSplit).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching records: {e}")
            return []


class StockSplitImporter:

    def __init__(self):
        pass

    def import_from_file(self, input_file_path: str) -> list[StockSplit]:
        logger.info(f"Try to import from a file path ({input_file_path})...")
        try:
            fp = open(input_file_path, "rb")
            # One is going to pass it as an integer also as an index 0(0-indexed).
            # That means the first sheet.
            const_sheet_name = 0
            # Read an Excel file into a pandas DataFrame.
            # Also, read the row 0(0-indexed) to use for the column labels of the parsed DataFrame.
            df = pandas.read_excel(fp, sheet_name=const_sheet_name)
            fp.close()
        except IOError as e:
            logger.error("An IO error has been occurred.")
            logger.error(e)
            return []
        return self._build_stock_split(df)

    def _build_stock_split(self, df: pandas.DataFrame) -> list[StockSplit]:
        list_of_stock_split = []
        for row in df.itertuples(index=True, name=None):
            t = StockSplit()
            # 1-indexed. not 0-indexed.
            symbol_namespace = row[1]
            symbol = row[2]
            event_date = row[3].date()
            numerator = int(row[4])
            denominator = int(row[5])

            t.symbol_namespace = symbol_namespace
            t.symbol = symbol
            t.event_date = event_date
            t.numerator = numerator
            t.denominator = denominator

            list_of_stock_split.append(t)

        logger.info(
            f"The length of list_of_expense_transaction is ({len(list_of_stock_split)})."
        )
        return list_of_stock_split


class StockSplitControl:

    def __init__(self, db_connection: DBConnection):
        self.db_impl = StockSplitDBImpl(db_connection)
        self.importer = StockSplitImporter()

    def _get_list_to_be_appended(
        self, target_list: list[StockSplit], source_list: list[StockSplit]
    ) -> list[StockSplit]:
        """
        Here,
        `target_list` is a list which was read from a DB;
        `source_list` is a list which was read from a file.
        """
        len_target = len(target_list)
        len_source = len(source_list)
        logger.info(f"The length of target_list is ({len_target})")
        logger.info(f"The length of source_list is ({len_source})")
        set_target = set(target_list)
        set_source = set(source_list)
        # Find element in set_source that are not in set_target
        difference_set = set_source - set_target
        list_to_return = list(difference_set)
        len_of_list_to_return = len(list_to_return)
        logger.info(f"The length of list_to_return is ({len_of_list_to_return})")
        return list_to_return

    def bootstrap(self):
        """
        This method makes sure that stock split data is in the database.
        """
        from tt.constants import Constants
        stock_splits_data_file_path = os.path.join(Constants.input_data_dir_path, "stock_splits.xlsx")
        # Create a table if needed. When `create_table` returns `False`, ignore it.
        result = self.db_impl.create_table()
        if result:
            logger.info("A table about stock splits has been created.")
        list_read_from_db = self.db_impl.get_all()
        list_imported = self.importer.import_from_file(
            stock_splits_data_file_path
        )
        list_to_be_appended = self._get_list_to_be_appended(
            list_read_from_db, list_imported
        )
        # Ignore the return value.
        self.db_impl.insert_records(list_to_be_appended)

    def get_all_filtered_by_symbol_and_symbol_namespace(
        self, symbol: str, symbol_namespace
    ) -> list[StockSplit]:
        return self.db_impl.get_all_filtered_by_symbol_and_symbol_namespace(
            symbol, symbol_namespace
        )
