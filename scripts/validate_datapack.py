"""Validate the DrakesCraft 1.21.11 dialog datapack without external packages."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIALOG_DIR = ROOT / "data" / "drakescraft" / "dialog"
INPUT_KEY = re.compile(r"^[A-Za-z0-9_]+$")
STATIC_ACTION_FIELDS = {
    "minecraft:run_command": "command",
    "minecraft:show_dialog": "dialog",
    "minecraft:open_url": "url",
}
DYNAMIC_ACTION_FIELDS = {"minecraft:dynamic/run_command": "template"}
UNSAFE_TEXT = re.compile(r"[\U00002000-\U0010FFFF]")


def load_json(path: Path) -> dict:
    """Load one JSON object and report its path when parsing fails."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path.relative_to(ROOT)}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)}: root must be an object")
    return value


def validate_dialog(path: Path, known_dialogs: set[str]) -> list[str]:
    """Return all structural and cross-reference errors for one dialog."""
    errors: list[str] = []
    relative = path.relative_to(ROOT)
    dialog = load_json(path)
    for text in re.findall(r'"text"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', path.read_text(encoding="utf-8")):
        if UNSAFE_TEXT.search(text):
            errors.append(f"{relative}: text contains a client-unsafe symbol")
            break
    if dialog.get("type") != "minecraft:multi_action":
        errors.append(f"{relative}: type must be minecraft:multi_action")

    body = dialog.get("body")
    if not isinstance(body, dict) or body.get("type") != "minecraft:plain_message":
        errors.append(f"{relative}: body must be minecraft:plain_message")

    keys: set[str] = set()
    for control in dialog.get("inputs", []):
        key = control.get("key") if isinstance(control, dict) else None
        if not isinstance(key, str) or not INPUT_KEY.fullmatch(key):
            errors.append(f"{relative}: invalid input key {key!r}")
        elif key in keys:
            errors.append(f"{relative}: duplicate input key {key}")
        else:
            keys.add(key)

    actions = dialog.get("actions")
    if not isinstance(actions, list) or not actions:
        errors.append(f"{relative}: actions must be a non-empty list")
        return errors

    for index, button in enumerate(actions):
        action = button.get("action") if isinstance(button, dict) else None
        if not isinstance(action, dict):
            errors.append(f"{relative}: action {index} has no action object")
            continue
        action_type = action.get("type")
        required = STATIC_ACTION_FIELDS.get(action_type) or DYNAMIC_ACTION_FIELDS.get(action_type)
        if required is None:
            errors.append(f"{relative}: action {index} uses unsupported type {action_type!r}")
            continue
        if not isinstance(action.get(required), str) or not action[required].strip():
            errors.append(f"{relative}: action {index} requires {required}")
        if action_type == "minecraft:show_dialog" and action.get("dialog") not in known_dialogs:
            errors.append(f"{relative}: missing dialog reference {action.get('dialog')!r}")
        if action_type == "minecraft:dynamic/run_command":
            parameters = set(re.findall(r"\$\(([A-Za-z0-9_]+)\)", action["template"]))
            missing = parameters - keys
            if missing:
                errors.append(f"{relative}: action {index} references missing inputs {sorted(missing)}")
    return errors


def main() -> int:
    """Validate pack metadata, tag entry points, and every dialog."""
    errors: list[str] = []
    pack = load_json(ROOT / "pack.mcmeta").get("pack", {})
    if pack.get("min_format") != [94, 1] or pack.get("max_format") != [94, 1]:
        errors.append("pack.mcmeta: min_format and max_format must both be [94, 1]")

    dialog_files = sorted(DIALOG_DIR.glob("*.json"))
    known_dialogs = {f"drakescraft:{path.stem}" for path in dialog_files}
    tag = load_json(ROOT / "data" / "minecraft" / "tags" / "dialog" / "pause_screen_additions.json")
    entry_ids = {
        entry.get("id") if isinstance(entry, dict) else entry
        for entry in tag.get("values", [])
    }
    if "drakescraft:main_menu" not in entry_ids:
        errors.append("pause_screen_additions.json: drakescraft:main_menu is required")

    for path in dialog_files:
        errors.extend(validate_dialog(path, known_dialogs))

    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1
    print(f"[SUCCESS] Validated {len(dialog_files)} dialogs for data pack 94.1")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(f"[ERROR] {error}")
        raise SystemExit(1) from error
