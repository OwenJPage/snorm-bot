import asyncio
import logging
from collections.abc import Awaitable
from datetime import timedelta
from enum import Enum
from functools import cached_property
from typing import Any, Self, TypedDict

from pytube import Search
from yt_dlp import YoutubeDL


class Track:
    def __init__(self, title: str, url: str, thumbnail: str, duration_seconds: int):
        self._title = title
        self._url = url
        self._thumbnail = thumbnail
        self._duration_seconds = duration_seconds

    @property
    def title(self) -> str:
        return self._title

    @property
    def url(self) -> str:
        return self._url

    @property
    def thumbnail(self) -> str:
        return self._thumbnail

    @cached_property
    def duration(self) -> timedelta:
        return timedelta(seconds=self._duration_seconds)


class SearchDataType(Enum):
    TRACK = 1
    PLAYLIST = 2


class SearchData(TypedDict):
    type: SearchDataType
    title: str
    thumbnail: str
    length: int
    url: str


class YouTube:
    logger = logging.getLogger("handlers.YouTube")
    yt_dl = YoutubeDL(
        {
            "format": "bestaudio",
            "default_search": "ytsearch",
            "logger": logger.getChild("YoutubeDL"),
            "extract_flat": "in_playlist",
        }
    )

    @staticmethod
    def _generate_thumbnail_url(video_id: str) -> str:
        return f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"

    def __init__(self: Self):
        pass

    @classmethod
    async def _process_video(cls, info: Any) -> Track:
        return Track(
            title=info["title"],
            url=info["url"],
            thumbnail=cls._generate_thumbnail_url(info["id"]),
            duration_seconds=info["duration"],
        )

    @classmethod
    async def _process_playlist_video(cls, url: str) -> Track:
        info = await asyncio.to_thread(cls.yt_dl.extract_info, url=url, download=False)

        return await cls._process_video(info)

    @classmethod
    async def search_tracks(
        cls, query: str
    ) -> tuple[list[Awaitable[Track]], SearchData]:
        info = await asyncio.to_thread(
            cls.yt_dl.extract_info, url=query, download=False
        )

        tracks = (
            [
                asyncio.create_task(cls._process_playlist_video(v["url"]))
                for v in info["entries"]
            ]
            if "entries" in info
            else [cls._process_video(info)]
        )

        data = {
            "title": info["entries"][0]["title"]
            if "entries" in info and len(info["entries"]) == 1
            else info["title"],
            "thumbnail": cls._generate_thumbnail_url(info["entries"][0]["id"])
            if "entries" in info
            else info["thumbnail"],
            **(
                (
                    {
                        "type": SearchDataType.PLAYLIST,
                        "length": len(info["entries"]),
                        "url": info["webpage_url"],
                    }
                    if len(info["entries"]) > 1
                    else {
                        "type": SearchDataType.TRACK,
                        "length": info["entries"][0]["duration"],
                        "url": info["entries"][0]["url"],
                    }
                )
                if "entries" in info
                else {
                    "type": SearchDataType.TRACK,
                    "length": info["duration"],
                    "url": info["webpage_url"],
                }
            ),
        }

        return tracks, data

    @classmethod
    def get_autocompletes(cls, query: str) -> list[str]:
        # TODO: Find a way to use yt-dlp

        if query is None or query == "":
            return []

        # TODO: Clean
        logger = cls.logger.getChild("get_autocompletes")
        logger.info(f"Autocompleting {query}")
        search = Search(query)
        # suggestions = search.completion_suggestions
        results = map(lambda r: r.title, search.results[:10])
        autocompletes = [*results]
        # autocompletes = [*(results or []), *(suggestions or [])]
        logger.info(f"Suggestions: {autocompletes}")

        return autocompletes
