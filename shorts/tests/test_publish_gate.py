from __future__ import annotations

import unittest

from helix_shorts import HOST_REPO, PRODUCT_NAME, PUBLISH_HELD
from helix_shorts.publish_gate import PublishGateError, assert_held_for_human, publish_block


def _ok() -> dict:
    return {
        "product": PRODUCT_NAME,
        "host": HOST_REPO,
        "publish": publish_block(),
    }


class PublishGateTests(unittest.TestCase):
    def test_held_passes(self) -> None:
        assert_held_for_human(_ok())

    def test_auto_post_blocked(self) -> None:
        manifest = _ok()
        manifest["publish"]["auto_post"] = True
        with self.assertRaises(PublishGateError):
            assert_held_for_human(manifest)

    def test_youtube_blocked(self) -> None:
        manifest = _ok()
        manifest["publish"]["youtube"] = True
        with self.assertRaises(PublishGateError):
            assert_held_for_human(manifest)

    def test_status_must_be_held(self) -> None:
        manifest = _ok()
        manifest["publish"]["status"] = "published"
        with self.assertRaises(PublishGateError):
            assert_held_for_human(manifest)

    def test_block_shape(self) -> None:
        block = publish_block()
        self.assertEqual(block["status"], PUBLISH_HELD)
        self.assertIs(block["auto_post"], False)
        self.assertIs(block["instagram"], False)
        self.assertIs(block["bilibili"], False)


if __name__ == "__main__":
    unittest.main()
