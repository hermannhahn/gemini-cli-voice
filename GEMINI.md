# gemini-cli-voice

## Core Mandates
- Use the `speech` tool whenever the user asks to "falar", "dizer", "ler em voz alta", or any request that implies audio feedback.
- If the tool fails (e.g., Piper or model not found), inform the user and suggest checking `VOICE_PIPER_PATH` or `VOICE_MODEL_PATH`.
