# PRO — Profissões

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Manter o catálogo de profissões; a profissão individual é registrada em Vínculos e formação.

## Entrada e identificação

Profissões e cursos → Profissões

Raiz do componente/área: `app-catalogos`. Navegação interna sem troca de URL.

- Aba Profissões com aria-current=page.
- .workspace com aria-busy=false.

## Pré-condições

- Sessão administrativa válida.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#catalogo-busca` | Filtro por nome; Enter também executa pesquisar(). |
| `#catalogo-nome` | Obrigatório, 2–200 caracteres. |
| `#catalogo-descricao` | Descrição opcional, até 4000 caracteres. |
| `#cbo` | Opcional; seis dígitos após retirar espaços e hífen. Formato inválido é rejeitado pela API. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### PRO-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PRO](./03-profissoes.md).
- Persistência/rede: `GET da coleção com limite=50 e deslocamento atual.`.

Resultado:

- Reconsulta a página atual; conserva o filtro e o formulário em edição.

### PRO-BUSCAR — Buscar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Buscar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PRO](./03-profissoes.md).
- Campo associado: `#catalogo-busca`.
- Persistência/rede: `GET da coleção; busca enviada somente quando válida.`.

Resultado:

- Retorna à página 1.
- Aplica a busca somente com pelo menos dois caracteres; vazia ou com um caractere lista sem filtro.

### PRO-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PRO](./03-profissoes.md).
- Persistência/rede: `GET com deslocamento anterior.`.

Resultado:

- Retorna 50 registros, respeitando filtros; desabilitado na página 1.

### PRO-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PRO](./03-profissoes.md).
- Persistência/rede: `GET com deslocamento seguinte.`.

Resultado:

- Avança 50 registros; desabilitado se a página atual tiver menos de 50.

### PRO-ABA — Profissões

- Localizador: `{"escopo": "nav[aria-label=\"Catálogos de qualificação\"]", "papel": "button", "nome": "Profissões", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PRO](./03-profissoes.md).

Resultado:

- Seleciona o catálogo, zera busca/página, limpa o editor e recarrega a lista.

### PRO-EDITAR — Editar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PRO](./03-profissoes.md).

Resultado:

- Preenche Editar cadastro com os dados do registro, mantendo o mesmo ID.

### PRO-SALVAR — Salvar cadastro

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar cadastro", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PRO](./03-profissoes.md).
- Persistência/rede: `POST /api/v1/profissoes ou PUT /api/v1/profissoes/{id}`.

Resultado:

- Cria ou atualiza conforme o editor; exibe Catálogo salvo.
- Limpa o editor e recarrega a página com o filtro corrente.

### PRO-CANCELAR — Cancelar

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Cancelar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PRO](./03-profissoes.md).

Resultado:

- Descarta a edição e limpa o formulário, sem gravação.

### PRO-INATIVAR — Inativar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PRO](./03-profissoes.md).
- Persistência/rede: `DELETE /api/v1/profissoes/{id}`.
- Diálogo nativo `confirm`: Inativar {nome}? Os vínculos anteriores serão preservados no histórico.
- Ao cancelar o diálogo: Nenhuma alteração.

Resultado:

- Aceitar inativa e exibe Catálogo inativado.
- Registro sai da lista ativa; vínculos anteriores permanecem no histórico das pessoas.

## Cenários de aceitação

### PRO-C01 — Criar, buscar e editar

- **Dado:** Nome exclusivo por execução.
- **Quando:** Salvar cadastro válido; buscar pelo nome; Editar; alterar descrição; Salvar cadastro.
- **Então:** Catálogo salvo.; registro correto com descrição persistida.

### PRO-C02 — Nome inválido

- **Dado:** Editor novo.
- **Quando:** Deixar nome vazio ou com um caractere.
- **Então:** Salvar cadastro desabilitado; não ocorre POST.

### PRO-C03 — Preservar vínculos históricos

- **Dado:** Pessoa vinculada ao catálogo criado pelo cenário.
- **Quando:** Inativar o catálogo; abrir Pessoas → Vínculos e formação → aba correspondente e incluir histórico.
- **Então:** Catálogo deixa de ser oferecido como referência ativa; vínculo anterior consultável com histórico.

## Limites e particularidades

- A tela do catálogo não oferece histórico de catálogos. Histórico de vínculos fica na pessoa.
- Hash semântico existe no domínio, mas não há busca vetorial de profissões/cursos na interface inicial.

## Fontes da implementação

- [frontend/src/app/qualificacoes/catalogos.html](../../frontend/src/app/qualificacoes/catalogos.html)
- [frontend/src/app/qualificacoes/catalogos.ts](../../frontend/src/app/qualificacoes/catalogos.ts)
- [backend/business/view_models/qualificacoes.py](../../backend/business/view_models/qualificacoes.py)
