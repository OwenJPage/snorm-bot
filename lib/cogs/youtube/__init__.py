from discord import Bot

from .cog import YouTube


def setup(bot: Bot) -> None:
    bot.add_cog(YouTube(bot))
