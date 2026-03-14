# Project Overview: gemini-cli-voice

This directory contains the `gemini-cli-voice` project, which is a specialized extension designed to integrate text-to-speech capabilities into the Gemini CLI.

## Purpose

The primary goal of this extension is to enable the AI model to communicate with the user via spoken audio. By providing a `speech` tool, the model can convert text into speech, enhancing interactivity and accessibility. This is particularly useful for:
- Delivering verbal confirmations or instructions.
- Providing spoken responses to user queries.
- Creating a more natural conversational experience.

## Key Files

-   **README.md**: User-facing documentation describing the extension and its usage.
-   **GEMINI.md**: This internal documentation providing context for AI-driven development.
-   **tool_code.py**: Contains the Python implementation of the `speech` tool.

## Usage (Model's Perspective)

The model should use the `speech` tool whenever:
- The user explicitly asks for a voice response (e.g., "fale", "responda por voz", "leia isso").
- The user's intent implies verbal feedback is desired.
- The user's name is "Hermann", use phonetic spelling "Rérmann" for better pronunciation in audio.

### `speech(text: str)`
- **Description**: Converts the provided `text` into spoken audio using the Piper engine.
- **Language**: Ensure the `text` passed to the tool is in the same language as the user's request (typically Portuguese).
- **Phonetics**: For specific names or terms that might be mispronounced, you may use phonetic approximations in the input string.

## Development and Architecture

-   **Technologies**: Python for tool implementation, `piper` (text-to-speech engine), `aplay` (audio playback).
-   **Conventions**: Documentation for both users (`README.md`) and internal AI context (`GEMINI.md`) is maintained within this root directory. Tool definitions are inlined in `gemini-extension.json`; implementation is in `tool_code.py`.
