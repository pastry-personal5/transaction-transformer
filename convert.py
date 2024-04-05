# -*- coding: utf-8 -*-
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

import argparse
import csv
import re
import sys


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
    dst = f'%02d/%02d/%04d' % (mm, dd, yyyy)
    return dst


def convert_transaction_file(input_file, output_file):
    EXPECTED_COLUMN_LENGTH = 27
    reader = csv.reader(input_file, delimiter=',')
    FIELDNAMES = ['Open Date', 'Symbol/ISIN', 'Type', 'Amount', 'Open Price', 'Commission']
    writer = csv.DictWriter(output_file, dialect='excel', fieldnames=FIELDNAMES)
    writer.writeheader()
    num_row_read = 0
    num_row_written = 0
    for input_row in reader:
        num_row_read += 1
        if len(input_row) <= 1:
            print(f'[WARNING] Tow short row. Expected %d. Got (%s)' % (EXPECTED_COLUMN_LENGTH, input_row))
            continue
        elif len(input_row) != EXPECTED_COLUMN_LENGTH:
            print(f'[WARNING] A number of column in a row is not %d. Got %d. Let\'s process it.' % (EXPECTED_COLUMN_LENGTH, len(input_row)))
            print(input_row)

        output_row = {}

        if input_row[4] == '매도':
            output_row['Type'] = 'Sell'
        elif input_row[4] == '매수':
            output_row['Type'] = 'Buy'
        else:
            # Continue with the for loop, It means the other transaction except Sell and Buy.
            # i.e. Dividened
            # i.e. A header line
            continue

        try:
            output_row['Open Date'] = convert_kr_date_to_us_date(input_row[0])
        except MalformedDateError:
            print('[WARNING] A malformed date string has been found.')
            print(f'[WARNING] An input was: %s' % input_row)
            continue

        output_row['Symbol/ISIN'] = input_row[1]
        output_row['Amount'] = input_row[7]
        output_row['Open Price'] = input_row[8]

        pure_commission = input_row[16]
        tax = input_row[17]
        total_commission = float(pure_commission) + float(tax)
        output_row['Commission'] = f'%.2f' % total_commission

        writer.writerow(output_row)
        num_row_written += 1

    print(f'[INFO] Number of rows read(%d), written(%d)' % (num_row_read, num_row_written))


def convert(input_filepath, output_filepath):
    try:
        input_file = open(input_filepath, newline='', encoding='euc-kr')
        output_file = open(output_filepath, 'w', newline='', encoding='utf-8')
        convert_transaction_file(input_file, output_file)
        input_file.close()
        output_file.close()
    except IOError as e:
        print('[ERROR] IOError.', e)
        print(f'[ERROR] Input filepath was: %s' % input_filepath)


def main():
    parser = argparse.ArgumentParser(description='This tool converts financial transaction files')
    parser.add_argument('--input', type=str,
                        help='Input filepath')
    parser.add_argument('--output', type=str,
                        help='Output filepath')
    args = parser.parse_args()

    if args.input is None or args.output is None:
        print('[ERROR] Please provide an input filepath and an output filepath.')
        sys.exit(-1)
    convert(args.input, args.output)


if __name__ == '__main__':
    main()
