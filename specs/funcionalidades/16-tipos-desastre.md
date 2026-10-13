# TDE — Tipos de desastre

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Manter a tipologia local de desastres, com código estável.

## Entrada e identificação

Desastres e áreas → Tipos de desastre

Raiz do componente/área: `app-desastres`. Navegação interna sem troca de URL.

- Aba Tipos de desastre com aria-current=page; #desastre-nome visível.
-  .workspace com aria-busy=false.

## Pré-condições

- Sessão administrativa.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#desastre-busca` | Filtro por nome/título/descrição com dois ou mais caracteres; usar o botão Buscar (sem binding de Enter). |
| `#desastre-historico` | Incluir inativados. |
| `#desastre-nome` | Nome obrigatório, 2–200 caracteres. |
| `#desastre-descricao` | Descrição obrigatória, 2–4000 caracteres. |
| `#desastre-codigo` | Código estável obrigatório, único, até 50 caracteres alfanuméricos/_/-, primeiro alfanumérico; readonly na edição. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### TDE-ABA — Tipos de desastre

- Localizador: `{"escopo": "nav[aria-label=\"Desastres e áreas\"]", "papel": "button", "nome": "Tipos de desastre", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TDE](./16-tipos-desastre.md).

Resultado:

- Troca modalidade; fecha áreas, limpa busca/histórico/editor e volta à página 1.

### TDE-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TDE](./16-tipos-desastre.md).

Resultado:

- Recarrega a lista corrente.

### TDE-BUSCAR — Buscar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Buscar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TDE](./16-tipos-desastre.md).

Resultado:

- Aplica busca com pelo menos dois caracteres e volta à página 1.

### TDE-HISTORICO — Incluir inativados

- Localizador: `{"css": "#desastre-historico"}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [TDE](./16-tipos-desastre.md).

Resultado:

- Alterna inclusão de inativos, reconsulta a partir da página 1.

### TDE-EDITAR — Editar tipo

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar tipo", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TDE](./16-tipos-desastre.md).

Resultado:

- Preenche editor e torna código readonly.

### TDE-LIMPAR — Limpar cadastro

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Limpar cadastro", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TDE](./16-tipos-desastre.md).

Resultado:

- Descarta rascunho/ID/referências. Para ocorrência, restaura início local atual, situação em_monitoramento e lista de classificações vazia.

### TDE-SALVAR — Salvar desastre

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar desastre", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TDE](./16-tipos-desastre.md).
- Persistência/rede: `POST /api/v1/tipos-desastre ou PUT .../{id}`.

Resultado:

- Cria/atualiza; exibe Tipo de desastre salvo.
- Limpa editor e reconsulta lista.

### TDE-INATIVAR — Inativar tipo

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar tipo", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TDE](./16-tipos-desastre.md).
- Persistência/rede: `DELETE /api/v1/tipos-desastre/{id}`.
- Diálogo nativo `confirm`: Inativar o tipo {nome}?
- Ao cancelar o diálogo: Sem alteração.

Resultado:

- Aceitar inativa; exibe Tipo inativado.; sai da lista ativa.

### TDE-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TDE](./16-tipos-desastre.md).

Resultado:

- Recua 50 registros; bloqueado na página 1.

### TDE-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TDE](./16-tipos-desastre.md).

Resultado:

- Avança 50 registros; bloqueado com menos de 50.

## Cenários de aceitação

### TDE-C01 — Criar e consultar

- **Dado:** Dados exclusivos e referências preparadas.
- **Quando:** Preencher obrigatórios; Salvar desastre; Buscar.
- **Então:** Mensagem de sucesso e registro persistido; editor limpo.

### TDE-C02 — Código estável

- **Dado:** Tipo já criado.
- **Quando:** Editar tipo; conferir código; criar outro com mesmo código.
- **Então:** Código readonly na edição; duplicidade recusada pela API.

## Limites e particularidades

- Catálogo não é equivalência automática com COBRADE ou classificação oficial.
- Datas usam timezone do navegador no preenchimento e UTC no tráfego.
- Inativação difere de situação encerrado.

## Fontes da implementação

- [frontend/src/app/desastres/cadastros.html](../../frontend/src/app/desastres/cadastros.html)
- [frontend/src/app/desastres/cadastros.ts](../../frontend/src/app/desastres/cadastros.ts)
- [backend/business/servico/desastres.py](../../backend/business/servico/desastres.py)
