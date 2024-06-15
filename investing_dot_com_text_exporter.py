import csv
import datetime


from loguru import logger


from simple_portfolio import SimplePortfolio


def convert_python_date_to_us_date(src: datetime.date):
    dst = '%02d/%02d/%04d' % (src.month, src.day, src.year)
    return dst


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
