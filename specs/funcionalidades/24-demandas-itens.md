# DEM — Demandas e itens de necessidade

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Registrar as necessidades de uma área afetada com solicitante, prioridade, janela e quantidades, mantendo itens como um agregado.

## Entrada e identificação

Demandas e recomendações

Raiz do componente/área: `app-demandas`. Navegação interna sem troca de URL.

- h2 Demandas e Nova demanda/Editar demanda visíveis.
-  .workspace com aria-busy=false.

## Pré-condições

- Área ativa de ocorrência ativa.
- Pessoa solicitante ativa.
- Atividade/tipo de recurso e unidade ativos, compatíveis entre si.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#demanda-busca` | Busca textual do pedido; usar Buscar, não há binding de Enter. |
| `#demanda-area-id` | Área afetada obrigatória; busca #demanda-area-busca. Bloqueada na edição. |
| `#demanda-pessoa-id` | Pessoa solicitante obrigatória; busca #demanda-pessoa-busca. |
| `#demanda-titulo` | Obrigatório, 2–200 caracteres. |
| `#demanda-descricao` | Obrigatório, 2–4000 caracteres. |
| `#demanda-prioridade` | baixa, normal (padrão), alta, urgente; independente da gravidade da área. |
| `#demanda-inicio` | Obrigatório, datetime-local; convertido para UTC no envio. |
| `#demanda-prazo` | Obrigatório, datetime-local; igual ou posterior ao início. |
| `#demanda-situacao` | Apenas na edição: aberta ou cancelada. Criação envia aberta. |
| `#item-tipo-{i}` | Índice i começa em zero; atividade (padrão) ou recurso. Bloqueado para item persistido. |
| `#item-necessidade-{i}-id` | Atividade ou tipo de recurso obrigatório; bloqueado para item persistido. |
| `#item-unidade-{i}-id` | Unidade obrigatória; exatamente a cadastrada na necessidade. Bloqueada para item persistido. |
| `#item-quantidade-{i}` | Positiva, até 14 dígitos inteiros e quatro casas com ponto; padrão 1. API valida formato/positividade. |
| `#item-observacoes-{i}` | Opcional, até 4000 caracteres. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### DEM-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [DEM](./24-demandas-itens.md).

Resultado:

- Atualiza página/lista preservando filtro e editor.

### DEM-BUSCAR — Buscar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Buscar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [DEM](./24-demandas-itens.md).

Resultado:

- Retorna à página 1 e filtra com pelo menos dois caracteres; busca menor não é enviada.

### DEM-HISTORICO — Incluir inativados e itens removidos

- Localizador: `{"escopo": ".directory", "papel": "checkbox", "nome": "Incluir inativados e itens removidos", "exato": true}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [DEM](./24-demandas-itens.md).

Resultado:

- Alterna consulta histórica; mostra demandas inativadas e itens removidos com (removido); retorna à página 1.

### DEM-EDITAR — Editar demanda

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar demanda", "exato": true}`.
- Gesto: `click`.
- Condição: Demanda ativa e aberta.
- Destino: [DEM](./24-demandas-itens.md).

Resultado:

- Preenche cabeçalho e somente itens vigentes; preserva IDs existentes.
- Área e identidade/unidade de itens existentes ficam bloqueadas; aparece select Situação.

### DEM-LIMPAR — Limpar formulário

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Limpar formulário", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [DEM](./24-demandas-itens.md).

Resultado:

- Descarta edição; limpa cabeçalho; volta a Nova demanda com prioridade normal, situação aberta e um item novo de quantidade 1.

### DEM-TIPO — Necessidade

- Localizador: `{"css": "#item-tipo-{i}"}`.
- Gesto: `selectOption`.
- Condição: Item novo sem ID persistido.
- Destino: [DEM](./24-demandas-itens.md).

Resultado:

- Troca modalidade do item novo; limpa necessidade e unidade; carrega referências da modalidade escolhida.

### DEM-ADICIONAR — Adicionar item

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Adicionar item", "exato": true}`.
- Gesto: `click`.
- Condição: Menos de 100 itens no formulário.
- Destino: [DEM](./24-demandas-itens.md).

Resultado:

- Acrescenta item de rascunho com tipo atividade, referências vazias e quantidade 1; até 100 itens.

### DEM-REMOVER — Remover item

- Localizador: `{"escopo": "$item", "papel": "button", "nome": "Remover item", "exato": true}`.
- Gesto: `click`.
- Condição: Mais de um item no formulário.
- Destino: [DEM](./24-demandas-itens.md).
- Persistência/rede: `Sem requisição até Salvar demanda.`.

Resultado:

- Remove a linha do rascunho e reindexa IDs dos campos seguintes; mínimo um item.
- Não grava imediatamente. Ao salvar, itens persistidos removidos são inativados; novos removidos nunca são criados.

### DEM-SALVAR — Salvar demanda

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar demanda", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [DEM](./24-demandas-itens.md).
- Persistência/rede: `POST /api/v1/demandas ou PUT /api/v1/demandas/{id}`.

Resultado:

- Valida janela no frontend e envia cabeçalho/itens juntos.
- Em sucesso exibe Demanda salva.; limpa editor e reconsulta.
- POST cria aberta; PUT mantém aberta ou cancela. Cancelada deixa de oferecer Editar demanda.

### DEM-CANCELAR — Cancelar pedido

- Localizador: `{"css": "#demanda-situacao"}`.
- Gesto: `selectOption value=cancelada`.
- Condição: Edição de demanda aberta.
- Destino: [DEM](./24-demandas-itens.md).

Resultado:

- Seleciona cancelada no rascunho; somente Salvar demanda efetiva cancelamento. Não há confirmação nativa específica.

### DEM-INATIVAR — Inativar demanda

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar demanda", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [DEM](./24-demandas-itens.md).
- Persistência/rede: `DELETE /api/v1/demandas/{id}`.
- Diálogo nativo `confirm`: Inativar demanda preservando histórico?
- Ao cancelar o diálogo: Sem alteração.

Resultado:

- Aceitar inativa, exibe Demanda inativada., limpa editor e reconsulta preservando histórico.

### DEM-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [DEM](./24-demandas-itens.md).

Resultado:

- Recua 50 demandas; bloqueado na primeira página.

### DEM-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [DEM](./24-demandas-itens.md).

Resultado:

- Avança 50 demandas se a página atual tem 50.

### DEM-RECOMENDACOES — Recomendações e decisões

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Recomendações e decisões", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [RCO](./25-recomendacoes-decisoes.md).

Resultado:

- Abre app-recomendacoes para o pedido escolhido, com título Recomendações — {titulo}.
- Disponível também para consulta histórica de demanda cancelada/inativada; gerar nova análise fica bloqueado nesses casos.

## Cenários de aceitação

### DEM-C01 — Pedido com atividade e recurso

- **Dado:** Área, solicitante, atividade com unidade e tipo de recurso preparados.
- **Quando:** Preencher cabeçalho; configurar item de atividade; adicionar item de recurso com unidade compatível; Salvar demanda.
- **Então:** Demanda salva.; cartão lista dois itens e quantidades/unidades corretas; IDs persistidos.

### DEM-C02 — Quantidade ou unidade incompatível

- **Dado:** Cabeçalho válido e necessidade ativa.
- **Quando:** Informar quantidade 0/negativa/formato inválido, ou escolher unidade diferente da necessidade; salvar.
- **Então:** API recusa com role=alert; agregado não é gravado parcialmente.

### DEM-C03 — Remoção preserva histórico

- **Dado:** Pedido com pelo menos dois itens persistidos.
- **Quando:** Editar; Remover item em um deles; salvar; marcar histórico.
- **Então:** Pedido mantém item vigente e exibe removido no histórico; mínimo um item respeitado.

### DEM-C04 — Janela inválida

- **Dado:** Formulário preenchido.
- **Quando:** Informar prazo anterior ao início; Salvar demanda.
- **Então:** Alerta Informe uma janela de atendimento válida.; não envia gravação.

### DEM-C05 — Cancelar pedido

- **Dado:** Demanda aberta criada no cenário.
- **Quando:** Editar; selecionar Cancelar pedido; salvar; abrir Recomendações e decisões.
- **Então:** Situação cancelada; sem Editar demanda; geração de análise desabilitada; histórico consultável.

## Limites e particularidades

- Não existe botão Cancelar independente para a demanda: Limpar formulário descarta rascunho; Cancelar pedido é opção de situação que precisa ser salva.
- Itens existentes mudam quantidade/observações; trocar necessidade/unidade requer remover e adicionar outro item.
- Não há transições em_atendimento/concluida, atendimento, entrega ou reserva na etapa atual.
- Seletores por item devem ser identificados pelo fieldset/legend Item N; IDs são baseados na posição, não no UUID do banco.

## Fontes da implementação

- [frontend/src/app/demandas/cadastros.html](../../frontend/src/app/demandas/cadastros.html)
- [frontend/src/app/demandas/cadastros.ts](../../frontend/src/app/demandas/cadastros.ts)
- [backend/business/servico/demandas.py](../../backend/business/servico/demandas.py)
- [backend/business/view_models/operacao.py](../../backend/business/view_models/operacao.py)
