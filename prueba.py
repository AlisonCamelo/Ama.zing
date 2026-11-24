from dataclasses import dataclass
from typing import Optional, Tuple

MANDATORY_KEYS = (
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT",
)


class ConfigError(Exception):
    """Error de configuración (sintaxis, valores o fichero inválidos)."""


@dataclass
class MazeConfig:
    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None


def parse_int(key: str, raw: str) -> int:
    try:
        return int(raw)
    except ValueError:
        raise ConfigError(f"{key}: '{raw}' no es un entero válido") from None


def parse_coords(key: str, raw: str) -> Tuple[int, int]:
    parts = raw.split(",")
    if len(parts) != 2:
        raise ConfigError(
            f"{key}: formato inválido '{raw}', se esperaba 'x,y'"
        )
    x = parse_int(key, parts[0].strip())
    y = parse_int(key, parts[1].strip())
    return x, y


def parse_bool(key: str, raw: str) -> bool:
    value = raw.lower()
    if value == "true":
        return True
    if value == "false":
        return False
    raise ConfigError(f"{key}: '{raw}' debe ser True o False")


def read_pairs(path: str) -> Dict[str, str]:
    pairs: Dict[str, str] = {}

    try:
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise ConfigError(f"fichero no encontrado: '{path}'") from None
    except UnicodeDecodeError:
        raise ConfigError(f"'{path}' no es un fichero de texto") from None
    except OSError:
        raise ConfigError(f"no se pudo leer '{path}'") from None

    line_number = 0
    for line in lines:
        line_number += 1
        text = line.strip()

        if text == "" or text.startswith("#"):
            continue

        position = text.find("=")
        if position == -1:
            raise ConfigError(
                f"línea {line_number}: falta '=' en '{text}'"
            )

        key = text[:position].strip().upper()
        value = text[position + 1:].strip()

        if key == "":
            raise ConfigError(f"línea {line_number}: clave vacía")
        if value == "":
            raise ConfigError(f"línea {line_number}: {key} sin valor")
        if key in pairs:
            raise ConfigError(f"línea {line_number}: {key} repetida")

        pairs[key] = value

    return pairs


def check_point(key: str, point: Tuple[int, int], width: int, height: int) -> None:
    x = point[0]
    y = point[1]

    if x < 0 or x >= width or y < 0 or y >= height:
        raise ConfigError(
            f"{key}: ({x},{y}) fuera de los límites "
            f"(x entre 0 y {width - 1}, y entre 0 y {height - 1})"
        )


def load_config(path: str) -> MazeConfig:
    pairs = _read_pairs(path)

    missing = []
    for key in MANDATORY_KEYS:
        if key not in pairs:
            missing.append(key)
    if len(missing) > 0:
        raise ConfigError(
            "faltan claves obligatorias: " + ", ".join(missing)
        )

    width = parse_int("WIDTH", pairs["WIDTH"])
    height = parse_int("HEIGHT", pairs["HEIGHT"])
    if width < 2 or height < 2:
        raise ConfigError(
            f"WIDTH y HEIGHT deben ser >= 2 (recibido {width}x{height})"
        )

    entry = parse_coords("ENTRY", pairs["ENTRY"])
    exit_point = parse_coords("EXIT", pairs["EXIT"])
    check_point("ENTRY", entry, width, height)
    check_point("EXIT", exit_point, width, height)
    if entry == exit_point:
        raise ConfigError("ENTRY y EXIT deben ser celdas distintas")

    output_file = pairs["OUTPUT_FILE"]
    perfect = parse_bool("PERFECT", pairs["PERFECT"])

    seed = None
    if "SEED" in pairs:
        seed = parse_int("SEED", pairs["SEED"])

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit=exit_point,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
    )
