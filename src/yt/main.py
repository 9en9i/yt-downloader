import asyncio
from pathlib import Path
from typing import Any

import ffmpeg  # pyright: ignore[reportMissingTypeStubs]
from pytubefix import YouTube  # pyright: ignore[reportMissingTypeStubs]

_empty: Any = object()


async def download_segment(
    url: str,
    *,
    start: float,
    end: float,
    output: Path = _empty,
) -> Path:
    if output is _empty:
        output = Path("segment.mp4")

    if end < start:
        msg = "end must be greater than start"
        raise RuntimeError(msg)

    # 1. Скачиваем исходник
    yt = YouTube(
        url,
        use_oauth=True,
        allow_oauth_cache=True,
        token_file="./yt_oauth.json",  # noqa: S106
    )
    stream = yt.streams.get_highest_resolution()  # pyright: ignore[reportUnknownMemberType]
    if stream is None:
        msg = "stream not available"
        raise RuntimeError(msg)

    direct_url: str = stream.url  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    # ffmpeg-python работает sync, так что гоняем его в отдельном треде
    def run_ffmpeg() -> None:
        (
            ffmpeg.input(direct_url, ss=start, to=end)  # pyright: ignore[reportUnknownMemberType]
            .output(str(output), c="copy", loglevel="error")
            .overwrite_output()
            .run()
        )

    await asyncio.to_thread(run_ffmpeg)
    return output


async def main() -> None:
    out = await download_segment(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        start=10.0,
        end=25.0,
        output=Path("segment.mp4"),
    )
    print("saved:", out)


if __name__ == "__main__":
    asyncio.run(main())
