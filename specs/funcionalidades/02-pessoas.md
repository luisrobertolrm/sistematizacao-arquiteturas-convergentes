# PES — Pessoas

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Manter pessoas da rede e acessar seus vínculos e formação.

## Entrada e identificação

Pessoas

Raiz do componente/área: `app-root > main > .workspace`. Navegação interna sem troca de URL.

- Título h1 Pessoas
- Lista com aria-busy=false; botão Atualizar habilitado.

## Pré-condições

- Sessão administrativa válida.
- Dados com nome exclusivo por execução.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#cadastro-nome` | Obrigatório, 2–200 caracteres. |
| `#municipio` | Obrigatório, exatamente sete dígitos; usar 3550308 no cenário. |
| `#uf` | Obrigatório; UF brasileira, normalizada para maiúsculas pela API; padrão SP. |
| `#email` | Opcional; email válido quando informado, até 320 caracteres. |
| `#telefone` | Opcional; API normaliza pontuação e exige 8–15 dígitos, com + opcional. |
| `#latitude` | Opcional; entre -90 e 90, até sete casas; informar junto com longitude. |
| `#longitude` | Opcional; entre -180 e 180, até sete casas; informar junto com latitude. |
| `#situacao` | Valores pendente (padrão), validada, rejeitada. É validação administrativa. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### PES-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PES](./02-pessoas.md).
- Persistência/rede: `GET da coleção com limite=50 e deslocamento atual.`.

Resultado:

- Reconsulta a página atual; conserva o filtro e o formulário em edição.

### PES-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PES](./02-pessoas.md).
- Persistência/rede: `GET com deslocamento anterior.`.

Resultado:

- Retorna 50 registros, respeitando filtros; desabilitado na página 1.

### PES-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PES](./02-pessoas.md).
- Persistência/rede: `GET com deslocamento seguinte.`.

Resultado:

- Avança 50 registros; desabilitado se a página atual tiver menos de 50.

### PES-CRIAR — Cadastrar

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Cadastrar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PES](./02-pessoas.md).
- Persistência/rede: `POST /api/v1/pessoas`.

Resultado:

- Envia os dados e, em sucesso, exibe Cadastro salvo.
- Limpa o formulário para Novo cadastro e atualiza a página corrente da lista.
- A presença na página depende da paginação; não há busca nesta tela.

### PES-EDITAR — Editar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PES](./02-pessoas.md).

Resultado:

- Preenche o formulário com o registro escolhido, sem persistir ainda.
- Exibe Editar cadastro, Salvar alterações e Cancelar; foco em #cadastro-nome.

### PES-SALVAR — Salvar alterações

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar alterações", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PES](./02-pessoas.md).
- Persistência/rede: `PUT /api/v1/pessoas/{id}`.

Resultado:

- Atualiza o mesmo ID; exibe Cadastro salvo.
- Volta a Novo cadastro, limpa o formulário e recarrega a lista.

### PES-CANCELAR — Cancelar

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Cancelar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PES](./02-pessoas.md).
- Persistência/rede: `Nenhuma requisição de gravação.`.

Resultado:

- Descarta o rascunho de edição e volta ao formulário vazio, com UF SP e situação pendente.

### PES-INATIVAR — Inativar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PES](./02-pessoas.md).
- Persistência/rede: `DELETE /api/v1/pessoas/{id}`.
- Diálogo nativo `confirm`: Inativar o cadastro de {nome}? O histórico será preservado.
- Ao cancelar o diálogo: Não envia DELETE e conserva registro/formulário.

Resultado:

- Ao aceitar, inativa o registro; exibe Cadastro inativado.
- Limpa o editor e atualiza a lista ativa, na qual o registro não deve mais aparecer.

### PES-VINCULOS — Vínculos e formação

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Vínculos e formação", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [VIN-INS](./05-pessoa-instituicoes.md).
- Persistência/rede: `GET /api/v1/pessoas/{pessoa_id}/instituicoes`.

Resultado:

- Substitui lista/editor por app-vinculos, com o nome da pessoa em h2.
- Abre inicialmente a aba Instituições dos vínculos.

## Cenários de aceitação

### PES-C01 — Criar e editar cadastro

- **Dado:** Token válido; nome único e IBGE 3550308.
- **Quando:** Preencher nome/IBGE/UF; Cadastrar; localizar pelo h3; Editar; corrigir nome; Salvar alterações.
- **Então:** Mensagem de sucesso; mesmo ID atualizado. Em novo formulário, padrões restaurados.

### PES-C02 — Rejeitar coordenadas incompletas

- **Dado:** Cadastro com demais campos válidos.
- **Quando:** Informar somente latitude; tentar cadastrar.
- **Então:** API rejeita; role=alert; sem mensagem nova de sucesso nem novo registro. Corrigir com ambas as coordenadas ou limpar ambas.

### PES-C03 — Cancelar e confirmar inativação

- **Dado:** Registro criado por esta execução.
- **Quando:** Inativar e dispensar confirm; depois repetir e aceitar.
- **Então:** Primeira tentativa preserva o registro; segunda o remove da lista ativa.

## Limites e particularidades

- A lista não possui campo Buscar nem opção de histórico. Não procurar controles inexistentes.
- Registros inativados não têm reativação nesta interface.
- POST/PUT/DELETE exigem JWT administrativo.

## Fontes da implementação

- [frontend/src/app/app.html](../../frontend/src/app/app.html)
- [frontend/src/app/app.ts](../../frontend/src/app/app.ts)
- [frontend/src/app/core/api.ts](../../frontend/src/app/core/api.ts)
- [backend/business/view_models/cadastros.py](../../backend/business/view_models/cadastros.py)
