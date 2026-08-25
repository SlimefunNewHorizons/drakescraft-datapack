"""Genera los dialogos del menu de pausa a partir de una sola definicion.

Los dialogos son JSON repetitivo: cada boton son ocho lineas para decir una etiqueta y un
comando. Escribirlos a mano hizo que el datapack se quedase en treinta comandos mientras la guia
de la web ya documentaba noventa y uno, y que las diferencias entre ambos no se notasen.

Aqui la fuente de verdad es la tabla MENUS de abajo. El resto es traduccion mecanica al formato
que espera el cliente. Para anadir un comando se toca una linea, no un archivo.

Uso:
    python scripts/generate_dialogs.py

Despues conviene pasar el validador:
    python scripts/validate_datapack.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIALOG_DIR = ROOT / "data" / "drakescraft" / "dialog"

VOLVER = ("Volver al menu principal", "@main_menu")

# El validador rechaza cualquier caracter por encima de U+2000 porque no todos los clientes lo
# dibujan igual. Eso descarta guiones largos, comillas curvas y puntos suspensivos: aqui se usan
# guiones normales y comillas rectas a proposito.
# SkyBlock y OneBlock comparten los mismos subcomandos y solo cambia el prefijo del comando.
# Se declaran una vez y se generan los dos menus a partir de aqui: si manana se anade un
# subcomando, entra en las dos modalidades a la vez y no se pueden quedar descuadradas.
ISLA_ACCIONES = [
    ("Ir a tu isla", "go"),
    ("Ver tus puntos guardados", "homes"),
    ("Guardar este punto", "sethome"),
    ("Informacion de la isla", "info"),
    ("Reglas de dentro", "settings"),
    ("Cerrar o abrir la isla", "lock"),
    ("Nivel de tu isla", "level"),
    ("Ranking de islas", "top"),
    ("Valor del bloque en mano", "value"),
    ("Desglose del nivel", "detail"),
    ("Generadores de piedra", "generator"),
    ("Tu equipo", "team"),
    ("Islas vecinas", "near"),
    ("Ir al spawn", "spawn"),
    ("Idioma de los mensajes", "language"),
]

VOLVER_MODALIDADES = ("Volver a modalidades", "@modalidades_menu")

def _acciones_isla(prefijo, extras=()):
    """Traduce la tabla comun al prefijo de cada modalidad y anade lo propio de OneBlock."""
    filas = [(etiqueta, "/" + prefijo + " " + sub) for etiqueta, sub in ISLA_ACCIONES]
    filas += [
        ("Invitar a alguien", "$" + prefijo + " team invite $(target_player)"),
        ("Aceptar invitacion", "/" + prefijo + " team accept"),
        ("Salir del equipo", "/" + prefijo + " team leave"),
        ("Echar a alguien de la isla", "$" + prefijo + " expel $(target_player)"),
        ("Prohibirle la entrada", "$" + prefijo + " ban $(target_player)"),
        ("Levantar la prohibicion", "$" + prefijo + " unban $(target_player)"),
    ]
    filas += list(extras)
    filas.append(VOLVER_MODALIDADES)
    return filas

ISLA_ACCIONES_SKY = _acciones_isla("is")
ISLA_ACCIONES_OB = _acciones_isla("ob", extras=[
    ("Bloques rotos y fase (/ob count)", "/ob count"),
    ("Ver todas las fases (/ob phases)", "/ob phases"),
    ("Recuperar el bloque perdido", "/ob respawnblock"),
    ("Contador en pantalla (/ob bossbar)", "/ob bossbar"),
])

MENUS: dict[str, dict] = {
    "main_menu": {
        "title": "DRAKESCRAFT - Menu principal",
        "color": "gold",
        "external_title": "DrakesCraft",
        "columns": 2,
        "body": "Todos los comandos de jugador del servidor. Los que dependen de rango o de "
                "modalidad avisan al pulsarlos.",
        "actions": [
            ("Lo basico", "@basico_menu"),
            ("Casas y teletransporte", "@teleport_menu"),
            ("Moverte entre modalidades", "@modalidades_menu"),
            ("Proteger tu base", "@protection_menu"),
            ("Guardar y mover cosas", "@almacenamiento_menu"),
            ("Dinero, tiendas y subastas", "@economy_menu"),
            ("Trabajos, misiones y habilidades", "@trabajos_menu"),
            ("Kits, votos y recompensas", "@kits_menu"),
            ("Slimefun", "@slimefun_menu"),
            ("Social y chat", "@social_menu"),
            ("Traducir el chat", "@traduccion_menu"),
            ("Comodidades", "@utilities_menu"),
            ("Lo que solo existe aqui", "@exclusivo_menu"),
            ("Beneficios de rango", "@rank_menu"),
            ("Si un comando no funciona", "@ayuda_menu"),
            ("Panel de staff (solo staff)", "@staff_menu"),
        ],
    },
    "basico_menu": {
        "title": "Lo basico",
        "color": "yellow",
        "body": "Lo que vas a escribir todos los dias. Si eres nuevo, con esto te basta para "
                "empezar.",
        "actions": [
            ("Ir al spawn (/spawn)", "/spawn"),
            ("Quien esta conectado (/list)", "/list"),
            ("Marcarte como ausente (/afk)", "/afk"),
            ("Ver tu ping (/ping)", "/ping"),
            ("Tiempo jugado (/playtime)", "/playtime"),
            ("Las normas (/rules)", "/rules"),
            ("Mensaje del dia (/motd)", "/motd"),
            ("Listado del servidor (/help)", "/help"),
            VOLVER,
        ],
    },
    "teleport_menu": {
        "title": "Casas y teletransporte",
        "color": "yellow",
        "body": "Escribe el nombre de la casa o del jugador en los campos de arriba y luego pulsa "
                "el boton. Cuantas casas puedes tener depende de tu rango.",
        "inputs": [
            ("home_name", "Nombre de la casa:"),
            ("target_player", "Jugador (para TPA):"),
        ],
        "actions": [
            ("Ir al spawn (/spawn)", "/spawn"),
            ("Volver donde estabas (/back)", "/back"),
            ("Teletransporte aleatorio (/rtp)", "/rtp"),
            ("Ver todas tus casas (/homes)", "/homes"),
            ("Ir a una casa (/home)", "$home $(home_name)"),
            ("Guardar esta casa (/sethome)", "$sethome $(home_name)"),
            ("Borrar una casa (/delhome)", "$delhome $(home_name)"),
            ("Pedir ir a alguien (/tpa)", "$tpa $(target_player)"),
            ("Pedir que venga (/tpahere)", "$tpahere $(target_player)"),
            ("Aceptar peticion (/tpaccept)", "/tpaccept"),
            ("Rechazar peticion (/tpdeny)", "/tpdeny"),
            VOLVER,
        ],
    },
    "modalidades_menu": {
        "title": "Moverte entre modalidades",
        "color": "aqua",
        "body": "Cada modalidad tiene su propio inventario y su propia economia. El menu de "
                "modalidades es la forma recomendada de saltar entre ellas.",
        "inputs": [
            ("warp_name", "Nombre del warp:"),
        ],
        "actions": [
            ("Menu de modalidades (/modalidades)", "/modalidades"),
            ("Ir a Slimefun (/survival)", "/survival"),
            ("Tu isla de SkyBlock (/island)", "/island"),
            ("Comandos de SkyBlock", "@isla_sky_menu"),
            ("Tu isla de OneBlock (/ob)", "/ob"),
            ("Comandos de OneBlock", "@isla_ob_menu"),
            ("Punto aleatorio (/rtp)", "/rtp"),
            ("Warps publicos (/warps)", "/warps"),
            ("Ir a un warp (/warp)", "$warp $(warp_name)"),
            ("Warps de jugadores (/pw)", "/pw"),
            ("Abrir tu propio warp (/pw set)", "$pw set $(warp_name)"),
            VOLVER,
        ],
    },
    "protection_menu": {
        "title": "Proteger tu base",
        "color": "green",
        "body": "Las protecciones se ponen con un bloque. Escribe el nombre del jugador arriba "
                "para anadirlo o quitarlo de la tuya.",
        "inputs": [
            ("target_player", "Jugador:"),
        ],
        "actions": [
            ("Sacar bloque de proteccion (/ps get)", "/ps get"),
            ("De quien es esto (/ps info)", "/ps info"),
            ("Tus protecciones (/ps list)", "/ps list"),
            ("Cuantas te quedan (/ps count)", "/ps count"),
            ("Ir a tu proteccion (/ps home)", "/ps home"),
            ("Fijar ese punto (/ps sethome)", "/ps sethome"),
            ("Dejar construir a alguien", "$ps members add $(target_player)"),
            ("Quitarle el permiso", "$ps members remove $(target_player)"),
            ("Darle control total", "$ps owners add $(target_player)"),
            ("Unir dos protecciones (/ps merge)", "/ps merge"),
            ("Retirar la proteccion (/ps unclaim)", "/ps unclaim"),
            ("Ver u ocultar el borde (/borde)", "/borde"),
            ("Reglas de dentro (/ps flags)", "@protection_flags_menu"),
            VOLVER,
        ],
    },
    "almacenamiento_menu": {
        "title": "Guardar y mover cosas",
        "color": "gold",
        "body": "Contenedores y estaciones portatiles. Lo que metas en la papelera no vuelve.",
        "actions": [
            ("Tus bovedas personales (/pv)", "/pv"),
            ("Cofre de ender (/enderchest)", "/enderchest"),
            ("Papelera portatil (/disposal)", "/disposal"),
            ("Mesa de crafteo (/workbench)", "/workbench"),
            ("Yunque portatil (/anvil)", "/anvil"),
            ("Piedra de afilar (/grindstone)", "/grindstone"),
            ("Cortador de piedra (/stonecutter)", "/stonecutter"),
            ("Telar (/loom)", "/loom"),
            ("Mesa de cartografia (/cartographytable)", "/cartographytable"),
            ("Compactar en bloques (/condense)", "/condense"),
            VOLVER,
        ],
    },
    "economy_menu": {
        "title": "Dinero, tiendas y subastas",
        "color": "gold",
        "body": "Los anuncios y las compras no cruzan de una modalidad a otra. Comprueba donde "
                "estas antes de publicar algo.",
        "actions": [
            ("Tu dinero (/balance)", "/balance"),
            ("Quien tiene mas (/baltop)", "/baltop"),
            ("Transferir dinero (/pay)", "@pay_menu"),
            ("El banco (/sbank)", "/sbank"),
            ("Casa de subastas (/ah)", "/ah"),
            ("Mercado de Slimefun (/sfmercado)", "/sfmercado"),
            ("Tus tiendas de cofre (/qs)", "/qs"),
            ("Buscar tiendas (/qs find)", "/qs find"),
            ("Cuanto vale lo que llevas (/worth)", "/worth"),
            ("Vender lo de la mano (/sell)", "/sell"),
            ("Vender el inventario (/sellinv)", "/sellinv"),
            ("Menu del servidor (/drakestienda)", "/drakestienda"),
            ("Tienda web (/buy)", "/buy"),
            VOLVER,
        ],
    },
    "trabajos_menu": {
        "title": "Trabajos, misiones y habilidades",
        "color": "green",
        "body": "Los oficios te pagan por lo que ya haces. Las habilidades suben solas: no hay "
                "nada que gastar.",
        "inputs": [
            ("job_name", "Oficio (minero, talador, cazador...):"),
        ],
        "actions": [
            ("Los oficios (/jobs)", "/jobs"),
            ("Apuntarte a un oficio (/jobs join)", "$jobs join $(job_name)"),
            ("Salir de un oficio (/jobs leave)", "$jobs leave $(job_name)"),
            ("Las misiones (/quests)", "/quests"),
            ("Tus habilidades (/skills)", "/skills"),
            ("Tus numeros (/stats)", "/stats"),
            VOLVER,
        ],
    },
    "kits_menu": {
        "title": "Kits, votos y recompensas",
        "color": "yellow",
        "body": "La racha diaria se pierde si dejas de entrar. Los kits mensuales dependen de tu "
                "rango.",
        "actions": [
            ("Ver tus kits (/kit)", "/kit"),
            ("Kit inicial (/kit inicial)", "/kit inicial"),
            ("Recompensa diaria (/daily)", "/daily"),
            ("Enlaces para votar (/vote)", "/vote"),
            ("Reclamar llaves de voto (/claim)", "/claim"),
            VOLVER,
        ],
    },
    "slimefun_menu": {
        "title": "Slimefun",
        "color": "aqua",
        "body": "Solo en la modalidad Slimefun. Escribe arriba lo que busques y pulsa el boton de "
                "buscar en vez de navegar categorias.",
        "inputs": [
            ("search_text", "Buscar objeto:"),
        ],
        "actions": [
            ("Abrir la guia (/sf guide)", "/sf guide"),
            ("Buscar un objeto (/sf search)", "$sf search $(search_text)"),
            ("Tus estadisticas (/sf stats)", "/sf stats"),
            ("Calculadora de recetas (/sfcalc)", "/sfcalc"),
            ("Tus logros (/sfa)", "/sfa"),
            ("Ayuda de Networks (/networks)", "/networks"),
            ("Investigacion de Nexcavate (/nex)", "/nex"),
            ("SensibleToolbox (/stb)", "/stb"),
            ("Tus Dank Tech (/dank)", "/dank"),
            VOLVER,
        ],
    },
    "social_menu": {
        "title": "Social y chat",
        "color": "light_purple",
        "body": "Escribe arriba el jugador o el texto segun lo que vayas a usar. Ignorar a alguien "
                "no le avisa.",
        "inputs": [
            ("target_player", "Jugador:"),
            ("message_text", "Texto:"),
        ],
        "actions": [
            ("Mensaje privado (/msg)", "$msg $(target_player) $(message_text)"),
            ("Responder al ultimo (/r)", "$r $(message_text)"),
            ("Narrar una accion (/me)", "$me $(message_text)"),
            ("Tu correo interno (/mail)", "/mail"),
            ("Enviar correo (/mail send)", "$mail send $(target_player) $(message_text)"),
            ("Ignorar a alguien (/ignore)", "$ignore $(target_player)"),
            ("Cerrar los privados (/msgtoggle)", "/msgtoggle"),
            ("Equipos (/team)", "/team"),
            ("Pedir matrimonio (/marry)", "$marry $(target_player)"),
            ("Ir con tu pareja (/marry tp)", "/marry tp"),
            ("Llamar al staff (/helpop)", "$helpop $(message_text)"),
            VOLVER,
        ],
    },
    "traduccion_menu": {
        "title": "Traducir el chat",
        "color": "aqua",
        "body": "Escribe arriba el codigo de tu idioma (es, en, pt, fr) y pulsa el boton. Con "
                "/wwct stop lo apagas todo.",
        "inputs": [
            ("lang_code", "Idioma (es, en, pt, fr):"),
        ],
        "actions": [
            ("Traducir todo el chat (/wwct)", "$wwct $(lang_code)"),
            ("Solo lo que recibes (/wwctci)", "$wwctci $(lang_code)"),
            ("Solo lo que escribes (/wwctco)", "$wwctco $(lang_code)"),
            ("Fijar tu idioma (/wwcl)", "$wwcl $(lang_code)"),
            ("Apagar la traduccion (/wwct stop)", "/wwct stop"),
            VOLVER,
        ],
    },
    "utilities_menu": {
        "title": "Comodidades",
        "color": "yellow",
        "body": "Cosas pequenas que hacen el dia mas comodo. Escribe arriba lo que necesite el "
                "comando que vayas a usar.",
        "inputs": [
            ("skin_name", "Cuenta para la skin:"),
            ("target_player", "Jugador (para /seen):"),
        ],
        "actions": [
            ("Sentarte (/sit)", "/sit"),
            ("Tumbarte (/lay)", "/lay"),
            ("Gatear (/crawl)", "/crawl"),
            ("Girar (/spin)", "/spin"),
            ("Ponerte la skin de otro (/skin)", "$skin $(skin_name)"),
            ("Quitarte la skin (/skin clear)", "/skin clear"),
            ("Ponerte algo en la cabeza (/hat)", "/hat"),
            ("Tus coordenadas (/getpos)", "/getpos"),
            ("Quien anda cerca (/near)", "/near"),
            ("Cuando entro alguien (/seen)", "$seen $(target_player)"),
            ("Que llevas en la mano (/itemdb)", "/itemdb"),
            ("Cuadros de imagen (/imageframe)", "/imageframe"),
            ("Compartir datos en el chat", "@chat_placeholders_menu"),
            ("Marcarte como ausente (/afk)", "/afk"),
            VOLVER,
        ],
    },
    "exclusivo_menu": {
        "title": "Lo que solo existe aqui",
        "color": "light_purple",
        "body": "Los sistemas propios de DrakesCraft. No los vas a encontrar en otro servidor.",
        "actions": [
            ("Codice de magia (/arcana)", "/arcana"),
            ("El panteon (/dioses)", "/dioses"),
            ("Arena de jefes (/bosswarp)", "/bosswarp"),
            ("Tus cosmeticos (/cosmeticos)", "/cosmeticos"),
            ("Reproductor de musica (/music)", "/music"),
            ("La Papa de mar (/papademar)", "/papademar"),
            ("Pedir reinicio avisado (/restart30)", "/restart30"),
            VOLVER,
        ],
    },
    "isla_sky_menu": {
        "title": "Comandos de SkyBlock",
        "color": "aqua",
        "body": "Los mismos comandos existen en OneBlock cambiando /is por /ob. El tamano de tu "
                "isla depende de tu rango. Escribe arriba el jugador para invitar o expulsar.",
        "inputs": [
            ("target_player", "Jugador:"),
        ],
        "actions": ISLA_ACCIONES_SKY,
    },
    "isla_ob_menu": {
        "title": "Comandos de OneBlock",
        "color": "aqua",
        "body": "Los mismos comandos que en SkyBlock, mas los de fase, que solo existen aqui. "
                "Escribe arriba el jugador para invitar o expulsar.",
        "inputs": [
            ("target_player", "Jugador:"),
        ],
        "actions": ISLA_ACCIONES_OB,
    },
    "rank_menu": {
        "title": "Beneficios de rango",
        "color": "gold",
        "body": "Herramientas de rango. Solo funcionan si tu rango las incluye; este menu no "
                "entrega permisos.",
        "inputs": [
            ("new_nickname", "Nuevo apodo (/nick):"),
        ],
        "actions": [
            ("Vuelo personal (/fly)", "/fly"),
            ("Restaurar hambre (/feed)", "/feed"),
            ("Restaurar salud (/heal)", "/heal"),
            ("Reparar lo de la mano (/repair)", "/repair"),
            ("Tus cosmeticos (/cosmeticos)", "/cosmeticos"),
            ("Ponerte algo en la cabeza (/hat)", "/hat"),
            ("Yunque portatil (/anvil)", "/anvil"),
            ("Cofre de ender (/ec)", "/ec"),
            ("Mesa de crafteo (/craft)", "/craft"),
            ("Papelera portatil (/trash)", "/trash"),
            ("Jugadores cercanos (/near)", "/near"),
            ("Hora personal (/ptime)", "/ptime day"),
            ("Clima personal (/pweather)", "/pweather sun"),
            ("Cambiar apodo (/nick)", "$nick $(new_nickname)"),
            VOLVER,
        ],
    },
    "ayuda_menu": {
        "title": "Si un comando no funciona",
        "color": "red",
        "body": "Tres motivos explican casi todos los casos. "
                "1) \"No tienes permiso\": el comando existe pero tu rango no lo alcanza, o estas "
                "en una modalidad donde no aplica. "
                "2) \"Unknown command\": eso si es raro, significa que el plugin no cargo. Dilo en "
                "el foro de Discord. "
                "3) Funciona en una modalidad y en otra no: algunos sistemas estan separados a "
                "proposito, como la casa de subastas.",
        "actions": [
            ("Llamar al staff conectado (/helpop)", "/helpop"),
            ("Las normas (/rules)", "/rules"),
            ("Listado del servidor (/help)", "/help"),
            ("Enlace de Discord (/discord)", "/discord"),
            VOLVER,
        ],
    },
}


def construir_accion(destino: str) -> dict:
    """Traduce la forma corta de la tabla al objeto que espera el cliente.

    Tres prefijos: @ es otro dialogo, $ es un comando con huecos que rellena el jugador y una
    barra normal es un comando fijo.
    """
    if destino.startswith("@"):
        return {"type": "minecraft:show_dialog", "dialog": f"drakescraft:{destino[1:]}"}
    if destino.startswith("$"):
        return {"type": "minecraft:dynamic/run_command", "template": destino[1:]}
    return {"type": "minecraft:run_command", "command": destino}


def construir_dialogo(definicion: dict) -> dict:
    """Arma un dialogo completo a partir de su definicion."""
    dialogo: dict = {
        "type": "minecraft:multi_action",
        "title": {"text": definicion["title"], "bold": True, "color": definicion["color"]},
    }
    if "external_title" in definicion:
        dialogo["external_title"] = {"text": definicion["external_title"], "color": definicion["color"]}
    if "columns" in definicion:
        dialogo["columns"] = definicion["columns"]
        dialogo["pause"] = False

    dialogo["body"] = {
        "type": "minecraft:plain_message",
        "width": 360,
        "contents": {"text": definicion["body"]},
    }

    if definicion.get("inputs"):
        dialogo["inputs"] = [
            {"type": "minecraft:text", "key": clave, "label": {"text": etiqueta}}
            for clave, etiqueta in definicion["inputs"]
        ]

    dialogo["actions"] = [
        {"label": {"text": etiqueta}, "action": construir_accion(destino)}
        for etiqueta, destino in definicion["actions"]
    ]
    return dialogo


def main() -> int:
    DIALOG_DIR.mkdir(parents=True, exist_ok=True)
    for nombre, definicion in MENUS.items():
        destino = DIALOG_DIR / f"{nombre}.json"
        contenido = json.dumps(construir_dialogo(definicion), ensure_ascii=False, indent=2) + "\n"
        destino.write_text(contenido, encoding="utf-8")
        print(f"[INFO] {nombre}.json - {len(definicion['actions'])} botones")

    total = sum(len(d["actions"]) for n, d in MENUS.items() if n != "main_menu")
    print(f"[SUCCESS] {len(MENUS)} dialogos generados, {total} botones de comando")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
