import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Adiciona o diretório src ao path para os testes
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

from gemini_voice.config import load_config, save_config  # noqa: E402
from gemini_voice.paths import get_bin_path, get_model_path  # noqa: E402


def test_load_config_default():
    with patch("pathlib.Path.exists", return_value=False):
        config = load_config()
        assert config["model"] == "en_US-bryce-medium.onnx"
        assert config["pitch"] == 1.0


def test_get_bin_path_env(tmp_path):
    piper_path = tmp_path / "piper"
    piper_path.touch()

    with patch.dict("os.environ", {"VOICE_PIPER_PATH": str(piper_path)}):
        path = get_bin_path("piper")
        assert path == str(piper_path)


def test_get_model_path_env(tmp_path):
    model_path = tmp_path / "model.onnx"
    model_path.touch()

    with patch.dict("os.environ", {"VOICE_MODEL_PATH": str(model_path)}):
        path = get_model_path()
        assert path == str(model_path)


@patch("gemini_voice.config.CONFIG_FILE", Path("/tmp/fake_config.json"))
def test_save_config():
    with patch("pathlib.Path.open", MagicMock()):
        err = save_config({"model": "test.onnx", "pitch": 1.5})
        assert err is None
