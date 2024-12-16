#!/usr/bin/env python
import datetime

from loguru import logger
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
import yaml

from tt.bank_salad_expense_transaction import BankSaladExpenseTransaction
from tt.db_connection import DBConnection
from tt.db_impl_base import DBImplBase


Base = declarative_base()  # An sqlalchemy's base class.


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
