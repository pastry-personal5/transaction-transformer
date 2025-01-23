"""
This module does masking and unmasking of sensitive data in configuration files.
"""

import argparse
import sys
import yaml

from loguru import logger


def build_config(config_filepath: str) -> dict:
    config = {}
    try:
        config_file = open(config_filepath, "rb")
        config = yaml.safe_load(config_file)
        config_file.close()
    except IOError as e:
        logger.error("IOError.", e)
        logger.error("Configuration filepath was: %s" % config_filepath)
        return None
    return config


def validate_config(config):
    try:
        masks = config["masks"]
        for m in masks:
            files = m["files"]
            replacement = m["replacement"]
            for f in files:
                if len(f) <= 0:
                    return False
                for r in replacement:
                    before = r["before"]
                    after = r["after"]
                    if len(before) <= 0 or len(after) <= 0:
                        return False
        return True
    except KeyError as e:
        logger.error("KeyError.", e)
        return False


def do_main_thing_with_args(args):
    MASK = 0
    UNMASK = 1
    function = None
    if args.function == "mask":
        function = MASK
    elif args.function == "unmask":
        function = UNMASK
    else:
        logger.error("Function must be given. Use --function.")
        sys.exit(-1)

    config = build_config(args.config)
    if config is None:
        logger.error("Configuration must be given. Use --config.")
        sys.exit(-1)
    result = validate_config(config)
    if not result:
        logger.error("Configuration is malformed.")
        sys.exit(-1)

    masks = config["masks"]
    for m in masks:
        files = m["files"]
        replacement = m["replacement"]

        for filepath in files:
            output_lines = []
            try:
                f = open(filepath, "r", encoding="utf-8")
                for line in f.readlines():
                    for r in replacement:
                        if function == MASK:
                            line = line.replace(r["before"], r["after"])
                        else:
                            line = line.replace(r["after"], r["before"])
                    output_lines.append(line)
                f.close()

                f = open(filepath, "w", encoding="utf-8")
                f.writelines(output_lines)
                f.close()
            except IOError as e:
                logger.error("IOError.", e)
                logger.error("Filepath was: %s" % filepath)
                sys.exit(-1)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--config", type=str, help="Configuration filepath")
    parser.add_argument(
        "--function", type=str, help="Function. Either |mask| or |unmask|"
    )
    args = parser.parse_args()

    do_main_thing_with_args(args)


if __name__ == "__main__":
    main()
