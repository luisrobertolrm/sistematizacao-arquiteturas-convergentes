# TIR — Tipos de recurso

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Classificar bens/insumos e padronizar unidade e controle individual/estoque.

## Entrada e identificação

Recursos e ofertas → Tipos de recurso

Raiz do componente/área: `app-recursos`. Navegação interna sem troca de URL.

- Aba Tipos de recurso com aria-current=page; editor visível.
-  .workspace com aria-busy=false.

## Pré-condições

- Sessão administrativa.
- Referências ativas: unidade.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#recurso-busca` | Busca textual com dois caracteres ou mais; Enter também pesquisa. |
| `#recurso-historico` | Incluir cadastros inativados. |
| `#recurso-descricao` | Descrição opcional, até 4000 caracteres. |
| `#recurso-nome` | Obrigatório, 2–200 caracteres. |
| `#recurso-categoria` | veiculo, equipamento (padrão), material, insumo. |
| `#recurso-modo` | individual (padrão), estoque. |
| `#recurso-ref-id` | Unidade de medida ativa obrigatória; busca #recurso-ref-busca. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### TIR-ABA — Tipos de recurso

- Localizador: `{"escopo": "nav[aria-label=\"Recursos e ofertas\"]", "papel": "button", "nome": "Tipos de recurso", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TIR](./12-tipos-recurso.md).

Resultado:

- Abre modalidade; fecha recursos da oferta; limpa busca/histórico/editor e volta à página 1.

### TIR-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TIR](./12-tipos-recurso.md).

Resultado:

- Reconsulta a lista na página/filtros atuais.

### TIR-BUSCAR — Buscar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Buscar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TIR](./12-tipos-recurso.md).

Resultado:

- Volta à página 1; aplica busca com dois caracteres ou mais, senão lista sem filtro.

### TIR-HISTORICO — Incluir cadastros inativados

- Localizador: `{"css": "#recurso-historico"}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [TIR](./12-tipos-recurso.md).

Resultado:

- Alterna inativos e retorna à página 1; cartões inativos não oferecem Editar/Inativar.

### TIR-EDITAR — Editar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TIR](./12-tipos-recurso.md).

Resultado:

- Preenche Editar cadastro; a referência principal de recurso/oferta fica bloqueada.

### TIR-SALVAR — Salvar cadastro

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar cadastro", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TIR](./12-tipos-recurso.md).
- Persistência/rede: `POST /api/v1/tipos-recurso ou PUT /api/v1/tipos-recurso/{id}`.

Resultado:

- Cria ou altera; exibe Cadastro salvo.
- Limpa editor, restaura padrões e reconsulta a lista.

### TIR-LIMPAR — Limpar

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Limpar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TIR](./12-tipos-recurso.md).
- Persistência/rede: `Sem gravação.`.

Resultado:

- Descarta o rascunho de criação e restaura os padrões locais.

### TIR-CANCELAR — Cancelar

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Cancelar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TIR](./12-tipos-recurso.md).

Resultado:

- Descarta edição e retorna ao formulário novo; sem gravação.

### TIR-INATIVAR — Inativar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TIR](./12-tipos-recurso.md).
- Persistência/rede: `DELETE /api/v1/tipos-recurso/{id}`.
- Diálogo nativo `confirm`: Inativar {nome}? O histórico será preservado.
- Ao cancelar o diálogo: Sem alteração.

Resultado:

- Aceitar inativa, exibe Cadastro inativado., limpa editor e atualiza a consulta.

### TIR-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TIR](./12-tipos-recurso.md).

Resultado:

- Recua 50 registros; bloqueado na página 1.

### TIR-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TIR](./12-tipos-recurso.md).

Resultado:

- Avança 50 registros; bloqueado quando há menos de 50.

## Cenários de aceitação

### TIR-C01 — Criar e editar

- **Dado:** Referências e nomes exclusivos preparados.
- **Quando:** Preencher obrigatórios; Salvar cadastro; buscar registro; Editar; alterar descrição; salvar.
- **Então:** Cadastro salvo.; mesmo ID na edição; referências principais bloqueadas quando aplicável.

### TIR-C02 — Referência ausente

- **Dado:** Campos de texto válidos, referência/responsável ausente.
- **Quando:** Tentar Salvar cadastro.
- **Então:** Informe de seleção exigida em role=alert; nenhum POST/PUT.

### TIR-C03 — Preservar unidade de tipo utilizado

- **Dado:** Tipo já referenciado por recurso.
- **Quando:** Tentar salvar outra unidade/modo de controle.
- **Então:** API recusa e exibe role=alert; registro persistido não é alterado.

## Limites e particularidades

- Inativação preserva referências e histórico.
- Unidade e modo podem permanecer editáveis na tela; a API protege tipos já utilizados.
- Recursos e ofertas consultam seletores compartilhados; ver contrato-harness.md.

## Fontes da implementação

- [frontend/src/app/recursos/cadastros.html](../../frontend/src/app/recursos/cadastros.html)
- [frontend/src/app/recursos/cadastros.ts](../../frontend/src/app/recursos/cadastros.ts)
- [backend/business/servico/recursos.py](../../backend/business/servico/recursos.py)
