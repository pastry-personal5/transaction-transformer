#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module interprets command from a user, then do the job.
It uses `click` package to build a command line interface.
"""

import datetime
import os
import sys
from typing import Optional

import click
import yaml
from loguru import logger

import tt.kiwoom_text_importer
from tt.automated_text_importer import AutomatedTextImporterControl
from tt.bank_salad_expense_transaction import \
    BankSaladExpenseTransactionControl
from tt.bootstrap import BootstrapControl
from tt.db_connection import DBConnection
from tt.expense_category import (ExpenseCategoryControl,
                                 ExpenseCategoryTextPrinterImpl)
from tt.expense_transaction import ExpenseTransactionControl
from tt.fact_data_control import FactDataControl
from tt.simple_portfolio import SimplePortfolio
from tt.simple_portfolio_control import SimplePortfolioControl
from tt.simple_transaction import SimpleTransaction
from tt.simple_transaction_db_impl import SimpleTransactionDBImpl
from tt.simple_transaction_text_printer_impl import \
    SimpleTransactionTextPrinterImpl


class GlobalObjectControl:

    def __init__(self):
        self.global_flag_initialized_global_objects = False
        self.global_db_connection = None  # `tt.db_connection.DBConnection`
        self.global_config_ir = None
        self.fact_data_control = None


# Global variable
global_object_control = GlobalObjectControl()


@click.group()
def cli():
    # This is the base command group, providing a central entry point for the tool. Intentionally, one passes.
    """
    This program manages financial transactions.
    """
    pass


@cli.group()
def create():
    """
    This command creates an object.
    """
    pass


@cli.group()
def bootstrap():
    """
    This command bootstraps.
    """


@cli.group()
def delete():
    """
    This command deletes an object.
    """
    pass


@cli.group()
def export():
    """
    This command exports data to an external service.
    """
    pass


@cli.group()
def get():
    """
    This command gets and displays data.
    """
    pass


@cli.group()
def show():
    """
    This command shows data.
    """
    pass


# <program> create auto
@create.command()
def auto():
    """
    Import all transactions using automated text importer.
    """
    global global_object_control

    control = AutomatedTextImporterControl()
    control.load_module_config()
    (result, list_of_simple_transactions) = control.import_all_transactions()
    if not result or not list_of_simple_transactions:
        sys.exit(-1)

    global global_object_control
    if not global_object_control.global_db_connection.is_in_valid_state():
        logger.error("DB Connection is not valid. Please bootstrap first.")
        sys.exit(-1)
    db_impl = SimpleTransactionDBImpl(global_object_control.global_db_connection)
    db_impl.export_all(list_of_simple_transactions)

    simple_portfolio_control = SimplePortfolioControl(
        global_object_control.fact_data_control
    )
    # @FIXME(dennis.oh) Instead of None, read portfolio snapshot date from config.
    portfolio = simple_portfolio_control.build_portfolio(
        list_of_simple_transactions, None
    )
    simple_portfolio_control.do_investing_dot_com_portfolio_export(portfolio)


# <program> create kiwoom-transaction
@create.command()
@click.option("--kiwoom-config", required=True, help="Kiwoom configuration file path.")
@click.option(
    "--portfolio-snapshot-date",
    required=False,
    help="A date for portfolio snapshot. Optional.",
)
def kiwoom_transaction(kiwoom_config, portfolio_snapshot_date: Optional[str]):
    """
    Import Kiwoom Securities transaction file and create transaction records in a database.
    """

    flag_read_input_from_kiwoom = False
    if kiwoom_config is not None:
        flag_read_input_from_kiwoom = True

    if not flag_read_input_from_kiwoom:
        logger.error(
            "Currently only reading files from Kiwoom Securities is supported."
        )
        sys.exit(-1)

    portfolio_snapshot_date_obj = None
    if portfolio_snapshot_date:
        try:
            expected_date_format = "%Y-%m-%d"
            portfolio_snapshot_date_obj = datetime.datetime.strptime(
                portfolio_snapshot_date, expected_date_format
            ).date()
        except ValueError as e:
            logger.error(
                f"Error while parsing a portfolio snapshot date: ({portfolio_snapshot_date}). Expected date format is ({expected_date_format}). For example, 2007-12-31."
            )
            logger.error(e)
            sys.exit(-1)

    kiwoom_config_file_path = kiwoom_config
    list_of_simple_transactions = None

    try:
        list_of_simple_transactions = (
            tt.kiwoom_text_importer.build_list_of_simple_transactions(
                kiwoom_config_file_path
            )
        )
        if not list_of_simple_transactions:
            sys.exit(-1)
    except IOError as e:
        logger.error(f"IOError: {e}")
        logger.error("Input file path was: %s" % kiwoom_config_file_path)
        sys.exit(-1)

    global global_object_control
    if not global_object_control.global_db_connection.is_in_valid_state():
        logger.error("DB Connection is not valid. Please bootstrap first.")
        sys.exit(-1)
    db_impl = SimpleTransactionDBImpl(global_object_control.global_db_connection)
    db_impl.export_all(list_of_simple_transactions)

    simple_portfolio_control = SimplePortfolioControl(
        global_object_control.fact_data_control
    )
    portfolio = simple_portfolio_control.build_portfolio(
        list_of_simple_transactions, portfolio_snapshot_date_obj
    )
    simple_portfolio_control.do_investing_dot_com_portfolio_export(portfolio)


# <program> create bank-salad-expense-transaction
@create.command()
@click.option(
    "-f",
    "--file",
    required=True,
    help="A file exported from Bank Salad which contains expense transactions.",
)
@click.option("-u", "--user-identifier", required=True, help="A user identifier.")
def bank_salad_expense_transaction(file: str, user_identifier: str):
    """
    Import a file generated from Bank Salad service which contains expense transactions.
    """
    global global_object_control

    control = BankSaladExpenseTransactionControl(
        global_object_control.global_db_connection
    )
    result = control.import_and_append_from_file(file, user_identifier)
    if result:
        logger.info("Succeeded.")
    else:
        logger.info("Failed.")


# <program> create expense-transaction
@create.command()
@click.option("-u", "--user-identifier", required=True, help="A user identifier.")
def expense_transaction(user_identifier: str):
    """
    Create general expense transaction data from "Bank Salad expense transaction data in the database."
    """
    global global_object_control

    control = ExpenseTransactionControl(global_object_control.global_db_connection)
    result = control.import_and_append_from_database(user_identifier)
    if result:
        logger.info("Succeeded.")
    else:
        logger.info("Failed.")


# <program> create expense-category
@create.command()
@click.option(
    "-f",
    "--file",
    required=True,
    help="A file contains expense category configuration.",
)
def expense_category(file):
    """
    Create or update records of expense category based on a given file.
    """
    global global_object_control

    control = ExpenseCategoryControl(global_object_control.global_db_connection)
    result = control.import_and_append_from_file(file)
    if result:
        logger.info("Succeeded.")
    else:
        logger.info("Failed.")


@bootstrap.command()
def database():
    global global_object_control
    bootstrap_control = BootstrapControl()
    bootstrap_control.bootstrap(global_object_control.global_db_connection)


# <program> delete bank-salad-expense-transaction
@delete.command()
def bank_salad_expense_transaction():
    """
    Delete data or drop a table w.r.t. bank salad expense transactions.
    """
    global global_object_control

    control = BankSaladExpenseTransactionControl(
        global_object_control.global_db_connection
    )
    result = control.delete()
    if result:
        logger.info("Succeeded.")
    else:
        logger.info("Failed.")


# <program> delete expense-category
@delete.command()
def expense_category():
    """
    Create or update records of expense category based on a given file.
    """
    global global_object_control

    control = ExpenseCategoryControl(global_object_control.global_db_connection)
    result = control.delete()
    if result:
        logger.info("Succeeded.")
    else:
        logger.info("Failed.")


# <program> delete expense-category
@delete.command()
def expense_transaction():
    """
    Delete data or drop a table w.r.t. expense transactions.
    """
    global global_object_control

    control = ExpenseTransactionControl(global_object_control.global_db_connection)
    result = control.delete()
    if result:
        logger.info("Succeeded.")
    else:
        logger.info("Failed.")


# <program> export yahoo-finance
@export.command()
def yahoo_finance():
    # @FIXME(dennis.oh) Instead of None, read portfolio.
    portfolio = None
    # global global_object_control
    # control = SimplePortfolioControl(global_object_control.fact_data_control)
    # control.do_yahoo_finance_web_export(portfolio)
    pass


# <program> get simple-transaction
@get.command()
@click.option("--symbol", help="Stock symbol to match.")
def simple_transaction(symbol):
    """
    List simple transactions.
    """
    global global_object_control

    # Get records from the database.
    db_impl = SimpleTransactionDBImpl(global_object_control.global_db_connection)

    if symbol:
        simple_transaction_filter = SimpleTransactionDBImpl.SimpleTransactionFilter()
        simple_transaction_filter.flag_filter_by["symbol"] = True
        simple_transaction_filter.value_dict["symbol"] = symbol
        simple_transaction_records = db_impl.get_records_with_filter(
            simple_transaction_filter
        )
        printer_impl = SimpleTransactionTextPrinterImpl()
        printer_impl.print_all(simple_transaction_records)
    else:
        simple_transaction_records = db_impl.get_all_records()
        printer_impl = SimpleTransactionTextPrinterImpl()
        printer_impl.print_all(simple_transaction_records)


# <program> get expense-category --user-identifier <USER IDENTIFIER>
@get.command()
@click.option("--user-identifier", help="User identifier")
def expense_category(user_identifier):
    """
    List expense categories.
    """

    global global_object_control

    # Get records from the database
    control = ExpenseCategoryControl(global_object_control.global_db_connection)
    if user_identifier:
        list_of_expense_category = control.get_all_filtered_by_user_identifier(
            user_identifier
        )
        printer_impl = ExpenseCategoryTextPrinterImpl()
        printer_impl.print_all(list_of_expense_category)
    else:
        list_of_expense_category = control.get_all()
        printer_impl = ExpenseCategoryTextPrinterImpl()
        printer_impl.print_all(list_of_expense_category)


@show.command()
def auto():
    from tt.automated_text_importer_helper import AutomatedTextImporterHelper
    AutomatedTextImporterHelper.show_all_candidate_files()


def build_global_config(global_config_file_path: str) -> dict:
    global_config_to_return = {}
    try:
        config_file = open(global_config_file_path, "rb")
        config = yaml.safe_load(config_file)
        global_config_to_return = config.copy()
        config_file.close()
    except IOError as e:
        logger.error(f"IOError: {e}")
        logger.error("A configuration file path was: %s" % global_config_file_path)
        return None
    return global_config_to_return


def lazy_init_global_objects(global_config_ir):
    global global_object_control
    if global_object_control.global_flag_initialized_global_objects is True:
        return
    global_object_control.global_flag_initialized_global_objects = True
    global_object_control.global_db_connection = DBConnection(global_config_ir)
    global_object_control.global_db_connection.do_initial_setup()
    if global_object_control.global_db_connection.is_in_valid_state():
        global_object_control.fact_data_control = FactDataControl(
            global_object_control.global_db_connection
        )
        global_object_control.fact_data_control.bootstrap()


def initialize_global_objects():
    global global_object_control
    from tt.constants import Constants
    const_global_config_file_path = os.path.join(Constants.config_dir_path, "global_config.yaml")
    global_object_control.global_config_ir = build_global_config(
        const_global_config_file_path
    )

    if global_object_control.global_config_ir is None:
        logger.error("Global configuration is malformed.")
        sys.exit(-1)
    lazy_init_global_objects(global_object_control.global_config_ir)


def cleanup_global_objects():
    if global_object_control.global_db_connection:
        global_object_control.global_db_connection.close()


def main():
    initialize_global_objects()
    cli()
    cleanup_global_objects()


if __name__ == "__main__":
    main()
