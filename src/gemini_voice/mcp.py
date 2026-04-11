import json
import sys
from pathlib import Path
from typing import Any

from gemini_voice.config import load_config, save_config
from gemini_voice.paths import MODELS_DIR, get_bin_path, get_model_path
from gemini_voice.piper import run_speech_task

VERSION = "1.3.5"


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
    # Note: On Windows, UTF-8 is ensured by setting PYTHONUTF8=1 in launcher.js env.

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
                response["result"] = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "gemini-cli-voice-mcp", "version": VERSION},
                }
            elif method == "tools/list":
                config = load_config()
                voice_status = "ENABLED" if config.get("enabled", True) else "DISABLED"
                
                response["result"] = {
                    "tools": [
                        {
                            "name": "speech",
                            "description": (
                                f"CRITICAL: PRIMARY tool for audio responses. (CURRENT STATUS: {voice_status}) "
                                "Use this tool to speak text aloud to the user. "
                                "CONVERSATION RULES: "
                                f"(1) Since VOICE_MODE is {voice_status}, "
                                + ("ALWAYS call this tool for EVERY response. " if voice_status == "ENABLED" else "only call this if explicitly asked. ") +
                                "(2) Keep voice messages short, conversational and direct (1-2 sentences). "
                                "(3) Do NOT repeat the user's name at the start of every message. "
                                "TOKEN ECONOMY: "
                                "(A) Speech is slower than reading: be concise. "
                                "(B) Skip filler words and redundant pleasantries. "
                                "MANDATORY: Speak in the same language as the user (e.g., Brazilian Portuguese)."
                            ),
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string", "description": "The exact text to be spoken."}
                                },
                                "required": ["text"],
                            },
                        },
                        {
                            "name": "voice_toggle",
                            "description": "Enable or disable automatic voice response mode (VOICE_MODE).",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "enabled": {
                                        "type": "boolean",
                                        "description": "True to enable automatic speech for every turn, False to disable.",
                                    }
                                },
                                "required": ["enabled"],
                            },
                        },
                        {
                            "name": "model",
                            "description": "Change the active Piper voice model (.onnx). Use this when the user asks for a different voice or language.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "model": {
                                        "type": "string",
                                        "description": "Voice model filename or path (e.g., 'pt_BR-faber-medium').",
                                    }
                                },
                                "required": ["model"],
                            },
                        },
                        {
                            "name": "pitch",
                            "description": "Adjust the speaking speed (pitch/length_scale). Range: 0.5 (slow) to 2.0 (fast). Default: 1.0.",
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
