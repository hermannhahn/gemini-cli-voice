# Gemini CLI Voice Extension

Esta extensão adiciona a ferramenta `speech` ao Gemini CLI, permitindo que o modelo se comunique através de áudio sintetizado utilizando o motor Piper (TTS).

## Arquitetura e Estrutura Profissional

O projeto segue padrões modernos de desenvolvimento híbrido (Node.js e Python):

- **Modularização**: Lógica separada em pacotes Python em `src/gemini_voice/`.
- **Tipagem Estática**: Uso extensivo de *type hints* e validação com `mypy`.
- **Linting & Formatação**: Padronizado com `ruff` para máxima velocidade e consistência.
- **Testes**: Suíte de testes automatizada com `pytest`.
- **Gerenciamento de Dependências**: Ambiente virtual Python isolado gerenciado via scripts `npm`.

## Requisitos do Sistema

1.  **Python 3.10+**
2.  **Node.js & npm**
3.  **Aplay** (Linux) ou **PowerShell** (Windows) para reprodução de áudio.

## Instalação e Configuração

Para configurar o ambiente de desenvolvimento:
```bash
npm install
npm run setup:py
```

Isso criará um ambiente virtual `.venv` e instalará todas as ferramentas de desenvolvimento.

## Instalação no Gemini CLI

```bash
gemini extensions install https://github.com/hermannhahn/gemini-cli-voice.git
```

## Desenvolvimento

- **Linting e Tipos**: `npm run lint`
- **Testes**: `npm run test`
- **Formatação Automática**: `npm run format:py`

## Como Adicionar Mais Vozes

Baixe vozes compatíveis do Piper:  
👉 [Hugging Face - Piper Voices](https://huggingface.co/rhasspy/piper-voices/tree/main)

Salve os arquivos `.onnx` e `.json` na pasta `models/` ou configure o caminho via:
```bash
gemini extensions config gemini-cli-voice "Voice Model Path" /caminho/completo/sua-voz.onnx
```

Ou via variáveis de ambiente:
```bash
export VOICE_PIPER_PATH="/caminho/para/piper"
export VOICE_MODEL_PATH="/caminho/para/sua-voz.onnx"
## Comandos Disponíveis

- `/voice:enable`: Ativa o modo de voz automático. O modelo passará a usar a voz em todas as respostas.
- `/voice:disable`: Desativa o modo de voz automático. O modelo voltará a responder apenas por texto.
- `/voice:model`: Altera o modelo de voz (.onnx).
- `/voice:pitch`: Altera a velocidade/tom da voz (multiplicador).

## Ferramentas Disponíveis

### `speech(text: str)`
Converte o texto fornecido em áudio falado e o reproduz imediatamente. Se o modo de voz estiver ativo (`VOICE_MODE: ENABLED`), o modelo chamará esta ferramenta automaticamente.

### `voice_toggle(enabled: bool)`
Ativa ou desativa o modo de resposta automática por voz.

### `model(model: str)`
Altera o modelo de voz em tempo real.

### `pitch(pitch: float)`
Altera a velocidade/tom da voz (multiplicador).

## Como Adicionar Mais Vozes

