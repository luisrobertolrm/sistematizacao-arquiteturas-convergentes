---
name: executar-pacote-testes-ui
description: Executar a suite modular de testes de interface Playwright com comando unico, realizando validacao de specs, checagem da aplicacao e exibindo historico e diagnosticos de falha.
---

# Executar Suite Modular de Testes de Interface (Playwright)

Executa de ponta a ponta a suite modular de testes de interface grafica com Playwright gerada no padrao `3.0.0`, de forma totalmente automatizada.

O comando orquestra:
1. **Validacao de Contrato**: Valida o `mapeamento.json` e todos os arquivos `spec.json` antes de iniciar navegadores.
2. **Health-Check da Aplicacao**: Verifica se o frontend/servidor esta online na URL alvo (com espera inteligente).
3. **Execucao Playwright**: Dispara os testes em lote (ou de uma funcionalidade isolada).
4. **Atualizacao de Historico**: Grava automaticamente o resultado no arquivo `historico.json` de cada funcionalidade (retendo as ultimas 5 execucoes em formato FIFO).
5. **Diagnostico de Falhas**: Exibe resumo visual e detalha o motivo de eventuais erros para a IA ou desenvolvedor.

---

## Como Executar

### 1. No Terminal (PowerShell ou Bash)

Na raiz do projeto testado:

```powershell
# Executar a suite completa (todas as funcionalidades)
.\testar-ui.ps1

# Executar com navegador Chromium visivel (modo headed)
.\testar-ui.ps1 -Headed

# Executar apenas uma funcionalidade isolada (ex: pessoas)
.\testar-ui.ps1 -Feature pessoas -Headed

# Executar apontando para uma URL ou porta diferente
.\testar-ui.ps1 -Url http://localhost:3000
```

Se o script `testar-ui.ps1` nao estiver na raiz da aplicacao, execute diretamente via Node:

```powershell
node C:\Git\testes\scripts\testar-ui.mjs --suite specs/mapeamento.json --url http://localhost:4200
```

---

## Parametros Suportados

| Parametro | Descricao | Padrao |
|---|---|---|
| `--url <url>` | URL base onde a aplicacao frontend esta respondendo | `http://localhost:4200` |
| `--suite <path>` | Caminho do catalogo `mapeamento.json` | Detectado automaticamente em `./specs` |
| `--feature <nome\|path>` | Nome da pasta da feature ou caminho direto para seu `spec.json` | Executa a suite inteira |
| `--headed` | Abre a janela visivel do navegador para acompanhar o teste | `false` (headless) |
| `--timeout <seg>` | Tempo maximo de espera pela subida da aplicacao | `20` segundos |
| `--no-wait` | Pula a checagem de conexao com o servidor | `false` |
| `--storage-state <file>` | Arquivo de sessao/cookies pré-autenticado | `null` |
| `--output <dir>` | Diretorio customizado para salvar relatorios e screenshots | `artefatos/relatorios/<runId>` |

---

## Papel da IA ao Usar Esta Skill

Quando o usuario pedir no chat para executar os testes (ex: `/executar-pacote-testes-ui` ou *"Execute os testes de interface"*):

1. **Disparar o comando**:
   Execute `node C:\Git\testes\scripts\testar-ui.mjs` (ou `.\testar-ui.ps1`) com os argumentos solicitados pelo usuario.
2. **Interpretar os resultados**:
   - Analisar o resumo emitido no terminal.
   - Para qualquer funcionalidade que tenha retornado `[FALHA]`, inspecionar o arquivo `specs/<funcionalidade>/historico.json` correspondente.
3. **Apresentar relatorio executivo claro no chat**:
   - Quantas funcionalidades foram testadas, quantas passaram e quantas falharam.
   - Para cada falha: explicar com precisao qual passo falhou (ex: botão não visível, timeout de rede, asserção de texto divergente).
   - Informar o caminho das evidencias e screenshots gravados em `artefatos/relatorios/`.
   - Propor a correcao necessária (seja um ajuste no frontend ou um ajuste na spec).
