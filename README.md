# Gemini CLI Voice Extension

Esta extensão adiciona a ferramenta `speech` ao Gemini CLI, permitindo que o modelo se comunique através de áudio sintetizado utilizando o motor Piper (TTS).

## Como Funciona

A extensão opera como um servidor **MCP (Model Context Protocol)** nativo via `stdio`. Ela não possui dependências externas de Python, o que a torna leve e fácil de instalar em diferentes ambientes.

## Requisitos do Sistema

Para que a sintetização funcione, sua máquina deve ter instalado:
1.  **Piper**: O motor de texto para fala. [Download aqui](https://github.com/rhasspy/piper).
2.  **Aplay**: Utilitário de reprodução de áudio (padrão em sistemas Linux/ALSA).
3.  **Modelo de Voz (.onnx)**: Um arquivo de voz compatível com o Piper (ex: `miro_pt-BR.onnx`).

## Instalação

Você pode instalar esta extensão diretamente do repositório:
```bash
gemini extensions install https://github.com/seu-usuario/gemini-cli-voice
```

## Configuração de Caminhos (Portabilidade)

A extensão tenta localizar o executável `piper` e o modelo `.onnx` automaticamente em pastas comuns e no `PATH` do sistema. Caso seus arquivos estejam em locais customizados, você pode configurar os caminhos através de variáveis de ambiente ou via comando de configuração da extensão:

```bash
# Configurando via variáveis de ambiente
export VOICE_PIPER_PATH="/caminho/para/piper"
export VOICE_MODEL_PATH="/caminho/para/modelo.onnx"
```

Ou diretamente no Gemini CLI (se suportado pela versão):
```bash
gemini extensions config gemini-cli-voice VOICE_PIPER_PATH /caminho/para/piper
```

## Ferramentas Disponíveis

### `speech(text: str)`
Converte o texto fornecido em áudio falado e o reproduz imediatamente.
-   **Parâmetros**:
    -   `text` (string): O texto a ser falado pelo modelo.
