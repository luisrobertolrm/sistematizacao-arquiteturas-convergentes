# MOD — Modelos de IA e seleção por finalidade

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Cadastrar identidades de embedding/inferência e selecionar um modelo ativo de cada finalidade.

## Entrada e identificação

Configuração de IA → Modelos de IA

Raiz do componente/área: `app-ia-configuracao`. Navegação interna sem troca de URL.

- Aba Modelos de IA com aria-current=page.
- #modelo-identificador visível; .workspace com aria-busy=false.

## Pré-condições

- Conexão ativa.
- Para selecionar embedding: todos os índices das atividades ativas prontos e atuais; catálogo vazio satisfaz cobertura.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#ia-busca` | Busca cadastro textual. |
| `#modelo-conexao-id` | Conexão ativa obrigatória; seletor bloqueado ao editar. |
| `#modelo-identificador` | Identificador exato no provedor, obrigatório, até 200 caracteres; readonly ao editar. |
| `#modelo-revisao` | Revisão descritiva opcional, até 200 caracteres; readonly ao editar. |
| `#modelo-finalidade` | embedding (padrão) ou inferencia_texto; disabled ao editar. |
| `#modelo-dimensao` | Somente embedding, inteiro 1–16384; padrão 3 é valor de formulário, não escolha do modelo real; readonly ao editar. |
| `#modelo-ativo` | Selecionar para esta finalidade. Desmarcado por padrão. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### MOD-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MOD](./21-modelos-ia.md).

Resultado:

- Atualiza a página corrente sem limpar o editor.

### MOD-BUSCAR — Buscar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Buscar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MOD](./21-modelos-ia.md).

Resultado:

- Volta à página 1; envia busca somente com dois caracteres ou mais; usar botão, sem Enter vinculado.

### MOD-HISTORICO — Incluir inativados

- Localizador: `{"escopo": ".directory", "papel": "checkbox", "nome": "Incluir inativados", "exato": true}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [MOD](./21-modelos-ia.md).

Resultado:

- Alterna histórico e retorna à página 1; não reativa cadastros.

### MOD-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MOD](./21-modelos-ia.md).

Resultado:

- Recua 50 registros; bloqueado na página 1.

### MOD-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MOD](./21-modelos-ia.md).

Resultado:

- Avança 50 registros; bloqueado quando há menos de 50.

### MOD-LIMPAR — Limpar formulário

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Limpar formulário", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MOD](./21-modelos-ia.md).

Resultado:

- Descarta a edição/rascunho e restaura padrões do formulário.

### MOD-ABA — Modelos de IA

- Localizador: `{"escopo": "nav[aria-label=\"Configuração de IA\"]", "papel": "button", "nome": "Modelos de IA", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MOD](./21-modelos-ia.md).

Resultado:

- Abre aba e limpa busca/histórico/página/formulários.

### MOD-FINALIDADE — Finalidade

- Localizador: `{"css": "#modelo-finalidade"}`.
- Gesto: `selectOption`.
- Condição: Controle visível e habilitado.
- Destino: [MOD](./21-modelos-ia.md).

Resultado:

- Mostra dimensão em embedding, oculta em inferencia_texto; ao enviar texto, dimensão vai nula.

### MOD-ATIVO — Selecionar para esta finalidade

- Localizador: `{"css": "#modelo-ativo"}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [MOD](./21-modelos-ia.md).

Resultado:

- Altera intenção de seleção no rascunho; persiste somente ao Salvar modelo.

### MOD-EDITAR — Editar seleção

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar seleção", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MOD](./21-modelos-ia.md).

Resultado:

- Preenche Seleção do modelo; identidade/revisão/finalidade/dimensão/conexão bloqueadas; permite mudar seleção.

### MOD-SALVAR — Salvar modelo

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar modelo", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MOD](./21-modelos-ia.md).
- Persistência/rede: `POST /api/v1/modelos-ia ou PUT .../{id}`.

Resultado:

- Cria ou atualiza seleção; exibe Modelo salvo.; limpa editor e recarrega.
- Ao selecionar outro modelo da mesma finalidade, o anterior passa a Não selecionado atomicamente.
- Seleção de texto não exige regenerar embeddings.

### MOD-INATIVAR — Inativar modelo

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar modelo", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MOD](./21-modelos-ia.md).
- Persistência/rede: `DELETE /api/v1/modelos-ia/{id}`.
- Diálogo nativo `confirm`: Inativar este cadastro?
- Ao cancelar o diálogo: Sem alteração.

Resultado:

- Aceitar inativa e remove seleção; exibe Cadastro inativado.; preserva referências históricas.

### MOD-PREPARAR — Preparar índices

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Preparar índices", "exato": true}`.
- Gesto: `click`.
- Condição: Modelo não inativado de finalidade embedding.
- Destino: [IND](./22-indices-atividades.md).

Resultado:

- Abre aba Índices de atividades e preseleciona o ID deste modelo.
- Limpa filtros/página de listagem; não ativa modelo nem inicia indexação.

## Cenários de aceitação

### MOD-C01 — Cadastrar os dois tipos

- **Dado:** Conexão ativa e identificadores de teste compatíveis.
- **Quando:** Criar embedding não selecionado com dimensão do provedor; criar inferencia_texto selecionado.
- **Então:** Dois cartões com finalidades corretas; inferência com Dimensão: Não se aplica.

### MOD-C02 — Cobertura incompleta

- **Dado:** Atividade ativa ainda sem índice atual neste modelo.
- **Quando:** Editar seleção; marcar ativo; Salvar modelo.
- **Então:** 409 com alerta de cobertura incompleta; seleção anterior preservada.

### MOD-C03 — Preparar e selecionar

- **Dado:** Cobertura integral foi preparada em IND.
- **Quando:** Editar seleção; marcar ativo; salvar.
- **Então:** Cartão Selecionado; outro modelo da mesma finalidade desmarcado; modelos de outra finalidade independentes.

## Limites e particularidades

- Ativo significa selecionado por finalidade; inativado é um estado distinto.
- Trocar identidade/dimensão/revisão/conexão requer novo cadastro.

## Fontes da implementação

- [frontend/src/app/ia/configuracao.html](../../frontend/src/app/ia/configuracao.html)
- [frontend/src/app/ia/configuracao.ts](../../frontend/src/app/ia/configuracao.ts)
- [backend/business/servico/modelos_ia.py](../../backend/business/servico/modelos_ia.py)
