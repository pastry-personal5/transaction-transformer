"""
Meritz Text Importer
This module implements a text importer for Meritz Securities.
It reads transaction data from text files provided by Meritz Securities.
As of 2025-11-27, it supports only overseas stock transactions.
"""

# Fields:
# "상품구분", 0
# "거래일자", 1
# "주문일자", 2
# "거래구분", 3
# "거래소", 4
# "종목코드", 5
# "종목명",
# "통화",
# "거래수량",
# "거래단가(외화)",
# "거래/정산금액", 10
# "원화입출금액",
# "매매금액(외화)",
# "수수료(외화)",
# "제비용(외화)",
# "유가잔고", 15
# "외화잔고",
# "원화잔고",
# "거래단가(원화)",
# "매매금액(원화)",
# "수수료(원화)", 20
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

# Old fields:
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
import re
import sys
from datetime import date, datetime
from typing import List, Tuple

from loguru import logger

from tt import symbol_config
from tt.automated_text_importer_base_impl import AutomatedTextImporterBaseImpl
from tt.automated_text_importer_helper import AutomatedTextImporterHelper
from tt.simple_transaction import SimpleTransaction


class MeritzTextImporter(AutomatedTextImporterBaseImpl):

    def __init__(self):
        super().__init__()
        self.securities_firm_id = "meritz"

    def concat_and_cleanup_local_files_if_needed(self) -> bool:
        return super().concat_and_cleanup_local_files_if_needed()

    def _is_transaction_type_buy(self, transaction_type: str) -> bool:
        STRING_FOR_TYPE_BUY = "해외주식매수"
        STRING_FOR_TYPE_BUY_ALT_0000 = "해외주식 매수"
        return transaction_type in [STRING_FOR_TYPE_BUY, STRING_FOR_TYPE_BUY_ALT_0000]

    def _is_transaction_type_sell(self, transaction_type: str) -> bool:
        STRING_FOR_TYPE_SELL = "해외주식매도"
        STRING_FOR_TYPE_SELL_ALT_0000 = "해외주식 매도"
        return transaction_type in [STRING_FOR_TYPE_SELL, STRING_FOR_TYPE_SELL_ALT_0000]

    def _is_transaction_type_stock_insertion_from_other_securities_firm(self, transaction_type: str) -> bool:
        STRING_FOR_TYPE_STOCK_INSERTION_FROM_OTHER_SECURITIES_FIRM = "타사대체입고"
        return transaction_type == STRING_FOR_TYPE_STOCK_INSERTION_FROM_OTHER_SECURITIES_FIRM

    def _is_transaction_type_stock_deletion_from_other_securities_firm(self, transaction_type: str) -> bool:
        STRING_FOR_TYPE_STOCK_DELETION_TO_OTHER_SECURITIES_FIRM = "타사대체출고"
        return transaction_type == STRING_FOR_TYPE_STOCK_DELETION_TO_OTHER_SECURITIES_FIRM

    def _is_transaction_type_stock_split_merge_insertion(self, transaction_type: str) -> bool:
        STRING_FOR_TYPE_STOCK_SPLIT_MERGE_INSERTION = "액면분할병합입고"
        return transaction_type == STRING_FOR_TYPE_STOCK_SPLIT_MERGE_INSERTION

    def _is_transaction_type_stock_split_merge_deletion(self, transaction_type: str) -> bool:
        STRING_FOR_TYPE_STOCK_SPLIT_MERGE_DELETION = "액면분할병합출고"
        return transaction_type == STRING_FOR_TYPE_STOCK_SPLIT_MERGE_DELETION

    def _is_transaction_type_inbound_transfer_resulted_from_event(self, transaction_type: str) -> bool:
        STRING_FOR_TYPE_INBOUND_TRANSFER_RESULTED_FROM_EVENT = "이벤트입고"
        return transaction_type == STRING_FOR_TYPE_INBOUND_TRANSFER_RESULTED_FROM_EVENT

    def _get_list_of_simple_transactions_from_stream(self, input_stream, account, symbol_config: symbol_config.SymbolConfig) -> list[SimpleTransaction]:
        list_of_simple_transactions = []
        EXPECTED_COLUMN_LENGTH = 37
        CONST_OPEN_DATE_COLUMN = 1
        CONST_TRANSACTION_TYPE_COLUMN = 3
        CONST_AMOUNT_COLUMN = 8
        CONST_OPEN_PRICE_COLUMN = 9
        CONST_PURE_COMMISSION_COLUMN = 13
        CONST_TAX_COLUMN = 14
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
                open_date = datetime.strptime(input_row[CONST_OPEN_DATE_COLUMN], "%Y-%m-%d").date()
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

            transaction_type = input_row[CONST_TRANSACTION_TYPE_COLUMN].strip()

            if self._is_transaction_type_sell(transaction_type):
                transaction.transaction_type = (
                    SimpleTransaction.SimpleTransactionTypeEnum.TYPE_SELL
                )
            elif self._is_transaction_type_buy(transaction_type):
                transaction.transaction_type = (
                    SimpleTransaction.SimpleTransactionTypeEnum.TYPE_BUY
                )
            elif self._is_transaction_type_stock_split_merge_insertion(transaction_type):
                transaction.transaction_type = (
                    SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_INSERTION
                )
            elif self._is_transaction_type_stock_split_merge_deletion(transaction_type):
                transaction.transaction_type = (
                    SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_SPLIT_MERGE_DELETION
                )
            elif self._is_transaction_type_inbound_transfer_resulted_from_event(transaction_type):
                transaction.transaction_type = (
                    SimpleTransaction.SimpleTransactionTypeEnum.TYPE_INBOUND_TRANSFER_RESULTED_FROM_EVENT
                )
            elif self._is_transaction_type_stock_insertion_from_other_securities_firm(transaction_type):
                transaction.transaction_type = (
                    SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_INSERTION_CAUSED_BY_OTHER_SECURITIES_FIRM
                )
            elif self._is_transaction_type_stock_deletion_from_other_securities_firm(transaction_type):
                transaction.transaction_type = (
                    SimpleTransaction.SimpleTransactionTypeEnum.TYPE_STOCK_DELETION_CAUSED_BY_OTHER_SECURITIES_FIRM
                )
            else:
                # Continue with the for loop, It means the other transaction except types above.
                # i.e. Dividend
                # i.e. A header line
                continue



            transaction.account = account
            transaction.open_date = open_date

            CONST_SYMBOL_COLUMN = 5

            raw_symbol_input = input_row[CONST_SYMBOL_COLUMN]
            original_namespace = self.securities_firm_id
            (legit_namespace, legit_symbol) = symbol_config.get_namespace_and_symbol_by_raw_input(original_namespace, raw_symbol_input)
            transaction.namespace = legit_namespace
            transaction.symbol = legit_symbol

            transaction.amount = float(input_row[CONST_AMOUNT_COLUMN].replace(",", ""))
            transaction.open_price = float(input_row[CONST_OPEN_PRICE_COLUMN].replace(",", ""))

            pure_commission = input_row[CONST_PURE_COMMISSION_COLUMN]
            tax = input_row[CONST_TAX_COLUMN]
            total_commission = float(pure_commission) + float(tax)
            transaction.commission = float("%.2f" % total_commission)



            transactions_of_current_date.append(transaction)

        # Do this once at the last
        if transactions_of_current_date is not None:
            AutomatedTextImporterHelper.append_transactions_of_current_date(
                list_of_simple_transactions, transactions_of_current_date
            )

        return list_of_simple_transactions
