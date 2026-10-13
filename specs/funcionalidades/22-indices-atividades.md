# IND — Índices semânticos das atividades

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Preparar embeddings por modelo sem duplicar os textos do catálogo.

## Entrada e identificação

Configuração de IA → Índices de atividades → Opcional: entrar por Modelos de IA → Preparar índices

Raiz do componente/área: `app-ia-configuracao`. Navegação interna sem troca de URL.

- Aba Índices de atividades com aria-current=page; h2 Preparar indexação.
- .workspace com aria-busy=false.

## Pré-condições

- Modelo de embedding ativo cadastralmente, mesmo não selecionado.
- Atividades ativas; endpoint permitido/configuração/chave compatíveis e provedor acessível.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#indice-modelo-id` | Modelo para gerar embeddings; selecionar pela identidade/ID do cenário. Lista atual oferece também modelos de texto; API rejeita finalidade incorreta. |
| `#indice-atividade-id` | Atividade ativa a adicionar ao lote; busca #indice-atividade-busca. |
| `.lote-indices` | IDs de atividades selecionadas, até 50 distintas; contém Remover do lote. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### IND-ABA — Índices de atividades

- Localizador: `{"escopo": "nav[aria-label=\"Configuração de IA\"]", "papel": "button", "nome": "Índices de atividades", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [IND](./22-indices-atividades.md).

Resultado:

- Abre índices, volta página 1 e reconsulta. Não limpa lote nem modelo já escolhido.

### IND-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [IND](./22-indices-atividades.md).

Resultado:

- Atualiza índices da página; a listagem não é filtrada pelo modelo selecionado no editor.

### IND-ADICIONAR — Adicionar ao lote

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Adicionar ao lote", "exato": true}`.
- Gesto: `click`.
- Condição: Atividade selecionada, lote menor que 50, sem ocupação.
- Destino: [IND](./22-indices-atividades.md).

Resultado:

- Adiciona ID da atividade selecionada se ainda não está no lote.
- Máximo 50; duplicata não acrescenta entrada nem gera mensagem; seleção da atividade continua preenchida.

### IND-REMOVER — Remover do lote

- Localizador: `{"escopo": ".lote-indices li", "papel": "button", "nome": "Remover do lote", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [IND](./22-indices-atividades.md).

Resultado:

- Remove somente o ID da linha escolhida do rascunho; não apaga índice persistido.

### IND-INDEXAR — Indexar lote

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Indexar lote", "exato": true}`.
- Gesto: `click`.
- Condição: Modelo escolhido e lote não vazio.
- Destino: [IND](./22-indices-atividades.md).
- Persistência/rede: `POST /api/v1/indices-atividade/indexar`.

Resultado:

- Envia modelo e IDs; gera/publica o lote completo atomicamente.
- Exibe Lote indexado. Selecione o modelo após completar a cobertura.; atualiza a listagem.
- Lote e modelo selecionado permanecem preenchidos; indexar não ativa modelo.

### IND-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [IND](./22-indices-atividades.md).

Resultado:

- Recua 50 índices; bloqueado na primeira página.

### IND-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [IND](./22-indices-atividades.md).

Resultado:

- Avança 50 índices se a página atual tem 50.

## Cenários de aceitação

### IND-C01 — Gerar lote

- **Dado:** Modelo de embedding de teste e atividades ativas.
- **Quando:** Adicionar atividades distintas; Indexar lote.
- **Então:** Índices com Atualizado · pronta e ID do modelo correto. Não confundir índices de modelos diferentes.

### IND-C02 — Finalidade incorreta

- **Dado:** Modelo de texto escolhido no seletor.
- **Quando:** Adicionar atividade e indexar.
- **Então:** API retorna 409; role=alert; lote não é publicado.

### IND-C03 — Conteúdo invalidado

- **Dado:** Atividade com índice atual.
- **Quando:** Editar descrição ou termo em ATV/TRM; voltar e Atualizar índices.
- **Então:** Índice correspondente fica Pendente ou desatualizado · pendente; regenerar atualiza.

### IND-C04 — Falha do provedor

- **Dado:** Provedor do cenário indisponível/incompatível.
- **Quando:** Indexar lote.
- **Então:** Erro sanitizado; sem publicação parcial; operação deixa estado ocupado e permite tentar novamente.

## Limites e particularidades

- A busca semântica no mesmo painel tem especificação própria BUS.
- Seletor do modelo para indexar não seleciona o modelo usado pela busca.
- Não há botões de apagar índice, limpar lote inteiro, fila/background ou progresso persistido.
- Indexação exige dimensão exata do provedor; campo de dimensão não ajusta automaticamente o resultado.

## Fontes da implementação

- [frontend/src/app/ia/configuracao.html](../../frontend/src/app/ia/configuracao.html)
- [frontend/src/app/ia/configuracao.ts](../../frontend/src/app/ia/configuracao.ts)
- [frontend/src/app/core/operacao-api.ts](../../frontend/src/app/core/operacao-api.ts)
- [backend/business/servico/indices.py](../../backend/business/servico/indices.py)
