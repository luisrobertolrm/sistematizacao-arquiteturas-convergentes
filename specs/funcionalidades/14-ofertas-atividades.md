# OFE — Ofertas de atividades

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Registrar a atividade que pessoa ou instituição oferece no município.

## Entrada e identificação

Recursos e ofertas → Ofertas de atividades

Raiz do componente/área: `app-recursos`. Navegação interna sem troca de URL.

- Aba Ofertas de atividades com aria-current=page; editor visível.
-  .workspace com aria-busy=false.

## Pré-condições

- Sessão administrativa.
- Referências ativas: atividade e responsável; unidade se declarar capacidade.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#recurso-busca` | Busca textual com dois caracteres ou mais; Enter também pesquisa. |
| `#recurso-historico` | Incluir cadastros inativados. |
| `#recurso-descricao` | Descrição complementar opcional, até 4000 caracteres. |
| `#recurso-ref-id` | Atividade ativa obrigatória; select bloqueado na edição. |
| `#recurso-dono-tipo` | instituicoes (padrão) ou pessoas. Trocar limpa o responsável selecionado. |
| `#responsavel-ref-id` | Responsável ativo obrigatório; busca #responsavel-ref-busca. |
| `#recurso-municipio` | Sete dígitos obrigatórios. Recurso: localização; oferta: município de atendimento. |
| `#oferta-capacidade` | Opcional; se informada, positiva e até quatro casas. Exige unidade ativa da atividade. |
| `#oferta-validacao` | pendente (padrão), validada, rejeitada. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### OFE-ABA — Ofertas de atividades

- Localizador: `{"escopo": "nav[aria-label=\"Recursos e ofertas\"]", "papel": "button", "nome": "Ofertas de atividades", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFE](./14-ofertas-atividades.md).

Resultado:

- Abre modalidade; fecha recursos da oferta; limpa busca/histórico/editor e volta à página 1.

### OFE-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFE](./14-ofertas-atividades.md).

Resultado:

- Reconsulta a lista na página/filtros atuais.

### OFE-BUSCAR — Buscar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Buscar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFE](./14-ofertas-atividades.md).

Resultado:

- Volta à página 1; aplica busca com dois caracteres ou mais, senão lista sem filtro.

### OFE-HISTORICO — Incluir cadastros inativados

- Localizador: `{"css": "#recurso-historico"}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [OFE](./14-ofertas-atividades.md).

Resultado:

- Alterna inativos e retorna à página 1; cartões inativos não oferecem Editar/Inativar.

### OFE-EDITAR — Editar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFE](./14-ofertas-atividades.md).

Resultado:

- Preenche Editar cadastro; a referência principal de recurso/oferta fica bloqueada.

### OFE-SALVAR — Salvar cadastro

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar cadastro", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFE](./14-ofertas-atividades.md).
- Persistência/rede: `POST /api/v1/ofertas-atividade ou PUT /api/v1/ofertas-atividade/{id}`.

Resultado:

- Cria ou altera; exibe Cadastro salvo.
- Limpa editor, restaura padrões e reconsulta a lista.

### OFE-LIMPAR — Limpar

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Limpar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFE](./14-ofertas-atividades.md).
- Persistência/rede: `Sem gravação.`.

Resultado:

- Descarta o rascunho de criação e restaura os padrões locais.

### OFE-CANCELAR — Cancelar

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Cancelar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFE](./14-ofertas-atividades.md).

Resultado:

- Descarta edição e retorna ao formulário novo; sem gravação.

### OFE-INATIVAR — Inativar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFE](./14-ofertas-atividades.md).
- Persistência/rede: `DELETE /api/v1/ofertas-atividade/{id}`.
- Diálogo nativo `confirm`: Inativar {nome}? O histórico será preservado.
- Ao cancelar o diálogo: Sem alteração.

Resultado:

- Aceitar inativa, exibe Cadastro inativado., limpa editor e atualiza a consulta.

### OFE-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFE](./14-ofertas-atividades.md).

Resultado:

- Recua 50 registros; bloqueado na página 1.

### OFE-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFE](./14-ofertas-atividades.md).

Resultado:

- Avança 50 registros; bloqueado quando há menos de 50.

### OFE-DONO — Responsável *

- Localizador: `{"css": "#recurso-dono-tipo"}`.
- Gesto: `selectOption`.
- Condição: Controle visível e habilitado.
- Destino: [OFE](./14-ofertas-atividades.md).

Resultado:

- Troca o tipo de responsável, limpa sua seleção/nome e consulta opções da modalidade escolhida.

### OFE-RECURSOS — Recursos da oferta

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Recursos da oferta", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OFR](./15-recursos-oferta.md).

Resultado:

- Abre app-oferta-recursos para a oferta e responsável selecionados.
- Oferta inativada abre em modo histórico com formulário bloqueado.

## Cenários de aceitação

### OFE-C01 — Criar e editar

- **Dado:** Referências e nomes exclusivos preparados.
- **Quando:** Preencher obrigatórios; Salvar cadastro; buscar registro; Editar; alterar descrição; salvar.
- **Então:** Cadastro salvo.; mesmo ID na edição; referências principais bloqueadas quando aplicável.

### OFE-C02 — Referência ausente

- **Dado:** Campos de texto válidos, referência/responsável ausente.
- **Quando:** Tentar Salvar cadastro.
- **Então:** Informe de seleção exigida em role=alert; nenhum POST/PUT.

### OFE-C03 — Capacidade sem unidade

- **Dado:** Atividade sem unidade selecionada.
- **Quando:** Tentar salvar capacidade declarada numérica.
- **Então:** API recusa e exibe role=alert; registro persistido não é alterado.

## Limites e particularidades

- Inativação preserva referências e histórico.
- Duplicidade ativa de atividade/responsável/município é recusada. Validação registra data administrativa da oferta.
- Recursos e ofertas consultam seletores compartilhados; ver contrato-harness.md.

## Fontes da implementação

- [frontend/src/app/recursos/cadastros.html](../../frontend/src/app/recursos/cadastros.html)
- [frontend/src/app/recursos/cadastros.ts](../../frontend/src/app/recursos/cadastros.ts)
- [backend/business/servico/recursos.py](../../backend/business/servico/recursos.py)
