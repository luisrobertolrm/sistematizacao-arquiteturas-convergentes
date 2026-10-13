# UNI — Unidades de medida

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Padronizar unidades para capacidades e quantidades.

## Entrada e identificação

Atividades e unidades → Unidades de medida

Raiz do componente/área: `app-capacidades`. Navegação interna sem troca de URL.

- Aba Unidades de medida com aria-current=page.
- Editor #capacidade-codigo visível; .workspace com aria-busy=false.

## Pré-condições

- Sessão administrativa.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#capacidade-busca` | Busca por nome/código; atividades também por descrição e termos ativos. Enter equivale a Buscar. |
| `#capacidade-historico` | Inclui cadastros inativados na listagem. |
| `#capacidade-codigo` | Obrigatório e único, até 50 caracteres: primeiro alfanumérico, demais alfanuméricos, _ ou -. Somente leitura na edição. |
| `#capacidade-nome` | Obrigatório, 2–200 caracteres. |
| `#capacidade-simbolo` | Obrigatório, até 30 caracteres. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### UNI-ABA — Unidades de medida

- Localizador: `{"escopo": "nav[aria-label=\"Catálogos de capacidades\"]", "papel": "button", "nome": "Unidades de medida", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [UNI](./08-unidades-medida.md).

Resultado:

- Seleciona a modalidade, volta à página 1, zera busca/histórico, fecha termos e limpa o editor.

### UNI-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [UNI](./08-unidades-medida.md).

Resultado:

- Recarrega a página corrente preservando filtros e editor.

### UNI-BUSCAR — Buscar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Buscar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [UNI](./08-unidades-medida.md).
- Campo associado: `#capacidade-busca`.

Resultado:

- Volta à página 1 e aplica filtro com dois caracteres ou mais; vazio/um caractere remove filtro.

### UNI-HISTORICO — Incluir cadastros inativados

- Localizador: `{"css": "#capacidade-historico"}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [UNI](./08-unidades-medida.md).

Resultado:

- Alterna histórico e retorna à página 1; inativos têm identificação e não permitem edição direta.

### UNI-EDITAR — Editar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [UNI](./08-unidades-medida.md).

Resultado:

- Preenche Editar cadastro; código fica readonly.
- Foco em #capacidade-nome; referências e alertas de referência inativa aparecem quando aplicável.

### UNI-SALVAR — Salvar capacidade

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar capacidade", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [UNI](./08-unidades-medida.md).
- Persistência/rede: `POST /api/v1/unidades-medida ou PUT /api/v1/unidades-medida/{id}`.

Resultado:

- Cria ou atualiza; exibe Cadastro salvo.
- Limpa o editor e recarrega a lista com filtros atuais.

### UNI-CANCELAR — Cancelar

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Cancelar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [UNI](./08-unidades-medida.md).

Resultado:

- Descarta edição e volta ao formulário de novo cadastro, sem gravação.

### UNI-INATIVAR — Inativar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [UNI](./08-unidades-medida.md).
- Persistência/rede: `DELETE /api/v1/unidades-medida/{id}`.
- Diálogo nativo `confirm`: Inativar {nome}? As referências anteriores serão preservadas.
- Ao cancelar o diálogo: Nenhuma alteração.

Resultado:

- Aceitar inativa, exibe Cadastro inativado., limpa editor e recarrega; histórico mantém registro.

### UNI-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [UNI](./08-unidades-medida.md).

Resultado:

- Recua 50 registros; bloqueado na página 1.

### UNI-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [UNI](./08-unidades-medida.md).

Resultado:

- Avança 50 registros; bloqueado se há menos de 50 na página.

## Cenários de aceitação

### UNI-C01 — Cadastrar e reencontrar

- **Dado:** Código/nome exclusivos e referências ativas.
- **Quando:** Preencher obrigatórios; Salvar capacidade; Buscar pelo nome.
- **Então:** Cadastro salvo.; cartão correto; ao editar código readonly.

### UNI-C02 — Duplicidade de código

- **Dado:** Já existe registro com o código de teste.
- **Quando:** Tentar novo cadastro com esse código.
- **Então:** API recusa; role=alert; não cria duplicata.

### UNI-C03 — Histórico

- **Dado:** Registro exclusivo do cenário.
- **Quando:** Inativar e aceitar; marcar histórico.
- **Então:** Cartão Inativado aparece sem Editar/Inativar.

## Limites e particularidades

- Código da unidade é estável. Nome e símbolo permanecem editáveis no serviço atual; não presumir bloqueio desses textos por estarem em uso. A proteção da referência de unidade em atividades/tipos é uma regra distinta, descrita nas respectivas specs.
- Sem telas para requisitos obrigatórios de profissão/curso nesta etapa.

## Fontes da implementação

- [frontend/src/app/capacidades/catalogos.html](../../frontend/src/app/capacidades/catalogos.html)
- [frontend/src/app/capacidades/catalogos.ts](../../frontend/src/app/capacidades/catalogos.ts)
- [backend/business/servico/capacidades.py](../../backend/business/servico/capacidades.py)
