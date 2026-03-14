# Gemini CLI Voice Extension

This extension provides a `speech` tool for the Gemini CLI, allowing the model to convert text into spoken audio using the Piper text-to-speech engine.

## Usage

The `speech` tool can be invoked by the model with a text input. This text will be synthesized into speech and played through the system's audio output.

**Example (conceptual model usage):**

```
Agent: "Estou pronto para começar o dia."
// Model internally calls the speech tool with "Estou pronto para começar o dia."
// User hears the spoken phrase.
```

## Tool Details

### `speech(text: str)`

Converts the provided `text` into spoken audio using the Piper text-to-speech engine.

-   **Parameters:**
    -   `text` (str): The text to be converted to speech.

## Installation and Configuration

This extension relies on the `piper` text-to-speech engine and `aplay` for audio playback. Ensure these are installed and configured correctly on your system.

The `speech` tool executes the following shell command:
`/home/hermann/piper/piper/piper -q --model /home/hermann/piper/miro_pt-BR.onnx --length_scale 1.2 --output-raw | aplay -r 22050 -f S16_LE -t raw 2>/dev/null`

**Note:** The path to the `piper` executable and the `miro_pt-BR.onnx` model file must match your system's setup.
