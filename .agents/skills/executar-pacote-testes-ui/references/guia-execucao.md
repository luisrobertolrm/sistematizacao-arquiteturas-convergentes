# Guia de Referencia - Execucao de Testes UI

## 1. Visao Geral

Esta skill conecta as especificacoes no padrao `3.0.0` (armazenadas em `specs/`) ao executor Playwright de forma 100% automatizada.

## 2. Requisitos de Ambiente

- **Node.js**: v20 ou superior.
- **Componente de Browser**: Chromium do Playwright registrado na maquina (caso necessario, rode `implantar.ps1`).
- **Aplicacao Frontend**: Rodando em `http://localhost:4200` (ou URL configurada).

## 3. Resolucao de Falhas Comuns

### 3.1 Falha de Health-Check (Timeout ao conectar)
- **Causa**: O frontend da aplicacao nao foi iniciado antes de disparar o comando.
- **Solucao**: Inicie o servidor frontend no diretorio da aplicacao (ex: `npm start` ou `ng serve`).

### 3.2 Falha de Validacao de Schema
- **Causa**: Algum arquivo `spec.json` possui sintaxe invalida, campo obrigatorio faltando ou assercoes mal formatadas.
- **Solucao**: Corrija o arquivo apontado pelo validador antes de rodar os testes.

### 3.3 Falha de Seletor ou Acao no Playwright
- **Causa**: O elemento na tela nao apareceu dentro do tempo limite, o seletor mudou ou o elemento estava desabilitado.
- **Solucao**:
  1. Consulte o screenshot e detalhes do erro no arquivo de log ou em `artefatos/relatorios/`.
  2. Verifique se a acao depende de pré-condicoes (ex: autenticacao ou banco com dados cadastrados).
  3. Atualize o seletor no `spec.json` ou corrija o componente Angular correspondente.
