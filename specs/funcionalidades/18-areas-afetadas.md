# ARE — Áreas afetadas e avaliação territorial

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Delimitar a localidade afetada, registrar gravidade/situação e acompanhar a data da avaliação administrativa.

## Entrada e identificação

Desastres e áreas → Ocorrências → No cartão: Áreas e mapa

Raiz do componente/área: `app-areas`. Navegação interna sem troca de URL.

- h2 Áreas de {ocorrência}.
- .workspace com aria-busy=false; app-mapa-areas inicializado.

## Pré-condições

- Ocorrência existente; ativa para cadastrar/editar/avaliar.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#area-busca` | Busca nome/descrição/município; usar Buscar áreas. |
| `#area-historico` | Inclui áreas inativadas; forçado/bloqueado em ocorrência inativada. |
| `#area-nome` | Obrigatório, 2–200 caracteres. |
| `#area-descricao` | Obrigatório, 2–4000 caracteres. |
| `#area-municipio` | Sete dígitos obrigatórios; não centraliza o mapa automaticamente. |
| `#area-gravidade` | baixa, moderada (padrão), alta, critica. |
| `#area-situacao` | em_avaliacao (padrão), em_resposta, em_recuperacao, encerrada. |
| `app-mapa-areas [role="region"]` | Polígono obrigatório produzido no mapa; ver MAP. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### ARE-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ARE](./18-areas-afetadas.md).

Resultado:

- Atualiza página/lista e polígonos de áreas consultadas.

### ARE-BUSCAR — Buscar áreas

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Buscar áreas", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ARE](./18-areas-afetadas.md).

Resultado:

- Retorna à página 1 e aplica filtro com dois caracteres ou mais; polígonos passam a refletir os resultados.

### ARE-HISTORICO — Incluir áreas inativadas

- Localizador: `{"css": "#area-historico"}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [ARE](./18-areas-afetadas.md).

Resultado:

- Alterna histórico e volta à página 1; polígonos inativados usam traço descontínuo.

### ARE-VER — Ver delimitação

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Ver delimitação", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MAP](./19-mapa-desenho.md).

Resultado:

- Cancela desenho em andamento e seleciona a geometria da área; enquadra polígono no mapa.
- Não preenche os campos nem muda o ID em edição. Não salva nem abre outra tela.

### ARE-EDITAR — Editar área

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar área", "exato": true}`.
- Gesto: `click`.
- Condição: Área e ocorrência ativas.
- Destino: [ARE](./18-areas-afetadas.md).

Resultado:

- Cancela desenho, preenche editor e seleciona geometria; mostra Editar área.

### ARE-LIMPAR — Limpar área

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Limpar área", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ARE](./18-areas-afetadas.md).

Resultado:

- Descarta edição/desenho/geometria; limpa campos; restaura moderada/em_avaliacao.

### ARE-SALVAR — Salvar área

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar área", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ARE](./18-areas-afetadas.md).
- Persistência/rede: `POST /api/v1/desastres/{desastre_id}/areas ou PUT .../{area_id}`.

Resultado:

- Cria/altera área; exibe Área salva.; limpa editor e atualiza lista/mapa.
- Mudança de gravidade/situação atualiza data da avaliação; alteração só de nome/descrição/geometria preserva a data anterior.

### ARE-AVALIAR — Confirmar avaliação atual

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Confirmar avaliação atual", "exato": true}`.
- Gesto: `click`.
- Condição: Área e ocorrência ativas.
- Destino: [ARE](./18-areas-afetadas.md).
- Persistência/rede: `POST /api/v1/desastres/{desastre_id}/areas/{id}/avaliar`.
- Diálogo nativo `confirm`: Confirmar avaliação atual de {nome}: {gravidade}, {situacao}?
- Ao cancelar o diálogo: Sem alteração.

Resultado:

- Aceitar registra nova avaliação com a gravidade/situação exibidas, mesmo sem mudança desses valores.
- Exibe Avaliação confirmada.; atualiza data, limpa editor e reconsulta.

### ARE-INATIVAR — Inativar área

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar área", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ARE](./18-areas-afetadas.md).
- Persistência/rede: `DELETE /api/v1/desastres/{desastre_id}/areas/{id}`.
- Diálogo nativo `confirm`: Inativar a área {nome}?
- Ao cancelar o diálogo: Sem alteração.

Resultado:

- Aceitar exibe Área inativada.; limpa editor/reconsulta; permitido mesmo com ocorrência inativada.

### ARE-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ARE](./18-areas-afetadas.md).

Resultado:

- Recua 50 áreas e atualiza polígonos da página.

### ARE-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ARE](./18-areas-afetadas.md).

Resultado:

- Avança 50 áreas quando a página atual tem 50.

### ARE-VOLTAR — Voltar às ocorrências

- Localizador: `{"escopo": ":scope > .section-head", "papel": "button", "nome": "Voltar às ocorrências", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).

Resultado:

- Fecha áreas/mapa e reconsulta as ocorrências com filtros/página anteriores.

## Cenários de aceitação

### ARE-C01 — Cadastrar área com polígono

- **Dado:** Ocorrência ativa e mapa inicializado.
- **Quando:** Preencher obrigatórios; desenhar triângulo simples; concluir; Salvar área.
- **Então:** Área salva.; cartão com gravidade/situação/avaliação; polígono reaparece a partir do banco.

### ARE-C02 — Sem geometria

- **Dado:** Textos/município válidos, sem delimitação.
- **Quando:** Salvar área.
- **Então:** Alerta Desenhe e conclua a delimitação da área no mapa.; não envia gravação.

### ARE-C03 — Correção versus reavaliação

- **Dado:** Área existente; capturar Avaliada em e timestamps da API para precisão.
- **Quando:** Editar apenas nome; salvar; depois mudar gravidade; salvar; confirmar avaliação atual.
- **Então:** Correção mantém ultima_avaliacao_em; mudança e confirmação explícita geram avaliação nova.

### ARE-C04 — Ocorrência inativada

- **Dado:** Abrir áreas de ocorrência histórica.
- **Quando:** Consultar controles.
- **Então:** Histórico marcado/desabilitado; formulário/desenho bloqueados; sem Editar área/Confirmar avaliação; Ver delimitação e inativação de área ativa disponíveis.

## Limites e particularidades

- Ver delimitação altera a geometria selecionada compartilhada com o editor. Para editar outro registro, clicar Editar área; para novo, Limpar área.
- Gravidade não muda automaticamente a prioridade da demanda.
- O mapa exibe apenas a página atual de áreas.

## Fontes da implementação

- [frontend/src/app/desastres/areas.html](../../frontend/src/app/desastres/areas.html)
- [frontend/src/app/desastres/areas.ts](../../frontend/src/app/desastres/areas.ts)
