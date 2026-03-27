import sys
import json
import subprocess
import os
import tempfile
import platform
import shutil

# Caminhos padrão absolutos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
MODELS_DIR = os.path.join(BASE_DIR, "models")
BIN_DIR = os.path.join(BASE_DIR, "bin")
DEFAULT_MODEL = "en_US-ryan-low.onnx"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"model": DEFAULT_MODEL, "pitch": 1.0}

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except OSError as e:
        return str(e)
    return None

def get_bin_path(bin_name):
    system = platform.system().lower()
    if system == "linux":
        path = os.path.join(BIN_DIR, "linux", bin_name)
    elif system == "windows":
        if not bin_name.endswith(".exe"):
            bin_name += ".exe"
        path = os.path.join(BIN_DIR, "windows", bin_name)
    else:
        return None

    if os.path.exists(path):
        return path
    return None

def get_model_path():
    config = load_config()
    model_val = config.get("model", DEFAULT_MODEL)

    if os.path.isabs(model_val) and os.path.exists(model_val):
        return model_val

    model_path = os.path.join(MODELS_DIR, model_val)
    if os.path.exists(model_path):
        return model_path

    fallback_default = os.path.join(MODELS_DIR, DEFAULT_MODEL)
    if os.path.exists(fallback_default):
        return fallback_default

    if os.path.exists(MODELS_DIR):
        files = sorted(os.listdir(MODELS_DIR))
        for f in files:
            if f.endswith(".onnx"):
                return os.path.join(MODELS_DIR, f)
    return None

def run_speech_task(piper_exe, model_file, length_scale, text):
    system = platform.system().lower()

    # Prepara o ambiente para carregar bibliotecas locais
    env = os.environ.copy()
    if system == "linux":
        linux_bin_dir = os.path.join(BIN_DIR, "linux")
        env["LD_LIBRARY_PATH"] = f"{linux_bin_dir}:{env.get('LD_LIBRARY_PATH', '')}"

    # Cria arquivo temporário para o WAV
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        temp_wav = tf.name

    try:
        # 1. Piper gera o WAV
        piper_cmd = [piper_exe, "-q", "--model", model_file, "--length_scale", str(length_scale), "--output_file", temp_wav]
        with subprocess.Popen(piper_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env) as p:
            p.communicate(input=text.encode('utf-8'))

        if system == "linux":
            aplay_exe = get_bin_path("aplay")
            if not aplay_exe:
                aplay_exe = shutil.which("aplay")

            if aplay_exe:
                # 2. Toca o WAV de forma síncrona
                subprocess.run([aplay_exe, temp_wav], check=False, stderr=subprocess.DEVNULL)

        elif system == "windows":
            # 2. PowerShell toca o WAV de forma síncrona
            ps_cmd = f"powershell -c \"(New-Object Media.SoundPlayer '{temp_wav}').PlaySync()\""
            subprocess.run(ps_cmd, shell=True, check=False, stderr=subprocess.DEVNULL)

        return None
    except subprocess.SubprocessError as e:
        return str(e)
    except OSError as e:
        return str(e)
    finally:
        # 3. Limpa o arquivo temporário
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except OSError:
                pass

def speech_handler(arguments):
    text = arguments.get("text", "")
    if not text.strip():
        return {"content": [{"type": "text", "text": "Error: Empty text."}]}

    config = load_config()
    piper_exe = get_bin_path("piper")
    model_file = get_model_path()

    if not piper_exe:
        return {"isError": True, "content": [{"type": "text", "text": "Error: Piper binary not found."}]}
    if not model_file:
        return {"isError": True, "content": [{"type": "text", "text": "Error: Voice model not found."}]}

    pitch = float(config.get("pitch", 1.0))
    length_scale = 1.0 / pitch if pitch > 0 else 1.0

    # Chamada TOTALMENTE SÍNCRONA
    error = run_speech_task(piper_exe, model_file, length_scale, text)

    if error:
        return {"isError": True, "content": [{"type": "text", "text": f"Error during playback: {error}"}]}

    return {"content": [{"type": "text", "text": f"Finished speaking (Model: {os.path.basename(model_file)})"}]}

def set_config_handler(arguments):
    config = load_config()
    updated = False

    if "model" in arguments:
        model_val = arguments["model"]
        if os.path.isabs(model_val) and os.path.isfile(model_val) and model_val.endswith(".onnx"):
            config["model"] = model_val
            updated = True
        else:
            if not model_val.endswith(".onnx"):
                model_val += ".onnx"
            if os.path.exists(os.path.join(MODELS_DIR, model_val)):
                config["model"] = model_val
                updated = True
            else:
                return {"isError": True, "content": [{"type": "text", "text": f"Error: Model '{model_val}' not found."}]}

    if "pitch" in arguments:
        try:
            config["pitch"] = float(arguments["pitch"])
            updated = True
        except ValueError:
            return {"isError": True, "content": [{"type": "text", "text": "Error: Pitch must be a number."}]}

    if updated:
        err = save_config(config)
        if err:
            return {"isError": True, "content": [{"type": "text", "text": f"Error saving config: {err}"}]}
        return {"content": [{"type": "text", "text": f"Voice configuration updated: Model={os.path.basename(config['model'])}, Pitch={config['pitch']}"}]}

    return {"content": [{"type": "text", "text": "No changes applied."}]}

def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line)
            method = request.get("method")
            req_id = request.get("id")

            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "gemini-cli-voice-mcp", "version": "1.2.3"}
                    }
                }
            elif method == "notifications/initialized":
                continue

            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": [
                            {
                                "name": "speech",
                                "description": "Converts text to spoken audio and blocks until finished. MANDATORY: Use model's language.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "text": {"type": "string", "description": "Text to speak."}
                                    },
                                    "required": ["text"]
                                }
                            },
                            {
                                "name": "model",
                                "description": "Change voice model (.onnx).",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "model": {"type": "string", "description": "Voice model file."}
                                    },
                                    "required": ["model"]
                                }
                            },
                            {
                                "name": "pitch",
                                "description": "Change voice speed (pitch).",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "pitch": {"type": "number", "description": "Speed multiplier."}
                                    },
                                    "required": ["pitch"]
                                }
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                tool_name = request.get("params", {}).get("name")
                params = request.get("params", {}).get("arguments", {})

                if tool_name == "speech":
                    result = speech_handler(params)
                elif tool_name in ("model", "pitch"):
                    result = set_config_handler(params)
                else:
                    result = {"isError": True, "content": [{"type": "text", "text": "Tool not found"}]}

                response = {"jsonrpc": "2.0", "id": req_id, "result": result}
            else:
                response = {"jsonrpc": "2.0", "id": req_id, "result": {}}

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except EOFError:
            break
        except (json.JSONDecodeError, KeyError, ValueError):
            continue

if __name__ == "__main__":
    main()
