# MAP — Mapa e desenho de delimitações

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Permitir revisão territorial e criação de polígono simples para o formulário da área.

## Entrada e identificação

Fluxo ARE: Áreas e mapa

Raiz do componente/área: `app-mapa-areas`. Navegação interna sem troca de URL.

- Região Mapa para delimitar áreas afetadas visível.
- .leaflet-container presente; botão Desenhar nova delimitação habilitado se ocorrência ativa.

## Pré-condições

- Tela de áreas aberta.
- Tiles externos opcionais para o desenho; mapa Leaflet deve inicializar.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#mapa-centro-latitude` | Obrigatória para centralizar; ponto decimal, -85 a 85; padrão -23.5505. |
| `#mapa-centro-longitude` | Obrigatória para centralizar; ponto decimal, -180 a 180; padrão -46.6333. |
| `.mapa-area[role="region"]` | Clique adiciona vértice somente durante desenho; até 200 vértices. Coordenadas GeoJSON na ordem longitude/latitude. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### MAP-ENQUADRAR — Enquadrar áreas da página

- Localizador: `{"escopo": ":scope", "papel": "button", "nome": "Enquadrar áreas da página", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MAP](./19-mapa-desenho.md).

Resultado:

- Ajusta a vista para polígonos da página corrente; bloqueado se não há áreas; não persiste.

### MAP-INICIAR — Desenhar nova delimitação

- Localizador: `{"escopo": ":scope", "papel": "button", "nome": "Desenhar nova delimitação", "exato": true}`.
- Gesto: `click`.
- Condição: Mapa pronto e ocorrência ativa.
- Destino: [MAP](./19-mapa-desenho.md).

Resultado:

- Limpa geometria/desenho anteriores e inicia coleta de vértices.
- Status instrui clicar no mapa e concluir; não salva a área.

### MAP-PONTO — Clique no mapa

- Localizador: `{"css": ".mapa-area[role=\"region\"]"}`.
- Gesto: `click com posição relativa`.
- Condição: Controle visível e habilitado.
- Destino: [MAP](./19-mapa-desenho.md).

Resultado:

- Adiciona vértice e atualiza Vértices do desenho; desenha marcadores/linha.
- Sem efeito fora do modo desenho, quando bloqueado ou após 200 pontos.

### MAP-DESFAZER — Desfazer ponto

- Localizador: `{"escopo": ":scope", "papel": "button", "nome": "Desfazer ponto", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MAP](./19-mapa-desenho.md).

Resultado:

- Remove somente o último vértice do desenho corrente; bloqueado sem pontos ou fora do desenho.

### MAP-CONCLUIR — Concluir delimitação

- Localizador: `{"escopo": ":scope", "papel": "button", "nome": "Concluir delimitação", "exato": true}`.
- Gesto: `click`.
- Condição: Ocorrência ativa; em desenho, pelo menos três pontos.
- Destino: [ARE](./18-areas-afetadas.md).

Resultado:

- Fecha o anel automaticamente e encerra desenho, com três ou mais vértices.
- Status Delimitação pronta para salvar no formulário da área.; formulário reconhece delimitação selecionada.
- Não valida toda a geometria nem grava no banco até Salvar área.

### MAP-LIMPAR — Limpar delimitação

- Localizador: `{"escopo": ":scope", "papel": "button", "nome": "Limpar delimitação", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MAP](./19-mapa-desenho.md).

Resultado:

- Apaga seleção/desenho locais; mantém campos de texto da área; área persistida não é apagada.

### MAP-CENTRALIZAR — Centralizar coordenadas

- Localizador: `{"escopo": ":scope", "papel": "button", "nome": "Centralizar coordenadas", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MAP](./19-mapa-desenho.md).

Resultado:

- Centraliza vista nas coordenadas com zoom 13; não geocodifica município, não altera geometria nem grava.

### MAP-ZOOM-MAIS — Zoom in

- Localizador: `{"css": ".leaflet-control-zoom-in"}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MAP](./19-mapa-desenho.md).

Resultado:

- Aumenta zoom respeitando limite 19.

### MAP-ZOOM-MENOS — Zoom out

- Localizador: `{"css": ".leaflet-control-zoom-out"}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [MAP](./19-mapa-desenho.md).

Resultado:

- Diminui zoom respeitando limite 2.

### MAP-ATRIBUICAO — OpenStreetMap

- Localizador: `{"escopo": ".leaflet-control-attribution", "papel": "link", "nome": "OpenStreetMap", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: externo.

Resultado:

- Abre o destino de atribuição https://www.openstreetmap.org/copyright; link não salva nem navega para módulo interno.

## Cenários de aceitação

### MAP-C01 — Desenho real por eventos

- **Dado:** Mapa visível em dimensão suficiente e ocorrência ativa.
- **Quando:** Iniciar; clicar posições relativas (0.25,0.30), (0.70,0.30), (0.70,0.75); concluir.
- **Então:** Status de geometria pronta; salvar pelo formulário ARE e reencontrar a delimitação.

### MAP-C02 — Desfazer e limite mínimo

- **Dado:** Desenho com dois vértices.
- **Quando:** Conferir Concluir desabilitado; adicionar terceiro; Desfazer ponto.
- **Então:** Contagem volta a dois e Concluir desabilita; não há geometria concluída.

### MAP-C03 — Polígono cruzado

- **Dado:** Área com textos válidos.
- **Quando:** Desenhar pontos em ordem que cruza bordas; concluir; Salvar área.
- **Então:** API recusa geometria inválida com role=alert; nenhuma área nova. Limpar e redesenhar permite corrigir.

### MAP-C04 — Falha de tiles

- **Dado:** Simular indisponibilidade do fundo somente no cenário dedicado.
- **Quando:** Abrir mapa e desenhar geometria.
- **Então:** Status informa falha do fundo; ferramentas e desenho continuam utilizáveis.

## Limites e particularidades

- Cores: baixa verde; moderada ocre; alta laranja; crítica vinho. São avaliações administrativas.
- Polígono simples sem buracos; API rejeita cruzamentos/degeneração e valida limites de 3–200 vértices.
- Não usar clique sobre zoom/atribuição para adicionar ponto. Exemplo Playwright em contrato-harness.md.
- Arrastar a região altera a vista; clicar em polígono pode mostrar tooltip de nome/gravidade, sem selecionar editor.

## Fontes da implementação

- [frontend/src/app/desastres/mapa.ts](../../frontend/src/app/desastres/mapa.ts)
- [backend/business/view_models/desastres.py](../../backend/business/view_models/desastres.py)
