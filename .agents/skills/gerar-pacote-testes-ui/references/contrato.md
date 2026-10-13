# Contrato da Suíte Modular de Testes — 3.0.0

Este documento é a referência normativa para a IA produtora gerar suítes de testes funcionais e de interface.

---

## 1. Estrutura de Arquivos

```text
specs/
  mapeamento.json                  # Catálogo mestre
  <funcionalidade>/
    spec.json                      # Especificação funcional
    historico.json                 # Histórico das últimas 5 execuções
```

- Todos os arquivos devem estar em formato UTF-8 e caminhos relativos usando `/`.
- Cada arquivo de especificação representa um módulo ou funcionalidade do sistema.

---

## 2. Catálogo Mestre (`mapeamento.json`)

- `versao_contrato`: `"3.0.0"`.
- `projeto`: Objeto com `nome` da aplicação, `base_url` (opcional/referência), `gerado_por` e `atualizado_em` (ISO 8601).
- `funcionalidades`: Array de módulos contendo:
  - `id`: Identificador estável em formato kebab-case (ex: `cadastro-cliente`).
  - `nome`: Nome amigável da funcionalidade.
  - `arquivo_spec`: Caminho relativo para o arquivo `spec.json`.
  - `arquivo_historico`: Caminho relativo para o arquivo `historico.json`.
  - `objetivo`: Resumo do objetivo funcional de negócio.
  - `total_fluxos`: Quantidade inteira de fluxos principais.
  - `total_excecoes`: Quantidade inteira de cenários de exceção.

---

## 3. Especificação da Funcionalidade (`spec.json`)

Contém as seções:

### 3.1 `funcionalidade`
- `id`: Identificador único.
- `nome`: Título legível.
- `objetivo`: Propósito de negócio coberto pela especificação.
- `rota_inicial`: Rota de entrada da funcionalidade (ex: `/clientes`).

### 3.2 `pre_condicoes`
- Lista de requisitos operacionais para os testes (ex: usuário autenticado, base populada).

### 3.3 `fluxos`
Lista de fluxos principais (caminho feliz). Cada fluxo contém:
- `id`: Identificador do fluxo (ex: `FLUXO-01`).
- `titulo`: Nome do fluxo.
- `descricao`: Detalhes do cenário.
- `passos`: Sequência de ações de UI.
- `resultado_esperado`: Objeto com `descricao` e `verificacoes` (ao menos uma asserção observável).
- `excecoes`: Lista de cenários de desvio ou erro:
  - `id`: Identificador da exceção (ex: `EXC-01-01`).
  - `cenario`: Descrição do desvio ou erro simulado.
  - `passos`: Sequência de passos que disparam o desvio.
  - `resultado_esperado`: Objeto com `descricao` e `verificacoes` esperadas.

---

## 4. Ações e Seletores Suportados

### 4.1 Ações
| Ação (`acao` ou `action`) | Alvo obrigatório | Valor obrigatório | Descrição |
|---|---|---|---|
| `goto` | Não | Sim (rota `/...`) | Navega para uma rota relativa à base URL. |
| `reload` | Não | Não | Recarrega a página atual. |
| `click` | Sim | Não | Clica no elemento. Aceita `dialog: "accept"` ou `"dismiss"`. |
| `fill` | Sim | Sim (texto) | Preenche campo de texto ou input. |
| `select` | Sim | Sim (valor) | Seleciona opção em elemento select. |
| `check` / `uncheck` | Sim | Não | Marca ou desmarca caixa de seleção. |
| `press` | Sim | Sim (tecla) | Pressiona tecla do teclado (ex: `Enter`). |
| `visible` | Sim | Opcional (texto) | Assegura que o elemento está visível (e contém texto, se informado). |
| `hidden` | Sim | Não | Assegura que o elemento está oculto ou ausente do DOM. |
| `text` | Sim | Sim (texto) | Assegura que o elemento possui exatamente o texto esperado. |
| `value` | Sim | Sim (texto) | Assegura que o input possui o valor esperado. |
| `count` | Sim | Sim (inteiro) | Assegura a contagem exata de elementos correspondentes. |
| `url` | Não | Sim (rota `/...`) | Assegura que a URL atual corresponde ao caminho esperado. |

### 4.2 Seletores
O objeto `alvo` (ou `target`) aceita exatamente uma das propriedades:
- `role`: Papel acessível do elemento (ex: `button`, `alert`, `textbox`), opcionalmente com `name` exato.
- `label`: Rótulo de acessibilidade ou tag `<label>` associada.
- `text`: Texto exato visível do elemento.
- `testId`: Atributo `data-testid` estável.
- `css`: Seletor CSS (usar apenas quando não houver seletores acessíveis disponíveis).

---

## 5. Histórico das Últimas 5 Execuções (`historico.json`)

Estrutura inicial mantida na pasta de cada funcionalidade:
```json
{
  "funcionalidade_id": "<id>",
  "max_historico": 5,
  "execucoes": []
}
```

O executor Playwright insere a execução mais recente na primeira posição e descarta registros além de 5, mantendo:
- `run_id`: Identificador da execução.
- `data_hora`: Timestamp ISO 8601.
- `status`: `"OK"` ou `"FALHA"`.
- `duracao_ms`: Tempo total em milissegundos.
- `resumo`: Resumo quantitativo.
- `motivo_falha`: String com o erro ocorrido (ou `null`).
- `falha`: Objeto detalhado com fluxo, exceção e screenshot (ou `null`).
- `detalhes`: Status individual de cada fluxo e exceção.
