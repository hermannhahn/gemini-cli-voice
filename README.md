# Gemini CLI Voice Extension

[![Gemini CLI Extension](https://img.shields.io/badge/Gemini%20CLI-Extension-blue?logo=google-gemini&logoColor=white)](https://geminicli.com/extensions/gemini-cli-voice)
[![Version](https://img.shields.io/github/package-json/v/hermannhahn/gemini-cli-voice)](https://github.com/hermannhahn/gemini-cli-voice/releases)
[![CI/CD Workflow](https://github.com/hermannhahn/gemini-cli-voice/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/hermannhahn/gemini-cli-voice/actions/workflows/ci-cd.yml)
[![License](https://img.shields.io/github/license/hermannhahn/gemini-cli-voice)](https://github.com/hermannhahn/gemini-cli-voice/blob/main/LICENSE)
[![GitHub Topics](https://img.shields.io/github/topics/hermannhahn/gemini-cli-voice)](https://github.com/hermannhahn/gemini-cli-voice)

This extension adds the `speech` tool to Gemini CLI, allowing the model to communicate via synthesized audio using the Piper (TTS) engine. Now fully implemented in TypeScript for better performance and reliability.

## Professional Architecture and Structure

The project follows modern TypeScript development standards:

- **Modularization**: Logic separated into TypeScript modules in `src/`.
- **Static Typing**: Full type safety with TypeScript.
- **Bundling**: High-performance bundling using Webpack.
- **MCP Native**: Uses the official `@modelcontextprotocol/sdk`.
- **Cross-Platform**: Built-in support for Windows (PowerShell) and Linux (Aplay).

## System Requirements

1.  **Node.js & npm**
2.  **Aplay** (Linux) or **PowerShell** (Windows) for audio playback.

## Installation and Setup

To set up the development environment:
```bash
npm install
npm run build
```

## Installation in Gemini CLI

```bash
gemini extensions install https://github.com/hermannhahn/gemini-cli-voice.git
```

## Available Commands

### `/voice:enable`
Enables automatic voice response mode. From this moment on, the model MUST respond via the `speech` tool for all interactions.

### `/voice:disable`
Disables automatic voice response mode. The model will revert to text-only responses unless the `speech` tool is explicitly requested.

### `/voice:model [model_name]`
Changes the voice model (.onnx) used.
- **Without arguments**: Shows the current model and presents a list of available models for interactive selection (using `ask_user`).
- **With argument (name or path)**: Attempts to configure the specified model directly.
- **Supported models**: Includes voices in English, Portuguese, Spanish, French, German, Chinese, and Russian.

### `/voice:pitch [value]`
Changes the voice speed/pitch multiplier.
- **Without arguments**: Shows the current pitch and requests a new value (e.g., between 0.5 and 2.0) via an interactive interface.
- **With argument (number)**: Configures the pitch multiplier directly.

## Available Tools

### `mcp_voice_speech(text: string)`
Converts the provided text to spoken audio and plays it immediately. This is the primary tool for voice responses.
- **Conversation Rules**: If voice mode is active, the model should use only this tool, keep messages short (1-3 sentences), and skip unnecessary preambles.

### `mcp_voice_voice_toggle(enabled: boolean)`
Internally enables or disables automatic voice response mode.

### `mcp_voice_model(model: string)`
Changes the voice model (.onnx) in real-time, validating the path or filename in the `models/` folder.

### `mcp_voice_pitch(pitch: number)`
Changes the voice speed/pitch multiplier in real-time.

## How to Add More Voices

You can expand your voice library by downloading compatible Piper models (.onnx and .json):  
👉 **[Hugging Face - Piper Voices](https://huggingface.co/rhasspy/piper-voices/tree/main)**

### Configuration Methods

1. **Using a Custom Folder (Recommended)**:  
   Download your preferred voices to any folder on your system and point the extension to it:
   ```bash
   /voice:model /path/to/your/custom/models/folder/
   ```
   The extension will list all `.onnx` files in that folder for you to choose from.

2. **Using a Direct File Path**:  
   If you want to switch to a specific model directly:
   ```bash
   /voice:model /path/to/your-voice.onnx
   ```

3. **Manual Placement**:  
   Save both `.onnx` and `.json` files in the `models/` folder of this extension. They will then appear in the interactive selection list when you run `/voice:model` without arguments.
