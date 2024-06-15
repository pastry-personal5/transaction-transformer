# -*- coding: utf-8 -*-
"""
This module interprets command from a user, the do the job.


* Please note that mandatory fields are:
** Symbol/ISIN
** Open Price
** Amount

거래일자 // Open Date
종목코드 // Symbol/ISIN
거래소
거래종류
적요명 // Type
종목명 // Name
통화
거래수량 // Amount
거래단가/환율 // Open Price
거래금액
예수금잔고
거래금액(외)
정산금액
정산금액(외)
외화예수금잔고
세금합
수수료(외) // Commission
인지세 // # This goes to commission
유가금잔
미수(원/주)
미수(외)
연체합
변제합
변제합(외)
매체구분
처리시간
외국납부세액

"""

import argparse
import csv
import datetime
import re
import sys
import yaml

from loguru import logger
import mariadb_exporter

from simple_portfolio import SimplePortfolio
from simple_transaction import SimpleTransaction


def convert_kr_date_string_to_date(src):
    pattern = re.compile(r'([0-9]{4})/([0-9]{2})/([0-9]{2})')
    result = pattern.match(src)
    if not result:
        raise MalformedDateError()
    yyyy = int(result.group(1))
    mm = int(result.group(2))
    dd = int(result.group(3))
    return datetime.date(year=yyyy, month=mm, day=dd)


def convert_python_date_to_us_date(src: datetime.date):
    dst = '%02d/%02d/%04d' % (src.month, src.day, src.year)
    return dst


class MalformedDateError(Exception):
    "Raised when a date string is malformed"


def convert_kr_date_to_us_date(src):
    """
    |convert_kr_date_to_us_date| convertes strings: YYYY/MM/DD to MM/DD/YYYY.
    i.e.
    2023/05/30
    05/30/2023
    """
    pattern = re.compile(r'([0-9]{4})/([0-9]{2})/([0-9]{2})')
    result = pattern.match(src)
    if not result:
        raise MalformedDateError()
    yyyy = int(result.group(1))
    mm = int(result.group(2))
    dd = int(result.group(3))
    dst = '%02d/%02d/%04d' % (mm, dd, yyyy)
    return dst


def append_transactions_of_current_date(list_of_simple_transactions: list, transactions_of_current_date: list):
    for t in transactions_of_current_date:
        if t.type == SimpleTransaction.TYPE_STOCK_SPLIT_MERGE_DELETION:
            list_of_simple_transactions.append(t)
    for t in transactions_of_current_date:
        if t.type == SimpleTransaction.TYPE_STOCK_SPLIT_MERGE_INSERTION:
            list_of_simple_transactions.append(t)
    for t in transactions_of_current_date:
        if t.type == SimpleTransaction.TYPE_BUY:
            list_of_simple_transactions.append(t)
    for t in transactions_of_current_date:
        if t.type == SimpleTransaction.TYPE_SELL:
            list_of_simple_transactions.append(t)


# This function merges two lists of |SimpleTransactions| objects. It's based on date-by-date iteration.
# Note: Perfomance-wise, this function can be improved a lot.
def merge_simple_transactions(first: list, second: list) -> list:
    merged = []
    len_first = len(first)
    len_second = len(second)
    if len_second == 0:
        return first
    i = 0
    j = 0
    current_date = first[0].open_date
    transactions_of_current_date = None
    today = datetime.date.today()
    while current_date <= today:
        transactions_of_current_date = []
        while i < len_first:
            f = first[i]
            f_date = f.open_date
            if f_date > current_date:
                break
            transactions_of_current_date.append(f)
            i += 1
        while j < len_second:
            s = second[j]
            s_date = s.open_date
            if s_date > current_date:
                break
            transactions_of_current_date.append(s)
            j += 1
        append_transactions_of_current_date(merged, transactions_of_current_date)
        current_date += datetime.timedelta(days=1)

    return merged


def build_list_of_simple_transactions(config_filepath):
    try:
        config_file = open(config_filepath, 'rb')
        config = yaml.safe_load(config_file)

        transaction_filepath = config['primary']['file']
        account = config['primary']['account']
        try:
            logger.info(f'Reading ({transaction_filepath}) ...')
            transaction_file = open(transaction_filepath, newline='', encoding='euc-kr')
            primary_list = get_list_of_simple_transactions_from_stream(transaction_file, account)
            transaction_file.close()
        except IOError as e:
            logger.error('IOError.', e)
            logger.error('Transaction filepath was: %s' % transaction_filepath)

        merged = primary_list.copy()

        added = config['added']
        for item in added:
            added_transaction_filepath = item['file']
            account = item['account']
            try:
                logger.info(f'Reading ({added_transaction_filepath}) ...')
                added_transaction_file = open(added_transaction_filepath, newline='', encoding='euc-kr')
                added_transactions = get_list_of_simple_transactions_from_stream(added_transaction_file, account)
                logger.info(f'Length of added was ({len(added_transactions)})')
                merged = merge_simple_transactions(merged, added_transactions)
                logger.info(f'Length of merged was ({len(merged)})')
                added_transaction_file.close()
            except IOError as e:
                logger.error('IOError.', e)
                logger.error('Transaction filepath was: %s' % transaction_filepath)
        config_file.close()
    except IOError as e:
        logger.error('IOError.', e)
        logger.error('Configuration filepath was: %s' % config_filepath)
        return None
    return merged


# This function parses a 'Kiwoom' CSV file and returns the Python list of |SimpleTransaction| objects.
#
# Note: We know the date of the transaction; We don't know the time of the transaction.
# Because of that, a heuristic has been implemented. That means:
# To ensure that 'BUY' transactions are listed before 'SELL' transaction(s) on the same day,
# additional logic is implemented. See |append_transactions_of_current_date| for details.
def get_list_of_simple_transactions_from_stream(input_stream, account):
    list_of_simple_transactions = []
    EXPECTED_COLUMN_LENGTH = 27
    STRING_FOR_TYPE_BUY = '매수'
    STRING_FOR_TYPE_SELL = '매도'
    STRING_FOR_TYPE_STOCK_SPLIT_MERGE_INSERTION = '액면분할병합입고'
    STRING_FOR_TYPE_STOCK_SPLIT_MERGE_DELETION = '액면분할병합출고'
    # STRING_FOR_TYPE_STOCK_INSERTION = '대체입고'
    # STRING_FOR_TYPE_STOCK_DELETION = '대체출고'
    reader = csv.reader(input_stream, delimiter=',')
    # FIELDNAMES = ['Open Date', 'Symbol/ISIN', 'Type', 'Amount', 'Open Price', 'Commission']
    num_row_read = 0
    transactions_of_current_date = None
    current_date = None
    for input_row in reader:
        num_row_read += 1
        if input_row[0] == 'Version=1.0':
            # One can ignore this
            continue
        elif input_row[0] == '거래일자':
            # Assume that this is the header row. Let's skip the header.
            continue
        if len(input_row) <= 1:
            logger.warning('Tow short row. Expected %d. Got (%s)' % (EXPECTED_COLUMN_LENGTH, input_row))
            continue
        if len(input_row) != EXPECTED_COLUMN_LENGTH:
            logger.warning('A number of column in a row is not %d. Got %d. Let\'s process it.' % (EXPECTED_COLUMN_LENGTH, len(input_row)))
            logger.warning(f'Input was: {input_row}')
        try:
            open_date = convert_kr_date_string_to_date(input_row[0])
        except MalformedDateError:
            logger.warning('A malformed date string has been found.')
            logger.warning('An input was: %s' % str(input_row))
            continue
        if transactions_of_current_date is None:
            # Initial condition
            transactions_of_current_date = []
            current_date = open_date
        elif current_date != open_date:
            # Not the same day
            append_transactions_of_current_date(list_of_simple_transactions, transactions_of_current_date)
            transactions_of_current_date = []
            current_date = open_date
        elif current_date > open_date:
            logger.error('The input file is not sorted by date.')
            sys.exit(-1)
        else:
            # It means the same day.
            pass

        transaction = SimpleTransaction()

        transaction.account = account
        transaction.open_date = open_date

        if input_row[4] == STRING_FOR_TYPE_SELL:
            transaction.type = SimpleTransaction.TYPE_SELL
        elif input_row[4] == STRING_FOR_TYPE_BUY:
            transaction.type = SimpleTransaction.TYPE_BUY
        elif input_row[4] == STRING_FOR_TYPE_STOCK_SPLIT_MERGE_INSERTION:
            transaction.type = SimpleTransaction.TYPE_STOCK_SPLIT_MERGE_INSERTION
        elif input_row[4] == STRING_FOR_TYPE_STOCK_SPLIT_MERGE_DELETION:
            transaction.type = SimpleTransaction.TYPE_STOCK_SPLIT_MERGE_DELETION
        else:
            # Continue with the for loop, It means the other transaction except types above.
            # i.e. Dividend
            # i.e. A header line
            continue

        transaction.symbol = input_row[1]
        transaction.amount = float(input_row[7].replace(',', ''))
        transaction.open_price = float(input_row[8].replace(',', ''))

        pure_commission = input_row[16]
        tax = input_row[17]
        total_commission = float(pure_commission) + float(tax)
        transaction.commission = float('%.2f' % total_commission)

        transactions_of_current_date.append(transaction)

    # Do this once at the last
    append_transactions_of_current_date(list_of_simple_transactions, transactions_of_current_date)

    return list_of_simple_transactions


def do_mariadb_transaction_export(global_config, list_of_simple_transactions):
    exporter = mariadb_exporter.SimpleMariaDBExporter(global_config)
    exporter.export_all(list_of_simple_transactions)


def build_portfolio(list_of_simple_transactions):
    p = SimplePortfolio()
    for transaction in list_of_simple_transactions:
        p.record(transaction)
    return p


def do_investing_dot_com_file_export_to_stream(output_file, portfolio: SimplePortfolio):
    FIELDNAMES = ['Open Date', 'Symbol/ISIN', 'Type', 'Amount', 'Open Price', 'Commission']
    writer = csv.DictWriter(output_file, dialect='excel', fieldnames=FIELDNAMES)
    writer.writeheader()
    num_row_written = 0
    for key in portfolio.p.keys():
        p = portfolio.p[key]
        if p['amount'] > 0.0:
            output_row = {}
            output_row['Type'] = 'Buy'
            output_row['Open Date'] = convert_python_date_to_us_date(p['open_date'])
            output_row['Symbol/ISIN'] = key
            output_row['Amount'] = p['amount']
            output_row['Open Price'] = '%.4f' % p['open_price']
            output_row['Commission'] = '%.2f' % 0.0

            writer.writerow(output_row)
            num_row_written += 1

    logger.info('Number of rows written(%d)' % (num_row_written))


def do_investing_dot_com_portfolio_export(portfolio: SimplePortfolio) -> None:
    try:
        FILEPATH = './data/investing_dot_com_portfolio.txt'
        f = open(FILEPATH, 'w', encoding='utf-8')
        do_investing_dot_com_file_export_to_stream(f, portfolio)
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
    if args.global_config is None:
        logger.error('Global configuration filepath must be provided. Use --global_config.')
        sys.exit(-1)

    global_config_filepath = args.global_config
    global_config = build_global_config(global_config_filepath)

    if global_config is None:
        logger.error('Global configuration is malformed.')
        sys.exit(-1)

    flag_read_input_from_kiwoom = False
    if args.kiwoom_config is not None:
        flag_read_input_from_kiwoom = True

    if not flag_read_input_from_kiwoom:
        logger.error('Currently only reading files from Kiwoom Securities is supported.')
        sys.exit(-1)

    if flag_read_input_from_kiwoom:
        kiwoom_config_filepath = args.kiwoom_config
        list_of_simple_transactions = None

        try:
            list_of_simple_transactions = build_list_of_simple_transactions(kiwoom_config_filepath)
            if not list_of_simple_transactions:
                sys.exit(-1)
        except IOError as e:
            logger.error('IOError: {e}')
            logger.error('Input filepath was: %s' % kiwoom_config_filepath)
            sys.exit(-1)

        do_mariadb_transaction_export(global_config, list_of_simple_transactions)

        portfolio = build_portfolio(list_of_simple_transactions)

        do_investing_dot_com_portfolio_export(portfolio)


def main():
    parser = argparse.ArgumentParser(description='This tool manages financial transactions and portfolios')

    parser.add_argument('--global_config', type=str,
                        help='Global configuration filepath')
    parser.add_argument('--kiwoom_config', type=str,
                        help='Kiwoom configuration filepath')
    args = parser.parse_args()

    do_main_thing_with_args(args)


if __name__ == '__main__':
    main()
