#!/usr/bin/env python
import datetime

from loguru import logger
import mariadb
from pandas import DataFrame
import pandas
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import yaml

from tt.db_connection import DBConnection
from tt.db_impl_base import DBImplBase

Base = declarative_base()  # An sqlalchemy's base class.


class BankSaladExpenseTransaction(Base):

    __tablename__ = 'bank_salad_expense_transactions'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
    }
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    account = sqlalchemy.Column(sqlalchemy.String(128))
    amount = sqlalchemy.Column(sqlalchemy.Integer)
    category0 = sqlalchemy.Column(sqlalchemy.String(128))
    category1 = sqlalchemy.Column(sqlalchemy.String(128))
    currency = sqlalchemy.Column(sqlalchemy.String(128))
    transaction_datetime = sqlalchemy.Column(sqlalchemy.DateTime)  # KST
    type = sqlalchemy.Column(sqlalchemy.String(128))
    memo0 = sqlalchemy.Column(sqlalchemy.String(128))
    memo1 = sqlalchemy.Column(sqlalchemy.String(128))
    user_identifier = sqlalchemy.Column(sqlalchemy.String(128))
    imported_at = sqlalchemy.Column(sqlalchemy.DateTime)  # UTC

    CORE_FIELD_LENGTH = 11  # The length of items - account, amount, etc.

    def __init__(self):
        self.account = None
        self.amount = 0
        self.category0 = None
        self.category1 = None
        self.currency = None
        self.transaction_datetime = None  # Python datetime.datetime
        self.type = None
        self.memo0 = None
        self.memo1 = None
        self.user_identifier = None
        self.imported_at = None  # UTC

    def __eq__(self, other):
        '''
        `__eq__` tests equality.
        @Warning Several fields are ignored, intentionally.
        '''
        if isinstance(other, BankSaladExpenseTransaction):
            return self.account == other.account \
                and self.amount == other.amount \
                and self.category0 == other.category0 \
                and self.category1 == other.category1 \
                and self.currency == other.currency \
                and self.transaction_datetime == other.transaction_datetime \
                and self.type == other.type \
                and self.memo0 == other.memo0 \
                and self.memo1 == other.memo1 \
                and self.user_identifier == other.user_identifier
        return False

    def __hash__(self):
        '''
        `__hash__` returns a unique hash of an object.
        @Warning Several fields are ignored, intentionally.
        '''
        return hash((self.account,
                     self.amount,
                     self.category0,
                     self.category1,
                     self.currency,
                     self.transaction_datetime,
                     self.type,
                     self.memo0,
                     self.memo1,
                     self.user_identifier))

    def __str__(self):
        return f'transaction_datetime({self.transaction_datetime}) type({self.type}) category0({self.category0}) category1({self.category1}) memo0({self.memo0}) amount({self.amount}) currency({self.currency}) account({self.account}) memo1({self.memo1}) user_identifier({self.user_identifier}) imported_at({self.imported_at})'


class BankSaladExpenseTransactionDBImpl(DBImplBase):

    def __init__(self, db_connection: DBConnection) -> None:
        super().__init__(db_connection)

    def _get_session(self):
        Session = sessionmaker(bind=self.db_connection.engine)
        return Session()

    def create_table(self) -> bool:
        # Use the inspector
        inspector = sqlalchemy.inspect(self.db_connection.engine)
        table_name = BankSaladExpenseTransaction.__tablename__
        if table_name in inspector.get_table_names():
            return True
        BankSaladExpenseTransaction.__table__.create(self.db_connection.engine)
        return True

    def insert_records(self, list_of_transaction: list[BankSaladExpenseTransaction]) -> bool:
        session = self._get_session()
        try:
            session.add_all(list_of_transaction)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error during record insertion: {e}")
            return False
        finally:
            session.close()

    def get_all(self) -> list[BankSaladExpenseTransaction]:
        try:
            with self._get_session() as session:
                return session.query(BankSaladExpenseTransaction).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching records: {e}")
            return []


class BankSaladExpenseTransactionControl():

    def __init__(self, db_connection: DBConnection):
        self.db_impl = BankSaladExpenseTransactionDBImpl(db_connection)
        self.importer = BankSaladExpenseTransactionImporter()

    def _import_from_file(self, input_file_path: str, user_identifier: str) -> list[BankSaladExpenseTransaction]:
        return self.importer.import_from_file(input_file_path, user_identifier)

    def import_and_append_from_file(self, input_file_path: str, user_identifier: str) -> bool:
        list_of_bank_salad_expense_transaction = self._import_from_file(input_file_path, user_identifier)
        if not list_of_bank_salad_expense_transaction:
            return False
        # Create a table if needed. Insert records.
        if not self.db_impl.create_table():
            return False
        list_of_expense_transaction_to_be_appended = self._get_list_of_expense_transaction_to_be_appended(list_of_bank_salad_expense_transaction)
        if not self.db_impl.insert_records(list_of_expense_transaction_to_be_appended):
            return False
        return True

    def _get_list_of_expense_transaction_to_be_appended(self, source_list: list[BankSaladExpenseTransaction]) -> list[BankSaladExpenseTransaction]:
        '''
        Here,
        `target_list` is a list which was read from a DB;
        `source_list` is a list which was read from a file.
        '''
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


class BankSaladExpenseTransactionImporter():

    def __init__(self):
        pass

    def import_from_file(self, input_file_path: str, user_identifier: str) -> list[BankSaladExpenseTransaction]:
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
        return self._bulid_expense_transaction(df, user_identifier)

    def _bulid_expense_transaction(self, df: DataFrame, user_identifier: str) -> list[BankSaladExpenseTransaction]:
        current_datetime = datetime.datetime.now(datetime.timezone.utc)
        list_of_expense_transaction = []
        for row in df.itertuples(index=True, name=None):
            t = BankSaladExpenseTransaction()
            # 1-indexed. not 0-indexed.
            transaction_date = row[1].date()
            transaction_time = row[2]
            t.transaction_datetime = datetime.datetime(year=transaction_date.year, month=transaction_date.month, day=transaction_date.day) \
                + datetime.timedelta(hours=transaction_time.hour, minutes=transaction_time.minute, seconds=transaction_time.second)  # Python datetime.datetime
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
            t.user_identifier = user_identifier
            t.imported_at = current_datetime
            list_of_expense_transaction.append(t)

        logger.info(f'The length of list_of_expense_transaction is ({len(list_of_expense_transaction)}).')
        return list_of_expense_transaction


class ExpenseTransaction(Base):

    __tablename__ = 'expense_transactions'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
    }
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    amount = sqlalchemy.Column(sqlalchemy.Integer)
    category0 = sqlalchemy.Column(sqlalchemy.String(128))
    category1 = sqlalchemy.Column(sqlalchemy.String(128))
    converted_at = sqlalchemy.Column(sqlalchemy.DateTime)  # UTC
    currency = sqlalchemy.Column(sqlalchemy.String(128))
    memo0 = sqlalchemy.Column(sqlalchemy.String(128))
    memo1 = sqlalchemy.Column(sqlalchemy.String(128))
    source_account = sqlalchemy.Column(sqlalchemy.String(128))
    target_account = sqlalchemy.Column(sqlalchemy.String(128))
    transaction_datetime = sqlalchemy.Column(sqlalchemy.DateTime)  # KST
    user_identifier = sqlalchemy.Column(sqlalchemy.String(128))

    CORE_FIELD_LENGTH = 10  # The length of items - account, amount, etc.

    def __init__(self):
        self.amount = 0
        self.category0 = None
        self.category1 = None
        self.converted_at = None  # UTC.
        self.currency = None
        self.memo0 = None
        self.memo1 = None
        self.source_account = None
        self.target_account = None
        self.transaction_datetime = None  # datetime.datetime. KST.
        self.user_identifier = None

    def __str__(self):
        return f'transaction_datetime({self.transaction_datetime}) category0({self.category0}) category1({self.category1}) memo0({self.memo0}) memo1({self.memo1}) amount({self.amount}) currency({self.currency}) source_account({self.source_account}) target_account({self.target_account}) user_identifier({self.user_identifier})'

    def __eq__(self, other):
        '''
        `__eq__` tests equality.
        # @Warning Please note that `__eq__` function is customized one. Several are ignored, intentionally. Ignored fields are [category0, category1, memo0, memo1].
        '''
        if isinstance(other, ExpenseTransaction):
            return self.amount == other.amount \
                and self.currency == other.currency \
                and self.source_account == other.source_account \
                and self.target_account == other.target_account \
                and self.transaction_datetime == other.transaction_datetime \
                and self.user_identifier == other.user_identifier
        return False

    def __hash__(self):
        '''
        `__hash__` returns a unique hash of an object.
        @Warning Please note that `__eq__` function is customized one. Several fields are ignored, intentionally. Ignored fields are [category0, category1, memo0, memo1].
        '''
        return hash((self.amount,
                     self.currency,
                     self.source_account,
                     self.target_account,
                     self.transaction_datetime,
                     self.user_identifier))


class ExpenseTransactionDBImpl(DBImplBase):

    def __init__(self, db_connection):
        super().__init__(db_connection)

    def create_table(self) -> bool:
        if self._is_table_in_database(ExpenseTransaction.__tablename__):
            return False
        ExpenseTransaction.__table__.create(self.db_connection.engine)
        return True

    def drop_table(self) -> bool:
        if not self._is_table_in_database(ExpenseTransaction.__tablename__):
            return False
        ExpenseTransaction.__table__.drop(self.db_connection.engine)
        return True

    def insert_records(self, list_of_transaction: list[ExpenseTransaction]) -> bool:
        session = self._get_session()
        try:
            session.add_all(list_of_transaction)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error during record insertion: {e}")
            return False
        finally:
            session.close()

    def get_all(self) -> list[ExpenseTransaction]:
        try:
            with self._get_session() as session:
                return session.query(ExpenseTransaction).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching records: {e}")
            return []


class ExpenseTransactionControl():

    def __init__(self, db_connection: DBConnection):
        self.importer = BankSaladExpenseTransactionImporter()
        self.db_impl = ExpenseTransactionDBImpl(db_connection)
        self.conversion_rule = self._load_conversion_rule()

    def import_and_append_from_database(self, user_identifier: str) -> bool:
        return False

    def import_and_append_from_file(self, input_file_path: str, user_identifier: str) -> bool:
        list_of_bank_salad_expense_transaction = self.importer.import_from_file(input_file_path, user_identifier)
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
            t.transaction_datetime = item.transaction_datetime
            t.category0 = self._get_category(conversion_rule, item.category0, item.category1, item.memo0, item.account, item.memo1)
            t.category1 = None  # For future use.
            t.amount = item.amount
            t.currency = item.currency
            t.source_account = item.account
            t.target_account = None
            t.memo0 = item.memo0
            t.memo1 = item.memo1
            t.user_identifier = item.user_identifier

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
