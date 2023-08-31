import logging
from typing import Dict, List, Self

from discord import (
    ApplicationContext,
    AutocompleteContext,
    Bot,
    Cog,
    slash_command,
)
from discord.commands import Option, guild_only

from lib.cogs.youtube.embeds import (
    EnqueuedPlaylistEmbed,
    EnqueuedTrackEmbed,
    NoVoiceChannelEmbed,
    WrongVoiceChannelEmbed,
)
from lib.cogs.youtube.queue_service import QueueHandler, State
from lib.handlers.YouTube import SearchDataType, YouTube as YouTubeHandler
from lib.structures.snorm_embed import ErrorEmbed


class YouTube(Cog):
    def __init__(self: Self, bot: Bot):
        self._bot = bot
        self._logger = logging.getLogger("cogs.YouTube")

        self._queues: Dict[int, QueueHandler] = {}

    # _youtube_group = SlashCommandGroup(name="youtube", description="YouTube related commands")

    @staticmethod
    def play_video_autocomplete(ctx: AutocompleteContext) -> List[str]:
        return YouTubeHandler.get_autocompletes(ctx.value)

    @slash_command(name="play", description="Search for a YouTube video and play it")
    @guild_only()
    async def play_video(
        self: Self,
        ctx: ApplicationContext,
        query: Option(
            str,
            "The search query, either a video name or a url",  # autocomplete=play_video_autocomplete,
        ),
    ) -> None:
        await ctx.defer()  # Display thinking while the bot does its thing

        if ctx.user.voice is None:
            await ctx.send_followup(embed=NoVoiceChannelEmbed(), ephemeral=True)
            return

        # Check if queue handler already exists
        if (
            ctx.guild_id not in self._queues
            or await self._queues[ctx.guild_id].check_state() == State.DEAD
        ):
            # Create new queue handler
            new_handler = QueueHandler(ctx.user.voice.channel, ctx.channel)
            await new_handler.start()

            self._queues[ctx.guild_id] = new_handler

        handler = self._queues[ctx.guild_id]

        if not handler.check_channel(ctx.user.voice.channel):
            await ctx.send_followup(embed=WrongVoiceChannelEmbed(), ephemeral=True)
            return

        try:
            tracks, data = await YouTubeHandler.search_tracks(query)

            # TODO: Probably a good idea to extract this to a separate method
            if await handler.check_state() == State.DEAD:
                handler = QueueHandler(ctx.user.voice.channel, ctx.channel)
                await handler.start()
                self._queues[ctx.guild_id] = handler

            await handler.enqueue(tracks)

            match data["type"]:
                case SearchDataType.TRACK:
                    await ctx.send_followup(
                        embed=EnqueuedTrackEmbed(
                            track_name=data["title"],
                            thumbnail=data["thumbnail"],
                            url=data["url"],
                        )
                    )
                case SearchDataType.PLAYLIST:
                    await ctx.send_followup(
                        embed=EnqueuedPlaylistEmbed(
                            playlist_name=data["title"],
                            thumbnail=data["thumbnail"],
                            track_count=data["length"],
                            url=data["url"],
                        )
                    )
        except Exception as e:
            self._logger.error(
                "Error occurred while retrieving query results", exc_info=e
            )
            await ctx.send_followup(
                embed=ErrorEmbed(
                    message="Error while retrieving query results", error=e
                )
            )
