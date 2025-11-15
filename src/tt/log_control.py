"""Small compatibility bridge that forwards stdlib `logging` records to Loguru.

This module installs an intercepting handler that converts standard
``logging`` records into Loguru calls so libraries using the standard
logging API route their output through Loguru's configurable sink system.

See Loguru docs for details:
https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
"""

import inspect
import logging

from loguru import logger


class InterceptHandler(logging.Handler):
    """A logging.Handler that forwards LogRecord objects to Loguru.

    Behavior:
    - Map the stdlib logging level name to a Loguru level when possible.
    - Walk the call stack to find the original caller frame so Loguru can
      attribute the message to the correct source (file/line/function).
    - Preserve exception information (exc_info) when present.
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Determine the Loguru level corresponding to the stdlib level name.
        # If Loguru doesn't have a named level for this record, fall back
        # to using the numeric level number.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Walk back through frames to find the first frame that isn't part
        # of the logging module. The `depth` tells Loguru how many frames
        # to skip so the logged message appears to come from the original
        # caller (rather than this handler or the logging module).
        frame, depth = inspect.currentframe(), 0
        # Skip frames that are from the logging implementation itself.
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        # Forward to Loguru, preserving exception info and supplying the
        # computed stack depth so Loguru reports the correct caller.
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# Replace any existing handlers with our interceptor so all stdlib
# logging goes through Loguru. `force=True` ensures this configuration
# is applied even if logging was previously configured elsewhere.
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
