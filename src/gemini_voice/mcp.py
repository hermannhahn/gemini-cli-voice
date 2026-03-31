import json
import sys
from pathlib import Path
from typing import Any

from gemini_voice.config import load_config, save_config
from gemini_voice.paths import MODELS_DIR, get_bin_path, get_model_path
from gemini_voice.piper import run_speech_task

VERSION = "1.2.23"


def speech_handler(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handler for the 'speech' tool."""
    text = arguments.get("text", "")
    if not text.strip():
        return {"content": [{"type": "text", "text": "Error: Empty text."}]}

    config = load_config()
    piper_exe = get_bin_path("piper")
    model_file = get_model_path()

    if not piper_exe:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "Error: Piper binary not found."}],
        }
    if not model_file:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "Error: Voice model not found."}],
        }

    pitch = float(config.get("pitch", 1.0))
    length_scale = 1.0 / pitch if pitch > 0 else 1.0

    error = run_speech_task(piper_exe, model_file, length_scale, text)

    if error:
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Error during playback: {error}"}],
        }

    return {
        "content": [
            {
                "type": "text",
                "text": f"Finished speaking (Model: {Path(model_file).name})",
            }
        ]
    }


def voice_toggle_handler(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handler for the 'voice_toggle' tool."""
    config = load_config()
    enabled = arguments.get("enabled", False)
    config["enabled"] = enabled

    err = save_config(config)
    if err:
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Error saving config: {err}"}],
        }

    status = "ENABLED" if enabled else "DISABLED"
    msg = f"Voice mode is now {status}."

    return {
        "content": [
            {
                "type": "text",
                "text": msg,
            }
        ]
    }


def set_config_handler(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handler for 'model' and 'pitch' tools."""
    config = load_config()
    updated = False

    if "model" in arguments:
        model_val = arguments["model"]
        if not model_val.endswith(".onnx"):
            model_val += ".onnx"

        model_path = Path(model_val)

        # 1. Try as absolute path
        if model_path.is_absolute() and model_path.is_file():
            config["model"] = str(model_path)
            updated = True
        else:
            # 2. Try to resolve against MODELS_DIR
            name_only = model_path.name
            if (MODELS_DIR / name_only).exists():
                config["model"] = name_only
                updated = True
            elif (MODELS_DIR / model_val).exists():
                config["model"] = model_val
                updated = True
            # 3. Try as relative path to current CWD
            elif model_path.exists() and model_path.is_file():
                config["model"] = str(model_path.resolve())
                updated = True
            else:
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Error: Model '{model_val}' not found."}],
                }

    if "pitch" in arguments:
        try:
            config["pitch"] = float(arguments["pitch"])
            updated = True
        except ValueError:
            return {
                "isError": True,
                "content": [{"type": "text", "text": "Error: Pitch must be a number."}],
            }

    if updated:
        err = save_config(config)
        if err:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Error saving config: {err}"}],
            }
        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Voice configuration updated: "
                        f"Model={Path(config['model']).name}, "
                        f"Pitch={config['pitch']}"
                    ),
                }
            ]
        }

    return {"content": [{"type": "text", "text": "No changes applied."}]}


def main() -> None:
    """Main loop for the MCP server."""
    # Redirect stderr to prevent library messages from breaking stdout
    import os
    sys.stderr = Path(os.devnull).open("w")  # noqa: SIM115

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                continue

            method = request.get("method")
            req_id = request.get("id")

            # Notifications have no ID and should not be answered
            if req_id is None and method != "initialize":
                continue

            response: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id}

            if method == "initialize":
                config = load_config()
                instructions = ""
                if config.get("enabled", False):
                    instructions = (
                        "VOICE MODE IS ENABLED. For every single response, "
                        "you MUST use the 'speech' tool. Do NOT output plain text."
                    )
                response["result"] = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "gemini-cli-voice-mcp", "version": VERSION},
                    "instructions": instructions,
                }
            elif method == "tools/list":
                response["result"] = {
                    "tools": [
                        {
                            "name": "speech",
                            "description": (
                                "Converts text to spoken audio and blocks until finished. "
                                "This is the PRIMARY tool for audio responses. "
                                "CONVERSATION RULES: "
                                "(1) If VOICE_MODE: ENABLED is active, ALWAYS call this tool "
                                "(2) Keep voice messages short and conversational (1-3 sentences). "
                                "Do NOT say the user's name every time at the beginning of voice "
                                "messages, answer directly."
                                "TOKEN ECONOMY: "
                                "(A) Keep 'text' under 2 sentences — speech is slower than "
                                "reading, so less is more. "
                                "(C) Skip filler words. "
                                "MANDATORY: Use model's language."
                            ),
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string", "description": "Text to speak."}
                                },
                                "required": ["text"],
                            },
                        },
                        {
                            "name": "voice_toggle",
                            "description": "Enable or disable automatic voice response mode.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "enabled": {
                                        "type": "boolean",
                                        "description": "True to enable, False to disable.",
                                    }
                                },
                                "required": ["enabled"],
                            },
                        },
                        {
                            "name": "model",
                            "description": "Change voice model (.onnx).",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "model": {
                                        "type": "string",
                                        "description": "Voice model file.",
                                    }
                                },
                                "required": ["model"],
                            },
                        },
                        {
                            "name": "pitch",
                            "description": "Change voice speed (pitch).",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "pitch": {
                                        "type": "number",
                                        "description": "Speed multiplier.",
                                    }
                                },
                                "required": ["pitch"],
                            },
                        },
                    ]
                }
            elif method == "tools/call":
                tool_name = request.get("params", {}).get("name")
                params = request.get("params", {}).get("arguments", {})

                if tool_name == "speech":
                    result = speech_handler(params)
                elif tool_name == "voice_toggle":
                    result = voice_toggle_handler(params)
                elif tool_name in ("model", "pitch"):
                    result = set_config_handler(params)
                else:
                    result = {
                        "isError": True,
                        "content": [{"type": "text", "text": f"Tool '{tool_name}' not found"}],
                    }

                response["result"] = result
            else:
                # For unknown methods that require response
                response["error"] = {"code": -32601, "message": f"Method '{method}' not found"}

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except EOFError:
            break
        except Exception:
            # In case of catastrophic error, try not to break the loop silently
            continue
