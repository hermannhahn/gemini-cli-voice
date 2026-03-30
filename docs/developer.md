# Developer Documentation

This document provides technical information about the architecture, development workflow, and deployment process for the Gemini CLI Voice Extension.

## Architecture Overview

The project uses a hybrid architecture combining Node.js (for the Gemini CLI extension shell) and Python (for the MCP - Model Context Protocol server).

### Key Components

- **Node.js Shell**: Defined in `package.json` and `gemini-extension.json`. It registers the extension and its commands.
- **MCP Server**: Implemented in `tool_code.py` (entry point) and supported by the `gemini_voice` Python package in `src/`.
- **Piper TTS Engine**: A fast, local text-to-speech engine. Binaries are stored in `bin/` and models in `models/`.
- **Commands**: Located in `commands/voice/`, these define the behavior of `/voice:*` commands.

## Technical Stack

- **Python 3.10+**: Core logic, MCP implementation, and Piper integration.
- **Node.js & npm**: Extension packaging, script management, and release automation.
- **Piper**: High-quality local TTS.
- **Ruff**: Fast Python linting and formatting.
- **MyPy**: Static type checking.
- **Pytest**: Unit testing.

## Development Workflow

1.  **Branching**: Work should be done on the `development` branch.
2.  **Modifications**: Apply changes to the source code or command definitions.
3.  **Testing**:
    - Run unit tests: `npm run test:py`.
    - Run linting: `npm run lint:py`.
    - Run type checking: `npm run typecheck:py`.
4.  **Local Verification**:
    - Ask the user to restart the CLI to test modifications.
5.  **Commit and Push**: Always push changes to the `development` branch first.

## Deploy Workflow

1.  **Version Update**: Run `npm run update:version`. This script:
    - Runs all checks (lint, tests).
    - Updates the version in `package.json` and related files.
    - Commits and pushes the version bump.
2.  **Pull Request**: Create a PR from `development` to `main` using `gh pr create`.
3.  **Review**: Wait for user review and approval.
4.  **Merge**: Once approved, merge the PR (e.g., using `gh pr merge`).
5.  **Deploy**: Run `npm run deploy` from the `development` branch. This script:
    - Switches to `main`.
    - Pulls changes.
    - Creates and pushes a git tag (e.g., `v1.2.21`).
    - Creates a GitHub release.
    - Updates the local extension instance.
    - Returns to `development` branch.
6.  **Final Verification**: Ask the user to restart the CLI and verify the new version.

## Model Management

Voices are stored in the `models/` directory as `.onnx` files with corresponding `.json` metadata.
To add new voices:
1.  Download from [Piper Voices](https://huggingface.co/rhasspy/piper-voices/tree/main).
2.  Place `.onnx` and `.json` in the `models/` folder.
3.  Update `commands/voice/model.toml` if you want to include them in the interactive selection menu.

## Configuration

Settings are persisted in a JSON file located at `~/.gemini/gemini-cli-voice.json`.
The configuration includes:
- `enabled`: Boolean flag for automatic voice response mode.
- `model`: Name or path of the current voice model (.onnx).
- `pitch`: Speed multiplier (float).
