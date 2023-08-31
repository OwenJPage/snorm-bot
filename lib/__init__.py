import logging
from pathlib import Path

from lib.structures.bot import Snorm


async def main(bot_token: str) -> None:
    logger = logging.getLogger("main")

    logger.info("Initialising bot")
    bot = Snorm(Path("lib/cogs"))

    logger.info("Starting bot")

    await bot.start(bot_token)
