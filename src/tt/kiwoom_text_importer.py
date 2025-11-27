"""
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

import csv
import datetime
import os
import re
import sys
from typing import Tuple, List
import yaml

from loguru import logger

from tt.automated_text_importer_base_impl import AutomatedTextImporterBaseImpl
from tt.automated_text_importer_helper import AutomatedTextImporterHelper
from tt.malformed_date_error import MalformedDateError
from tt.simple_transaction import SimpleTransaction


def get_correct_line_for_pattern_0000(
    prefix: str, postfix: str, match_object: re.Match
) -> str:

    to_insert = (
        match_object.group(1)
        + ","
        + '"'
        + match_object.group(2)
        + '"'
        + ","
        + match_object.group(3)
    )
    new_line = prefix + to_insert + postfix
    return new_line


def get_correct_line_for_pattern_0001(
    prefix: str, postfix: str, match_object: re.Match
) -> str:

    to_insert = (
        match_object.group(1)
        + ","
        + '"'
        + match_object.group(2)
        + '"'
        + ","
        + '"'
        + match_object.group(3)
        + '"'
    )
    new_line = prefix + to_insert + postfix
    return new_line


# "abcd", defg, "hijk"
def get_corrected_line_for_pattern_0000(line: str, match_object: re.Match) -> str:
    span = match_object.span()
    prefix = line[0:span[0]]  # Ends with ','
    postfix = line[span[1]:]  # Starts with data of a column

    return get_correct_line_for_pattern_0000(prefix, postfix, match_object)


# "abcd", defg, hijk
def get_corrected_line_for_pattern_0001(line: str, match_object: re.Match) -> str:
    span = match_object.span()
    prefix = line[0:span[0]]  # Ends with ','
    postfix = line[span[1]:]  # Starts with data of a column

    # It's a heuristic to find a normal case.
    group3 = match_object.group(3)

    # If `group3` was not there before the match...
    if group3 not in prefix:
        logger.info(
            "Skipping correction. Even with suspected abnormality/malformed data."
        )
        return line  # Return an un-modified.
    # If `group3` is just "000"...
    if group3 == "000":
        logger.info(
            "Skipping correction. Even with suspected abnormality/malformed data."
        )
        return line  # Return an un-modified.

    return get_correct_line_for_pattern_0001(prefix, postfix, match_object)


def cleanup_with_filepath(filepath):
    # Read
    f = open(filepath, "r", encoding="cp949")
    lines = f.readlines()
    f.close()

    lines_read = len(lines)
    logger.info(f"Lines read: ({lines_read})")

    # Write
    f = open(filepath, "w", encoding="cp949")
    pattern_0000 = re.compile(r"(\"[0-9,\.]+\"),(1,000),(\"[0-9,\.]+\")")
    pattern_0001 = re.compile(r"(\"[0-9,\.]+\"),(1,000),([0-9\.]+)")
    count_matched = 0
    for line in lines:
        match_object_0000 = re.search(pattern_0000, line)
        match_object_0001 = re.search(pattern_0001, line)
        if match_object_0000:
            count_matched += 1
            logger.info("Problematic line:")
            logger.info(line)
            line = get_corrected_line_for_pattern_0000(line, match_object_0000)
            logger.info("Fixed line:")
            logger.info(line)
        elif match_object_0001:
            count_matched += 1
            logger.info("Problematic line:")
            logger.info(line)
            line = get_corrected_line_for_pattern_0001(line, match_object_0001)
            logger.info("Fixed line:")
            logger.info(line)
        f.write(line)

    f.close()

    logger.info(f"The count of matched lines: ({count_matched})")


def convert_kr_date_string_to_date(src):
    pattern = re.compile(r"([0-9]{4})/([0-9]{2})/([0-9]{2})")
    result = pattern.match(src)
    if not result:
        raise MalformedDateError()
    yyyy = int(result.group(1))
    mm = int(result.group(2))
    dd = int(result.group(3))
    return datetime.date(year=yyyy, month=mm, day=dd)


def build_list_of_simple_transactions(config_filepath: str) -> list[SimpleTransaction]:
    try:
        config_file = open(config_filepath, "rb")
        config = yaml.safe_load(config_file)

        transaction_filepath = config["primary"]["file"]
        account = config["primary"]["account"]
        try:
            logger.info(f"Reading ({transaction_filepath}) ...")
            transaction_file = open(transaction_filepath, newline="", encoding="euc-kr")
            primary_list = get_list_of_simple_transactions_from_stream(
                transaction_file, account
            )
            transaction_file.close()
        except IOError as e:
            logger.error(f"IOError: {e}")
            logger.error("Transaction filepath was: %s" % transaction_filepath)
            return None

        merged = primary_list.copy()

        added = config["added"]
        for item in added:
            added_transaction_filepath = item["file"]
            account = item["account"]
            try:
                logger.info(f"Reading ({added_transaction_filepath}) ...")
                added_transaction_file = open(
                    added_transaction_filepath, newline="", encoding="euc-kr"
                )
                added_transactions = get_list_of_simple_transactions_from_stream(
                    added_transaction_file, account
                )
                logger.info(f"Length of added was ({len(added_transactions)})")
                merged = AutomatedTextImporterHelper.merge_simple_transactions(merged, added_transactions)
                logger.info(f"Length of merged was ({len(merged)})")
                added_transaction_file.close()
            except IOError as e:
                logger.error(f"IOError: {e}")
                logger.error("Transaction filepath was: %s" % transaction_filepath)
        config_file.close()
    except IOError as e:
        logger.error(f"IOError: {e}")
        logger.error("Configuration filepath was: %s" % config_filepath)
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
    STRING_FOR_TYPE_BUY = "매수"
    STRING_FOR_TYPE_SELL = "매도"
    STRING_FOR_TYPE_STOCK_SPLIT_MERGE_INSERTION = "액면분할병합입고"
    STRING_FOR_TYPE_STOCK_SPLIT_MERGE_DELETION = "액면분할병합출고"
    # STRING_FOR_TYPE_STOCK_INSERTION = '대체입고'
    # STRING_FOR_TYPE_STOCK_DELETION = '대체출고'
    STRING_FOR_TYPE_INBOUND_TRANSFER_RESULTED_FROM_EVENT = "이벤트입고"
    reader = csv.reader(input_stream, delimiter=",")
    # FIELDNAMES = ['Open Date', 'Symbol/ISIN', 'Type', 'Amount', 'Open Price', 'Commission']
    num_row_read = 0
    transactions_of_current_date = None
    current_date = None
    for input_row in reader:
        num_row_read += 1
        if input_row[0] == "Version=1.0":
            # One can ignore this
            continue
        if input_row[0] == "거래일자":
            # Assume that this is the header row. Let's skip the header.
            continue
        if len(input_row) <= 1:
            logger.warning(
                "Tow short row. Expected %d. Got (%s)"
                % (EXPECTED_COLUMN_LENGTH, input_row)
            )
            continue
        if len(input_row) != EXPECTED_COLUMN_LENGTH:
            logger.warning(
                "A number of column in a row is not %d. Got %d. Let's process it."
                % (EXPECTED_COLUMN_LENGTH, len(input_row))
            )
            logger.warning(f"Input was: {input_row}")
        try:
            open_date = convert_kr_date_string_to_date(input_row[0])
        except MalformedDateError:
            logger.warning("A malformed date string has been found.")
            logger.warning("An input was: %s" % str(input_row))
            continue
        if transactions_of_current_date is None:
            # Initial condition
            transactions_of_current_date = []
            current_date = open_date
        elif current_date != open_date:
            # Not the same day
            AutomatedTextImporterHelper.append_transactions_of_current_date(
                list_of_simple_transactions, transactions_of_current_date
            )
            transactions_of_current_date = []
            current_date = open_date
        elif current_date > open_date:
            logger.error("The input file is not sorted by date.")
            sys.exit(-1)
        else:
            # It means the same day.
            pass

        transaction = SimpleTransaction()

        transaction.account = account
        transaction.open_date = open_date

        transaction.symbol = input_row[1]
        transaction.amount = float(input_row[7].replace(",", ""))
        transaction.open_price = float(input_row[8].replace(",", ""))

        pure_commission = input_row[16]
        tax = input_row[17]
        total_commission = float(pure_commission) + float(tax)
        transaction.commission = float("%.2f" % total_commission)

        input_row[4] = input_row[4].strip()

        if input_row[4] == STRING_FOR_TYPE_SELL:
            transaction.transaction_type = (
                SimpleTransaction.SimpleTransactionTypeEnum.TYPE_SELL
            )
        elif input_row[4] == STRING_FOR_TYPE_BUY:
            transaction.transaction_type = (
                SimpleTransaction.SimpleTransactionTypeEnum.TYPE_BUY
            )
        elif input_row[4] == STRING_FOR_TYPE_STOCK_SPLIT_MERGE_INSERTION:
            transaction.transaction_type = (
                SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_INSERTION
            )
        elif input_row[4] == STRING_FOR_TYPE_STOCK_SPLIT_MERGE_DELETION:
            transaction.transaction_type = (
                SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_DELETION
            )
        elif input_row[4] == STRING_FOR_TYPE_INBOUND_TRANSFER_RESULTED_FROM_EVENT:
            transaction.transaction_type = (
                SimpleTransaction.SimpleTransactionTypeEnum.TYPE_INBOUND_TRANSFER_RESULTED_FROM_EVENT
            )
        else:
            # Continue with the for loop, It means the other transaction except types above.
            # i.e. Dividend
            # i.e. A header line
            continue

        transactions_of_current_date.append(transaction)

    # Do this once at the last
    AutomatedTextImporterHelper.append_transactions_of_current_date(
        list_of_simple_transactions, transactions_of_current_date
    )

    return list_of_simple_transactions


class KiwoomTextImporter(AutomatedTextImporterBaseImpl):

    def __init__(self):
        super().__init__()
        self.securities_firm_id = "kiwoom" # securities firm id

    def import_transactions(self, concatenated_file_meta: list[tuple[str, str]]) -> Tuple[bool, List[SimpleTransaction]]:
        # Implementation for Kiwoom
        logger.info("Importing transactions for Kiwoom...")
        if not concatenated_file_meta or len(concatenated_file_meta) <= 0:
            return (False, [])

        index = 0
        merged = []
        for meta in concatenated_file_meta:
            (transaction_filepath, account) = meta
            transaction_file = open(transaction_filepath, newline="", encoding="euc-kr")
            imported_list = get_list_of_simple_transactions_from_stream(
                transaction_file, account
            )
            transaction_file.close()
            if index == 0:
                merged = imported_list.copy()
            else:
                merged = AutomatedTextImporterHelper.merge_simple_transactions(merged, imported_list)
            index += 1

        logger.info(f"Total imported transactions: {len(merged)}")

        return (True, merged)

    def _cleanup_files(self, concatenated_file_meta: tuple[str, str]) -> None:
        # Implementation for Kiwoom
        for (filepath, account) in concatenated_file_meta:
            logger.info(f"Cleaning up file: {os.path.basename(filepath)}")
            cleanup_with_filepath(filepath)
