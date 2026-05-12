from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from doctor_link.core.command_runner import run_command


def probe_media(path: Path, ffprobe_binary: str = "ffprobe", timeout_seconds: int = 30) -> dict[str, Any]:
    """Probe a media file using ffprobe and return structured metadata.

    If ffprobe is missing or the file cannot be parsed, the returned payload still
    contains the command result so Doctor link can include it as evidence.
    """
    path = path.resolve()
    command = [
        ffprobe_binary,
        "-v",
        "error",
        "-show_format",
        "-show_streams",
        "-print_format",
        "json",
        str(path),
    ]
    result = run_command(command, timeout_seconds=timeout_seconds)

    payload: dict[str, Any] = {
        "file": str(path),
        "command": result.to_dict(),
        "ok": False,
        "format": None,
        "streams": [],
        "error": None,
    }

    if result.returncode != 0:
        payload["error"] = result.stderr or "ffprobe returned a non-zero exit code."
        return payload

    try:
        parsed = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        payload["error"] = f"Failed to parse ffprobe JSON output: {exc}"
        return payload

    payload["ok"] = True
    payload["format"] = parsed.get("format")
    payload["streams"] = parsed.get("streams", [])
    return payload


def summarize_media_probe(probe: dict[str, Any]) -> dict[str, Any]:
    """Create a compact summary from a full ffprobe payload."""
    streams = probe.get("streams") or []
    video = [item for item in streams if item.get("codec_type") == "video"]
    audio = [item for item in streams if item.get("codec_type") == "audio"]
    subtitles = [item for item in streams if item.get("codec_type") == "subtitle"]

    return {
        "file": probe.get("file"),
        "ok": probe.get("ok"),
        "format_name": (probe.get("format") or {}).get("format_name"),
        "duration": (probe.get("format") or {}).get("duration"),
        "video_streams": len(video),
        "audio_streams": len(audio),
        "subtitle_streams": len(subtitles),
        "video_codecs": sorted({item.get("codec_name") for item in video if item.get("codec_name")}),
        "audio_codecs": sorted({item.get("codec_name") for item in audio if item.get("codec_name")}),
        "subtitle_codecs": sorted({item.get("codec_name") for item in subtitles if item.get("codec_name")}),
        "error": probe.get("error"),
    }
