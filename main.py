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

import investing_dot_com_text_exporter
import kiwoom_text_importer
import mariadb_exporter

from simple_portfolio import SimplePortfolio
from yahoo_finance_web_exporter import YahooFinanceWebExporter


def do_mariadb_transaction_export(global_config, list_of_simple_transactions):
    exporter = mariadb_exporter.SimpleMariaDBExporter(global_config)
    exporter.export_all(list_of_simple_transactions)


def build_portfolio(list_of_simple_transactions):
    p = SimplePortfolio()
    for transaction in list_of_simple_transactions:
        p.record(transaction)
    return p


def do_investing_dot_com_portfolio_export(portfolio: SimplePortfolio) -> None:
    try:
        FILEPATH = './data/investing_dot_com_portfolio.txt'
        f = open(FILEPATH, 'w', encoding='utf-8')
        investing_dot_com_text_exporter.do_investing_dot_com_file_export_to_file(f, portfolio)
        f.close()
    except IOError as e:
        logger.error(f'IOError: {e}')
        logger.error('Filepath was: %s' % FILEPATH)


def build_global_config(global_config_filepath: str) -> dict:
    global_config = {}
    try:
        config_file = open(global_config_filepath, 'rb')
        config = yaml.safe_load(config_file)
        global_config = config.copy()
        config_file.close()
    except IOError as e:
        logger.error(f'IOError: {e}')
        logger.error('Configuration filepath was: %s' % global_config_filepath)
        return None
    return global_config


def do_main_thing_with_args(args):
    pass


def do_yahoo_finance_web_export(portfolio):
    config_filepath = './config/yahoo.yaml'
    yahoo_finance_web_exporter = YahooFinanceWebExporter()
    if not yahoo_finance_web_exporter.read_config(config_filepath):
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


@create.command()
@click.option('--global-config', required=True, help='Global configuration filepath.')
@click.option('--kiwoom-config', required=True, help='Kiwoom configuration filepath.')
def kiwoom_transaction(global_config, kiwoom_config):
    """
    Import Kiwoom Securities transaction file and create transaction records in a database.
    """
    if global_config is None:
        logger.error('Global configuration filepath must be provided. Use --global_config.')
        sys.exit(-1)

    global_config_filepath = global_config
    global_config_dict = build_global_config(global_config_filepath)

    if global_config_dict is None:
        logger.error('Global configuration is malformed.')
        sys.exit(-1)

    flag_read_input_from_kiwoom = False
    if kiwoom_config is not None:
        flag_read_input_from_kiwoom = True

    if not flag_read_input_from_kiwoom:
        logger.error('Currently only reading files from Kiwoom Securities is supported.')
        sys.exit(-1)

    if flag_read_input_from_kiwoom:
        kiwoom_config_filepath = kiwoom_config
        list_of_simple_transactions = None

        try:
            list_of_simple_transactions = kiwoom_text_importer.build_list_of_simple_transactions(kiwoom_config_filepath)
            if not list_of_simple_transactions:
                sys.exit(-1)
        except IOError as e:
            logger.error(f'IOError: {e}')
            logger.error('Input filepath was: %s' % kiwoom_config_filepath)
            sys.exit(-1)

        do_mariadb_transaction_export(global_config_dict, list_of_simple_transactions)

        portfolio = build_portfolio(list_of_simple_transactions)

        do_investing_dot_com_portfolio_export(portfolio)


@cli.group()
def export():
    """
    This command exports data to an external service.
    """
    pass


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


if __name__ == '__main__':
    cli()
