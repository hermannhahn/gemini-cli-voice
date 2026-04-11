import json
import logging
import sys
from pathlib import Path
from typing import Any

# Add src directory to path
src_path = Path(__file__).resolve().parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from gemini_voice.config import load_config, save_config
from gemini_voice.paths import get_bin_path, get_model_path
from gemini_voice.piper import piper_speak

VERSION = "1.3.5"

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("gemini-voice-mcp")


def speech_handler(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handler for the 'speech' tool."""
    text = arguments.get("text", "")
    if not text:
        return {"content": [{"type": "text", "text": "Error: No text provided."}], "isError": True}

    config = load_config()
    model = get_model_path(config.get("model"))
    piper_exe = get_bin_path("piper")

    if not model or not Path(model).exists():
        return {
            "content": [{"type": "text", "text": f"Error: Model not found at {model}"}],
            "isError": True,
        }

    if not piper_exe or not Path(piper_exe).exists():
        return {
            "content": [{"type": "text", "text": f"Error: Piper not found at {piper_exe}"}],
            "isError": True,
        }

    # Execute piper-speak
    err = piper_speak(text, model, piper_exe, pitch=config.get("pitch", 1.0))

    if err:
        return {"content": [{"type": "text", "text": f"Error: {err}"}], "isError": True}

    return {"content": [{"type": "text", "text": "OK"}]}


def voice_toggle_handler(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handler for the 'voice_toggle' tool."""
    enabled = arguments.get("enabled", True)
    config = load_config()
    config["enabled"] = enabled
    save_config(config)

    status = "enabled" if enabled else "disabled"
    return {"content": [{"type": "text", "text": f"Voice mode {status}."}]}


def model_handler(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handler for the 'model' tool."""
    model_name = arguments.get("model", "")
    if not model_name:
        return {"content": [{"type": "text", "text": "Error: No model name provided."}], "isError": True}

    # Check if file exists in models directory
    model_path = get_model_path(model_name)
    if not model_path or not Path(model_path).exists():
        return {
            "content": [{"type": "text", "text": f"Error: Model {model_name} not found."}],
            "isError": True,
        }

    config = load_config()
    config["model"] = model_name
    save_config(config)

    return {"content": [{"type": "text", "text": f"Voice model changed to {model_name}."}]}


def pitch_handler(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handler for the 'pitch' tool."""
    try:
        pitch = float(arguments.get("pitch", 1.0))
    except (ValueError, TypeError):
        return {"content": [{"type": "text", "text": "Error: Invalid pitch value."}], "isError": True}

    config = load_config()
    config["pitch"] = pitch
    save_config(config)

    return {"content": [{"type": "text", "text": f"Voice pitch changed to {pitch}."}]}


def get_config_handler(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handler for the 'get_config' tool (internal use)."""
    config = load_config()
    return {"content": [{"type": "text", "text": json.dumps(config)}]}


def set_config_handler(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handler for the 'set_config' tool (internal use)."""
    try:
        new_config = arguments.get("config", {})
        if not isinstance(new_config, dict):
            return {"content": [{"type": "text", "text": "Error: Invalid config."}], "isError": True}

        config = load_config()
        config.update(new_config)
        save_config(config)
        return {"content": [{"type": "text", "text": "Config updated."}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}


def main() -> None:
    """Main loop for the MCP server."""
    # Note: On Windows, UTF-8 is ensured by setting PYTHONUTF8=1 in launcher.js env.

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            req_id = request.get("id")

            if not method:
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
                v_status = "ENABLED" if config.get("enabled", True) else "DISABLED"
                p_text = "ALWAYS call this tool for EVERY response. "
                s_text = "only call this if explicitly asked. "
                v_instr = p_text if v_status == "ENABLED" else s_text

                response["result"] = {
                    "tools": [
                        {
                            "name": "speech",
                            "description": (
                                f"CRITICAL: PRIMARY tool for audio responses. (STATUS: {v_status}) "
                                "Use this tool to speak text aloud to the user. "
                                "CONVERSATION RULES: "
                                f"(1) Since VOICE_MODE is {v_status}, {v_instr}"
                                "(2) Keep voice messages short and direct (1-2 sentences). "
                                "(3) Do NOT repeat the user's name at the start. "
                                "TOKEN ECONOMY: "
                                "(A) Speech is slower than reading: be concise. "
                                "(B) Skip filler words and redundant pleasantries. "
                                "MANDATORY: Speak in the same language as the user."
                            ),
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "text": {
                                        "type": "string",
                                        "description": "The exact text to be spoken.",
                                    }
                                },
                                "required": ["text"],
                            },
                        },
                        {
                            "name": "voice_toggle",
                            "description": "Enable/disable automatic voice response mode.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "enabled": {
                                        "type": "boolean",
                                        "description": "True: automatic speech, False: manual.",
                                    }
                                },
                                "required": ["enabled"],
                            },
                        },
                        {
                            "name": "model",
                            "description": "Change the active Piper voice model (.onnx).",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "model": {
                                        "type": "string",
                                        "description": "Model filename (e.g., 'pt_BR-faber').",
                                    }
                                },
                                "required": ["model"],
                            },
                        },
                        {
                            "name": "pitch",
                            "description": "Adjust speaking speed. Range: 0.5 to 2.0.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "pitch": {
                                        "type": "number",
                                        "description": "Speed multiplier. Default: 1.0.",
                                    }
                                },
                                "required": ["pitch"],
                            },
                        },
                    ]
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "speech":
                    response["result"] = speech_handler(arguments)
                elif tool_name == "voice_toggle":
                    response["result"] = voice_toggle_handler(arguments)
                elif tool_name == "model":
                    response["result"] = model_handler(arguments)
                elif tool_name == "pitch":
                    response["result"] = pitch_handler(arguments)
                else:
                    response["error"] = {"code": -32601, "message": f"Tool not found: {tool_name}"}
            else:
                response["error"] = {"code": -32601, "message": f"Method not found: {method}"}

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except Exception as e:
            logger.exception("Error in main loop")
            err_resp = {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
