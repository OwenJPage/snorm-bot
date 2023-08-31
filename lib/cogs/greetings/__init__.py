from discord import Bot

from .cog import Greetings


def setup(bot: Bot) -> None:
    bot.add_cog(Greetings(bot))
