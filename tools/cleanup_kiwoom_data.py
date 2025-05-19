"""
This module cleans up transaction data from Kiwoom Securities.
It fixes double-quotation problems.
It is a workaround for the Kiwoom Securities' CSV export issue.
The CSV export from Kiwoom Securities has a problem with double-quotation marks.

It is a kind of data cleansing.

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


@click.command()
@click.option("--file", help="A file to cleanup")
def cleanup(file):
    logger.info(file)
    if file:
        try:
            cleanup_with_filepath(file)
        except IOError as e:
            logger.error("An IO error has been occurred.")
            logger.error(e)
            sys.exit(1)


def main():
    cleanup()


if __name__ == "__main__":
    main()
