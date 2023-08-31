import sys
from logging import INFO, Logger, StreamHandler

from lib.structures.logger_formatter import SnormLogFormatter


class SnormLogger(Logger):
    def __init__(self, name: str, level=INFO) -> None:
        super().__init__(name, level)

        self.propagate = True
        handler = StreamHandler(sys.stdout)
        handler.setFormatter(SnormLogFormatter())

        self.addHandler(handler)
