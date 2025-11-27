"""
Meritz Text Importer
This module implements a text importer for Meritz Securities.
It reads transaction data from text files provided by Meritz Securities.
As of 2025-11-27, it supports only overseas stock transactions.
"""

# Fields:
# "상품구분",
# "거래일자",
# "주문일자",
# "거래구분",
# "거래소",
# "종목코드",  # 5
# "종목명",
# "통화",
# "거래수량",
# "거래단가(외화)",
# "거래/정산금액",  # 10
# "원화입출금액",
# "매매금액(외화)",
# "수수료(외화)",
# "제비용(외화)",
# "유가잔고",
# "외화잔고",
# "원화잔고",
# "거래단가(원화)",
# "매매금액(원화)",
# "수수료(원화)",
# "제비용(원화)",
# "기준환율",
# "거래번호",
# "원거래번호",
# "매체구분",
# "관리점",
# "대출이자",
# "이자계산시작일",
# "이자계산종료일",
# "대출일자(질권설정일)",
# "만기일자",
# "대출전잔",
# "대출금잔",
# "대출금액",
# "대출상환금액",
# "미상환대출연체료"

import csv
from datetime import date, datetime
import re
import sys
from typing import Tuple, List

from loguru import logger

from tt.automated_text_importer_base_impl import AutomatedTextImporterBaseImpl
from tt.automated_text_importer_helper import AutomatedTextImporterHelper
from tt.simple_transaction import SimpleTransaction


class MeritzTextImporter(AutomatedTextImporterBaseImpl):

    def __init__(self):
        super().__init__()
        self.securities_firm_id = "meritz"

    def concat_and_cleanup_local_files_if_needed(self) -> bool:
        return super().concat_and_cleanup_local_files_if_needed()

    def import_transactions(self, concatenated_file_meta: list[tuple[str, str]]) -> Tuple[bool, List[SimpleTransaction]]:
        # Implementation for Meritz
        logger.info("Importing transactions for Meritz...")
        if not concatenated_file_meta or len(concatenated_file_meta) <= 0:
            return (False, [])

        index = 0
        merged = []
        for meta in concatenated_file_meta:
            (transaction_filepath, account) = meta
            transaction_file = open(transaction_filepath, newline="", encoding="euc-kr")
            imported_list = self._get_list_of_simple_transactions_from_stream(
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

    def _get_list_of_simple_transactions_from_stream(self, input_stream, account):
        list_of_simple_transactions = []
        EXPECTED_COLUMN_LENGTH = 37
        STRING_FOR_TYPE_BUY = "해외주식매수"
        STRING_FOR_TYPE_SELL = "해외주식매도"
        STRING_FOR_TYPE_STOCK_SPLIT_MERGE_INSERTION = "액면분할병합입고"  # @FIXME(dennis.oh) Confirm this string is used or not.
        STRING_FOR_TYPE_STOCK_SPLIT_MERGE_DELETION = "액면분할병합출고"  # @FIXME(dennis.oh) Confirm this string is used or not.
        # STRING_FOR_TYPE_STOCK_INSERTION = "대체입고"  # @FIXME(dennis.oh) Confirm this string is used or not.
        # STRING_FOR_TYPE_STOCK_DELETION = "대체출고"  # @FIXME(dennis.oh) Confirm this string is used or not.
        STRING_FOR_TYPE_INBOUND_TRANSFER_RESULTED_FROM_EVENT = "이벤트입고"  # @FIXME(dennis.oh) Confirm this string is used or not.
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
            if input_row[0] == "상품구분":
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
                open_date = datetime.strptime(input_row[2], "%Y-%m-%d").date()
            except ValueError:
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

            transaction.symbol = self._get_transaction_symbol_from_input_row(input_row)
            transaction.amount = float(input_row[8].replace(",", ""))
            transaction.open_price = float(input_row[9].replace(",", ""))

            pure_commission = input_row[13]
            tax = input_row[14]
            total_commission = float(pure_commission) + float(tax)
            transaction.commission = float("%.2f" % total_commission)

            transaction_type = input_row[3].strip()

            if transaction_type == STRING_FOR_TYPE_SELL:
                transaction.transaction_type = (
                    SimpleTransaction.SimpleTransactionTypeEnum.TYPE_SELL
                )
            elif transaction_type== STRING_FOR_TYPE_BUY:
                transaction.transaction_type = (
                    SimpleTransaction.SimpleTransactionTypeEnum.TYPE_BUY
                )
            elif transaction_type == STRING_FOR_TYPE_STOCK_SPLIT_MERGE_INSERTION:
                transaction.transaction_type = (
                    SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_INSERTION
                )
            elif transaction_type == STRING_FOR_TYPE_STOCK_SPLIT_MERGE_DELETION:
                transaction.transaction_type = (
                    SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_DELETION
                )
            elif transaction_type == STRING_FOR_TYPE_INBOUND_TRANSFER_RESULTED_FROM_EVENT:
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
        if transactions_of_current_date is not None:
            AutomatedTextImporterHelper.append_transactions_of_current_date(
                list_of_simple_transactions, transactions_of_current_date
            )

        return list_of_simple_transactions

    def _get_transaction_symbol_from_input_row(self, input_row) -> str:
        """
        Get the transaction symbol from the input row.
        Args:
            input_row: A list of strings representing a row from the input CSV.
        Returns:
            The transaction symbol as a string.
        """
        # For Meritz, we will use the "종목코드" (index 5) as the symbol.
        raw_symbol = input_row[5].strip()
        pattern = re.compile(r"(\w+)\.OQ")
        matched = pattern.match(raw_symbol)
        if matched:
            return matched.group(1)
        return raw_symbol
