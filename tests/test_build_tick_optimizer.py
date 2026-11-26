"""Regression tests for the DrakesCraft_TickOptimizer datapack override builder."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from scripts.build_tick_optimizer import OVERRIDE_FILES, build_tick_optimizer


class BuildTickOptimizerTest(unittest.TestCase):
    """Verify Stellarity, Incendium, and SVM Powers tick override regressions."""

    def test_builds_directory_with_all_optimizations(self) -> None:
        """Verify directory output and key selector/tag optimizations."""
        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory) / "DrakesCraft_TickOptimizer"
            written = build_tick_optimizer(out_dir)
            self.assertEqual(written, len(OVERRIDE_FILES))

            stellarity_main = (
                out_dir / "data/stellarity/function/entity/main.mcfunction"
            ).read_text(encoding="utf-8")
            self.assertIn(
                "type=#stellarity:end_variant_animals,tag=!stellarity.aware,tag=!smithed.entity,predicate=stellarity:entity/end_variant_animals",
                stellarity_main,
            )

            awareness_tag = json.loads(
                (
                    out_dir
                    / "data/stellarity/tags/entity_type/entity_awareness_checks.json"
                ).read_text(encoding="utf-8")
            )
            self.assertFalse(awareness_tag["replace"])
            self.assertIn("#stellarity:end_variant_animals", awareness_tag["values"])

            incendium_main = (
                out_dir / "data/incendium/function/clocks/main.mcfunction"
            ).read_text(encoding="utf-8")
            self.assertNotIn("unless score @s in.eid matches 0..32767", incendium_main)

            incendium_reset = (
                out_dir / "data/incendium/function/technical/entity_id/reset.mcfunction"
            ).read_text(encoding="utf-8")
            self.assertIn(
                "execute as @e[type=#incendium:mobs_no_player,tag=in.checked] run function incendium:technical/entity_id/init",
                incendium_reset,
            )

            svm_tick = (out_dir / "data/svm_ep/function/tick.mcfunction").read_text(
                encoding="utf-8"
            )
            self.assertIn("tag @e[tag=executor] remove executor", svm_tick)
            self.assertIn("tag @e[tag=same_id] remove same_id", svm_tick)
            self.assertNotIn("\ntag @e remove executor", svm_tick)
            self.assertNotIn("\ntag @e remove same_id", svm_tick)
            self.assertIn("kill @e[type=marker,tag=rotator]", svm_tick)
            self.assertIn(
                "execute as @a[scores={svm_ep.restore_health=1..}]", svm_tick
            )
            self.assertIn(
                "execute as @e[tag=svm_ep.black_hole,scores={svm_ep.kill_at=1..}",
                svm_tick,
            )
            self.assertIn(
                "execute as @e[scores={svm_ep.ability.using=0..}] if entity @s[predicate=!svm_ep:time_stopped]",
                svm_tick,
            )
            self.assertIn(
                "execute as @e[type=item_display,scores={svm_ep.particle=1..}", svm_tick
            )

            input_track = (
                out_dir / "data/input/function/slot_change/track.mcfunction"
            ).read_text(encoding="utf-8")
            self.assertIn("execute as @s[tag=svm_ep.power_user]", input_track)

    def test_builds_valid_zip_archive(self) -> None:
        """Verify ZIP archive output contains all expected files and valid JSON."""
        with tempfile.TemporaryDirectory() as directory:
            out_zip = Path(directory) / "DrakesCraft_TickOptimizer.zip"
            written = build_tick_optimizer(out_zip)
            self.assertEqual(written, len(OVERRIDE_FILES))
            with ZipFile(out_zip, "r") as archive:
                self.assertEqual(set(archive.namelist()), set(OVERRIDE_FILES.keys()))
                mcmeta = json.loads(archive.read("pack.mcmeta").decode("utf-8"))
                self.assertEqual(mcmeta["pack"]["min_format"], 61)


if __name__ == "__main__":
    unittest.main()
