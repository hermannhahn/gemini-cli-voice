# Project Overview: gemini-cli-voice

Este diretório contém a extensão `gemini-cli-voice`, projetada para integrar capacidades de text-to-speech (TTS) nativamente ao Gemini CLI.

## Propósito

A extensão permite que o modelo responda ao usuário via áudio falado, utilizando o motor Piper. O modelo deve usar a ferramenta `speech` sempre que for solicitado a falar, ler algo ou responder por voz.

## Arquitetura e Implementação

A extensão foi implementada como um **servidor MCP (Model Context Protocol)** autônomo. 

- **gemini-extension.json**: Define o manifesto da extensão e o servidor MCP do tipo `stdio`.
- **tool_code.py**: Contém o servidor MCP em Python que gerencia as requisições de ferramentas e lida com a sintetização via Piper.
- **Protocolo**: Utiliza JSON-RPC 2.0 via entrada e saída padrão (stdin/stdout).
- **Sem Dependências**: O código foi escrito em Python puro para garantir portabilidade imediata após o download, sem necessidade de pacotes externos.

## Uso pelo Modelo (Perspectiva de IA)

O modelo deve invocar a ferramenta `speech` nas seguintes situações:
- O usuário solicita explicitamente uma resposta por voz ("fale", "responda por voz", "leia isso").
- A intenção do usuário implica um feedback falado.
- Para o usuário "Hermann", deve-se usar a fonética "Rérmann" nas strings enviadas para a ferramenta para garantir uma pronúncia correta pelo motor de voz.

### Ferramenta: `speech(text: str)`
- **Descrição**: Converte o texto fornecido em áudio utilizando o motor Piper e o reproduz.
- **Linguagem**: O texto deve estar no mesmo idioma da solicitação do usuário (geralmente Português).
- **Tratamento de Erros**: O modelo deve informar ao usuário se a ferramenta falhar (ex: executável Piper não encontrado) e sugerir a configuração correta do ambiente.

## Configuração de Portabilidade

A extensão utiliza descoberta dinâmica de caminhos para o executável `piper` e o modelo de voz (`.onnx`). Desenvolvedores podem sobrescrever os caminhos padrões utilizando as variáveis de ambiente:
- `VOICE_PIPER_PATH`
- `VOICE_MODEL_PATH`
