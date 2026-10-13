# ATV — Atividades

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Manter a descrição canônica dos serviços que pessoas/instituições podem oferecer.

## Entrada e identificação

Atividades e unidades → Atividades

Raiz do componente/área: `app-capacidades`. Navegação interna sem troca de URL.

- Aba Atividades com aria-current=page.
- Editor #capacidade-codigo visível; .workspace com aria-busy=false.

## Pré-condições

- Sessão administrativa.
- Categoria ativa; unidade ativa se houver quantidade.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#capacidade-busca` | Busca por nome/código; atividades também por descrição e termos ativos. Enter equivale a Buscar. |
| `#capacidade-historico` | Inclui cadastros inativados na listagem. |
| `#capacidade-codigo` | Obrigatório e único, até 50 caracteres: primeiro alfanumérico, demais alfanuméricos, _ ou -. Somente leitura na edição. |
| `#capacidade-nome` | Obrigatório, 2–200 caracteres. |
| `#capacidade-descricao` | Descrição obrigatória, 2–4000 caracteres. |
| `#categoria-ref-id` | Categoria ativa obrigatória; seletor com busca #categoria-ref-busca. |
| `#unidade-ref-id` | Unidade ativa opcional; seletor com busca #unidade-ref-busca. Obrigatória no uso quantitativo em demandas/capacidade de oferta. |
| `#atividade-orientacoes` | Orientações opcionais, até 4000 caracteres. |
| `#atividade-restricoes` | Restrições descritivas opcionais, até 4000 caracteres. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### ATV-ABA — Atividades

- Localizador: `{"escopo": "nav[aria-label=\"Catálogos de capacidades\"]", "papel": "button", "nome": "Atividades", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ATV](./10-atividades.md).

Resultado:

- Seleciona a modalidade, volta à página 1, zera busca/histórico, fecha termos e limpa o editor.

### ATV-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ATV](./10-atividades.md).

Resultado:

- Recarrega a página corrente preservando filtros e editor.

### ATV-BUSCAR — Buscar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Buscar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ATV](./10-atividades.md).
- Campo associado: `#capacidade-busca`.

Resultado:

- Volta à página 1 e aplica filtro com dois caracteres ou mais; vazio/um caractere remove filtro.

### ATV-HISTORICO — Incluir cadastros inativados

- Localizador: `{"css": "#capacidade-historico"}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [ATV](./10-atividades.md).

Resultado:

- Alterna histórico e retorna à página 1; inativos têm identificação e não permitem edição direta.

### ATV-EDITAR — Editar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ATV](./10-atividades.md).

Resultado:

- Preenche Editar cadastro; código fica readonly.
- Foco em #capacidade-nome; referências e alertas de referência inativa aparecem quando aplicável.

### ATV-SALVAR — Salvar capacidade

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar capacidade", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ATV](./10-atividades.md).
- Persistência/rede: `POST /api/v1/atividades ou PUT /api/v1/atividades/{id}`.

Resultado:

- Cria ou atualiza; exibe Cadastro salvo.
- Limpa o editor e recarrega a lista com filtros atuais.

### ATV-CANCELAR — Cancelar

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Cancelar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ATV](./10-atividades.md).

Resultado:

- Descarta edição e volta ao formulário de novo cadastro, sem gravação.

### ATV-INATIVAR — Inativar

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ATV](./10-atividades.md).
- Persistência/rede: `DELETE /api/v1/atividades/{id}`.
- Diálogo nativo `confirm`: Inativar {nome}? As referências anteriores serão preservadas.
- Ao cancelar o diálogo: Nenhuma alteração.

Resultado:

- Aceitar inativa, exibe Cadastro inativado., limpa editor e recarrega; histórico mantém registro.

### ATV-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ATV](./10-atividades.md).

Resultado:

- Recua 50 registros; bloqueado na página 1.

### ATV-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [ATV](./10-atividades.md).

Resultado:

- Avança 50 registros; bloqueado se há menos de 50 na página.

### ATV-TERMOS — Termos e sinônimos

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Termos e sinônimos", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TRM](./11-termos-sinonimos.md).

Resultado:

- Abre app-termos com título Termos e sinônimos · {atividade}.
- Lista e editor de atividades saem da tela; navegação de catálogos continua visível.
- Para atividade inativada, abre em modo histórico.

## Cenários de aceitação

### ATV-C01 — Cadastrar e reencontrar

- **Dado:** Código/nome exclusivos e referências ativas.
- **Quando:** Preencher obrigatórios; Salvar capacidade; Buscar pelo nome.
- **Então:** Cadastro salvo.; cartão correto; ao editar código readonly.

### ATV-C02 — Duplicidade de código

- **Dado:** Já existe registro com o código de teste.
- **Quando:** Tentar novo cadastro com esse código.
- **Então:** API recusa; role=alert; não cria duplicata.

### ATV-C03 — Histórico

- **Dado:** Registro exclusivo do cenário.
- **Quando:** Inativar e aceitar; marcar histórico.
- **Então:** Cartão Inativado aparece sem Editar/Inativar.

## Limites e particularidades

- Salvar sem categoria, embora o botão possa estar habilitado, exibe Informe categoria e descrição da atividade. Textos/termos alterados atualizam hash e invalidam índices semânticos no servidor.
- Sem telas para requisitos obrigatórios de profissão/curso nesta etapa.

## Fontes da implementação

- [frontend/src/app/capacidades/catalogos.html](../../frontend/src/app/capacidades/catalogos.html)
- [frontend/src/app/capacidades/catalogos.ts](../../frontend/src/app/capacidades/catalogos.ts)
- [backend/business/servico/capacidades.py](../../backend/business/servico/capacidades.py)
