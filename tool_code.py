import sys
import json
import subprocess
import os
import shutil
import threading

def find_piper():
    # ... (rest remains same until speech_handler)
    # 1. Tenta encontrar no PATH do sistema
    piper_path = shutil.which("piper")
    if piper_path:
        return piper_path
    
    # 2. Tenta caminhos comuns (incluindo o seu atual como fallback)
    home = os.path.expanduser("~")
    common_paths = [
        os.path.join(home, "piper/piper/piper"),
        os.path.join(home, "piper/piper"),
        os.path.join(home, "piper"),
        "/usr/local/bin/piper"
    ]
    
    for path in common_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None

def find_model():
    # 1. Tenta encontrar no diretório da extensão ou no home
    home = os.path.expanduser("~")
    extension_dir = os.path.dirname(os.path.abspath(__file__))
    
    model_names = ["miro_pt-BR.onnx", "pt_BR-faber-medium.onnx"] # Modelos comuns
    search_dirs = [
        extension_dir,
        os.path.join(home, "piper"),
        "/usr/local/share/piper"
    ]
    
    # Se houver um caminho específico no seu home
    legacy_path = os.path.join(home, "piper/miro_pt-BR.onnx")
    if os.path.isfile(legacy_path):
        return legacy_path

    for d in search_dirs:
        for m in model_names:
            path = os.path.join(d, m)
            if os.path.isfile(path):
                return path

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

    piper_exe = os.environ.get("VOICE_PIPER_PATH") or find_piper()
    model_file = os.environ.get("VOICE_MODEL_PATH") or find_model()

    if not piper_exe:
        return {"isError": True, "content": [{"type": "text", "text": "Error: Piper not found."}]}
    if not model_file:
        return {"isError": True, "content": [{"type": "text", "text": "Error: Voice model not found."}]}

    command = f"'{piper_exe}' -q --model '{model_file}' --length_scale 1.2 --output-raw | aplay -r 22050 -f S16_LE -t raw 2>/dev/null"

    try:
        threading.Thread(target=run_speech_task, args=(command, text), daemon=True).start()
        return {"content": [{"type": "text", "text": "Speech started."}]}
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": f"Error: {str(e)}"}]}

def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            version = json.load(open(os.path.join(os.path.dirname(__file__), 'package.json'))).get('version', '1.0.0')
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
                        "serverInfo": {"name": "gemini-cli-voice-mcp", "version": version}
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
                                "description": "Converts text to spoken audio via Piper. IMPORTANT: Use this tool whenever the user asks to speech or use voice.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "text": {"type": "string", "description": "The text to be converted to speech."}
                                    },
                                    "required": ["text"]
                                }
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                tool_name = request.get("params", {}).get("name")
                arguments = request.get("params", {}).get("arguments", {})
                
                if tool_name == "speech":
                    result = speech_handler(arguments)
                    response = {"jsonrpc": "2.0", "id": req_id, "result": result}
                else:
                    response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Tool not found"}}
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
