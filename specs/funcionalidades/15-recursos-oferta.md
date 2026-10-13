# OFR — Recursos vinculados à oferta

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Relacionar bens/insumos ao serviço com quantidade de uso prevista, sem reservar estoque.

## Entrada e identificação

Recursos e ofertas → Ofertas de atividades → No cartão da oferta: Recursos da oferta

Raiz do componente/área: `app-oferta-recursos`. Navegação interna sem troca de URL.

- h2 Recursos de {atividade} — {responsável}.
- .workspace com aria-busy=false.

## Pré-condições

- Oferta existente.
- Oferta ativa para criar/editar.
- Recurso ativo com tipo/unidade válidos.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#oferta-recurso-ref-id` | Recurso obrigatório; bloqueado na edição. Busca #oferta-recurso-ref-busca. |
| `#oferta-recurso-quantidade` | Padrão 1; positivo, até quatro casas; individual exige 1. Unidade vem do tipo. |
| `#oferta-recurso-historico` | Inclui vínculos inativados; forçado/bloqueado em oferta inativada. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### OFR-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFR](./15-recursos-oferta.md).

Resultado:

- Atualiza os vínculos com a página/histórico atuais.

### OFR-HISTORICO — Incluir vínculos inativados

- Localizador: `{"css": "#oferta-recurso-historico"}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [OFR](./15-recursos-oferta.md).

Resultado:

- Alterna histórico e volta à página 1.

### OFR-EDITAR — Editar vínculo

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar vínculo", "exato": true}`.
- Gesto: `click`.
- Condição: Oferta e vínculo ativos.
- Destino: [OFR](./15-recursos-oferta.md).

Resultado:

- Preenche quantidade e recurso; select do recurso fica bloqueado.

### OFR-SALVAR — Salvar vínculo

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar vínculo", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFR](./15-recursos-oferta.md).
- Persistência/rede: `POST /api/v1/ofertas-atividade/{oferta_id}/recursos ou PUT .../{vinculo_id}`.

Resultado:

- Cria/altera vínculo, exibe Vínculo salvo.
- Limpa editor (quantidade 1) e reconsulta a lista.

### OFR-LIMPAR — Limpar vínculo

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Limpar vínculo", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFR](./15-recursos-oferta.md).

Resultado:

- Limpa ID/recurso/quantidade do editor, sem persistir; volta à quantidade 1.

### OFR-INATIVAR — Inativar vínculo

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar vínculo", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFR](./15-recursos-oferta.md).
- Persistência/rede: `DELETE /api/v1/ofertas-atividade/{oferta_id}/recursos/{id}`.
- Diálogo nativo `confirm`: Inativar o vínculo com {recurso_nome}?
- Ao cancelar o diálogo: Sem alteração.

Resultado:

- Aceitar exibe Vínculo inativado.; limpa editor e recarrega.
- Permitido para vínculo ativo mesmo que a oferta já esteja inativada.

### OFR-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFR](./15-recursos-oferta.md).

Resultado:

- Recua 50 vínculos; bloqueado na primeira página.

### OFR-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFR](./15-recursos-oferta.md).

Resultado:

- Avança 50 vínculos; bloqueado se menos de 50.

### OFR-VOLTAR — Voltar às ofertas

- Localizador: `{"escopo": ":scope > .section-head", "papel": "button", "nome": "Voltar às ofertas", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFE](./14-ofertas-atividades.md).

Resultado:

- Fecha app-oferta-recursos e recarrega a lista de Ofertas de atividades com filtros/página anteriores.

## Cenários de aceitação

### OFR-C01 — Vincular e editar

- **Dado:** Oferta e recurso ativos do cenário.
- **Quando:** Selecionar recurso; Salvar vínculo; Editar vínculo; alterar quantidade válida; salvar.
- **Então:** Vínculo salvo.; ID preservado; recurso bloqueado na edição.

### OFR-C02 — Duplicidade e quantidade

- **Dado:** Recurso já vinculado à oferta.
- **Quando:** Tentar outro vínculo ativo do mesmo recurso; tentar quantidade 0 ou 2 para individual.
- **Então:** API recusa; lista não ganha duplicata nem quantidade inválida.

### OFR-C03 — Oferta histórica

- **Dado:** Oferta do cenário inativada.
- **Quando:** Abrir Recursos da oferta via histórico.
- **Então:** Aviso de oferta inativada; fieldset bloqueado; consulta/paginação disponíveis; vínculo ativo ainda pode ser inativado.

## Limites e particularidades

- Sem reserva automática nem autorização para usar recursos de outro responsável.
- Vínculo não representa disponibilidade do recurso.

## Fontes da implementação

- [frontend/src/app/recursos/vinculos.html](../../frontend/src/app/recursos/vinculos.html)
- [frontend/src/app/recursos/vinculos.ts](../../frontend/src/app/recursos/vinculos.ts)
