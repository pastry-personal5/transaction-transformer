"""
This module just shows content of a euc-kr-encoded file - e.g. From Kiwoom - to utf-8-locale console.
"""

import argparse
import sys

from loguru import logger


def main():
    parser = argparse.ArgumentParser(description="This tool shows content of a file")
    parser.add_argument("input")
    args = parser.parse_args()
    if args.input is None:
        logger.error("Please provide an input filepath.")
        sys.exit(-1)

    show(args.input)


def show(input_filepath):
    try:
        input_file = open(input_filepath, newline="", encoding="euc-kr")
        for line in input_file.readlines():
            sys.stdout.buffer.write(line.strip().encode("utf-8"))
            sys.stdout.buffer.write(("\n").encode("utf-8"))
        input_file.close()
    except IOError as e:
        logger.error(f"IOError: {e}")
        logger.error(f"Input filepath was: {input_filepath}")


if __name__ == "__main__":
    main()
