"""Bound synchronous exploration-map searches in Dungeons and Taverns archives."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile


MAP_PREFIX = "data/nova_structures/loot_table/maps/"
EXPLORATION_MAP = "minecraft:exploration_map"
DEFAULT_RADIUS = 8


def bound_exploration_maps(value: object, radius: int) -> int:
    """Set a small search radius on every exploration-map function in a JSON tree."""
    changed = 0
    if isinstance(value, dict):
        if value.get("function") == EXPLORATION_MAP:
            if value.get("search_radius") != radius:
                value["search_radius"] = radius
                changed += 1
        for child in value.values():
            changed += bound_exploration_maps(child, radius)
    elif isinstance(value, list):
        for child in value:
            changed += bound_exploration_maps(child, radius)
    return changed


def count_unbounded(value: object, radius: int) -> int:
    """Count exploration-map functions that do not use the required radius."""
    if isinstance(value, dict):
        own = int(
            value.get("function") == EXPLORATION_MAP
            and value.get("search_radius") != radius
        )
        return own + sum(count_unbounded(child, radius) for child in value.values())
    if isinstance(value, list):
        return sum(count_unbounded(child, radius) for child in value)
    return 0


def patch_archive(source_path: Path, output_path: Path, radius: int) -> tuple[int, int]:
    """Write and verify a patched archive while preserving unrelated ZIP entries."""
    changed_functions = 0
    changed_files = 0
    try:
        with ZipFile(source_path, "r") as source, ZipFile(
            output_path, "w", ZIP_DEFLATED
        ) as output:
            for entry in source.infolist():
                payload = source.read(entry)
                if entry.filename.startswith(MAP_PREFIX) and entry.filename.endswith(".json"):
                    document = json.loads(payload.decode("utf-8-sig"))
                    changed = bound_exploration_maps(document, radius)
                    if changed:
                        payload = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode()
                        changed_functions += changed
                        changed_files += 1
                        print(f"[FIX] {entry.filename}: {changed}")
                output.writestr(entry, payload)
    except (OSError, UnicodeError, json.JSONDecodeError, BadZipFile) as error:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(f"Could not patch {source_path}: {error}") from error

    if changed_functions == 0:
        output_path.unlink(missing_ok=True)
        raise RuntimeError("No unbounded Dungeons and Taverns map functions were found")

    try:
        with ZipFile(output_path, "r") as verification:
            unbounded = 0
            for entry in verification.infolist():
                if entry.filename.startswith(MAP_PREFIX) and entry.filename.endswith(".json"):
                    document = json.loads(verification.read(entry).decode("utf-8-sig"))
                    unbounded += count_unbounded(document, radius)
            corrupt_entry = verification.testzip()
    except (OSError, UnicodeError, json.JSONDecodeError, BadZipFile) as error:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(f"Could not verify patched archive: {error}") from error

    if unbounded or corrupt_entry:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"Patched archive failed verification: unbounded={unbounded}, corrupt={corrupt_entry}"
        )
    return changed_files, changed_functions


def main() -> int:
    """Parse CLI arguments and create one bounded Dungeons and Taverns archive."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="original Dungeons and Taverns ZIP")
    parser.add_argument("output", type=Path, help="destination for the patched ZIP")
    parser.add_argument("--radius", type=int, default=DEFAULT_RADIUS)
    args = parser.parse_args()

    if args.source.resolve() == args.output.resolve():
        parser.error("source and output must be different files")
    if not args.source.is_file():
        parser.error(f"source archive does not exist: {args.source}")
    if not 1 <= args.radius <= 16:
        parser.error("radius must be between 1 and 16 chunks")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    files, functions = patch_archive(args.source, args.output, args.radius)
    print(
        f"[SUCCESS] Bounded {functions} exploration maps in {files} files "
        f"to {args.radius} chunks: {args.output}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"[ERROR] {error}")
        raise SystemExit(1) from error
