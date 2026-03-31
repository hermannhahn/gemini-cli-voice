# Plano de Melhoria para Galeria de Extensões

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Garantir que a extensão seja indexada e aprovada na galeria oficial do Gemini CLI.

**Architecture:** Adição de metadados obrigatórios (licença, tópicos do GitHub) e execução do workflow de deploy para sincronizar com a branch `main`.

**Tech Stack:** Git, Node.js (npm scripts).

---

### Task 1: Adicionar arquivo de Licença

**Files:**
- Create: `LICENSE`

- [ ] **Step 1: Criar arquivo LICENSE com texto ISC**

```text
ISC License

Copyright (c) 2026, Hermann Hahn

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
```

- [ ] **Step 2: Verificar se o arquivo foi criado**

Run: `ls -l LICENSE`
Expected: Arquivo LICENSE presente.

- [ ] **Step 3: Commit**

```bash
git add LICENSE
git commit -m "chore: add ISC license file for extension gallery"
```

### Task 2: Atualizar manifest e preparar deploy

**Files:**
- Modify: `gemini-extension.json`
- Modify: `package.json`

- [ ] **Step 1: Ajustar descrição no gemini-extension.json**

```json
{
  "name": "gemini-cli-voice",
  "version": "1.2.22",
  "description": "High-quality local text-to-speech (TTS) for Gemini CLI using Piper.",
  ...
}
```

- [ ] **Step 2: Garantir que a versão no package.json está correta**
(Já está em 1.2.22, mas vamos garantir que as mudanças pendentes sejam commitadas).

- [ ] **Step 3: Commit das alterações de configuração**

```bash
git add gemini-extension.json package.json
git commit -m "chore: update extension metadata for better gallery display"
```

### Task 3: Executar Workflow de Deploy

- [ ] **Step 1: Executar o comando de deploy oficial**

Run: `npm run deploy`
Description: Este comando faz o merge de `development` para `main`, cria a tag e o release no GitHub.

- [ ] **Step 2: Verificar status final**

Run: `git status`
Expected: De volta na branch `development`.
