# VIN-CUR — Cursos e formação da pessoa

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Registrar a relação individual da pessoa com cursos, mantendo validação administrativa e histórico.

## Entrada e identificação

Pessoas → No cartão da pessoa: Vínculos e formação → Na navegação Vínculos da pessoa: Cursos

Raiz do componente/área: `app-vinculos`. Navegação interna sem troca de URL.

- h2 com nome da pessoa do cenário.
- Aba Cursos com aria-current=page; .workspace com aria-busy=false.

## Pré-condições

- Pessoa ativa.
- Referência ativa no catálogo correspondente.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#referencia-busca` | Busca referência ativa; mínimo dois caracteres para filtrar. |
| `#referencia-id` | Instituição, profissão ou curso conforme a aba; obrigatório; opções por nome. |
| `#vinculo-validacao` | pendente (padrão), validada, rejeitada. |
| `#emissor` | Obrigatório, 2–200 caracteres. |
| `#conclusao` | Data obrigatória YYYY-MM-DD. |
| `#curso-validade` | Opcional; não anterior à conclusão. |
| `#carga` | Opcional; número positivo com ponto decimal, até duas casas. |
| `#comprovante` | Opcional, até 500 caracteres; referência opaca como documento:spec-123. Sem upload, query ou credenciais. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### VIN-CUR-ABA — Cursos

- Localizador: `{"escopo": "nav[aria-label=\"Vínculos da pessoa\"]", "papel": "button", "nome": "Cursos", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-CUR](./07-pessoa-cursos.md).

Resultado:

- Troca a modalidade de vínculo; limpa o editor e volta à página 1; conserva a opção de histórico.

### VIN-CUR-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-CUR](./07-pessoa-cursos.md).

Resultado:

- Recarrega os vínculos da pessoa, aba e página atuais.

### VIN-CUR-HISTORICO — Incluir inativados e referências inativas

- Localizador: `{"escopo": ".directory", "papel": "checkbox", "nome": "Incluir inativados e referências inativas", "exato": true}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-CUR](./07-pessoa-cursos.md).

Resultado:

- Marcado: consulta com incluir_inativos=true, incluindo vínculos com referências inativas.
- Desmarcado: retorna à consulta normal; ambas as ações voltam à página 1.

### VIN-CUR-EDITAR — Editar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar", "exato": true}`.
- Gesto: `click`.
- Condição: Vínculo ainda não inativado.
- Destino: [VIN-CUR](./07-pessoa-cursos.md).

Resultado:

- Preenche Editar vínculo, referência e campos individuais; situação atual é preservada.

### VIN-CUR-SALVAR — Salvar vínculo

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar vínculo", "exato": true}`.
- Gesto: `click`.
- Condição: Referência selecionada, formulário válido e sem carregamento.
- Destino: [VIN-CUR](./07-pessoa-cursos.md).
- Persistência/rede: `POST /api/v1/pessoas/{pessoa_id}/cursos ou PUT .../{vinculo_id}`.

Resultado:

- Cria ou altera o vínculo da pessoa selecionada; exibe Vínculo salvo.
- Limpa o editor e reconsulta a lista.

### VIN-CUR-CANCELAR — Cancelar

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Cancelar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-CUR](./07-pessoa-cursos.md).

Resultado:

- Descarta rascunho e limpa referência/campos; volta a Novo vínculo.

### VIN-CUR-INATIVAR — Inativar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-CUR](./07-pessoa-cursos.md).
- Persistência/rede: `DELETE /api/v1/pessoas/{pessoa_id}/cursos/{vinculo_id}`.
- Diálogo nativo `confirm`: Inativar este vínculo? O registro será preservado no histórico.
- Ao cancelar o diálogo: Sem alteração.

Resultado:

- Aceitar exibe Vínculo inativado.; limpa editor e recarrega.
- Pode ser consultado com histórico, sem botões Editar/Inativar.

### VIN-CUR-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-CUR](./07-pessoa-cursos.md).

Resultado:

- Recua 50 vínculos; desabilitado na página 1.

### VIN-CUR-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-CUR](./07-pessoa-cursos.md).

Resultado:

- Avança 50 vínculos; desabilitado com menos de 50 na página atual.

### VIN-CUR-VOLTAR — Voltar às pessoas

- Localizador: `{"escopo": ":scope > .section-head", "papel": "button", "nome": "Voltar às pessoas", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PES](./02-pessoas.md).

Resultado:

- Fecha app-vinculos e mostra o cadastro de Pessoas.
- Mantém a lista/página da tela de origem; não faz nova consulta automaticamente.

## Cenários de aceitação

### VIN-CUR-C01 — Criar e consultar vínculo

- **Dado:** Pessoa e referência do cenário ativas.
- **Quando:** Abrir a aba; selecionar referência; preencher campos obrigatórios; Salvar vínculo.
- **Então:** Vínculo salvo.; cartão mostra referência e validação escolhidas.

### VIN-CUR-C02 — Editar, cancelar e persistir

- **Dado:** Vínculo ativo.
- **Quando:** Editar; alterar campo; Cancelar; Editar novamente; alterar e Salvar vínculo.
- **Então:** Cancelar não grava. Salvar mantém ID e atualiza dados.

### VIN-CUR-C03 — Inativar e recuperar histórico

- **Dado:** Vínculo criado pelo cenário.
- **Quando:** Inativar e aceitar; incluir inativados e referências inativas.
- **Então:** Registro histórico exibe data de inativação e não oferece edição.

## Limites e particularidades

- Botões Buscar/Anterior/Próxima do seletor precisam de escopo app-referencia; a lista da pessoa tem paginação própria.
- O seletor de referência é compartilhado e está descrito em contrato-harness.md.
- Validação administrativa não comprova aptidão ou disponibilidade operacional.
- Renovação pode gerar outro registro de conclusão; comprovante é apenas texto.

## Fontes da implementação

- [frontend/src/app/qualificacoes/vinculos.html](../../frontend/src/app/qualificacoes/vinculos.html)
- [frontend/src/app/qualificacoes/vinculos.ts](../../frontend/src/app/qualificacoes/vinculos.ts)
- [frontend/src/app/qualificacoes/referencia.ts](../../frontend/src/app/qualificacoes/referencia.ts)
- [backend/business/view_models/qualificacoes.py](../../backend/business/view_models/qualificacoes.py)
