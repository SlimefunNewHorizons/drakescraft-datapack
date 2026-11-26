"""Build the DrakesCraft_TickOptimizer override datapack for Stellarity, Incendium, and SVM Powers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


PACK_MCMETA: dict[str, object] = {
    "pack": {
        "pack_format": 61,
        "supported_formats": [61, 999],
        "min_format": 61,
        "max_format": 999,
        "description": "DrakesCraft: Tick optimizer for Stellarity, Incendium, and SVM Powers (Ticket #430)",
    }
}

STELLARITY_ENTITY_MAIN = """# Pixies
  execute as @e[type=vex,tag=!stellarity.pixie,tag=!smithed.entity,tag=!stellarity.aware,predicate=stellarity:entity/pixie_can_spawn_in] at @s run function stellarity:entity/pixie/check

# Slay Queen ✨✨✨✨✨
# (Empress of Light)
  execute if score #empress_of_light.is_alive stellarity.misc matches 1 as @e[type=vindicator,tag=stellarity.empress_of_light] at @s run function stellarity:entity/empress_of_light/main
  execute if score #empress_of_light.is_alive stellarity.misc matches 1 as @e[type=marker,tag=stellarity.empress_of_light.tracker] at @s run function stellarity:entity/empress_of_light/animations/death/check_death with entity @s data."stellarity:owner"
  execute if score #empress_of_light.is_alive stellarity.misc matches 1 unless entity @e[type=vindicator,tag=stellarity.empress_of_light] unless entity @e[type=marker,tag=stellarity.empress_of_light.spawn_animation] as @e[type=item_display,tag=stellarity.empress_of_light.ethereal_lance] at @s run function stellarity:entity/empress_of_light/attacks/clear_all
  execute if score #empress_of_light.is_alive stellarity.misc matches 1 unless entity @e[type=vindicator,tag=stellarity.empress_of_light] unless entity @e[type=marker,tag=stellarity.empress_of_light.spawn_animation] run scoreboard players set #empress_of_light.is_alive stellarity.misc 0

# Dragon stuff
  execute as @e[type=ender_dragon,tag=stellarity.ender_dragon] at @s run function stellarity:entity/dragon/main

# execute as @e[type=husk,tag=stellarity.enderling] at @s run function stellarity:entity/enderlings/main
# execute as @e[type=evoker,tag=stellarity.warlock] at @s run function stellarity:entity/warlock/main

execute as @e[type=zombified_piglin,tag=stellarity.flesh_piglin] at @s run function stellarity:entity/flesh_piglin/main

# execute as @e[type=slime,predicate=stellarity:location/in_the_end,tag=!stellarity.voided_slime,tag=!stellarity.end_city] at @s run function stellarity:entity/voided_slime/abort_offsprings
  execute as @e[type=marker,tag=stellarity.spawn_egg] at @s run function stellarity:entity/handle_spawn_egg with entity @s data

execute if score #shulking.is_alive stellarity.misc matches 1 as @e[type=allay,tag=stellarity.shulking] at @s run function stellarity:entity/shulking/main
execute if score #shulking.is_alive stellarity.misc matches 1 as @e[type=shulker,tag=stellarity.shulking.body] at @s run function stellarity:entity/shulking/main_body
execute if score #shulking.is_alive stellarity.misc matches 1 as @e[type=item_display,tag=stellarity.shulking.spike] at @s run function stellarity:entity/shulking/attacks/spike/loop

execute as @e[type=#stellarity:end_variant_animals,tag=!stellarity.aware,tag=!smithed.entity,predicate=stellarity:entity/end_variant_animals] run function stellarity:entity/animal/convert
execute as @e[type=sheep,tag=!stellarity.invalid_animal,tag=!smithed.entity] at @s run function stellarity:entity/animal/convert_sheep

execute if score #shulking.is_alive stellarity.misc matches 1 as @e[tag=stellarity.shulking.body] at @s run bossbar set stellarity:shulking players @a[distance=..64]
execute if score #shulking.is_alive stellarity.misc matches 1 unless entity @e[tag=stellarity.shulking.body] run function stellarity:entity/shulking/death/clear_bossbar

execute if score #shulking.is_alive stellarity.misc matches 1 as @e[type=item_display,tag=stellarity.shulking.ray] at @s run function stellarity:entity/shulking/attacks/ray/loop with entity @s data."stellarity:owner"
"""

STELLARITY_AWARENESS_TAG: dict[str, object] = {
    "replace": False,
    "values": [
        "#stellarity:end_variant_animals",
    ],
}

INCENDIUM_CLOCKS_MAIN = """# clock: 1t

schedule function incendium:clocks/main 1t replace

function incendium:technical/main
execute as @a at @s run function incendium:player/main

# mob init
execute as @e[type=#incendium:mobs_no_player, tag=!in.checked] at @s run function incendium:entity/mob/init

execute as @e[type=#incendium:mobs_no_player, tag=in.ticking_entity] at @s run function incendium:entity/mob/main

execute as @e[type=#incendium:mobs,scores={in.frozen=1..},predicate=incendium:random/10] run function incendium:entity/chilling

# other
execute as @e[type=#incendium:other, tag=!in.checked] at @s run function incendium:entity/other/init

execute as @e[type=#incendium:other, tag=in.ticking_entity] at @s run function incendium:entity/other/main

execute if entity @a[tag=nbs_borderofli] run function incendium:border_of_life/tick
"""

INCENDIUM_ENTITY_ID_RESET = """# from ./check
# reset

scoreboard players reset * in.eid
tag @e[tag=in.eid_0] remove in.eid_0
tag @e[tag=in.eid_1] remove in.eid_1
tag @e[tag=in.eid_2] remove in.eid_2
tag @e[tag=in.eid_3] remove in.eid_3
tag @e[tag=in.eid_4] remove in.eid_4
tag @e[tag=in.eid_5] remove in.eid_5
tag @e[tag=in.eid_6] remove in.eid_6
tag @e[tag=in.eid_7] remove in.eid_7
tag @e[tag=in.eid_8] remove in.eid_8
tag @e[tag=in.eid_9] remove in.eid_9
tag @e[tag=in.eid_10] remove in.eid_10
tag @e[tag=in.eid_11] remove in.eid_11
tag @e[tag=in.eid_12] remove in.eid_12
tag @e[tag=in.eid_13] remove in.eid_13
tag @e[tag=in.eid_14] remove in.eid_14
execute as @e[type=#incendium:mobs_no_player,tag=in.checked] run function incendium:technical/entity_id/init

tellraw @a[tag=in.admin,tag=in.debug] {translate:"incendium.system.eid.reset",fallback:"Resetting entity IDs", "color": "#ff8000"}
"""

SVM_EP_TICK = """# DrakesCraft override of svm_ep:tick (Ticket #430)
# 1. Narrows player/power-user-only and item_display-only score selectors so Minecraft
#    does not scan all ~2,000+ world entities via Scoreboard.getPlayerScoreInfo every tick.
# 2. Evaluates scores={...} before predicate=!svm_ep:time_stopped so the predicate is only
#    checked on entities that actually hold the active score.
# 3. Filters tag @e[tag=executor] remove executor and tag @e[tag=same_id] remove same_id.

execute if score tick svm_ep.function matches 1 run return 0
kill @e[type=marker,tag=rotator]
#DIED
execute as @a[scores={svm_ep.died=1..}] run function svm_ep:player/died



#TIME STOP
scoreboard players add %WORLD svm_ep.tick 1
execute as @a[scores={svm_ep.restore_health=1..}] run function svm_ep:player/restore_health
execute if score tick svm_ep.function matches 2 run return 0




execute as @e[tag=svm_ep.power_user,scores={svm_ep.tick_acceleration=1..},predicate=!svm_ep:time_stopped] run function svm_ep:time/give_extra_ticks
execute if score tick svm_ep.function matches 3 run return 0

execute as @e[tag=svm_ep.power_user,scores={svm_ep.time_stopping=1..}] run function svm_ep:time/stopper
execute as @e[scores={svm_ep.time_stopped=0}] run function svm_ep:time/unstop_entity
scoreboard players remove @e[scores={svm_ep.time_stopped=1..}] svm_ep.time_stopped 1
execute if score tick svm_ep.function matches 4 run return 0




#PROJECTILES
tag @e[type=#minecraft:impact_projectiles,tag=!svm_ep.arrow_redirected] add svm_ep.can_redirect
scoreboard players set @e[type=#minecraft:impact_projectiles] svm_ep.projectile 1
execute if score tick svm_ep.function matches 5 run return 0



#NPC
execute as @e[tag=svm_ep.npc,tag=!svm_ep.npc_display,predicate=!svm_ep:time_stopped] at @s run function svm_ep:npc/tick
execute if score tick svm_ep.function matches 6 run return 0

#USING ABILITY
execute as @e[scores={svm_ep.ability.using=0..}] if entity @s[predicate=!svm_ep:time_stopped] run function svm_ep:ability/using
execute as @e[scores={svm_ep.using_move=1..}] if entity @s[predicate=!svm_ep:time_stopped] run function svm_ep:ability/using_move
execute if score tick svm_ep.function matches 7 run return 0


#tech
execute as @e[tag=svm_ep.black_hole,scores={svm_ep.kill_at=1..},predicate=!svm_ep:time_stopped] if score @s svm_ep.kill_at <= %WORLD svm_ep.tick run kill @s[type=!player]
execute as @e[scores={svm_ep.kill_after=0..}] if entity @s[predicate=!svm_ep:time_stopped] at @s run function svm_ep:system/kill_after/tick
execute as @e[type=#svm_ep:technical,type=!item,tag=!svm_ep.npc,tag=!svm_ep.no_tick,predicate=!svm_ep:time_stopped] at @s run function svm_ep:selected_tick
execute if score tick svm_ep.function matches 8 run return 0


#PARTICLE
execute as @e[type=item_display,scores={svm_ep.particle=1..},predicate=!svm_ep:time_stopped] run function svm_ep:particle_tick
execute if score tick svm_ep.function matches 9 run return 0


#PROJECTILE
execute as @e[type=!#minecraft:impact_projectiles,type=!player,scores={svm_ep.projectile=-100..}] if entity @s[predicate=!svm_ep:time_stopped] run function svm_ep:projectile/tick
execute if score tick svm_ep.function matches 10 run return 0




#POWERS
execute as @e[tag=svm_ep.power_user,predicate=!svm_ep:time_stopped] at @s run function svm_ep:power/user_tick
execute if score tick svm_ep.function matches 11 run return 0






#EFFECTS
execute as @e[scores={svm_ep.effect=1..}] if entity @s[predicate=!svm_ep:time_stopped] run function svm_ep:entity/effect/tick
execute if score tick svm_ep.function matches 12 run return 0


execute as @e[scores={svm_ep.p.explosion_barrier_effect=1..}] if entity @s[predicate=!svm_ep:time_stopped] run function svm_ep:power/explosion/barrier/effect
execute as @e[scores={svm_ep.p.fire_on_fire=1..}] if entity @s[predicate=!svm_ep:time_stopped] run function svm_ep:power/fire/on_fire
execute as @e[scores={svm_ep.portal_delay=1..}] if entity @s[predicate=!svm_ep:time_stopped] run scoreboard players remove @s svm_ep.portal_delay 1
execute as @e[scores={svm_ep.p.dimension_front_delay=1..}] if entity @s[predicate=!svm_ep:time_stopped] run scoreboard players remove @s svm_ep.p.dimension_front_delay 1
execute if score tick svm_ep.function matches 13 run return 0


execute if score %WORLD_SPEED svm_ep.world_settings matches 0.. run function svm_ep:system/world/speeded_up
execute if score %METEOR_RAIN svm_ep.world_settings matches 0.. run function svm_ep:system/world/meteor_rain
execute if score tick svm_ep.function matches 12 run return 0


#LAGGY
execute as @e[tag=svm_ep.explosion_ray,limit=25,sort=random,predicate=!svm_ep:time_stopped] at @s run function svm_ep:power/explosion/destroyer/projectile_tick
execute as @e[tag=svm_ep.lightning_ready,limit=1,sort=random,predicate=!svm_ep:time_stopped] at @s run function svm_ep:power/lightning/lightning_place/summon
execute as @e[tag=svm_ep.flora_oak_leaves,limit=10,predicate=!svm_ep:time_stopped] at @s run function svm_ep:power/flora/tree_place/place_leaf2
execute as @e[tag=svm_ep.flora_oak_leaves,limit=10,sort=random,predicate=!svm_ep:time_stopped] at @s run function svm_ep:power/flora/tree_place/place_leaf2
execute as @e[tag=svm_ep.flora_tree_big,limit=2,predicate=!svm_ep:time_stopped] at @s run function svm_ep:power/flora/tree_big/projectile_tick
execute as @e[tag=svm_ep.flora_tree_big,limit=2,sort=random,predicate=!svm_ep:time_stopped] at @s run function svm_ep:power/flora/tree_big/projectile_tick
execute as @e[tag=svm_ep.iceberg_projectile,sort=random,limit=25,predicate=!svm_ep:time_stopped] at @s run function svm_ep:power/ice/berg/projectile_tick
execute if score tick svm_ep.function matches 13 run return 0

scoreboard players add @e[type=marker,tag=svm_ep.placed_ice,predicate=!svm_ep:time_stopped] svm_ep.lifetime 1
execute as @e[type=marker,tag=svm_ep.placed_ice,scores={svm_ep.lifetime=160..},limit=50,predicate=!svm_ep:time_stopped] at @s run function svm_ep:power/ice/berg/destroy_ice
tag @e[tag=svm_ep.tag_to_remove_1_entity_per_tick,limit=1] remove svm_ep.tag_to_remove_1_entity_per_tick
execute if score tick svm_ep.function matches 14 run return 0


#BLOCK
tag @e[tag=executor] remove executor
tag @e[tag=same_id] remove same_id
"""

INPUT_SLOT_CHANGE_TRACK = """execute as @s[tag=svm_ep.power_user] store result score @s input.selected_slot run data get entity @s SelectedItemSlot
execute as @s[tag=svm_ep.power_user] unless score @s input.selected_slot_last_tick = @s input.selected_slot run function input:slot_change/on_change
"""

OVERRIDE_FILES: dict[str, str] = {
    "pack.mcmeta": json.dumps(PACK_MCMETA, ensure_ascii=False, indent=2) + "\n",
    "data/stellarity/function/entity/main.mcfunction": STELLARITY_ENTITY_MAIN,
    "data/stellarity/tags/entity_type/entity_awareness_checks.json": (
        json.dumps(STELLARITY_AWARENESS_TAG, ensure_ascii=False, indent=2) + "\n"
    ),
    "data/incendium/function/clocks/main.mcfunction": INCENDIUM_CLOCKS_MAIN,
    "data/incendium/function/technical/entity_id/reset.mcfunction": INCENDIUM_ENTITY_ID_RESET,
    "data/svm_ep/function/tick.mcfunction": SVM_EP_TICK,
    "data/input/function/slot_change/track.mcfunction": INPUT_SLOT_CHANGE_TRACK,
}


def build_tick_optimizer(output_path: Path) -> int:
    """Write the DrakesCraft_TickOptimizer override datapack as a directory or ZIP archive."""
    if output_path.suffix.lower() == ".zip":
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(output_path, "w", ZIP_DEFLATED) as archive:
            for relative, content in sorted(OVERRIDE_FILES.items()):
                archive.writestr(relative, content.encode("utf-8"))
        with ZipFile(output_path, "r") as verification:
            corrupt = verification.testzip()
            if corrupt is not None:
                output_path.unlink(missing_ok=True)
                raise RuntimeError(f"Corrupt ZIP entry in {output_path}: {corrupt}")
        return len(OVERRIDE_FILES)

    output_path.mkdir(parents=True, exist_ok=True)
    for relative, content in sorted(OVERRIDE_FILES.items()):
        target = output_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return len(OVERRIDE_FILES)


def main() -> int:
    """Parse CLI arguments and generate the DrakesCraft_TickOptimizer override pack."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output",
        type=Path,
        help="destination directory or .zip file for DrakesCraft_TickOptimizer",
    )
    args = parser.parse_args()
    count = build_tick_optimizer(args.output)
    print(f"[SUCCESS] Wrote {count} files to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
