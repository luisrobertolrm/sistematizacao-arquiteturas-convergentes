---
name: gerar-pacote-testes-ui
description: Gerar suíte de testes de interface modular em JSON para validação com Playwright. Usar quando a IA que desenvolveu uma aplicação web precisar entregar especificações estruturadas de funcionalidades, fluxos principais, resultados esperados e exceções, sem compartilhar o código-fonte ou banco de dados.
---

# Gerar Suíte Modular de Testes de Interface (Padrão 3.0.0)

Produzir uma suíte de testes modular e autocontida no padrão `3.0.0`, pronta para execução direta pelo sistema de teste via Playwright.

A IA produtora (que desenvolveu a aplicação) analisa seu próprio código e especificações de tela, e gera uma pasta de testes organizada por **Funcionalidade**, com um catálogo mestre no nível raiz e arquivos de histórico rotativo.

---

## Estrutura de Entrega

A suíte gerada deve seguir esta organização de pastas e arquivos:

```text
specs/
  mapeamento.json                  # Catálogo mestre com índice de todas as funcionalidades
  <nome-da-funcionalidade>/         # Uma pasta para cada funcionalidade
    spec.json                      # Objetivo, Fluxos Principais, Resultados e Exceções
    historico.json                 # Arquivo inicializado das 5 últimas execuções (FIFO)
```

---

## Procedimento de Geração

1. **Mapeamento Geral (`mapeamento.json`)**:
   - Criar o catálogo mestre na raiz da suíte listando cada funcionalidade com seu `id`, `nome`, `arquivo_spec`, `arquivo_historico`, `objetivo` e contagem de fluxos/exceções.

2. **Para cada Funcionalidade (`<funcionalidade>/spec.json`)**:
   - Declarar o **Objetivo** da funcionalidade em linguagem clara de negócio.
   - Declarar as **Pré-condições** de ambiente (ex: usuário autenticado, base populada).
   - Definir os **Fluxos Principais (Caminho Feliz)**:
     - `passos`: Sequência de ações na tela (`click`, `fill`, `select`, `press`, `goto`).
     - `resultado_esperado`: Lista de `verificacoes` observáveis (`visible`, `hidden`, `text`, `value`, `count`, `url`).
   - Definir os **Fluxos de Exceções**:
     - Para cada cenário de erro, desvio ou validação (ex: campos obrigatórios vazios, e-mail duplicado, cancelamento):
     - Declarar o `cenario`, os `passos` que disparam o desvio e o `resultado_esperado` com suas respectivas `verificacoes` (ex: mensagens de validação, permanência na rota).

3. **Histórico Inicial (`<funcionalidade>/historico.json`)**:
   - Criar dentro da pasta da funcionalidade o arquivo inicial de histórico:
     ```json
     {
       "funcionalidade_id": "<id-da-funcionalidade>",
       "max_historico": 5,
       "execucoes": []
     }
     ```
   - O executor externo atualizará este arquivo automaticamente a cada rodada de teste, retendo rigorosamente as últimas 5 execuções com status `OK`/`FALHA`, tempo em ms e motivo detalhado de eventuais erros.

4. **Regras de Seletores e Dados**:
   - **Seletores Acessíveis**: Preferir `role` com `name` (ex: `{ "role": "button", "name": "Salvar" }`), `label` (ex: `{ "label": "E-mail" }`), `testId` ou `text`. Evitar seletores CSS complexos e frágeis.
   - **Isolamento de Dados**: Utilizar a variável `{{RUN_ID}}` em textos ou campos que exigem unicidade (ex: `"Cliente {{RUN_ID}}"`). O executor substituirá pelo identificador da execução.
   - **Independência dos Testes**: Cada fluxo ou exceção deve ser auto-contido ou preparar seus próprios dados necessários caso dependa de registros criados na tela.

5. **Validação da Suíte**:
   - Executar o validador incluído na skill para garantir que a estrutura e as asserções estão em conformidade:
     ```powershell
     node <pasta-da-skill>/scripts/validar-pacote.mjs <caminho>/mapeamento.json
     ```

---

## Fronteiras e Boas Práticas

- **Sem código executável ou dependências**: Gerar exclusivamente especificações declarativas em JSON. Não embutir scripts bash, comandos de banco ou funções de código.
- **Asserções Obrigatórias**: Todo fluxo principal e toda exceção **devem** ter ao menos uma verificação observável de tela (`visible`, `hidden`, `text`, `value`, `count`, `url`). Clicar sem verificar resultado não constitui teste aprovado.
- **Entrega**: Entregar a pasta completa da suíte ou um arquivo ZIP contendo `mapeamento.json` na raiz.
