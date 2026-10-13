# TRM — Termos e sinônimos da atividade

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Ampliar a busca textual e a entrada canônica do embedding sem duplicar a descrição da atividade.

## Entrada e identificação

Atividades e unidades → Atividades → No cartão da atividade: Termos e sinônimos

Raiz do componente/área: `app-termos`. Navegação interna sem troca de URL.

- h2 Termos e sinônimos · {nome}.
- .workspace com aria-busy=false.

## Pré-condições

- Atividade existente; ativa para criar/editar.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#atividade-termo` | Obrigatório, 2–200 caracteres. Servidor normaliza maiúsculas/espaços para unicidade na atividade. |
| `#termos-historico` | Incluir termos inativados; forçado e bloqueado quando a atividade estiver inativada. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### TRM-SALVAR — Salvar termo

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar termo", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TRM](./11-termos-sinonimos.md).
- Persistência/rede: `POST /api/v1/atividades/{atividade_id}/termos ou PUT .../{termo_id}`.

Resultado:

- Cria ou altera termo e exibe Termo salvo.
- Limpa editor; atualiza lista, data e hash da atividade.

### TRM-EDITAR — Editar termo

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar termo", "exato": true}`.
- Gesto: `click`.
- Condição: Atividade e termo ativos.
- Destino: [TRM](./11-termos-sinonimos.md).

Resultado:

- Preenche #atividade-termo; exibe Editar termo e Cancelar edição.

### TRM-CANCELAR — Cancelar edição

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Cancelar edição", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TRM](./11-termos-sinonimos.md).

Resultado:

- Limpa campo/ID de edição e volta a Novo termo; sem gravar.

### TRM-INATIVAR — Inativar termo

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar termo", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TRM](./11-termos-sinonimos.md).
- Persistência/rede: `DELETE /api/v1/atividades/{atividade_id}/termos/{termo_id}`.
- Diálogo nativo `confirm`: Inativar o termo “{termo}”? O registro será preservado.
- Ao cancelar o diálogo: Nenhuma alteração.

Resultado:

- Aceitar inativa, exibe Termo inativado. e atualiza lista/hash.
- Termo ainda ativo de atividade inativada pode ser inativado; não é permitido editar/criar nesse contexto.

### TRM-HISTORICO — Incluir termos inativados

- Localizador: `{"css": "#termos-historico"}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [TRM](./11-termos-sinonimos.md).

Resultado:

- Alterna inclusão de termos inativados e retorna à página 1.

### TRM-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TRM](./11-termos-sinonimos.md).

Resultado:

- Recua 50 termos; bloqueado na página 1.

### TRM-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TRM](./11-termos-sinonimos.md).

Resultado:

- Avança 50 termos; bloqueado com menos de 50 na página.

### TRM-RASTRO — Rastreabilidade do conteúdo

- Localizador: `{"escopo": ".editor", "papel": null, "css": "summary", "texto": "Rastreabilidade do conteúdo"}`.
- Gesto: `toggle`.
- Condição: Controle visível e habilitado.
- Destino: [TRM](./11-termos-sinonimos.md).

Resultado:

- Expande/recolhe o details; mostra hash atual calculado pelo servidor.

### TRM-VOLTAR — Voltar às atividades

- Localizador: `{"escopo": ":scope > .section-head", "papel": "button", "nome": "Voltar às atividades", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ATV](./10-atividades.md).

Resultado:

- Fecha app-termos; volta à listagem de Atividades com os filtros/página anteriores.
- Recarrega as atividades para refletir alterações.

## Cenários de aceitação

### TRM-C01 — Termo participa da busca

- **Dado:** Atividade ativa e termo único.
- **Quando:** Salvar termo; Voltar às atividades; Buscar pelo termo.
- **Então:** Termo salvo.; atividade encontrada por busca textual.

### TRM-C02 — Duplicidade normalizada

- **Dado:** Termo já ativo na mesma atividade.
- **Quando:** Salvar variante com caixa/espaços extras.
- **Então:** 409 e role=alert; somente um termo ativo normalizado.

### TRM-C03 — Hash e histórico

- **Dado:** Hash corrente visível no details.
- **Quando:** Editar termo ou inativá-lo; incluir histórico.
- **Então:** Hash muda quando conteúdo canônico muda; termo inativado permanece identificado.

### TRM-C04 — Atividade inativada

- **Dado:** Abrir Termos e sinônimos de atividade histórica.
- **Quando:** Consultar tela e termos.
- **Então:** Aviso de consulta; histórico marcado/desabilitado; formulário de termo ausente e sem Editar termo.

## Limites e particularidades

- Salvar um termo não gera embeddings automaticamente; preparar novamente em Índices de atividades.
- Não há botão Atualizar próprio nesta tela; alterações, paginação e histórico recarregam dados.

## Fontes da implementação

- [frontend/src/app/capacidades/termos.html](../../frontend/src/app/capacidades/termos.html)
- [frontend/src/app/capacidades/termos.ts](../../frontend/src/app/capacidades/termos.ts)
