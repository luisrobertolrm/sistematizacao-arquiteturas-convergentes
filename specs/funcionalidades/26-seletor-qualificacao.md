# SEL-QUAL — Seletor de instituição, profissão ou curso

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Selecionar uma referência ativa sem sair do formulário, com busca/paginação independentes da lista principal.

## Entrada e identificação

Formulário que usa app-referencia → Identificar a instância pelo select #referencia-id

Raiz do componente/área: `app-referencia`. Navegação interna sem troca de URL.

- Select de referência habilitado quando não bloqueado; opções carregadas.

## Pré-condições

- Tela de origem montada e rota/tipo configurados.
- Usar prefixo da instância descrito na spec da funcionalidade; vários seletores coexistem.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#referencia-busca` | Busca de referências; vazio/um caractere consulta sem filtro. Digitar sozinho não pesquisa. |
| `#referencia-id` | Select nativo com UUID como value; selecionar por label único ou ID obtido nas fixtures. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### SEL-QUAL-BUSCAR — Buscar

- Localizador: `{"escopo": ":scope", "papel": "button", "nome": "Buscar", "exato": true}`.
- Gesto: `click`.
- Condição: Componente montado, sem consulta em andamento e controle habilitado.
- Destino: contexto de origem.

Resultado:

- Reconsulta opções a partir da página 1 com busca de dois caracteres ou mais; não altera a referência selecionada nem salva formulário.

### SEL-QUAL-ANTERIOR — Anterior

- Localizador: `{"escopo": ":scope", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Componente montado, sem consulta em andamento e controle habilitado.
- Destino: contexto de origem.

Resultado:

- Recua 50 opções; bloqueado na página 1. Paginação é independente da listagem de cadastros.

### SEL-QUAL-PROXIMA — Próxima

- Localizador: `{"escopo": ":scope", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Componente montado, sem consulta em andamento e controle habilitado.
- Destino: contexto de origem.

Resultado:

- Avança 50 opções se a página tem 50; conserva o ID selecionado, mesmo fora da página.

### SEL-QUAL-SELECIONAR — Selecionar referência

- Localizador: `{"css": "#referencia-id"}`.
- Gesto: `selectOption`.
- Condição: Componente montado, sem consulta em andamento e controle habilitado.
- Destino: contexto de origem.

Resultado:

- Atualiza a seleção local do formulário; não faz POST/PUT. Opção vazia limpa seleção.

## Cenários de aceitação

### SEL-QUAL-C01 — Busca e escolha sem navegação

- **Dado:** Referência ativa conhecida fora da lista inicial.
- **Quando:** Preencher busca; clicar Buscar; escolher opção do cenário.
- **Então:** Select contém o ID esperado; URL e formulário de origem permanecem; salvar é ação independente.

### SEL-QUAL-C02 — Paginação de opções

- **Dado:** Ambiente com pelo menos 51 referências ativas do tipo.
- **Quando:** Avançar opções; voltar; escolher uma e mudar a busca.
- **Então:** Página do seletor muda; página da lista principal não muda; seleção é mantida mesmo fora das opções visíveis.

## Limites e particularidades

- Não clicar no primeiro Buscar/Anterior/Próxima da página sem escopo de componente.
- Referência já selecionada fora da página/filtro recebe option de preservação; texto pode ser Referência selecionada/Cadastro selecionado quando nome não disponível.
- Erro do seletor aparece no role=alert da própria instância; aguardar também o fim dessa consulta.
- O bloqueio de um fieldset pai também se aplica aos controles descendentes.

## Fontes da implementação

- [frontend/src/app/qualificacoes/referencia.ts](../../frontend/src/app/qualificacoes/referencia.ts)
