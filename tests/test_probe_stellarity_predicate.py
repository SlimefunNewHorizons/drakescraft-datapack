"""Guard overlay preservation and the evidence accepted by the runtime probe."""

from pathlib import Path
import tempfile
import unittest
import warnings
from zipfile import ZipFile

from scripts.probe_stellarity_predicate import PREDICATE, fixture, summarize


class StellarityPredicateProbeTest(unittest.TestCase):
    def test_preserves_metadata_and_all_overlay_bytes(self):
        entries = {"pack.mcmeta": b'{"pack":{"min_format":94,"max_format":999}}',
                   PREDICATE: b'{"type":"minecraft:location_check"}',
                   "overlay_data_26_2/" + PREDICATE:
                       b'{"condition":"minecraft:location_check"}',
                   "overlay_data_1_21_11/" + PREDICATE: b'[]'}
        with tempfile.TemporaryDirectory() as directory:
            source, output = (Path(directory) / n for n in ("source.zip", "probe.zip"))
            with ZipFile(source, "w") as archive:
                for name, data in entries.items():
                    archive.writestr(name, data)
                archive.writestr("data/minecraft/tags/function/tick.json", b"{}")
            self.assertEqual(set(fixture(source, output)), set(entries))
            with ZipFile(output) as archive:
                self.assertEqual({n: archive.read(n) for n in archive.namelist()}, entries)

    def test_refuses_duplicate_or_missing_input_and_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = (Path(directory) / n for n in ("source.zip", "probe.zip"))
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with ZipFile(source, "w") as archive:
                    archive.writestr("pack.mcmeta", "{}")
                    archive.writestr("pack.mcmeta", "{}")
                    archive.writestr(PREDICATE, "[]")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                fixture(source, output)
            self.assertFalse(output.exists())
            with ZipFile(source, "w") as archive:
                archive.writestr("pack.mcmeta", "{}")
            with self.assertRaisesRegex(ValueError, "Missing"):
                fixture(source, output)
            with ZipFile(source, "a") as archive:
                archive.writestr(PREDICATE, "[]")
            output.write_bytes(b"preserve existing artifact")
            with self.assertRaises(FileExistsError):
                fixture(source, output)
            self.assertEqual(output.read_bytes(), b"preserve existing artifact")

    def test_requires_semantics_clean_parse_and_saved_shutdown(self):
        lines = ["[Server thread/INFO]: Done (1s)!", *[
            f"[Server thread/INFO]: [Server] STELLARITY389_{marker}"
            for marker in ("BELOW", "BOUNDARY", "ABOVE", "END")],
            "[Server thread/INFO]: All dimensions are saved"]
        self.assertTrue(summarize(lines, 0)["ok"])
        for invalid, code in ((lines[:-1], 0), (lines, 1), (lines, None),
                              (lines[1:], 0), (lines[:2] + lines[3:], 0),
                              (lines + ["[Server thread/ERROR]: Bad predicate"], 0),
                              (lines + [lines[1]], 0)):
            self.assertFalse(summarize(invalid, code)["ok"])
        echoes = [line.replace("[Server] ", "") for line in lines]
        self.assertFalse(summarize(echoes, 0)["ok"])


if __name__ == "__main__":
    unittest.main()
