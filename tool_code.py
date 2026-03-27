import sys
import json
import subprocess
import os
import shutil
import threading

# Caminhos padrão absolutos baseados na localização do script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
MODELS_DIR = os.path.join(BASE_DIR, "models")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"model": "pt_BR-faber-medium.onnx", "pitch": 1.0}

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        return str(e)
    return None

def find_piper():
    piper_path = shutil.which("piper")
    if piper_path:
        return piper_path
    
    home_piper = os.path.expanduser("~/piper/piper/piper")
    if os.path.isfile(home_piper) and os.access(home_piper, os.X_OK):
        return home_piper
    return None

def get_model_path():
    config = load_config()
    model_path = os.path.join(MODELS_DIR, config.get("model", "pt_BR-faber-medium.onnx"))
    if os.path.exists(model_path):
        return model_path
    
    if os.path.exists(MODELS_DIR):
        for f in sorted(os.listdir(MODELS_DIR)):
            if f.endswith(".onnx"):
                return os.path.join(MODELS_DIR, f)
    return None

def run_speech_task(command, text):
    try:
        p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
        p.communicate(input=text.encode('utf-8'))
    except Exception:
        pass

def speech_handler(arguments):
    text = arguments.get("text", "")
    if not text.strip():
        return {"content": [{"type": "text", "text": "Error: Empty text."}]}

    config = load_config()
    piper_exe = find_piper()
    model_file = get_model_path()

    if not piper_exe:
        return {"isError": True, "content": [{"type": "text", "text": "Error: Piper binary not found."}]}
    if not model_file:
        return {"isError": True, "content": [{"type": "text", "text": "Error: Voice model not found."}]}

    pitch = float(config.get("pitch", 1.0))
    length_scale = 1.0 / pitch if pitch > 0 else 1.0

    command = f"'{piper_exe}' -q --model '{model_file}' --length_scale {length_scale} --output-raw | aplay -r 22050 -f S16_LE -t raw 2>/dev/null"

    try:
        threading.Thread(target=run_speech_task, args=(command, text), daemon=True).start()
        return {"content": [{"type": "text", "text": f"Speech started (Model: {os.path.basename(model_file)}, Pitch: {pitch})"}]}
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": f"Error: {str(e)}"}]}

def list_models_handler():
    if not os.path.exists(MODELS_DIR):
        return {"isError": True, "content": [{"type": "text", "text": "Models directory not found."}]}
    
    models = [f for f in sorted(os.listdir(MODELS_DIR)) if f.endswith(".onnx")]
    return {"content": [{"type": "text", "text": "Available models:\n" + "\n".join(models)}]}

def set_config_handler(arguments):
    config = load_config()
    updated = False
    
    if "model" in arguments:
        model_name = arguments["model"]
        if not model_name.endswith(".onnx"):
            model_name += ".onnx"
        
        if os.path.exists(os.path.join(MODELS_DIR, model_name)):
            config["model"] = model_name
            updated = True
        else:
            return {"isError": True, "content": [{"type": "text", "text": f"Error: Model '{model_name}' not found in models/ directory."}]}
            
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
        return {"content": [{"type": "text", "text": f"Voice configuration updated: Model={config['model']}, Pitch={config['pitch']}"}]}
    
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
                        "serverInfo": {"name": "gemini-cli-voice-mcp", "version": "1.2.1"}
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
                                "description": "Converts text to spoken audio. Usage: speech(text='Hello')",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "text": {"type": "string", "description": "Text to speak"}
                                    },
                                    "required": ["text"]
                                }
                            },
                            {
                                "name": "voice_config",
                                "description": "Configure voice settings. Use to change model or pitch. Examples: voice_config(model='pt_BR-cadu-medium.onnx'), voice_config(pitch=1.2)",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "model": {"type": "string", "description": "Filename of the .onnx model"},
                                        "pitch": {"type": "number", "description": "Speed multiplier (e.g., 1.2)"}
                                    }
                                }
                            },
                            {
                                "name": "voice_list_models",
                                "description": "Lists all available voice models in the extension directory.",
                                "inputSchema": {"type": "object", "properties": {}}
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                tool_name = request.get("params", {}).get("name")
                arguments = request.get("params", {}).get("arguments", {})
                
                if tool_name == "speech":
                    result = speech_handler(arguments)
                elif tool_name == "voice_config":
                    result = set_config_handler(arguments)
                elif tool_name == "voice_list_models":
                    result = list_models_handler()
                else:
                    result = {"isError": True, "content": [{"type": "text", "text": "Tool not found"}]}
                
                response = {"jsonrpc": "2.0", "id": req_id, "result": result}
            else:
                response = {"jsonrpc": "2.0", "id": req_id, "result": {}}

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except EOFError:
            break
        except Exception:
            continue

if __name__ == "__main__":
    main()
