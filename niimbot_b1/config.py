import json
import os
import sys
from pathlib import Path


def get_app_config_dir() -> Path:
    if sys.platform.startswith("win"):
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "NiimBotB1"

        return Path.home() / "AppData" / "Roaming" / "NiimBotB1"

    return Path.home() / ".config" / "niimbot_b1"


APP_CONFIG_DIR = get_app_config_dir()
CONFIG_FILE = APP_CONFIG_DIR / "config.json"


DEFAULT_CONFIG = {
    "printer_address": "",
    "density": 5,
    "row_delay_s": 0.012,
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        cfg = DEFAULT_CONFIG.copy()
        cfg.update(data)
        return cfg

    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    APP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    cfg = DEFAULT_CONFIG.copy()
    cfg.update(config)

    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)


def config_file_path() -> Path:
    return CONFIG_FILE


def get_saved_printer_address() -> str:
    return load_config().get("printer_address", "") or ""


def set_saved_printer_address(address: str):
    cfg = load_config()
    cfg["printer_address"] = address or ""
    save_config(cfg)


def clear_saved_printer_address():
    cfg = load_config()
    cfg["printer_address"] = ""
    save_config(cfg)


def get_density() -> int:
    return int(load_config().get("density", 5))


def set_density(density: int):
    density = max(1, min(5, int(density)))
    cfg = load_config()
    cfg["density"] = density
    save_config(cfg)


def get_row_delay_s() -> float:
    return float(load_config().get("row_delay_s", 0.012))


def set_row_delay_s(row_delay_s: float):
    cfg = load_config()
    cfg["row_delay_s"] = float(row_delay_s)
    save_config(cfg)
