from types import TracebackType
from typing import Self

from aiohttp import ClientSession
from yarl import URL

from rocket_man.schemas import Video


class FrameXService:
    """ "
    FrameX API service.
    It allows downloading videos, frame by frame.
    """

    base_url = URL("https://framex-dev.wadrid.net") / "api" / "video"

    def __init__(self):
        self.session = ClientSession()

    async def __aenter__(self) -> Self:
        await self.session.__aenter__()
        return self

    async def __aexit__(
        self, tp: type[BaseException] | None, val: BaseException | None, tb: TracebackType | None
    ) -> None:
        await self.session.__aexit__(tp, val, tb)

    @classmethod
    def get_video_url(cls, video_name: str) -> URL:
        """
        Get the URL of a video.
        """
        return cls.base_url / video_name

    @classmethod
    def get_video_frame_url(cls, video_name: str, frame: int) -> URL:
        """
        Get the URL of a single frame from a video.
        """
        return cls.base_url / video_name / "frame" / str(frame)

    async def list_videos(self) -> list[Video]:
        """ "
        List all videos.
        """
        url = self.base_url
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            data = await resp.read()
            return Video.validate_json_list(data)

    async def get_video(self, video_name) -> Video:
        """
        Get video metadata.
        """
        url = self.get_video_url(video_name)
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            data = await resp.read()
            return Video.validate_json(data)

    async def get_video_frame(self, video_name: str, frame: int) -> bytes:
        """
        Get a single frame from a video as a JPEG image.
        """
        url = self.get_video_frame_url(video_name, frame)
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.read()
