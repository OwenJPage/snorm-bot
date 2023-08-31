from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING, Formatter, LogRecord
from typing import Dict


class SnormLogFormatter(Formatter):
    class _Colours:
        """
        ANSI escape codes for colours
        """

        reset: str = "\u001b[0m"
        bright: str = "\u001b[1m"
        dim: str = "\u001b[2m"
        underline: str = "\u001b[4m"
        fg: Dict[str, str] = {
            "black": "\u001b[30m",
            "red": "\u001b[31m",
            "green": "\u001b[32m",
            "yellow": "\u001b[33m",
            "blue": "\u001b[34m",
            "magenta": "\u001b[35m",
            "cyan": "\u001b[36m",
            "white": "\u001b[37m",
        }
        bg: Dict[str, str] = {
            "black": "\u001b[40m",
            "red": "\u001b[41m",
            "green": "\u001b[42m",
            "yellow": "\u001b[43m",
            "blue": "\u001b[44m",
            "magenta": "\u001b[45m",
            "cyan": "\u001b[46m",
            "white": "\u001b[47m",
        }

    _formats: Dict[int, str] = {
        DEBUG: _Colours.dim,
        INFO: _Colours.fg["cyan"],
        WARNING: _Colours.fg["yellow"],
        ERROR: _Colours.fg["red"],
        CRITICAL: _Colours.bright + _Colours.bg["red"] + _Colours.fg["yellow"],
    }

    def __init__(self) -> None:
        super().__init__(
            fmt="(%(asctime)s) [%(levelname)s] <%(name)s> %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record: LogRecord) -> str:
        return f"{self._formats[record.levelno]}{super().format(record)}{self._Colours.reset}"
