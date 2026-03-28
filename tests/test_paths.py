import sys
from pathlib import Path
from unittest.mock import patch

# Adiciona o diretório src ao path para os testes
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

from gemini_voice.paths import get_model_path  # noqa: E402


def test_get_model_path_redundant_prefix(tmp_path):
    # Mock MODELS_DIR to point to tmp_path/models
    models_dir = tmp_path / "models"
    models_dir.mkdir()

    # Create a dummy model file
    model_file = models_dir / "pt_BR-faber-medium.onnx"
    model_file.touch()

    # 1. Test with just filename
    with (
        patch("gemini_voice.paths.MODELS_DIR", models_dir),
        patch("gemini_voice.paths.load_config", return_value={"model": "pt_BR-faber-medium.onnx"}),
    ):
        path = get_model_path()
        assert path == str(model_file)

    # 2. Test with redundant "models/" prefix
    with (
        patch("gemini_voice.paths.MODELS_DIR", models_dir),
        patch(
            "gemini_voice.paths.load_config",
            return_value={"model": "models/pt_BR-faber-medium.onnx"},
        ),
    ):
        path = get_model_path()
        assert path == str(model_file)

    # 3. Test with "./models/" prefix
    with (
        patch("gemini_voice.paths.MODELS_DIR", models_dir),
        patch(
            "gemini_voice.paths.load_config",
            return_value={"model": "./models/pt_BR-faber-medium.onnx"},
        ),
    ):
        path = get_model_path()
        assert path == str(model_file)


def test_get_model_path_absolute(tmp_path):
    model_file = tmp_path / "abs-model.onnx"
    model_file.touch()

    with patch("gemini_voice.paths.load_config", return_value={"model": str(model_file)}):
        path = get_model_path()
        assert path == str(model_file)
