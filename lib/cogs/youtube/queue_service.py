import asyncio
import logging
from asyncio import Event, Lock, Task
from collections.abc import Awaitable
from enum import Enum
from typing import List

from discord import (
    ClientException,
    FFmpegOpusAudio,
    StageChannel,
    TextChannel,
    VoiceChannel,
    VoiceClient,
)

from lib.cogs.youtube.embeds import InactiveDisconnectEmbed, NowPlayingEmbed
from lib.handlers.YouTube import Track
from lib.structures.editable_queue import EditableQueue
from lib.structures.snorm_embed import ErrorEmbed


class State(Enum):
    INIT = 0
    ACTIVE = 1
    DEAD = 2


class QueueHandler:
    _ffmpeg_options = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }
    _logger = logging.getLogger("QueueHandler")

    def __init__(
        self, voice_channel: VoiceChannel | StageChannel, text_channel: TextChannel
    ):
        self._logger.info("Initialising new QueueHandler")
        self._lock = Lock()
        self._queue: EditableQueue[Awaitable[Track]] = EditableQueue()
        self._state = State.INIT
        self._voice_channel = voice_channel
        self._text_channel = text_channel
        self._voice_client: VoiceClient | None = None
        self._runner: Task | None = None

    async def start(self):
        self._logger.info("Starting QueueHandler service")
        await self._init_voice(self._voice_channel)
        self._runner = asyncio.create_task(self._run())

    async def _init_voice(self, voice_channel: VoiceChannel | StageChannel) -> None:
        try:
            self._voice_client = await voice_channel.connect()
            self._state = State.ACTIVE
        except ClientException:
            # TODO: Handle these errors appropriately
            raise

    async def _handle_disconnect(self) -> None:
        self._state = State.DEAD

    @classmethod
    def _play_finished(cls, event: Event):
        def inner(error: Exception | None) -> None:
            cls._logger.info("Finished playing")
            if error is not None:
                raise error

            event.set()

        return inner

    async def _run(self) -> None:
        while await self.check_state() == State.ACTIVE:
            try:
                next_track = await (
                    await asyncio.wait_for(self._queue.get(), timeout=300)
                )

                finished_playing_event = Event()
                self._logger.info(f"Playing {next_track.title}")
                self._voice_client.play(
                    FFmpegOpusAudio(next_track.url, **self._ffmpeg_options),
                    after=self._play_finished(finished_playing_event),
                )

                await self._text_channel.send(
                    embed=NowPlayingEmbed(
                        track_name=next_track.title, thumbnail=next_track.thumbnail
                    )
                )

                self._logger.info(f"Waiting until track has finished")
                await finished_playing_event.wait()
                self._logger.info(f"Finished waiting")
            except TimeoutError:
                await self._voice_client.disconnect(force=True)
                await self._handle_disconnect()
                await self._text_channel.send(embed=InactiveDisconnectEmbed())
                return
            except Exception as e:
                self._logger.error(f"Error in queue handler", exc_info=e)
                await self._text_channel.send(
                    embed=ErrorEmbed(f"Error while playing track", error=e)
                )
        else:
            self._logger.error("Handler is dead")

    async def enqueue(self, tracks: List[Awaitable[Track]]) -> None:
        async with self._lock:
            for track in tracks:
                await self._queue.put(track)

    async def check_state(self) -> State:
        if not self._voice_client.is_connected():
            await self._handle_disconnect()

        return self._state

    def check_channel(self, channel: VoiceChannel | StageChannel) -> bool:
        return self._voice_client.channel.id == channel.id
