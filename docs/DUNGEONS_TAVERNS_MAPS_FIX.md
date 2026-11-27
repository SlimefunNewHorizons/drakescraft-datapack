# Dungeons and Taverns Explorer Maps Fix (`v5.3.2`)

## Root Cause

In `world/datapacks/Dungeons and Taverns v5.3.2.zip` (`data/nova_structures/loot_table/maps/*.json`), all 72 structure/village chart loot tables start from `minecraft:map` and apply `minecraft:exploration_map` without an explicit `search_radius` (defaulting to `50` chunks = `800` blocks).

With `Terralith`, `Villages revamped`, and `Dungeons and Taverns` active on Season 2 (`world`), many target structures spawn beyond `800` blocks (e.g., `#minecraft:village` at `896` blocks, `#minecraft:on_ocean_explorer_maps` at `1,362` blocks, `nova_structures:lone_citadel` at `4,982` blocks). When `minecraft:exploration_map` fails to locate a target within `50` chunks, it leaves an uninitialized `minecraft:map` that turns into a normal player-centered map on right-click.

## Fix Applied

- Patched all **72** files under `data/nova_structures/loot_table/maps/*.json` in `Dungeons and Taverns v5.3.2.zip`:
  - `search_radius`: `250` chunks (`4,000` blocks)
  - `skip_existing_chunks`: `false` (queries the worldgen structure grid in `~1–43 ms` without synchronous chunk loading / watchdog stalls)
- Backup stored on Star VPS at `~/staging-dallas/Dungeons-and-Taverns-v5.3.2.zip.bak-20261127`.
- Takes effect on Dallas at the next safe server restart (or `/minecraft:reload`).
