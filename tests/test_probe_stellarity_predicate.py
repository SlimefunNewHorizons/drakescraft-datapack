"""Guard overlay preservation and the evidence accepted by the runtime probe."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch
import warnings
from zipfile import ZipFile

from scripts.probe_stellarity_predicate import PREDICATE, fixture, main, summarize


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

    def run_probe(self, *, write_error=None, flush_error=None, wait_error=None):
        """Exercise main with real fixture files and a controlled child process."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "source.zip"
            with ZipFile(archive, "w") as source:
                source.writestr("pack.mcmeta", "{}")
                source.writestr(PREDICATE, "[]")
            home = root / "server"
            for name in ("libraries", "cache", "versions"):
                (home / name).mkdir(parents=True)
            jar = home / "server.jar"
            jar.write_bytes(b"mock server; never executed")
            work = root / "probe"
            process = Mock()
            process.returncode = None
            process.poll.side_effect = lambda: process.returncode
            process.stdout = io.StringIO("\n".join([
                "[Server thread/INFO]: Done (1s)!", *[
                    f"[Server thread/INFO]: [Server] STELLARITY389_{marker}"
                    for marker in ("BELOW", "BOUNDARY", "ABOVE", "END")],
                "[Server thread/INFO]: Saved the game",
                "[Server thread/INFO]: All dimensions are saved", "",
            ]))
            process.stdin.write.side_effect = write_error
            process.stdin.flush.side_effect = flush_error

            def wait(timeout):
                if wait_error is not None:
                    raise wait_error
                process.returncode = 0
                return 0

            process.wait.side_effect = wait
            args = ["probe", "--archive", str(archive), "--server-home", str(home),
                    "--server-jar", str(jar), "--work-dir", str(work)]
            with patch("sys.argv", args), patch(
                    "scripts.probe_stellarity_predicate.subprocess.Popen",
                    return_value=process), redirect_stdout(io.StringIO()):
                code = main()
            result = json.loads((work / "result.json").read_text())
            self.assertTrue((work / "console.log").is_file())
            self.assertIn(PREDICATE, result["predicate_inputs"])
            self.assertEqual(len(result["archive_sha256"]), 64)
            self.assertEqual(len(result["server_jar_sha256"]), 64)
            return code, result, process

    def test_main_records_success_after_wait(self):
        code, result, process = self.run_probe()
        self.assertEqual(code, 0)
        self.assertTrue(result["ok"])
        self.assertIsNone(result["failure"])
        process.wait.assert_called_once_with(timeout=120)
        self.assertEqual(process.stdin.write.call_args.args, ("stop\n",))

    def test_broken_or_closed_stdin_still_waits_and_writes_failure_evidence(self):
        for method, error in (("write", BrokenPipeError("write pipe closed")),
                              ("flush", BrokenPipeError("flush pipe closed")),
                              ("write", ValueError("I/O operation on closed file"))):
            with self.subTest(method=method, error=type(error).__name__):
                code, result, process = self.run_probe(**{method + "_error": error})
                self.assertEqual(code, 1)
                self.assertFalse(result["ok"])
                self.assertIn(str(error), result["failure"])
                self.assertIn("Shutdown command failed", result["failure"])
                process.wait.assert_called_once_with(timeout=120)
                self.assertEqual(result["exit_code"], 0)

    def test_shutdown_failure_preserves_the_original_command_error(self):
        code, result, process = self.run_probe(write_error=[
            OSError("original command failure"), BrokenPipeError("stop pipe closed")])
        self.assertEqual(code, 1)
        self.assertIn("original command failure", result["failure"])
        self.assertIn("stop pipe closed", result["failure"])
        process.wait.assert_called_once_with(timeout=120)

    def test_stop_failure_prevents_success_after_all_checks_pass(self):
        code, result, process = self.run_probe(write_error=[
            None, None, None, None, None, BrokenPipeError("stop pipe closed")])
        self.assertEqual(code, 1)
        self.assertFalse(result["ok"])
        self.assertTrue(result["done"])
        self.assertTrue(result["saved"])
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["failure"], "Shutdown command failed: stop pipe closed")
        process.wait.assert_called_once_with(timeout=120)

    def test_shutdown_timeout_retains_both_failures_and_child(self):
        code, result, process = self.run_probe(
            write_error=BrokenPipeError("closed pipe"),
            wait_error=subprocess.TimeoutExpired("mock server", 120))
        self.assertEqual(code, 1)
        self.assertFalse(result["ok"])
        self.assertIsNone(result["exit_code"])
        self.assertIn("closed pipe", result["failure"])
        self.assertIn("Shutdown timed out", result["failure"])
        process.wait.assert_called_once_with(timeout=120)
        process.terminate.assert_not_called()
        process.kill.assert_not_called()


if __name__ == "__main__":
    unittest.main()
