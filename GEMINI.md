## Voice Interaction Rules

- **MANDATORY Voice Response:** If `[VOICE_MODE: ENABLED]` is present in the context or if the user recently activated voice mode (via `/voice:enable`), YOU MUST NEVER respond with plain text. Every single response you provide MUST be wrapped in the `speech` tool. This is non-negotiable for the voice interaction flow.
- **Continuous Mode:** Once voice mode is active, do not stop using the `speech` tool until you explicitly see `[VOICE_MODE: DISABLED]` or a clear command to deactivate it.
- **Context Salience:** Always look for the `[VOICE_MODE: ...]` marker in the last tool output to determine your current response format.
- **Language Consistency:** Always use the language of the voice model for speech generation.
