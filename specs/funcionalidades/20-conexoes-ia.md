# CON — Conexões de IA

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Cadastrar o endpoint compatível e a credencial protegida compartilhada pelos modelos.

## Entrada e identificação

Configuração de IA → Conexões de IA

Raiz do componente/área: `app-ia-configuracao`. Navegação interna sem troca de URL.

- Aba Conexões de IA com aria-current=page.
- #ia-nome visível e .workspace com aria-busy=false.

## Pré-condições

- Sessão administrativa.
- Chave Fernet válida no backend para conexões bearer.
- Endpoint precisa constar na allowlist do backend para chamadas posteriores, não para mera intenção do cadastro.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#ia-busca` | Busca cadastro com mínimo de dois caracteres. |
| `#ia-nome` | Obrigatório, 2–200 caracteres. |
| `#ia-url` | Obrigatório; URL HTTP(S) sem credenciais/query/fragmento, até 2000 caracteres; HTTP só em loopback. |
| `#ia-auth` | bearer (padrão) ou nenhuma. |
| `#ia-token` | Campo password somente em bearer. Obrigatório no novo cadastro bearer; vazio na edição preserva credencial. Máximo 8192 caracteres. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### CON-ATUALIZAR — Atualizar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Atualizar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [CON](./20-conexoes-ia.md).

Resultado:

- Atualiza a página corrente sem limpar o editor.

### CON-BUSCAR — Buscar

- Localizador: `{"escopo": ".directory", "papel": "button", "nome": "Buscar", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [CON](./20-conexoes-ia.md).

Resultado:

- Volta à página 1; envia busca somente com dois caracteres ou mais; usar botão, sem Enter vinculado.

### CON-HISTORICO — Incluir inativados

- Localizador: `{"escopo": ".directory", "papel": "checkbox", "nome": "Incluir inativados", "exato": true}`.
- Gesto: `check/uncheck`.
- Condição: Controle visível e habilitado.
- Destino: [CON](./20-conexoes-ia.md).

Resultado:

- Alterna histórico e retorna à página 1; não reativa cadastros.

### CON-ANTERIOR — Anterior

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Anterior", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [CON](./20-conexoes-ia.md).

Resultado:

- Recua 50 registros; bloqueado na página 1.

### CON-PROXIMA — Próxima

- Localizador: `{"escopo": ".directory .pagination", "papel": "button", "nome": "Próxima", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [CON](./20-conexoes-ia.md).

Resultado:

- Avança 50 registros; bloqueado quando há menos de 50.

### CON-LIMPAR — Limpar formulário

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Limpar formulário", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [CON](./20-conexoes-ia.md).

Resultado:

- Descarta a edição/rascunho e restaura padrões do formulário.

### CON-ABA — Conexões de IA

- Localizador: `{"escopo": "nav[aria-label=\"Configuração de IA\"]", "papel": "button", "nome": "Conexões de IA", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [CON](./20-conexoes-ia.md).

Resultado:

- Abre aba, zera busca/histórico/página e limpa formulários de cadastro.

### CON-AUTH — Autenticação

- Localizador: `{"css": "#ia-auth"}`.
- Gesto: `selectOption`.
- Condição: Controle visível e habilitado.
- Destino: [CON](./20-conexoes-ia.md).

Resultado:

- Bearer exibe campo de token; Nenhuma oculta-o e envia token nulo ao salvar.

### CON-EDITAR — Editar conexão

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Editar conexão", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [CON](./20-conexoes-ia.md).

Resultado:

- Preenche nome/URL/autenticação; nunca recupera token para o campo.
- Mostra Editar conexão e Novo token (vazio preserva o atual).

### CON-SALVAR — Salvar conexão

- Localizador: `{"escopo": ".editor", "papel": "button", "nome": "Salvar conexão", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [CON](./20-conexoes-ia.md).
- Persistência/rede: `POST /api/v1/conexoes-ia ou PUT .../{id}`.

Resultado:

- Cria/atualiza, exibe Conexão salva., limpa editor e reconsulta.
- Resposta/cartão mostram apenas presença de credencial; não exibem token nem cifra.

### CON-INATIVAR — Inativar conexão

- Localizador: `{"escopo": "$registro", "papel": "button", "nome": "Inativar conexão", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [CON](./20-conexoes-ia.md).
- Persistência/rede: `DELETE /api/v1/conexoes-ia/{id}`.
- Diálogo nativo `confirm`: Inativar este cadastro?
- Ao cancelar o diálogo: Sem alteração.

Resultado:

- Aceitar inativa, exibe Cadastro inativado. e reconsulta. Conexão com modelo selecionado é recusada pela API.

## Cenários de aceitação

### CON-C01 — Conexão sem autenticação

- **Dado:** Endpoint de teste local ou endpoint autorizado definido nas fixtures.
- **Quando:** Selecionar nenhuma; informar nome/URL; Salvar conexão.
- **Então:** Conexão salva.; cartão Sem autenticação. Cadastro não comprova conectividade com provedor.

### CON-C02 — Credencial protegida

- **Dado:** Chave Fernet do ambiente e token de teste obtido pelo harness.
- **Quando:** Criar bearer com token; editar sem preencher token; salvar.
- **Então:** Credencial protegida cadastrada.; campo token vazio na edição; credencial preservada no backend, ausente da resposta.

### CON-C03 — Conexão utilizada

- **Dado:** Modelo já referencia esta conexão.
- **Quando:** Editar conexão e tentar trocar URL/autenticação.
- **Então:** API retorna 409; role=alert. Renomear ou substituir token, sem mudar identidade, continua permitido.

### CON-C04 — Bearer incompleto

- **Dado:** Editor novo, nome/URL válidos.
- **Quando:** Salvar bearer sem token.
- **Então:** API recusa credencial ausente. O botão pode estar habilitado, pois token obrigatório não está validado pelo FormControl.

## Limites e particularidades

- Não há botão Testar conexão.
- Adaptador enviado é openai_compativel; não há seletor de fornecedor.
- Inativar conexão não é a mesma coisa que desselecionar um modelo.
- Credenciais são dados de ambiente do harness; não gravar valores em artefatos.

## Fontes da implementação

- [frontend/src/app/ia/configuracao.html](../../frontend/src/app/ia/configuracao.html)
- [frontend/src/app/ia/configuracao.ts](../../frontend/src/app/ia/configuracao.ts)
- [backend/business/servico/modelos_ia.py](../../backend/business/servico/modelos_ia.py)
