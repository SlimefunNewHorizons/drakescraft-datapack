"""Regression tests for bounded Dungeons and Taverns exploration maps."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from scripts.patch_dungeons_taverns_maps import MAP_PREFIX, patch_archive


class PatchDungeonsTavernsMapsTest(unittest.TestCase):
    """Verify targeted mutation, archive preservation, and fail-closed behavior."""

    def test_patches_only_nova_map_tables(self) -> None:
        """Limit target maps without changing an unrelated exploration-map table."""
        target = {
            "function": "minecraft:exploration_map",
            "destination": "#nova_structures:village",
        }
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.zip"
            output = Path(directory) / "output.zip"
            with ZipFile(source, "w") as archive:
                archive.writestr(f"{MAP_PREFIX}village.json", json.dumps(target))
                archive.writestr("data/other/loot_table/map.json", json.dumps(target))
                archive.writestr("pack.mcmeta", "unchanged")

            files, functions = patch_archive(source, output, 8)

            self.assertEqual((files, functions), (1, 1))
            with ZipFile(output) as archive:
                patched = json.loads(archive.read(f"{MAP_PREFIX}village.json"))
                unrelated = json.loads(archive.read("data/other/loot_table/map.json"))
                self.assertEqual(patched["search_radius"], 8)
                self.assertNotIn("search_radius", unrelated)
                self.assertEqual(archive.read("pack.mcmeta"), b"unchanged")

    def test_rejects_archive_without_target(self) -> None:
        """Fail instead of publishing an archive whose upstream layout changed."""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.zip"
            output = Path(directory) / "output.zip"
            with ZipFile(source, "w") as archive:
                archive.writestr("pack.mcmeta", "{}")

            with self.assertRaisesRegex(RuntimeError, "No unbounded"):
                patch_archive(source, output, 8)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
