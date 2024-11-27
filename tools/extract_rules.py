#!/usr/bin/env bash

import pprint
import sys

import click
from loguru import logger
import numpy
import pandas
from pandas import DataFrame


class Rule():

    def __init__(self):
        self.source_category0 = None
        self.source_category1 = None
        self.source_memo0 = None
        self.source_account = None
        self.source_memo1 = None
        self.target_category0 = None


@click.group()
def cli():
    pass


@cli.command()
@click.option('-f', '--file', required=True, help='A file to be loaded.')
def extract(file):
    input_file_path = file
    output_file_path = './data/processed.yaml'
    (result, df) = read_input_file(input_file_path)
    if not result:
        return None
    list_of_rules = process(df)
    if not list_of_rules:
        return None
    write_output_file(output_file_path, list_of_rules)


def read_input_file(input_file_path: str) -> tuple[bool, DataFrame]:
    logger.info(f'Try to import from a file path ({input_file_path})...')

    try:
        fp = open(input_file_path, 'rb')
        const_sheet_name = 0
        df = pandas.read_excel(fp, sheet_name=const_sheet_name)
        logger.info(pprint.pformat(df.info()))
        fp.close()
        return (True, df)
    except IOError as e:
        logger.error('An IO error has been occurred.')
        logger.error(e)
        return (False, None)


def process(df: DataFrame):
    list_of_rules = []
    set_of_rules = set()
    for row in df.itertuples(index=True, name=None):
        if pandas.isna(row[12]):
            continue
        rule = Rule()
        pprint.pprint('row[4]')
        pprint.pprint(row[4])
        pprint.pprint('row[5]')
        pprint.pprint(row[5])
        pprint.pprint('row[12]')
        pprint.pprint(row[12])
        rule.source_category0 = str(row[4])
        rule.source_category1 = str(row[5])
        rule.target_category0 = str(row[12])

        tuple_to_test = (rule.source_category0, rule.source_category1, rule.target_category0)
        if tuple_to_test in set_of_rules:
            logger.error('Duplicated rules have been found.')
            pprint.pprint(tuple_to_test)
            sys.exit(-1)
        else:
            set_of_rules.add(tuple_to_test)

        list_of_rules.append(rule)

    return list_of_rules


def write_output_file(output_file_path: str, list_of_rules: list[Rule]):
    """
    For example,
    rules:
      - source:
          category0: 앱테크
          category1: 미분류
          memo0:
          account:
          memo1:
        target:
          category0: 수입 앱테크
    """
    logger.info(f'Try to write a file with a file path ({output_file_path})...')

    try:
        fp = open(output_file_path, 'w', encoding='utf-8')
        lf = '\n'
        header = 'rules:' + lf
        fp.write(header)
        for rule in list_of_rules:
            if rule.source_category0:
                output_for_source_category0 = '    category0:' + ' ' + rule.source_category0 + lf
            else:
                output_for_source_category0 = '    category0:' + lf
            if rule.source_category1:
                output_for_source_category1 = '    category1:' + ' ' + rule.source_category1 + lf
            else:
                output_for_source_category1 = '    category1:' + lf
            if rule.source_memo0:
                output_for_source_memo0 = '    memo0:' + ' ' + rule.source_memo0 + lf
            else:
                output_for_source_memo0 = '    memo0:' + lf
            if rule.source_memo1:
                output_for_source_memo1 = '    memo1:' + ' ' + rule.source_memo1 + lf
            else:
                output_for_source_memo1 = '    memo1:' + lf
            if rule.source_account:
                output_for_source_account = '    memo1:' + ' ' + rule.source_account + lf
            else:
                output_for_source_account = '    memo1:' + lf
            if rule.target_category0:
                output_for_target_category0 = '    category0:' + ' ' + rule.target_category0 + lf
            else:
                output_for_target_category0 = '    category0:' + lf
            fp.write('  - source:' + lf)
            fp.write(output_for_source_category0)
            fp.write(output_for_source_category1)
            fp.write(output_for_source_memo0)
            fp.write(output_for_source_account)
            fp.write(output_for_source_memo1)
            fp.write('  - target:' + lf)
            fp.write(output_for_target_category0)
        fp.close()
    except IOError as e:
        logger.error('An IO error has been occurred.')
        logger.error(e)
        return None


def main():
    cli()


if __name__ == '__main__':
    main()