# VIN-PRO — Profissões da pessoa

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Registrar a relação individual da pessoa com profissões, mantendo validação administrativa e histórico.

## Entrada e identificação

Pessoas → No cartão da pessoa: Vínculos e formação → Na navegação Vínculos da pessoa: Profissões

Raiz do componente/área: `app-vinculos`. Navegação interna sem troca de URL.

- h2 com nome da pessoa do cenário.
- Aba Profissões com aria-current=page; .workspace com aria-busy=false.

## Pré-condições

- Pessoa ativa.
- Referência ativa no catálogo correspondente.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#referencia-busca` | Busca referência ativa; mínimo dois caracteres para filtrar. |
| `#referencia-id` | Instituição, profissão ou curso conforme a aba; obrigatório; opções por nome. |
| `#vinculo-validacao` | pendente (padrão), validada, rejeitada. |
| `#registro-profissional` | Opcional, até 100 caracteres; API converte para maiúsculas. |
| `#orgao` | Opcional, até 100 caracteres; API converte para maiúsculas. |
| `#registro-uf` | Opcional; UF brasileira, normalizada em maiúsculas. |
| `#profissao-validade` | Validade opcional YYYY-MM-DD. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### VIN-PRO-ABA — Profissões

- Localizador: `{"escopo": "nav[aria-label=\"Vínculos da pessoa\"]", "papel": "button", "nome": "Profissões", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-PRO](./06-pessoa-profissoes.md).

Resultado:

- Troca a modalidade de vínculo; limpa o editor e volta à página 1; conserva a opção de histórico.

### VIN-PRO-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-PRO](./06-pessoa-profissoes.md).

Resultado:

- Recarrega os vínculos da pessoa, aba e página atuais.

### VIN-PRO-HISTORICO — Incluir inativados e referências inativas

- Localizador: `{"escopo": ".directory", "papel": "checkbox", "nome": "Incluir inativados e referências inativas", "exato": true}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-PRO](./06-pessoa-profissoes.md).

Resultado:

- Marcado: consulta com incluir_inativos=true, incluindo vínculos com referências inativas.
- Desmarcado: retorna à consulta normal; ambas as ações voltam à página 1.

### VIN-PRO-EDITAR — Editar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar", "exato": true}`.
- Gesto: `click`.
- Condição: Vínculo ainda não inativado.
- Destino: [VIN-PRO](./06-pessoa-profissoes.md).

Resultado:

- Preenche Editar vínculo, referência e campos individuais; situação atual é preservada.

### VIN-PRO-SALVAR — Salvar vínculo

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar vínculo", "exato": true}`.
- Gesto: `click`.
- Condição: Referência selecionada, formulário válido e sem carregamento.
- Destino: [VIN-PRO](./06-pessoa-profissoes.md).
- Persistência/rede: `POST /api/v1/pessoas/{pessoa_id}/profissoes ou PUT .../{vinculo_id}`.

Resultado:

- Cria ou altera o vínculo da pessoa selecionada; exibe Vínculo salvo.
- Limpa o editor e reconsulta a lista.

### VIN-PRO-CANCELAR — Cancelar

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Cancelar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-PRO](./06-pessoa-profissoes.md).

Resultado:

- Descarta rascunho e limpa referência/campos; volta a Novo vínculo.

### VIN-PRO-INATIVAR — Inativar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-PRO](./06-pessoa-profissoes.md).
- Persistência/rede: `DELETE /api/v1/pessoas/{pessoa_id}/profissoes/{vinculo_id}`.
- Diálogo nativo `confirm`: Inativar este vínculo? O registro será preservado no histórico.
- Ao cancelar o diálogo: Sem alteração.

Resultado:

- Aceitar exibe Vínculo inativado.; limpa editor e recarrega.
- Pode ser consultado com histórico, sem botões Editar/Inativar.

### VIN-PRO-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-PRO](./06-pessoa-profissoes.md).

Resultado:

- Recua 50 vínculos; desabilitado na página 1.

### VIN-PRO-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-PRO](./06-pessoa-profissoes.md).

Resultado:

- Avança 50 vínculos; desabilitado com menos de 50 na página atual.

### VIN-PRO-VOLTAR — Voltar às pessoas

- Localizador: `{"escopo": ":scope > .section-head", "papel": "button", "nome": "Voltar às pessoas", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PES](./02-pessoas.md).

Resultado:

- Fecha app-vinculos e mostra o cadastro de Pessoas.
- Mantém a lista/página da tela de origem; não faz nova consulta automaticamente.

## Cenários de aceitação

### VIN-PRO-C01 — Criar e consultar vínculo

- **Dado:** Pessoa e referência do cenário ativas.
- **Quando:** Abrir a aba; selecionar referência; preencher campos obrigatórios; Salvar vínculo.
- **Então:** Vínculo salvo.; cartão mostra referência e validação escolhidas.

### VIN-PRO-C02 — Editar, cancelar e persistir

- **Dado:** Vínculo ativo.
- **Quando:** Editar; alterar campo; Cancelar; Editar novamente; alterar e Salvar vínculo.
- **Então:** Cancelar não grava. Salvar mantém ID e atualiza dados.

### VIN-PRO-C03 — Inativar e recuperar histórico

- **Dado:** Vínculo criado pelo cenário.
- **Quando:** Inativar e aceitar; incluir inativados e referências inativas.
- **Então:** Registro histórico exibe data de inativação e não oferece edição.

## Limites e particularidades

- Botões Buscar/Anterior/Próxima do seletor precisam de escopo app-referencia; a lista da pessoa tem paginação própria.
- O seletor de referência é compartilhado e está descrito em contrato-harness.md.
- Validação administrativa não comprova aptidão ou disponibilidade operacional.
- Registro e validade não constituem verificação junto ao órgão profissional.

## Fontes da implementação

- [frontend/src/app/qualificacoes/vinculos.html](../../frontend/src/app/qualificacoes/vinculos.html)
- [frontend/src/app/qualificacoes/vinculos.ts](../../frontend/src/app/qualificacoes/vinculos.ts)
- [frontend/src/app/qualificacoes/referencia.ts](../../frontend/src/app/qualificacoes/referencia.ts)
- [backend/business/view_models/qualificacoes.py](../../backend/business/view_models/qualificacoes.py)
