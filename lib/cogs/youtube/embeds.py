from lib.structures.snorm_embed import SnormEmbed, SnormEmbedColour


class NowPlayingEmbed(SnormEmbed):
    def __init__(self, track_name: str, thumbnail: str):
        super().__init__(
            title="Now playing", description=track_name, colour=SnormEmbedColour.GOOD
        )
        self.set_thumbnail(url=thumbnail)


class EnqueuedTrackEmbed(SnormEmbed):
    def __init__(self, track_name: str, thumbnail: str, url: str):
        super().__init__(
            title="Enqueued a track",
            description=f"[**{track_name}**]({url})",
            colour=SnormEmbedColour.GOOD,
        )
        self.set_image(url=thumbnail)


class EnqueuedPlaylistEmbed(SnormEmbed):
    def __init__(self, playlist_name: str, thumbnail: str, track_count: int, url: str):
        super().__init__(
            title=f"Enqueued {track_count} tracks",
            description=f"[**{playlist_name}**]({url})",
            colour=SnormEmbedColour.GOOD,
        )
        self.set_image(url=thumbnail)


class InactiveDisconnectEmbed(SnormEmbed):
    def __init__(self):
        super().__init__(
            title="Left the voice channel due to inactivity",
            colour=SnormEmbedColour.NEUTRAL,
        )


class NoVoiceChannelEmbed(SnormEmbed):
    def __init__(self):
        super().__init__(
            title="You must be in a voice channel to use this command",
            colour=SnormEmbedColour.BAD,
        )


class WrongVoiceChannelEmbed(SnormEmbed):
    def __init__(self):
        super().__init__(
            title="Snorm is already in another voice channel",
            colour=SnormEmbedColour.BAD,
        )
