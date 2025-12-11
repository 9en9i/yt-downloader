from __future__ import annotations
from pathlib import Path
from subprocess import run
from pytubefix import YouTube


def download_segment[
    start: float, end: float
](
    url: str,
    *,
    start: start,
    end: end,
    output: Path = Path("output.mp4"),
) -> Path:
    assert end > start, "end must be greater than start"

    # 1. Скачиваем исходник
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    full_path = Path(stream.download(filename="__temp_full_video.mp4"))

    # 2. Вырезаем нужный кусок
    # -ss <start> -to <end> сохраняет качество без повторного энкодинга
    run([
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-ss", str(start),
        "-to", str(end),
        "-i", str(full_path),
        "-c", "copy",
        str(output),
    ], check=True)

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