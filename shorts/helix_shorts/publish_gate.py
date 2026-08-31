"""Human publish gate. HelixBuilds shorts never auto-posts.

No Instagram, YouTube, or Bilibili accounts. A human must export from
OpenCut (the HelixBuilds editing host) if anything is published later.
"""

from __future__ import annotations

from typing import Any, Mapping

from helix_shorts import HOST_REPO, PRODUCT_NAME, PUBLISH_HELD

FORBIDDEN_KEYS = (
    "auto_post",
    "youtube_upload",
    "instagram_upload",
    "bilibili_upload",
    "ig_account",
    "yt_account",
)


class PublishGateError(ValueError):
    """Raised when a manifest tries to skip the human publish gate."""


def publish_block() -> dict[str, Any]:
    return {
        "status": PUBLISH_HELD,
        "auto_post": False,
        "accounts_required": False,
        "youtube": False,
        "instagram": False,
        "bilibili": False,
        "instruction": (
            "Review clips, edit in OpenCut (HelixBuilds editing), then a human "
            "publishes. This pipeline does not post."
        ),
    }


def llm_block() -> dict[str, Any]:
    return {
        "used": False,
        "dashscope": False,
        "qwen": False,
        "openai": False,
        "gemini": False,
        "path": "srt-heuristic-or-duration-split",
    }


def assert_held_for_human(manifest: Mapping[str, Any]) -> None:
    publish = manifest.get("publish")
    if not isinstance(publish, Mapping):
        raise PublishGateError("manifest missing publish block")
    if publish.get("status") != PUBLISH_HELD:
        raise PublishGateError(
            f"publish.status must be {PUBLISH_HELD!r}, got {publish.get('status')!r}"
        )
    if publish.get("auto_post") is not False:
        raise PublishGateError("auto_post must be false")
    for key in ("youtube", "instagram", "bilibili"):
        if publish.get(key) is True:
            raise PublishGateError(f"publish.{key} must not be enabled")
    if manifest.get("product") != PRODUCT_NAME:
        raise PublishGateError("manifest is not HelixBuilds shorts")
    if manifest.get("host") != HOST_REPO:
        raise PublishGateError("manifest host must be helixmaximusai/OpenCut")
