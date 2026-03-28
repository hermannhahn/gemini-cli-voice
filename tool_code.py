import os
import sys

# Adiciona a pasta src ao path para permitir imports do pacote gemini_voice
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from gemini_voice.mcp import main

if __name__ == "__main__":
    main()
