# RCO — Recomendações por IA e decisão administrativa

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Gerar sugestões com candidatos reais, revisar justificativas/limites e registrar decisão final sem reservar ou entregar recursos.

## Entrada e identificação

Demandas e recomendações → No cartão do pedido: Recomendações e decisões

Raiz do componente/área: `app-recomendacoes`. Navegação interna sem troca de URL.

- h2 Recomendações — {demanda}.
- .workspace com aria-busy=false; Histórico de análises visível.

## Pré-condições

- Demanda existente; ativa/aberta para gerar análise.
- Para geração: modelos selecionados de embedding e inferência, cobertura integral, provedores configurados.
- Candidatos elegíveis dependem de cadastros/ofertas validados e município, conforme contrato D009.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#decisao-justificativa` | Somente recomendação gerada; obrigatório, 2–4000 caracteres. Selecionar outra análise limpa o campo. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### RCO-GERAR — Gerar recomendação por IA

- Localizador: `{"escopo": ":scope", "papel": "button", "nome": "Gerar recomendação por IA", "exato": true}`.
- Gesto: `click`.
- Condição: Demanda ativa e aberta; sem operação em curso.
- Destino: [RCO](./25-recomendacoes-decisoes.md).
- Persistência/rede: `POST /api/v1/demandas/{demanda_id}/recomendacoes`.

Resultado:

- Executa análise e persiste nova recomendação; não sobrescreve decisões anteriores.
- Seleciona automaticamente a nova análise, mostra Sugestão gerada para análise administrativa. e reconsulta histórico na página 1.
- Apresenta justificativa, itens, quantidades sugeridas, nomes/papéis e pendências.

### RCO-ATUALIZAR — Atualizar histórico

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar histórico", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [RCO](./25-recomendacoes-decisoes.md).

Resultado:

- Atualiza somente a lista na página atual; não gera análise nem recarrega detalhe selecionado.

### RCO-VER — Ver recomendação

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Ver recomendação", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [RCO](./25-recomendacoes-decisoes.md).
- Persistência/rede: `Nenhuma chamada de detalhe no fluxo atual; usa item do histórico.`.

Resultado:

- Mostra no editor a análise do cartão escolhido, usando os dados já carregados na lista.
- Limpa justificativa de decisão e erro; apresenta controles de decisão somente se situação gerada.

### RCO-RASTRO — Rastreabilidade

- Localizador: `{"escopo": ".editor", "css": "summary", "texto": "Rastreabilidade"}`.
- Gesto: `toggle`.
- Condição: Controle visível e habilitado.
- Destino: [RCO](./25-recomendacoes-decisoes.md).

Resultado:

- Expande/recolhe detalhes dos IDs de modelos e hash de contexto.

### RCO-APROVAR — Aprovar sugestão

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Aprovar sugestão", "exato": true}`.
- Gesto: `click`.
- Condição: Análise selecionada gerada, justificativa válida, sem ocupação.
- Destino: [RCO](./25-recomendacoes-decisoes.md).
- Persistência/rede: `POST /api/v1/recomendacoes/{id}/decisao, situacao=aprovada`.
- Diálogo nativo `confirm`: Registrar esta decisão administrativa?
- Ao cancelar o diálogo: Não envia decisão; mantém análise gerada e justificativa preenchida.

Resultado:

- Ao aceitar, revalida contexto e registra situação aprovada, justificativa, autor do JWT e data do servidor.
- Exibe Decisão registrada.; remove formulário/botões de decisão e mostra Decisão registrada com dados.
- Atualiza histórico; não modifica pedido, estoque, agenda ou reserva.

### RCO-REJEITAR — Rejeitar sugestão

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Rejeitar sugestão", "exato": true}`.
- Gesto: `click`.
- Condição: Análise selecionada gerada e justificativa válida.
- Destino: [RCO](./25-recomendacoes-decisoes.md).
- Persistência/rede: `POST /api/v1/recomendacoes/{id}/decisao, situacao=rejeitada`.
- Diálogo nativo `confirm`: Registrar esta decisão administrativa?
- Ao cancelar o diálogo: Sem alteração; preserva justificativa.

Resultado:

- Ao aceitar registra situação rejeitada, justificativa, autor e data; exibe Decisão registrada.
- Decisão é final e única; remove controles de decisão e atualiza histórico.
- Rejeição pode registrar descarte mesmo com contexto desatualizado.

### RCO-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [RCO](./25-recomendacoes-decisoes.md).

Resultado:

- Recua 50 análises; não muda o detalhe selecionado.

### RCO-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [RCO](./25-recomendacoes-decisoes.md).

Resultado:

- Avança 50 análises quando a página atual tem 50; detalhe permanece.

### RCO-VOLTAR — Voltar às demandas

- Localizador: `{"escopo": ":scope > .section-head", "papel": "button", "nome": "Voltar às demandas", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [DEM](./24-demandas-itens.md).

Resultado:

- Fecha app-recomendacoes e recarrega demandas com busca/histórico/página anteriores.

## Cenários de aceitação

### RCO-C01 — Gerar e aprovar

- **Dado:** Pedido aberto com candidatos elegíveis e provedor de teste controlado.
- **Quando:** Gerar; revisar itens/nomes/pendências; preencher justificativa; Aprovar sugestão e aceitar confirm.
- **Então:** Nova análise aprovada no histórico; autor/data/justificativa visíveis; pedido/estoque sem alteração.

### RCO-C02 — Nova análise e rejeição

- **Dado:** Há recomendação aprovada anterior; pedido continua aberto.
- **Quando:** Gerar nova recomendação; preencher justificativa; Rejeitar sugestão e aceitar.
- **Então:** Histórico contém aprovada e rejeitada distintas; nenhuma decisão anterior sobrescrita.

### RCO-C03 — Justificativa e cancelamento do diálogo

- **Dado:** Análise gerada selecionada.
- **Quando:** Campo vazio/um caractere; depois justificativa válida; Aprovar e dispensar confirm.
- **Então:** Botões desabilitados sem justificativa válida; dispensar diálogo não grava e mantém gerada.

### RCO-C04 — Contexto desatualizado

- **Dado:** Análise gerada; em outra sessão alterar informação relevante do pedido/candidato.
- **Quando:** Tentar aprovar com justificativa.
- **Então:** 409 e role=alert; análise não é aprovada; gerar nova análise ou rejeitar a antiga.

### RCO-C05 — Histórico sem geração

- **Dado:** Pedido cancelado/inativado ou análise já decidida.
- **Quando:** Abrir recomendações e selecionar histórico.
- **Então:** Gerar desabilitado para pedido fechado/inativo; análise decidida mostra dados finais sem Aprovar/Rejeitar.

### RCO-C06 — Falha de IA

- **Dado:** Configuração ausente ou provedor com falha.
- **Quando:** Gerar recomendação.
- **Então:** Role=alert sanitizado; não aparece sugestão parcial persistida nem mensagem nova de sucesso.

## Limites e particularidades

- Serviços podem ter quantidade sugerida zero e candidatos válidos: capacidade por período não foi definida.
- Busca semântica contextual não amplia automaticamente ofertas elegíveis para atividades diferentes.
- Sem candidatos é um resultado possível com justificativas/pendências; não inventar nomes ou quantidade no teste.
- Qualidade de LLM real é avaliação separada de correção de interface; não exigir texto literal da IA.
- Algumas mensagens antigas podem continuar visíveis; sincronizar pelo resultado da operação atual e estado de dados.

## Fontes da implementação

- [frontend/src/app/demandas/recomendacoes.html](../../frontend/src/app/demandas/recomendacoes.html)
- [frontend/src/app/demandas/recomendacoes.ts](../../frontend/src/app/demandas/recomendacoes.ts)
- [backend/business/servico/recomendacoes.py](../../backend/business/servico/recomendacoes.py)
- [docs/ia-demandas-recomendacoes.md](../../docs/ia-demandas-recomendacoes.md)
