<div align="center">

<img src="./assets/datapack-hero.svg" width="100%" alt="DrakesCraft DataPack Banner" />

# DrakesCraft DataPack (Purpur 1.21.11)

**Native Server-Side Pause Menu Dialogs System for DrakesCraft Network**

[![Minecraft](https://img.shields.io/badge/Minecraft-1.21.11-00F2FE?style=for-the-badge&logo=minecraft&logoColor=white)](https://drakescraft.cl)
[![Purpur](https://img.shields.io/badge/Server-Purpur_1.21.11-8B5CF6?style=for-the-badge&logo=openjdk&logoColor=white)](https://purpurmc.org)
[![Type](https://img.shields.io/badge/Type-100%25_Server--Side_DataPack-F5C542?style=for-the-badge)](https://github.com/SlimefunNewHorizons)

</div>

> ### 🏰 ¡Únete a la Comunidad Oficial de DrakesCraft!
> 
> * 🎮 **IP del Servidor**: `mc.drakescraft.cl` *(Java 1.21.11 & Bedrock)*
> * 💬 **Discord Oficial**: [discord.gg/drakescraft](https://discord.gg/rv3vtXZTk7)
> * 🌐 **Web & Guía**: [web.drakescraft.cl](https://web.drakescraft.cl) — 🛒 **Tienda**: [web.drakescraft.cl/store](https://web.drakescraft.cl/store.html)
> 
> *¡Juega con este addon y más de 80 expansiones optimizadas en vivo en nuestra network de supervivencia técnica!*

---

---

## Overview

The **DrakesCraft DataPack** utilizes Minecraft 1.21.11's native **Dialogs** engine and `#minecraft:pause_screen_additions` tag system to inject a custom, interactive GUI directly into the player's Escape (Pause) menu.

**Zero Client Mods Required!** Works natively out of the box for all Java Edition 1.21.11 players joining `mc.drakescraft.cl`.

---

## Menu Architecture

Los dialogos **se generan**, no se escriben a mano. La fuente de verdad es la tabla `MENUS` de
`scripts/generate_dialogs.py`; los `.json` son su salida. Escribirlos a mano fue lo que dejo el
datapack en treinta comandos mientras la guia de la web ya documentaba noventa y uno, sin que la
diferencia se notase.

```bash
python scripts/generate_dialogs.py    # regenera los 16 dialogos
python scripts/validate_datapack.py   # comprueba formato y referencias cruzadas
```

El menu principal reparte 114 comandos distintos en quince secciones, alineadas una a una con las
de `guia-comandos.html` en la web para que ambas digan lo mismo:

| Seccion | Dialogo | Cubre |
| --- | --- | --- |
| Lo basico | `basico_menu` | spawn, list, afk, ping, playtime, rules, motd, help |
| Casas y teletransporte | `teleport_menu` | home, sethome, delhome, back, rtp, tpa, tpahere |
| Modalidades | `modalidades_menu` | modalidades, survival, island, ob, warps, pw |
| Proteger tu base | `protection_menu` + `protection_flags_menu` | ProtectionStones completo y sus flags |
| Guardar y mover cosas | `almacenamiento_menu` | pv, enderchest, disposal y estaciones portatiles |
| Dinero y tiendas | `economy_menu` + `pay_menu` | balance, baltop, sbank, ah, qs, sell, worth |
| Trabajos y habilidades | `trabajos_menu` | jobs, quests, skills, stats |
| Kits y votos | `kits_menu` | kit, daily, vote, claim |
| Slimefun | `slimefun_menu` | sf guide, sf search, sfcalc, sfa, networks, nex, stb, dank |
| Social y chat | `social_menu` | msg, mail, ignore, team, marry, helpop |
| Traducir el chat | `traduccion_menu` | wwct, wwctci, wwctco, wwcl |
| Comodidades | `utilities_menu` + `chat_placeholders_menu` | sit, skin, hat, getpos, near, seen, itemdb |
| Lo que solo existe aqui | `exclusivo_menu` | arcana, dioses, bosswarp, cosmeticos, music, papademar |
| Beneficios de rango | `rank_menu` | fly, feed, heal, repair, cosmeticos, nick, ptime |
| Si algo no funciona | `ayuda_menu` | los tres motivos por los que un comando falla |
| Staff | `staff_menu` | vanish, inspeccion, moderacion y gamemodes |

Los comandos que necesitan un argumento usan `minecraft:dynamic/run_command` con un campo de texto
en el propio dialogo, de modo que el jugador escribe el nombre de la casa o del jugador ahi mismo
en vez de tener que cerrar el menu.

El datapack es una interfaz; no concede permisos. Los kits los declara y valida Odysseia, no Essentials.

---

## Installation

1. Copy the `DrakesCraft_DataPack` directory into your world's datapacks folder:
   ```text
   <server-root>/world/datapacks/DrakesCraft_DataPack
   ```
2. Execute `/reload` in-game or restart your Purpur 1.21.11 server.
3. Open the pause menu in-game to access the **DrakesCraft** hub!

---

## Mojang 1.21.11 Dialog Codec

The pack targets data pack format `94.1`. Menus use `minecraft:multi_action`,
`actions`, and `minecraft:show_dialog` for navigation:

```json
{
  "type": "minecraft:multi_action",
  "title": {
    "text": "Titulo del menu",
    "bold": true,
    "color": "gold"
  },
  "body": {
    "type": "minecraft:plain_message",
    "contents": {
      "text": "Menu description or instructions here."
    }
  },
  "inputs": [
    {
      "type": "minecraft:text",
      "key": "input_key",
      "label": {
        "text": "Input Label:"
      }
    }
  ],
  "actions": [
    {
      "label": {"text": "Open economy"},
      "action": {
        "type": "minecraft:show_dialog",
        "dialog": "drakescraft:economy_menu"
      }
    }
  ]
}
```

Run `python scripts/validate_datapack.py` before deployment. The validator checks
pack version, JSON structure, input keys, action payloads, every internal dialog
reference, and client-unsafe decorative symbols. Dialog text intentionally uses
plain client-safe labels so it renders equally on supported resource packs.

## Production Compatibility Tools

DrakesCraft also ships a reproducible repair for the third-party **Villages
Revamped 1.21.11 v2.7** archive. That release contains six swamp jigsaw blocks
which incorrectly reference the nonexistent `minecraft:village/swamp/decor`
and `minecraft:village/swamp/streets` pools. On Purpur 1.21.11 this produces
missing-template-pool warnings while new terrain is generated.

Run the tool against a backed-up source archive and deploy only its verified
output:

```bash
python -m venv .venv-tools
.venv-tools/bin/pip install -r requirements-tools.txt
.venv-tools/bin/python scripts/patch_villages_revamped.py \
  "Villages Revamped 1.21.11 v2.7.fixed.zip" \
  "Villages Revamped 1.21.11 v2.7.fixed2.zip"
```

The patcher changes only those six NBT pool values, preserves every other ZIP
entry, checks the expected correction count, scans for stale namespaces, and
runs a ZIP integrity test before reporting success.

### Dungeons and Taverns chart watchdog protection

The upstream chart mechanic runs `minecraft:exploration_map` synchronously when
a player unfolds a chart. Its default 50-chunk search caused 10–40 second
watchdog stalls in production. Build a reversible server-safe archive with an
8-chunk search bound:

```bash
.venv-tools/bin/python scripts/patch_dungeons_taverns_maps.py \
  "Dungeons and Taverns v5.1.0.zip" \
  "Dungeons and Taverns v5.1.0.fixed-maps.zip"
```

The patcher touches only `nova_structures` map loot tables, preserves chart
behavior for nearby structures, validates every affected JSON document, tests
ZIP integrity, and refuses to publish an archive when no expected target exists.

---

<div align="center">

**DrakesCraft Labs** · Chile · Led by [**JackStar6677-1**](https://github.com/JackStar6677-1)

</div>

---

## 📄 License & Upstream Attribution

This project is a sovereign fork maintained by [**JackStar6677-1**](https://github.com/JackStar6677-1) under [**DrakesCraft Labs**](https://github.com/SlimefunNewHorizons).

- **Original Project:** Created by the upstream authors and the open-source community.
- **DrakesCraft Optimizations:** Modernized for Paper/Purpur 1.21.11+, Java 21, high concurrency, asynchronous safety, and exploit/duplication prevention.
- **License:** Distributed under the original **GNU General Public License v3.0 (GPLv3)** (or original upstream license). See the [LICENSE](LICENSE) file for complete terms.
