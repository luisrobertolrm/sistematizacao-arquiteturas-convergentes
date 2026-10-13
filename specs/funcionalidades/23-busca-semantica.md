# BUS — Busca de atividades por significado

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Encontrar serviços do catálogo próximos ao texto de uma necessidade, com rastreabilidade do modelo.

## Entrada e identificação

Configuração de IA → Índices de atividades → No editor: Busca semântica

Raiz do componente/área: `app-ia-configuracao`. Navegação interna sem troca de URL.

- #ia-consulta visível; .workspace com aria-busy=false.

## Pré-condições

- Modelo de embedding selecionado por MOD e cobertura atual integral do catálogo ativo.
- Endpoint/provedor disponíveis; base aceita até 5000 vetores atuais para busca exata.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#ia-consulta` | Necessidade textual obrigatória, 2–4000 caracteres. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### BUS-BUSCAR — Buscar por significado

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Buscar por significado", "exato": true}`.
- Gesto: `click`.
- Condição: Texto válido e sem outra operação em andamento.
- Destino: [BUS](./23-busca-semantica.md).
- Persistência/rede: `POST /api/v1/atividades/busca-semantica, texto e limite=10.`.

Resultado:

- Limpa o resultado semântico anterior e envia a consulta.
- Em sucesso, mostra Modelo utilizado: {id}, nomes e similaridade com três casas.
- Lista vazia exibe Nenhuma atividade encontrada.; não navega, edita nem cria demanda.

## Cenários de aceitação

### BUS-C01 — Buscar com cobertura

- **Dado:** Modelo selecionado e índices atuais; provedor controlado conhecido.
- **Quando:** Informar uma necessidade como distribuir suprimentos e Buscar por significado.
- **Então:** ID do modelo selecionado e resultados do catálogo. Não exigir score/ordem fixos com LLM real.

### BUS-C02 — Texto insuficiente

- **Dado:** Campo vazio ou com um caractere.
- **Quando:** Conferir botão de busca.
- **Então:** Desabilitado; nenhuma chamada.

### BUS-C03 — Modelo/cobertura ausentes

- **Dado:** Nenhum embedding selecionado ou atividade nova sem índice.
- **Quando:** Buscar texto válido.
- **Então:** Erro explícito em role=alert; sem resultado apresentado como sucesso.

### BUS-C04 — Independência do preparador

- **Dado:** Outro modelo escolhido em #indice-modelo-id, sem mudar seleção MOD.
- **Quando:** Executar busca semântica.
- **Então:** Modelo utilizado continua sendo o selecionado por finalidade, não o do lote.

## Limites e particularidades

- Similaridade não prova equivalência de serviço, capacidade, formação ou disponibilidade.
- Busca vetorial habilitada para atividades; profissões, cursos e recursos ainda não possuem tela de indexação vetorial.
- A tela não fornece botão de abrir/selecionar atividade a partir do resultado.

## Fontes da implementação

- [frontend/src/app/ia/configuracao.html](../../frontend/src/app/ia/configuracao.html)
- [frontend/src/app/ia/configuracao.ts](../../frontend/src/app/ia/configuracao.ts)
- [frontend/src/app/core/operacao-api.ts](../../frontend/src/app/core/operacao-api.ts)
