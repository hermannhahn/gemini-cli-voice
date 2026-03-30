# Gemini CLI Voice Extension

This extension adds the `speech` tool to Gemini CLI, allowing the model to communicate via synthesized audio using the Piper (TTS) engine.

## Professional Architecture and Structure

The project follows modern hybrid development standards (Node.js and Python):

- **Modularization**: Logic separated into Python packages in `src/gemini_voice/`.
- **Static Typing**: Extensive use of *type hints* and validation with `mypy`.
- **Linting & Formatting**: Standardized with `ruff` for maximum speed and consistency.
- **Testing**: Automated test suite with `pytest`.
- **Dependency Management**: Isolated Python virtual environment managed via `npm` scripts.

## System Requirements

1.  **Python 3.10+**
2.  **Node.js & npm**
3.  **Aplay** (Linux) or **PowerShell** (Windows) for audio playback.

## Installation and Setup

To set up the development environment:
```bash
npm install
npm run setup:py
```

This will create a `.venv` virtual environment and install all development tools.

## Installation in Gemini CLI

```bash
gemini extensions install https://github.com/hermannhahn/gemini-cli-voice.git
```

## Development

- **Linting and Types**: `npm run lint`
- **Tests**: `npm run test`
- **Automatic Formatting**: `npm run format:py`

## Available Commands

- `/voice:enable`: Enables automatic voice mode. The model will use voice for all responses.
- `/voice:disable`: Disables automatic voice mode. The model will revert to text-only responses.
- `/voice:model`: Changes the voice model (.onnx).
- `/voice:pitch`: Changes the voice speed/pitch (multiplier).

## Available Tools

### `speech(text: str)`
Converts the provided text to spoken audio and plays it immediately. If voice mode is active (`VOICE_MODE: ENABLED`), the model will call this tool automatically.

### `voice_toggle(enabled: bool)`
Enables or disables automatic voice response mode.

### `model(model: str)`
Changes the voice model in real-time.

### `pitch(pitch: float)`
Changes the voice speed/pitch (multiplier).

## How to Add More Voices

Download compatible Piper voices:  
👉 [Hugging Face - Piper Voices](https://huggingface.co/rhasspy/piper-voices/tree/main)

Save the `.onnx` and `.json` files in the `models/` folder or configure the path via:
```bash
gemini extensions config gemini-cli-voice "Voice Model Path" /full/path/to/your-voice.onnx
```

Or via environment variables:
```bash
export VOICE_PIPER_PATH="/path/to/piper"
export VOICE_MODEL_PATH="/path/to/your-voice.onnx"
```
