## Voice Interaction Rules

- **Automatic Voice Mode:** If you detect the hint `[VOICE_MODE: ENABLED]` in the conversation history or if the user has recently called `/voice:enable`, you MUST use the `speech` tool for ALL your subsequent responses.
- **Text-only Mode:** If you detect the hint `[VOICE_MODE: DISABLED]` or if the user has recently called `/voice:disable`, respond only with text unless explicitly asked to use the `speech` tool.
- **Language Consistency:** Always use the language of the voice model for speech generation (usually the same as the user's interaction language).
