# OCO — Ocorrências e classificações

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Registrar a ocorrência e seus tipos associados, com uma classificação principal.

## Entrada e identificação

Desastres e áreas → Ocorrências

Raiz do componente/área: `app-desastres`. Navegação interna sem troca de URL.

- Aba Ocorrências com aria-current=page; #desastre-nome visível.
-  .workspace com aria-busy=false.

## Pré-condições

- Sessão administrativa.
- Instituição coordenadora e pelo menos um tipo ativos.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#desastre-busca` | Filtro por nome/título/descrição com dois ou mais caracteres; usar o botão Buscar (sem binding de Enter). |
| `#desastre-historico` | Incluir inativados. |
| `#desastre-nome` | Título obrigatório, 2–200 caracteres. |
| `#desastre-descricao` | Descrição obrigatória, 2–4000 caracteres. |
| `#coordenadora-ref-id` | Instituição coordenadora ativa obrigatória; busca #coordenadora-ref-busca. |
| `#desastre-inicio` | Obrigatório, datetime-local; a tela converte para ISO UTC no envio. |
| `#desastre-situacao` | em_monitoramento (padrão), em_resposta, em_recuperacao, encerrado. |
| `#desastre-encerramento` | Obrigatório somente para encerrado, não anterior ao início; vazio nas outras situações. |
| `#classificacao-ref-id` | Tipo de desastre ativo a adicionar ao rascunho; busca #classificacao-ref-busca. |
| `input[name="classificacao-principal"]` | Um radio por classificação. Identificar pelo texto do contêiner; deve haver exatamente uma principal. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### OCO-ABA — Ocorrências

- Localizador: `{"escopo": "nav[aria-label=\"Desastres e áreas\"]", "papel": "button", "nome": "Ocorrências", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).

Resultado:

- Troca modalidade; fecha áreas, limpa busca/histórico/editor e volta à página 1.

### OCO-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).

Resultado:

- Recarrega a lista corrente.

### OCO-BUSCAR — Buscar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Buscar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).

Resultado:

- Aplica busca com pelo menos dois caracteres e volta à página 1.

### OCO-HISTORICO — Incluir inativados

- Localizador: `{"css": "#desastre-historico"}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).

Resultado:

- Alterna inclusão de inativos, reconsulta a partir da página 1.

### OCO-EDITAR — Editar ocorrência

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar ocorrência", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).

Resultado:

- Preenche cabeçalho, coordenadora e somente classificações vigentes; datas em horário local.

### OCO-LIMPAR — Limpar cadastro

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Limpar cadastro", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).

Resultado:

- Descarta rascunho/ID/referências. Para ocorrência, restaura início local atual, situação em_monitoramento e lista de classificações vazia.

### OCO-SALVAR — Salvar desastre

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar desastre", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).
- Persistência/rede: `POST /api/v1/desastres ou PUT .../{id}`.

Resultado:

- Cria/atualiza; exibe Ocorrência salva.
- Limpa editor e reconsulta lista.

### OCO-INATIVAR — Inativar ocorrência

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar ocorrência", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).
- Persistência/rede: `DELETE /api/v1/desastres/{id}`.
- Diálogo nativo `confirm`: Inativar {titulo}? Áreas e classificações serão preservadas.
- Ao cancelar o diálogo: Sem alteração.

Resultado:

- Aceitar inativa ocorrência; exibe Ocorrência inativada.; preserva áreas e classificações.

### OCO-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).

Resultado:

- Recua 50 registros; bloqueado na página 1.

### OCO-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).

Resultado:

- Avança 50 registros; bloqueado com menos de 50.

### OCO-ADICIONAR — Adicionar classificação

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Adicionar classificação", "exato": true}`.
- Gesto: `click`.
- Condição: Tipo escolhido; máximo 20 tipos distintos.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).

Resultado:

- Adiciona ao rascunho sem salvar no servidor; primeiro tipo torna-se principal.
- Limpa tipo selecionado. Duplicado ou limite de 20 gera alerta, sem adicionar.

### OCO-PRINCIPAL — Principal

- Localizador: `{"escopo": ".editor .record identificado pelo tipo", "papel": "radio", "nome": "Principal", "exato": true}`.
- Gesto: `check`.
- Condição: Controle visível e habilitado.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).

Resultado:

- Marca somente a classificação escolhida; desmarca as demais.
- Efeito apenas no rascunho até Salvar desastre.

### OCO-REMOVER — Remover classificação

- Localizador: `{"escopo": ".editor .record", "papel": "button", "nome": "Remover classificação", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).
- Persistência/rede: `Sem requisição imediata; persiste ao Salvar desastre.`.

Resultado:

- Remove do rascunho sem confirmação.
- Se remove a principal, a primeira remanescente torna-se principal; ao salvar, removidas existentes ficam históricas.

### OCO-AREAS — Áreas e mapa

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Áreas e mapa", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ARE](./18-areas-afetadas.md).

Resultado:

- Abre app-areas com Áreas de {titulo}.
- Ocorrência inativada abre histórico com criação/edição bloqueadas.

## Cenários de aceitação

### OCO-C01 — Criar e consultar

- **Dado:** Dados exclusivos e referências preparadas.
- **Quando:** Preencher obrigatórios; adicionar um ou mais tipos; selecionar principal; Salvar desastre; Buscar.
- **Então:** Mensagem de sucesso e registro persistido; editor limpo.

### OCO-C02 — Trocar principal

- **Dado:** Ocorrência com dois tipos.
- **Quando:** Editar ocorrência; marcar Principal no segundo tipo; Salvar desastre.
- **Então:** Somente o segundo é principal na lista; IDs de classificações mantidas preservados.

### OCO-C03 — Dados obrigatórios de operação

- **Dado:** Editor válido em nome/descrição.
- **Quando:** Tentar salvar sem coordenadora/classificações; depois tentar encerrado sem encerramento.
- **Então:** Alertas de seleção e de encerramento; não persiste versão incompleta.

### OCO-C04 — Ocorrência encerrada

- **Dado:** Ocorrência salva como encerrado com data válida.
- **Quando:** Editar e tentar mudar para em_resposta, com encerramento vazio.
- **Então:** API recusa reabertura; mostra role=alert; ocorrência continua encerrada.

## Limites e particularidades

- Catálogo não é equivalência automática com COBRADE ou classificação oficial.
- Datas usam timezone do navegador no preenchimento e UTC no tráfego.
- Inativação difere de situação encerrado.

## Fontes da implementação

- [frontend/src/app/desastres/cadastros.html](../../frontend/src/app/desastres/cadastros.html)
- [frontend/src/app/desastres/cadastros.ts](../../frontend/src/app/desastres/cadastros.ts)
- [backend/business/servico/desastres.py](../../backend/business/servico/desastres.py)
