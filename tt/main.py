#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module interprets command from a user, the do the job.
"""

import argparse
import sys
import yaml

import click
from loguru import logger

import tt.investing_dot_com_text_exporter
import tt.log_control
import tt.kiwoom_text_importer

from tt.bank_salad_expense_transaction import BankSaladExpenseTransactionControl
from tt.expense_transaction import ExpenseTransactionControl
from tt.db_connection import DBConnection
from tt.expense_category import ExpenseCategoryControl
from tt.expense_category import ExpenseCategoryTextPrinterImpl
from tt.simple_portfolio import SimplePortfolio
from tt.yahoo_finance_web_exporter import YahooFinanceWebExporter
from tt.simple_transaction_db_impl import SimpleTransactionDBImpl
from tt.simple_transaction_text_printer_impl import SimpleTransactionTextPrinterImpl


global_flag_initialized_global_objects = False
global_db_connection = None
global_config_ir = None


def build_portfolio(list_of_simple_transactions):
    p = SimplePortfolio()
    for transaction in list_of_simple_transactions:
        p.record(transaction)
    return p


def do_investing_dot_com_portfolio_export(portfolio: SimplePortfolio) -> None:
    try:
        output_file_path = './data/investing_dot_com_portfolio.txt'
        f = open(output_file_path, 'w', encoding='utf-8')
        tt.investing_dot_com_text_exporter.do_investing_dot_com_file_export_to_file(f, portfolio)
        f.close()
    except IOError as e:
        logger.error(f'IOError: {e}')
        logger.error('The file path was: %s' % output_file_path)


def do_yahoo_finance_web_export(portfolio):
    config_file_path = './config/yahoo.yaml'
    yahoo_finance_web_exporter = YahooFinanceWebExporter()
    if not yahoo_finance_web_exporter.read_config(config_file_path):
        return False
    if not yahoo_finance_web_exporter.verify_config():
        return False
    yahoo_finance_web_exporter.prepare_export()
    yahoo_finance_web_exporter.export_simple_portfolio(portfolio)
    yahoo_finance_web_exporter.cleanup()
    return True


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


# <program> create kiwoom-transaction
@create.command()
@click.option('--kiwoom-config', required=True, help='Kiwoom configuration file path.')
def kiwoom_transaction(kiwoom_config):
    """
    Import Kiwoom Securities transaction file and create transaction records in a database.
    """

    flag_read_input_from_kiwoom = False
    if kiwoom_config is not None:
        flag_read_input_from_kiwoom = True

    if not flag_read_input_from_kiwoom:
        logger.error('Currently only reading files from Kiwoom Securities is supported.')
        sys.exit(-1)

    if flag_read_input_from_kiwoom:
        kiwoom_config_file_path = kiwoom_config
        list_of_simple_transactions = None

        try:
            list_of_simple_transactions = tt.kiwoom_text_importer.build_list_of_simple_transactions(kiwoom_config_file_path)
            if not list_of_simple_transactions:
                sys.exit(-1)
        except IOError as e:
            logger.error(f'IOError: {e}')
            logger.error('Input file path was: %s' % kiwoom_config_file_path)
            sys.exit(-1)

        global global_db_connection
        db_impl = SimpleTransactionDBImpl(global_db_connection)
        db_impl.export_all(list_of_simple_transactions)

        portfolio = build_portfolio(list_of_simple_transactions)

        do_investing_dot_com_portfolio_export(portfolio)


# <program> create bank-salad-expense-transaction
@create.command()
@click.option('-f', '--file', required=True, help='A file exported from Bank Salad which contains expense transactions.')
@click.option('-u', '--user-identifier', required=True, help='A user identifier.')
def bank_salad_expense_transaction(file: str, user_identifier: str):
    """
    Import a file generated from Bank Salad service which contains expense transactions.
    """
    global global_db_connection

    control = BankSaladExpenseTransactionControl(global_db_connection)
    result = control.import_and_append_from_file(file, user_identifier)
    if result:
        logger.info('Succeeded.')
    else:
        logger.info('Failed.')


# <program> create expense-transaction
@create.command()
@click.option('-u', '--user-identifier', required=True, help='A user identifier.')
def expense_transaction(user_identifier: str):
    """
    Create general expense transaction data from "Bank Salad expense transaction data in the database."
    """
    global global_db_connection

    control = ExpenseTransactionControl(global_db_connection)
    result = control.import_and_append_from_database(user_identifier)
    if result:
        logger.info('Succeeded.')
    else:
        logger.info('Failed.')


# <program> create expense-category
@create.command()
@click.option('-f', '--file', required=True, help='A file contains expense category configuration.')
def expense_category(file):
    """
    Create or update records of expense category based on a given file.
    """
    global global_db_connection

    control = ExpenseCategoryControl(global_db_connection)
    result = control.import_and_append_from_file(file)
    if result:
        logger.info('Succeeded.')
    else:
        logger.info('Failed.')


@cli.group()
def delete():
    """
    This command deletes an object.
    """
    pass


# <program> delete bank-salad-expense-transaction
@delete.command()
def bank_salad_expense_transaction():
    """
    Delete data or drop a table w.r.t. bank salad expense transactions.
    """
    global global_db_connection

    control = BankSaladExpenseTransactionControl(global_db_connection)
    result = control.delete()
    if result:
        logger.info('Succeeded.')
    else:
        logger.info('Failed.')


# <program> delete expense-category
@delete.command()
def expense_category():
    """
    Create or update records of expense category based on a given file.
    """
    global global_db_connection

    control = ExpenseCategoryControl(global_db_connection)
    result = control.delete()
    if result:
        logger.info('Succeeded.')
    else:
        logger.info('Failed.')


# <program> delete expense-category
@delete.command()
def expense_transaction():
    """
    Delete data or drop a table w.r.t. expense transactions.
    """
    global global_db_connection

    control = ExpenseTransactionControl(global_db_connection)
    result = control.delete()
    if result:
        logger.info('Succeeded.')
    else:
        logger.info('Failed.')


@cli.group()
def export():
    """
    This command exports data to an external service.
    """
    pass


# <program> export yahoo-finance
@export.command()
def yahoo_finance():
    # @FIXME(dennis.oh) Instead of None, read portfolio.
    portfolio = None
    do_yahoo_finance_web_export(portfolio)


@cli.group()
def get():
    """
    This command gets and displays data.
    """
    pass


# <program> get simple-transaction
@get.command()
@click.option('--symbol', help='Stock symbol to match.')
def simple_transaction(symbol):
    """
    List simple transactions.
    """
    global global_db_connection

    # Get records from the database.
    db_impl = SimpleTransactionDBImpl(global_db_connection)

    if symbol:
        simple_transaction_filter = SimpleTransactionDBImpl.SimpleTransactionFilter()
        simple_transaction_filter.flag_filter_by['symbol'] = True
        simple_transaction_filter.value_dict['symbol'] = symbol
        simple_transaction_records = db_impl.get_records_with_filter(simple_transaction_filter)
        printer_impl = SimpleTransactionTextPrinterImpl()
        printer_impl.print_all(simple_transaction_records)
    else:
        simple_transaction_records = db_impl.get_all_records()
        printer_impl = SimpleTransactionTextPrinterImpl()
        printer_impl.print_all(simple_transaction_records)


# <program> get expense-category --user-identifier <USER IDENTIFIER>
@get.command()
@click.option('--user-identifier', help='User identifier')
def expense_category(user_identifier):
    """
    List expense categories.
    """

    global global_db_connection

    # Get records from the database
    control = ExpenseCategoryControl(global_db_connection)
    if user_identifier:
        list_of_expense_category = control.get_all_filtered_by_user_identifier(user_identifier)
        printer_impl = ExpenseCategoryTextPrinterImpl()
        printer_impl.print_all(list_of_expense_category)
    else:
        list_of_expense_category = control.get_all()
        printer_impl = ExpenseCategoryTextPrinterImpl()
        printer_impl.print_all(list_of_expense_category)


def build_global_config(global_config_file_path: str) -> dict:
    global_config_to_return = {}
    try:
        config_file = open(global_config_file_path, 'rb')
        config = yaml.safe_load(config_file)
        global_config_to_return = config.copy()
        config_file.close()
    except IOError as e:
        logger.error(f'IOError: {e}')
        logger.error('A configuration file path was: %s' % global_config_file_path)
        return None
    return global_config_to_return


def lazy_init_global_objects(global_config_ir):
    global global_flag_initialized_global_objects
    global global_db_connection
    if global_flag_initialized_global_objects is True:
        return
    global_flag_initialized_global_objects = True
    global_db_connection = DBConnection(global_config_ir)
    global_db_connection.do_initial_setup()


def initialize_global_objects():
    global global_config_ir
    global_config_file_path = './config/global_config.yaml'
    global_config_ir = build_global_config(global_config_file_path)

    if global_config_ir is None:
        logger.error('Global configuration is malformed.')
        sys.exit(-1)
    lazy_init_global_objects(global_config_ir)


def cleanup_global_objects():
    if global_db_connection:
        global_db_connection.close()


def main():
    initialize_global_objects()
    cli()
    cleanup_global_objects()


if __name__ == '__main__':
    main()
