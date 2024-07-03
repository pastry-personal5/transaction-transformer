"""
This module cleans up transaction data from Kiwoom Securities.
It fixes double-quotation problems.

Pattern to replace:

e.g.
```
* Old: "0.03",1,000,"1,000"
* New: "0.03","1,000","1,000"
```

e.g.
```
* Old: "0.03",1,000,449
* New: "0.03","1,000",449
```

"""
import re
import sys

import click
from loguru import logger


def get_corrected_line(line: str, match_object):
    span = match_object.span()
    prefix = line[0:span[0]]  # Ends with ','
    postfix = line[span[1]:]  # Starts with data of a column
    logger.info(prefix)
    logger.info(postfix)

    logger.info(match_object.group(1))
    logger.info(match_object.group(2))

    to_insert = match_object.group(1) + ',' + '\"' + match_object.group(2) + '\"' + ','
    new_line = prefix + to_insert + postfix
    return new_line


def cleanup_with_filepath(filepath):
    # Read
    f = open(filepath, 'r', encoding='cp949')
    lines = f.readlines()
    f.close()

    lines_read = len(lines)
    logger.info(f'Lines read: ({lines_read})')

    # Write
    f = open(filepath, 'w', encoding='cp949')
    pattern = re.compile(r'(\"[0-9,\.]+\"),(1,000),')
    count_matched = 0
    for line in lines:
        match_object = re.search(pattern, line)
        if match_object:
            logger.info(match_object)
            count_matched += 1
            line = get_corrected_line(line, match_object)
            logger.info(line)
        f.write(line)

    f.close()

    logger.info(f'The count of matched lines: ({count_matched})')


@click.command()
@click.option('--file', help='A file to cleanup')
def cleanup(file):
    logger.info(file)
    if file:
        try:
            cleanup_with_filepath(file)
        except IOError as e:
            logger.error('An IO error has been occurred.')
            logger.error(e)
            sys.exit(-1)


def main():
    cleanup()


if __name__ == '__main__':
    main()
