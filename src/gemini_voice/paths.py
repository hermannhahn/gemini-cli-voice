import os
import platform
from pathlib import Path

from gemini_voice.config import BASE_DIR, DEFAULT_MODEL, load_config

MODELS_DIR = BASE_DIR / "models"
BIN_DIR = BASE_DIR / "bin"


def get_bin_path(bin_name: str) -> str | None:
    """Retorna o caminho do binário para o sistema operacional atual."""
    # Prioridade para variável de ambiente
    if bin_name == "piper":
        env_path = os.environ.get("VOICE_PIPER_PATH")
        if env_path and Path(env_path).exists():
            return env_path

    system = platform.system().lower()
    if system == "linux":
        path = BIN_DIR / "linux" / bin_name
    elif system == "windows":
        if not bin_name.endswith(".exe"):
            bin_name += ".exe"
        path = BIN_DIR / "windows" / bin_name
    else:
        return None

    if path.exists():
        return str(path)
    return None


def get_model_path() -> str | None:
    """Retorna o caminho do modelo de voz .onnx."""
    # Prioridade para variável de ambiente
    env_path = os.environ.get("VOICE_MODEL_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    config = load_config()
    model_val = config.get("model", DEFAULT_MODEL)
    model_path = Path(model_val)

    if model_path.is_absolute() and model_path.exists():
        return str(model_path)

    # 1. Tentar diretamente como fornecido em MODELS_DIR
    relative_path = MODELS_DIR / model_val
    if relative_path.exists():
        return str(relative_path)

    # 2. Se falhar, tentar apenas o nome do arquivo se o caminho contiver diretórios (prefixo redundante)
    name_only = model_path.name
    name_path = MODELS_DIR / name_only
    if name_path.exists():
        return str(name_path)

    # 3. Fallback para o modelo padrão se o configurado falhar
    fallback_default = MODELS_DIR / DEFAULT_MODEL
    if fallback_default.exists():
        return str(fallback_default)

    if MODELS_DIR.exists():
        # Busca o primeiro arquivo .onnx disponível
        for f in sorted(MODELS_DIR.iterdir()):
            if f.suffix == ".onnx":
                return str(f)
    return None
