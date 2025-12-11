from pathlib import Path
from subprocess import run
from typing import Any

from pytubefix import YouTube  # pyright: ignore[reportMissingTypeStubs]

_empty: Any = object()


def download_segment(
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
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()  # pyright: ignore[reportUnknownMemberType]
    if stream is None:
        msg = "stream not available"
        raise RuntimeError(msg)
    result = stream.download(filename="__temp_full_video.mp4")
    if result is None:
        raise FileNotFoundError(url)
    full_path = Path(result)

    # 2. Вырезаем нужный кусок
    # -ss <start> -to <end> сохраняет качество без повторного энкодинга
    _ = run(  # noqa: S603
        [  # noqa: S607
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            str(start),
            "-to",
            str(end),
            "-i",
            str(full_path),
            "-c",
            "copy",
            str(output),
        ],
        check=True,
    )

    full_path.unlink(missing_ok=True)
    return output


if __name__ == "__main__":
    video = download_segment(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        start=10.0,
        end=25.0,
        output=Path("segment.mp4"),
    )
    print("saved:", video)
