# REC — Recursos

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Registrar bens e estoques sob responsabilidade de pessoa ou instituição.

## Entrada e identificação

Recursos e ofertas → Recursos

Raiz do componente/área: `app-recursos`. Navegação interna sem troca de URL.

- Aba Recursos com aria-current=page; editor visível.
-  .workspace com aria-busy=false.

## Pré-condições

- Sessão administrativa.
- Referências ativas: tipo de recurso e responsável.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#recurso-busca` | Busca textual com dois caracteres ou mais; Enter também pesquisa. |
| `#recurso-historico` | Incluir cadastros inativados. |
| `#recurso-descricao` | Descrição opcional, até 4000 caracteres. |
| `#recurso-nome` | Obrigatório, 2–200 caracteres. |
| `#recurso-ref-id` | Tipo de recurso ativo obrigatório; select bloqueado na edição. |
| `#recurso-dono-tipo` | instituicoes (padrão) ou pessoas. Trocar limpa o responsável selecionado. |
| `#responsavel-ref-id` | Responsável ativo obrigatório; busca #responsavel-ref-busca. |
| `#recurso-municipio` | Sete dígitos obrigatórios. Recurso: localização; oferta: município de atendimento. |
| `#recurso-identificacao` | Identificação opcional do bem/lote, até 200 caracteres. |
| `#recurso-quantidade` | Obrigatório; 1 para individual; estoque aceita zero ou mais. Até 14 dígitos inteiros e quatro casas, com ponto. |
| `#recurso-estado` | operacional (padrão), em_manutencao, indisponivel. |
| `#recurso-latitude` | Opcional, par com longitude; limites geográficos validados pela API. |
| `#recurso-longitude` | Opcional, par com latitude. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### REC-ABA — Recursos

- Localizador: `{"escopo": "nav[aria-label=\"Recursos e ofertas\"]", "papel": "button", "nome": "Recursos", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [REC](./13-recursos.md).

Resultado:

- Abre modalidade; fecha recursos da oferta; limpa busca/histórico/editor e volta à página 1.

### REC-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [REC](./13-recursos.md).

Resultado:

- Reconsulta a lista na página/filtros atuais.

### REC-BUSCAR — Buscar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Buscar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [REC](./13-recursos.md).

Resultado:

- Volta à página 1; aplica busca com dois caracteres ou mais, senão lista sem filtro.

### REC-HISTORICO — Incluir cadastros inativados

- Localizador: `{"css": "#recurso-historico"}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [REC](./13-recursos.md).

Resultado:

- Alterna inativos e retorna à página 1; cartões inativos não oferecem Editar/Inativar.

### REC-EDITAR — Editar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [REC](./13-recursos.md).

Resultado:

- Preenche Editar cadastro; a referência principal de recurso/oferta fica bloqueada.

### REC-SALVAR — Salvar cadastro

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar cadastro", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [REC](./13-recursos.md).
- Persistência/rede: `POST /api/v1/recursos ou PUT /api/v1/recursos/{id}`.

Resultado:

- Cria ou altera; exibe Cadastro salvo.
- Limpa editor, restaura padrões e reconsulta a lista.

### REC-LIMPAR — Limpar

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Limpar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [REC](./13-recursos.md).
- Persistência/rede: `Sem gravação.`.

Resultado:

- Descarta o rascunho de criação e restaura os padrões locais.

### REC-CANCELAR — Cancelar

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Cancelar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [REC](./13-recursos.md).

Resultado:

- Descarta edição e retorna ao formulário novo; sem gravação.

### REC-INATIVAR — Inativar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [REC](./13-recursos.md).
- Persistência/rede: `DELETE /api/v1/recursos/{id}`.
- Diálogo nativo `confirm`: Inativar {nome}? O histórico será preservado.
- Ao cancelar o diálogo: Sem alteração.

Resultado:

- Aceitar inativa, exibe Cadastro inativado., limpa editor e atualiza a consulta.

### REC-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [REC](./13-recursos.md).

Resultado:

- Recua 50 registros; bloqueado na página 1.

### REC-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [REC](./13-recursos.md).

Resultado:

- Avança 50 registros; bloqueado quando há menos de 50.

### REC-DONO — Responsável *

- Localizador: `{"css": "#recurso-dono-tipo"}`.
- Gesto: `selectOption`.
- Condição: Controle visível e habilitado.
- Destino: [REC](./13-recursos.md).

Resultado:

- Troca o tipo de responsável, limpa sua seleção/nome e consulta opções da modalidade escolhida.

## Cenários de aceitação

### REC-C01 — Criar e editar

- **Dado:** Referências e nomes exclusivos preparados.
- **Quando:** Preencher obrigatórios; Salvar cadastro; buscar registro; Editar; alterar descrição; salvar.
- **Então:** Cadastro salvo.; mesmo ID na edição; referências principais bloqueadas quando aplicável.

### REC-C02 — Referência ausente

- **Dado:** Campos de texto válidos, referência/responsável ausente.
- **Quando:** Tentar Salvar cadastro.
- **Então:** Informe de seleção exigida em role=alert; nenhum POST/PUT.

### REC-C03 — Quantidade de bem individual

- **Dado:** Tipo individual selecionado.
- **Quando:** Tentar salvar quantidade 2.
- **Então:** API recusa e exibe role=alert; registro persistido não é alterado.

## Limites e particularidades

- Inativação preserva referências e histórico.
- Quantidade cadastrada não é reserva nem saldo operacional de missão.
- Recursos e ofertas consultam seletores compartilhados; ver contrato-harness.md.

## Fontes da implementação

- [frontend/src/app/recursos/cadastros.html](../../frontend/src/app/recursos/cadastros.html)
- [frontend/src/app/recursos/cadastros.ts](../../frontend/src/app/recursos/cadastros.ts)
- [backend/business/servico/recursos.py](../../backend/business/servico/recursos.py)
