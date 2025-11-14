#!/usr/bin/env python
import datetime
import pprint

from loguru import logger
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
import yaml

from tt.bank_salad_expense_transaction import (
    BankSaladExpenseTransaction,
    BankSaladExpenseTransactionDBImpl,
)
from tt.db_connection import DBConnection
from tt.db_impl_base import DBImplBase


Base = declarative_base()  # An sqlalchemy's base class.


class ExpenseTransactionRule(Base):

    __tablename__ = "expense_transaction_rules"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
    }
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    category0 = sqlalchemy.Column(sqlalchemy.String(128))
    category1 = sqlalchemy.Column(sqlalchemy.String(128))
    command = sqlalchemy.Column(sqlalchemy.String(128))
    memo0 = sqlalchemy.Column(sqlalchemy.String(128))
    memo1 = sqlalchemy.Column(sqlalchemy.String(128))
    user_identifier = sqlalchemy.Column(sqlalchemy.String(128))

    CORE_FIELD_LENGTH = 4  # The length of items - account, amount, etc.

    def __init__(self):
        pass

    def __str__(self):
        return f"command({self.command}) category0({self.category0}) category1({self.category1}) memo0({self.memo0}) memo1({self.memo1}) user_identifier({self.user_identifier})"

    def __eq__(self, other):
        """
        `__eq__` tests equality.
        # @Warning Please note that `__eq__` function is customized one. Several are ignored, intentionally. Ignored fields are [category0, category1, memo0, memo1].
        """
        if isinstance(other, ExpenseTransactionRule):
            return (
                self.command == other.command
                and self.category0 == other.category0
                and self.category1 == other.category1
                and self.memo0 == other.memo0
                and self.memo1 == other.memo1
                and self.user_identifier == other.user_identifier
            )
        return False

    def __hash__(self):
        """
        `__hash__` returns a unique hash of an object.
        @Warning Please note that `__eq__` function is customized one. Several fields are ignored, intentionally. Ignored fields are [category0, category1, memo0, memo1].
        """
        return hash(
            (
                self.command,
                self.category0,
                self.category1,
                self.memo0,
                self.memo1,
                self.user_identifier,
            )
        )


class ExpenseTransactionRuleDBImpl(DBImplBase):

    def __init__(self, db_connection):
        super().__init__(db_connection)
        self.sa_table_class = ExpenseTransactionRule  # SQLAlchemy Table Class
        self.table_name = ExpenseTransactionRule.__tablename__

    def create_table(self) -> bool:
        assert self.table_name is not None

        if self._is_table_in_database(self.table_name):
            return False
        self.sa_table_class.__table__.create(self.db_connection.engine)
        return True

    def drop_table(self) -> bool:
        assert self.table_name is not None

        if not self._is_table_in_database(self.table_name):
            return False
        self.sa_table_class.__table__.drop(self.db_connection.engine)
        return True


class ExpenseTransactionRuleControl:

    def __init__(self, db_connection: DBConnection):
        self.db_impl = ExpenseTransactionRuleDBImpl(db_connection)

    def delete(self) -> bool:
        return self.db_impl.drop_table()

    def create(self) -> bool:
        return self.db_impl.create_table()
