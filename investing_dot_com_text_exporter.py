import csv
import datetime


from loguru import logger


from simple_portfolio import SimplePortfolio


def convert_python_date_to_us_date(src: datetime.date) -> str:
    """
    Convert a Python date object to a string in the format 'MM/DD/YYYY'.

    Args:
        src: The source Python date object to convert.

    Returns:
        A string representing the date in 'MM/DD/YYYY' format.
    """
    dst = '%02d/%02d/%04d' % (src.month, src.day, src.year)
    return dst


def do_investing_dot_com_file_export_to_file(output_file, portfolio) -> None:
    """
    Export the given SimplePortfolio to a CSV file in the format used by investing.com.

    Args:
        output_file: The file object to write the CSV data to.
        portfolio: The SimplePortfolio object containing the portfolio data to export.

    Returns:
        None

    Raises:
        Any errors that occur during the file writing process.
    """
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
