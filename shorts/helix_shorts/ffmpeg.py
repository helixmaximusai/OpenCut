"""Resolve ffmpeg/ffprobe. Adapted from AutoClip backend/utils/ffmpeg_utils.py."""

from __future__ import annotations

import os
import shutil
from typing import Optional


def _from_env(names: list[str]) -> Optional[str]:
    for name in names:
        value = os.getenv(name)
        if value and os.path.exists(value):
            return value
    return None


def get_ffmpeg_path() -> str:
    env_path = _from_env(["FFMPEG_PATH", "AUTOCLIP_FFMPEG_PATH"])
    if env_path:
        return env_path
    which = shutil.which("ffmpeg")
    if which:
        return which
    return "ffmpeg"


def get_ffprobe_path() -> str:
    env_path = _from_env(["FFPROBE_PATH", "AUTOCLIP_FFPROBE_PATH"])
    if env_path:
        return env_path
    which = shutil.which("ffprobe")
    if which:
        return which
    return "ffprobe"
