"""Evaluate Stellarity's shipped void predicate on a disposable Paper server.

Copy only the predicate, its overlays and pack metadata into a fixture. Never
start the supplied server directory or change its worlds, plugins or configs.
Run inside a resource-limited scope through build_seguro.sh on shared hosts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import queue
import re
import shutil
import subprocess
import threading
import time
from zipfile import ZipFile


PREDICATE = "data/stellarity/predicate/location/in_void.json"
MARKERS = {"BELOW", "BOUNDARY", "ABOVE", "END"}


def fixture(source: Path, output: Path) -> dict[str, str]:
    """Preserve every shipped overlay and reject duplicate or missing inputs."""
    with ZipFile(source) as archive:
        names = archive.namelist()
        selected = [n for n in names if n == "pack.mcmeta" or n == PREDICATE
                    or n.endswith("/" + PREDICATE)]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate archive entries")
        if "pack.mcmeta" not in selected or PREDICATE not in selected:
            raise ValueError("Missing Stellarity metadata or base predicate")
        payloads = {name: archive.read(name) for name in selected}
        for payload in payloads.values():
            json.loads(payload)
    with ZipFile(output, "x") as target:
        for name, payload in payloads.items():
            target.writestr(name, payload)
    return {name: hashlib.sha256(data).hexdigest() for name, data in payloads.items()}


def summarize(lines: list[str], exit_code: int | None) -> dict:
    """Accept actual server responses, never console echoes or partial results."""
    seen = [match[1] for line in lines if (match := re.search(
        r"\[Server\] STELLARITY389_(BELOW|BOUNDARY|ABOVE|END)\s*$", line))]
    errors = sum(bool(re.search(r"\bERROR\]", line)) for line in lines)
    warnings = sum(bool(re.search(r"\bWARN\]", line)) for line in lines)
    done = any("Done (" in line for line in lines)
    saved = any("All dimensions are saved" in line for line in lines)
    ok = (exit_code == 0 and done and saved and errors == 0
          and len(seen) == len(MARKERS) and set(seen) == MARKERS)
    return {"ok": ok, "exit_code": exit_code, "done": done, "saved": saved,
            "markers": seen, "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--server-home", required=True, type=Path)
    parser.add_argument("--server-jar", required=True, type=Path)
    parser.add_argument("--work-dir", required=True, type=Path,
                        help="New disposable directory; must not exist")
    parser.add_argument("--java", default="java")
    args = parser.parse_args()
    root = args.work_dir.resolve()
    root.mkdir(parents=True, exist_ok=False)
    packs = root / "world/datapacks"
    packs.mkdir(parents=True)
    inputs = fixture(args.archive, packs / "Stellarity-predicate.zip")
    for name in ("libraries", "cache", "versions"):
        shutil.copytree(args.server_home / name, root / name)
    (root / "eula.txt").write_text("eula=true\n")
    flat = json.dumps({"biome": "minecraft:plains", "layers": [
        {"block": "minecraft:bedrock", "height": 1}]})
    (root / "server.properties").write_text("\n".join([
        "server-ip=127.0.0.1", "server-port=0", "online-mode=true",
        "white-list=true", "max-players=1", "enable-rcon=false",
        "enable-query=false", "management-server-enabled=false",
        "pause-when-empty-seconds=-1", "level-seed=389",
        "level-type=minecraft:flat", "generator-settings=" + flat,
        "view-distance=2", "simulation-distance=2", "generate-structures=false",
        "allow-nether=false", "max-tick-time=60000", "spawn-chunk-radius=0", "",
    ]))
    (root / "bukkit.yml").write_text("settings:\n  allow-end: false\n")
    events = queue.Queue()
    lines = []
    with (root / "console.log").open("w") as log:
        process = subprocess.Popen([
            args.java, "-Xms512M", "-Xmx2G", "-XX:ActiveProcessorCount=2",
            "-Dterminal.jline=false", "-Dterminal.ansi=false", "-jar",
            str(args.server_jar.resolve()), "--nogui"], cwd=root,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1)

        def read():
            for line in process.stdout:
                log.write(line)
                log.flush()
                lines.append(line.rstrip())
                events.put(line)

        reader = threading.Thread(target=read, daemon=True)
        reader.start()

        def send(command):
            process.stdin.write(command + "\n")
            process.stdin.flush()

        def wait_for(needle, timeout=180):
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                try:
                    if needle in events.get(timeout=1):
                        return
                except queue.Empty:
                    if process.poll() is not None:
                        raise RuntimeError("Server exited before expected response")
            raise TimeoutError("Missing server response: " + needle)

        failure = None
        try:
            wait_for("Done (")
            for y, condition, marker in ((-65, "if", "BELOW"),
                                         (-64, "if", "BOUNDARY"),
                                         (-63, "unless", "ABOVE")):
                send(f"execute positioned 0 {y} 0 {condition} predicate "
                     f"stellarity:location/in_void run say STELLARITY389_{marker}")
            send("say STELLARITY389_END")
            wait_for("[Server] STELLARITY389_END", timeout=30)
            send("save-all flush")
            wait_for("Saved the game", timeout=60)
        except (OSError, RuntimeError, TimeoutError) as error:
            failure = str(error)
        finally:
            if process.poll() is None:
                send("stop")
                try:
                    process.wait(timeout=120)
                except subprocess.TimeoutExpired:
                    failure = "Shutdown timed out; process retained for investigation"
            if process.poll() is not None:
                reader.join(timeout=5)
        result = summarize(lines, process.poll())
        result.update({"archive_sha256": hashlib.sha256(args.archive.read_bytes()).hexdigest(),
                       "server_jar_sha256": hashlib.sha256(args.server_jar.read_bytes()).hexdigest(),
                       "predicate_inputs": inputs, "failure": failure})
        result["ok"] = result["ok"] and failure is None
        (root / "result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
