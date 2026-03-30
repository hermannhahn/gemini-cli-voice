import json
from pathlib import Path
from typing import Any, cast

# Caminhos padrão absolutos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = Path.home() / ".gemini"
CONFIG_FILE = CONFIG_DIR / "gemini-cli-voice.json"
DEFAULT_MODEL = "en_US-bryce-medium.onnx"


def load_config() -> dict[str, Any]:
    """Carrega as configurações do arquivo JSON persistente."""
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as f:
                config = cast(dict[str, Any], json.load(f))
                # Garante valores padrão se chaves estiverem ausentes
                if "enabled" not in config:
                    config["enabled"] = False
                return config
        except (json.JSONDecodeError, OSError):
            pass
    return {"model": DEFAULT_MODEL, "pitch": 1.0, "enabled": False}


def save_config(config: dict[str, Any]) -> str | None:
    """Salva as configurações no arquivo JSON persistente."""
    try:
        if not CONFIG_DIR.exists():
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except OSError as e:
        return str(e)
    return None
