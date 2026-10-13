# NAV — Acesso, sessão e navegação

Referência: 2026-10-09. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.

## Intenção

Acessar funcionalidades administrativas por token e navegar entre módulos na aplicação integrada.

## Entrada e identificação

Abrir a URL base da aplicação integrada

Raiz do componente/área: `app-root`. Navegação interna sem troca de URL.

- Sem token: #token visível, sem menu administrativo.
- Com token: navegação principal disponível.

## Pré-condições

- Frontend em http://127.0.0.1:4200/ ou BASE_URL do harness.
- API acessível pelo proxy /api; PostgreSQL migrado.
- JWT administrativo fornecido ao harness por configuração, sem registrar seu valor.

## Campos e controles de entrada

| Seletor relativo à raiz | Regra / intenção |
|---|---|
| `#token` | Campo password; token não vazio. Não é login por usuário/senha. |

## Ações e resultados esperados

Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).

### NAV-ACESSAR — Acessar cadastros

- Localizador: `{"escopo": ".access", "papel": "button", "nome": "Acessar cadastros", "exato": true}`.
- Gesto: `click`.
- Condição: #token preenchido. Com campo vazio, botão desabilitado.
- Destino: [NAV](./00-acesso-navegacao.md).
- Persistência/rede: `GET /api/v1/instituicoes no acesso inicial.`.

Resultado:

- Guarda token somente em memória, limpa o campo e solicita a lista da aba cadastral corrente (Instituições no primeiro acesso).
- Com credencial válida, apresenta lista/editor e navegação; autenticação é confirmada pela resposta da API.

### NAV-ENTER — Enter no token

- Localizador: `{"css": "#token"}`.
- Gesto: `press Enter`.
- Condição: Controle visível e habilitado.
- Destino: [NAV](./00-acesso-navegacao.md).

Resultado:

- Executa a mesma operação de Acessar cadastros.

### NAV-SAIR — Sair

- Localizador: `{"escopo": ".header-actions", "papel": "button", "nome": "Sair", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [NAV](./00-acesso-navegacao.md).
- Persistência/rede: `Nenhuma requisição de logout.`.

Resultado:

- Limpa token, dados e mensagens; fecha menu e volta à tela de Acesso administrativo.
- Não faz logout remoto. Ao acessar novamente, a aba cadastral anterior pode ser mantida; selecionar Instituições para reiniciar cenário.

### NAV-MENU — Menu

- Localizador: `{"escopo": ".header-actions", "papel": "button", "nome": "Menu", "exato": true}`.
- Gesto: `click`.
- Condição: Sessão com token; botão disponível no layout móvel.
- Destino: [NAV](./00-acesso-navegacao.md).

Resultado:

- Em viewport até 760 px, alterna o menu e aria-expanded true/false.
- Seleção de módulo fecha o menu. Abre com clique, Enter ou Espaço quando focado.

### NAV-INS — Instituições

- Localizador: `{"escopo": "nav[aria-label=\"Navegação principal\"]", "papel": "button", "nome": "Instituições", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [INS](./01-instituicoes.md).

Resultado:

- Exibe o módulo e o título h1 correspondente.
- Em nova entrada no módulo, a aba inicial é Instituições.
- Marca o botão principal com aria-current=page; fecha o menu móvel; não altera URL.

### NAV-PES — Pessoas

- Localizador: `{"escopo": "nav[aria-label=\"Navegação principal\"]", "papel": "button", "nome": "Pessoas", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PES](./02-pessoas.md).

Resultado:

- Exibe o módulo e o título h1 correspondente.
- Em nova entrada no módulo, a aba inicial é Pessoas.
- Marca o botão principal com aria-current=page; fecha o menu móvel; não altera URL.

### NAV-PRO — Profissões e cursos

- Localizador: `{"escopo": "nav[aria-label=\"Navegação principal\"]", "papel": "button", "nome": "Profissões e cursos", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [PRO](./03-profissoes.md).

Resultado:

- Exibe o módulo e o título h1 correspondente.
- Em nova entrada no módulo, a aba inicial é Profissões.
- Marca o botão principal com aria-current=page; fecha o menu móvel; não altera URL.

### NAV-UNI — Atividades e unidades

- Localizador: `{"escopo": "nav[aria-label=\"Navegação principal\"]", "papel": "button", "nome": "Atividades e unidades", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [UNI](./08-unidades-medida.md).

Resultado:

- Exibe o módulo e o título h1 correspondente.
- Em nova entrada no módulo, a aba inicial é Unidades de medida.
- Marca o botão principal com aria-current=page; fecha o menu móvel; não altera URL.

### NAV-TIR — Recursos e ofertas

- Localizador: `{"escopo": "nav[aria-label=\"Navegação principal\"]", "papel": "button", "nome": "Recursos e ofertas", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [TIR](./12-tipos-recurso.md).

Resultado:

- Exibe o módulo e o título h1 correspondente.
- Em nova entrada no módulo, a aba inicial é Tipos de recurso.
- Marca o botão principal com aria-current=page; fecha o menu móvel; não altera URL.

### NAV-OCO — Desastres e áreas

- Localizador: `{"escopo": "nav[aria-label=\"Navegação principal\"]", "papel": "button", "nome": "Desastres e áreas", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [OCO](./17-ocorrencias-classificacoes.md).

Resultado:

- Exibe o módulo e o título h1 correspondente.
- Em nova entrada no módulo, a aba inicial é Ocorrências.
- Marca o botão principal com aria-current=page; fecha o menu móvel; não altera URL.

### NAV-DEM — Demandas e recomendações

- Localizador: `{"escopo": "nav[aria-label=\"Navegação principal\"]", "papel": "button", "nome": "Demandas e recomendações", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [DEM](./24-demandas-itens.md).

Resultado:

- Exibe o módulo e o título h1 correspondente.
- Em nova entrada no módulo, a aba inicial é Demandas.
- Marca o botão principal com aria-current=page; fecha o menu móvel; não altera URL.

### NAV-CON — Configuração de IA

- Localizador: `{"escopo": "nav[aria-label=\"Navegação principal\"]", "papel": "button", "nome": "Configuração de IA", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [CON](./20-conexoes-ia.md).

Resultado:

- Exibe o módulo e o título h1 correspondente.
- Em nova entrada no módulo, a aba inicial é Conexões de IA.
- Marca o botão principal com aria-current=page; fecha o menu móvel; não altera URL.

### NAV-MARCA — RedeSolidária, início

- Localizador: `{"escopo": ".topbar", "papel": "link", "nome": "RedeSolidária, início", "exato": true}`.
- Gesto: `click`.
- Condição: Controle visível e habilitado.
- Destino: [NAV](./00-acesso-navegacao.md).

Resultado:

- Link href=/ recarrega a aplicação na raiz da origem.
- A sessão em memória é perdida e o acesso administrativo volta a ser solicitado.

### NAV-PULAR — Ir para o conteúdo

- Localizador: `{"papel": "link", "nome": "Ir para o conteúdo", "exato": true}`.
- Gesto: `focus + click`.
- Condição: Controle visível e habilitado.
- Destino: [NAV](./00-acesso-navegacao.md).

Resultado:

- Move a navegação para #conteudo; pode acrescentar #conteudo à URL. Não seleciona módulo.

## Cenários de aceitação

### NAV-C01 — Entrada válida

- **Dado:** Token válido e API disponível.
- **Quando:** Preencher #token e Acessar cadastros.
- **Então:** Lista carrega com sucesso e menu aparece; não basta a mera presença do menu para considerar autenticação aprovada.

### NAV-C02 — Token inválido ou expirado

- **Dado:** Token inválido e API disponível.
- **Quando:** Acessar cadastros.
- **Então:** API retorna 401/403 e role=alert informa erro. Estado atual mantém token/menu; Sair permite trocar o token.

### NAV-C03 — Menu móvel e recarga

- **Dado:** Viewport 390 px e sessão válida.
- **Quando:** Focar Menu, pressionar Espaço; abrir Pessoas; recarregar navegador.
- **Então:** Menu abre, Pessoas fica ativa e menu recolhe; recarga perde sessão e solicita token novamente.

## Limites e particularidades

- A aplicação não utiliza rotas Angular nem URLs por funcionalidade. Não usar rotas hash do protótipo na porta 4300.
- Ao mudar de módulo, componentes são destruídos e rascunhos locais podem ser descartados sem confirmação.
- Menu principal/Sair são bloqueados pelo carregamento dos cadastros principais; outros módulos gerenciam seu próprio estado.
- Uma resposta de erro não remove automaticamente o token da sessão.

## Fontes da implementação

- [frontend/src/app/app.html](../../frontend/src/app/app.html)
- [frontend/src/app/app.ts](../../frontend/src/app/app.ts)
- [frontend/src/app/core/api.ts](../../frontend/src/app/core/api.ts)
