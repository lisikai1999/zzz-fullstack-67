import subprocess
import shutil
from pathlib import Path

from models import Media


def generate_proxy(media: Media, proxies_dir: Path) -> Path | None:
    proxies_dir.mkdir(parents=True, exist_ok=True)

    if media.mime_type and media.mime_type.startswith("image/"):
        return _generate_image_proxy(media, proxies_dir)

    if media.mime_type and media.mime_type.startswith("video/"):
        return _generate_video_proxy(media, proxies_dir)

    return None


def _generate_image_proxy(media: Media, proxies_dir: Path) -> Path | None:
    try:
        from PIL import Image
        img = Image.open(media.original_path)
        img.thumbnail((854, 480))
        proxy_path = proxies_dir / f"{media.id}_proxy.jpg"
        img.convert("RGB").save(proxy_path, "JPEG", quality=60)
        img.close()
        return proxy_path
    except Exception:
        return None


def _generate_video_proxy(media: Media, proxies_dir: Path) -> Path | None:
    if not shutil.which("ffmpeg"):
        return _generate_video_thumbnail(media, proxies_dir)

    proxy_path = proxies_dir / f"{media.id}_proxy.mp4"
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(media.original_path),
                "-vf", "scale=-2:480",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "28",
                "-c:a", "aac",
                "-b:a", "64k",
                "-movflags", "+faststart",
                str(proxy_path),
            ],
            capture_output=True,
            timeout=300,
        )
        if proxy_path.exists() and proxy_path.stat().st_size > 0:
            return proxy_path
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return _generate_video_thumbnail(media, proxies_dir)


def _generate_video_thumbnail(media: Media, proxies_dir: Path) -> Path | None:
    if not shutil.which("ffmpeg"):
        return None

    thumb_path = proxies_dir / f"{media.id}_thumb.jpg"
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(media.original_path),
                "-vframes", "1",
                "-vf", "scale=-2:480",
                str(thumb_path),
            ],
            capture_output=True,
            timeout=30,
        )
        if thumb_path.exists():
            return thumb_path
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def probe_video_metadata(file_path: Path) -> dict:
    """Use ffprobe to get real video dimensions and duration."""
    if not shutil.which("ffprobe"):
        return {}

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            info = {}
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    info["width"] = int(stream.get("width", 0))
                    info["height"] = int(stream.get("height", 0))
                    break
            fmt = data.get("format", {})
            if "duration" in fmt:
                info["duration"] = float(fmt["duration"])
            return info
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    return {}
