from datetime import datetime
from enum import Enum

from discord import Colour, Embed


class SnormEmbedColour(Enum):
    # GOOD = Colour(0x96ff62)
    # BAD = Colour(0xff6262)
    # NEUTRAL = Colour(0x62d8ff)
    GOOD = Colour.brand_green()
    BAD = Colour.brand_red()
    NEUTRAL = Colour.blurple()


class SnormEmbed(Embed):
    def __init__(
        self, title: str, colour: SnormEmbedColour, description: str = Embed.Empty
    ):
        super().__init__(
            title=title,
            description=description,
            timestamp=datetime.now(),
            colour=colour.value,
        )
        self.set_footer(text="Snorm")


class ErrorEmbed(SnormEmbed):
    def __init__(self, message: str, error: Exception | None = None):
        super().__init__(
            title="An error occurred!",
            description=message if error is None else f"{message}\n*{error}*",
            colour=SnormEmbedColour.BAD,
        )
