import logging
from pathlib import Path
from typing import Self

from discord import Bot, Intents


class Snorm(Bot):
    def __init__(
        self: Self, cogs_dir: Path, intents: Intents = Intents.default()
    ) -> None:
        super().__init__(intents=intents)

        self._logger = logging.getLogger("Snorm")

        if cogs_dir.is_dir():
            self._logger.info(f"Loading cogs from {cogs_dir}")
            self.load_extensions(
                *[
                    cog_path.as_posix().replace("/", ".")
                    for cog_path in cogs_dir.iterdir()
                ]
            )
        else:
            err_str = f"Cannot load cogs: {cogs_dir} is not a directory"
            self._logger.critical(err_str, exc_info=NotADirectoryError(err_str))

    async def on_ready(self: Self) -> None:
        self._logger.info(f"Logged in as {self.user}")
