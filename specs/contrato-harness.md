# Contrato de operação para o harness Playwright

## Contexto e sessão

Configure `BASE_URL` para a aplicação integrada; padrão `http://127.0.0.1:4200/`. A API é acessada pelo navegador em URLs relativas `/api/v1/...`; o proxy de desenvolvimento aponta para `127.0.0.1:8000`. Use uma sessão administrativa válida, obtida conforme [backend/README.md](../backend/README.md#acesso-e-interface) — o comando CLI de emissão está nesse documento. Não existe tela de login por usuário/senha na etapa atual.

Ao abrir/recarregar a aplicação, preencher `#token` e clicar **Acessar cadastros**. Token fica somente em memória; recarga, link da marca ou Sair encerram essa memória. A presença do menu sozinha não confirma credencial válida: aguardar a consulta inicial bem-sucedida. Não salvar token, senha, cabeçalhos Authorization ou cifras nos relatórios/evidências.

As specs não presumem que o backend esteja iniciado. Conexão autenticada ao PostgreSQL e migrations aplicadas são pré-condições diferentes de uma API HTTP disponível. Falha de infraestrutura deve ser registrada como tal.

## Estrutura do catálogo

`catalogo.json` tem versão documental `1.0.0`, lista `funcionalidades` e lista `componentes_compartilhados`. Cada entrada contém:

| Propriedade | Interpretação |
|---|---|
| `id` | ID estável da funcionalidade, usado em destinos e relatórios. |
| `arquivo` | Markdown correspondente em `funcionalidades/`. |
| `intencao` | Objetivo de negócio da interface. |
| `entrada.caminho` | Sequência legível de navegação; cartão/instância depende das fixtures. |
| `entrada.raiz` | Seletor CSS da raiz do contexto, não uma URL. |
| `entrada.prontidao` | Evidências de que o destino correto foi apresentado. |
| `campos` | Seletores e regras de entrada, incluindo campos dinâmicos. |
| `acoes` | Ações com ID, controle, gesto, localizador, condição, resultado, destino e eventual rede/diálogo. |
| `cenarios` | Dado/Quando/Então e ID estável para execução e evidências. |
| `observacoes` | Limites e diferenças relevantes da implementação atual. |
| `fontes` | Arquivos que fundamentam a spec. |

`resultado` e `cenarios` são critérios documentais em linguagem natural. `http` descreve uma observação complementar, não um comando para substituir o clique por chamada direta. O JSON não é código executável nem segue automaticamente o schema particular do seu harness.

## Localizadores e escopos

Prefira `getByRole` com nome exato para botões/links, `getByLabel` para campos com rótulo associado e IDs existentes para controles dinâmicos. Não há `data-testid` definido pelo pacote. Não usar classes de cor, posição global, `nth()` arbitrário ou nomes inventados como se fossem seletores existentes.

No objeto `localizador`:

- `escopo` é relativo a `entrada.raiz`; `:scope` significa a raiz já selecionada.
- `papel`, `nome` e `exato` correspondem a `getByRole(papel, { name: nome, exact: exato })` dentro do escopo.
- `css` localiza o elemento diretamente. `texto`, quando presente, refina seu texto, como nos `summary` de rastreabilidade.
- `$registro` é o cartão `.directory article.record` identificado pela entidade do cenário. Não é um seletor CSS literal.
- `$item` é o fieldset de um item da demanda identificado por sua legenda `Item N`.
- `#item-quantidade-{i}` e os demais IDs com `{i}` usam índice zero do formulário atual. Remover item reindexa os seguintes.
- `{prefixo}` precisa ser substituído pelo prefixo real da instância, listado nas specs de origem.
- O escopo descritivo `.editor .record identificado pelo tipo` exige selecionar a classificação pelo nome do tipo, antes de operar o radio Principal.
- `destino` igual ao ID corrente significa permanecer no contexto; `contexto de origem` retorna ao formulário que contém o componente; `externo` é link fora da aplicação.

Os quatro seletores compartilhados possuem contratos próprios no índice. Exemplos de prefixos: `categoria-ref`, `unidade-ref`, `recurso-ref`, `responsavel-ref`, `coordenadora-ref`, `classificacao-ref`, `oferta-recurso-ref`, `modelo-conexao`, `indice-modelo`, `indice-atividade`, `demanda-area`, `demanda-pessoa`, `item-necessidade-0`, `item-unidade-0`.

Uma lista e um seletor podem ter botões **Anterior**, **Próxima** e **Buscar** na mesma tela. Scopar a lista em `.directory` e o seletor pela instância que contém o select esperado. Sempre exigir que o localizador resolva um único controle quando a ação é singular.

## Esperas e resultados

Após navegar, conferir título/aba/contexto e término da consulta. Muitos módulos usam `.workspace[aria-busy]`; os cadastros principais usam `.directory[aria-busy]`. Seletores têm carregamento próprio, geralmente expresso pelo select e botões desabilitados, sem `aria-busy` próprio. `disabled` herdado de `fieldset` também conta como bloqueio real.

Para gravações, iniciar a espera de resposta **antes** do clique. Combinar método/caminho HTTP, resposta bem-sucedida, mensagem e alteração visível no registro certo. Uma mensagem de sucesso antiga não é prova de que a ação atual funcionou. Há módulos que conservam mensagens/resultados entre algumas operações.

Não depender de `waitForTimeout`, `networkidle` global ou da mudança de URL: tiles do mapa são externos e a aplicação usa navegação em memória. Usar as esperas e asserções retryable do Playwright. Para provar persistência, Atualizar e reencontrar o registro; quando necessário, comparar IDs e estado por uma consulta complementar autorizada do harness.

Listas e seletores usam páginas de 50; **Próxima** fica habilitada com exatamente 50, mesmo que não exista a 51ª entrada. Uma próxima página vazia é válida nesse caso. **Anterior** volta ao conjunto anterior. Busca com menos de dois caracteres geralmente é omitida da requisição, não um erro de validação.

`role="status"` informa carregamento/sucesso; `role="alert"` informa erro. O frontend usa `detail` do ProblemDetails quando string, mensagem específica para falha de conexão e fallback genérico. Não exigir que mensagens de validação Pydantic estejam escritas junto ao campo se a interface só as apresenta no alerta global.

## Diálogos nativos

Inativar e registrar decisão abrem `window.confirm`, com texto definido em cada ação. Instalar o handler de `dialog` antes do clique. Executar cenários de aceitar e cancelar separadamente. Sem handler, Playwright pode dispensar o diálogo e a ação não será efetivada.

```typescript
page.once('dialog', async dialog => {
  expect(dialog.type()).toBe('confirm');
  await dialog.accept(); // dismiss() para o cenário de cancelamento
});
await registro.getByRole('button', { name: 'Inativar', exact: true }).click();
```

Remover item, remover classificação e remover atividade do lote são mudanças locais, sem confirm. A gravação, quando aplicável, ocorre em ação posterior de salvar/indexar.

## Exemplo de cadastro e edição

Trecho para incorporar ao harness existente, usando `Page`/`expect` da instalação Playwright dele. `NOME` deve ser único por execução; token vem da configuração protegida do harness. O exemplo não instala dependências nem é uma suite automaticamente executada por este pacote.

```typescript
await page.goto(BASE_URL);
await page.locator('#token').fill(ADMIN_TOKEN);
const consulta = page.waitForResponse(r =>
  r.request().method() === 'GET' &&
  new URL(r.url()).pathname === '/api/v1/instituicoes');
await page.getByRole('button', { name: 'Acessar cadastros', exact: true }).click();
expect((await consulta).ok()).toBeTruthy();

const nav = page.getByRole('navigation', { name: 'Navegação principal', exact: true });
await nav.getByRole('button', { name: 'Instituições', exact: true }).click();
const tela = page.locator('app-root > main > .workspace');
await expect(tela.locator('.directory')).toHaveAttribute('aria-busy', 'false');
await tela.locator('#cadastro-nome').fill(NOME);
await tela.locator('#municipio').fill('3550308');
await tela.locator('#uf').fill('SP');

const gravacao = page.waitForResponse(r =>
  r.request().method() === 'POST' &&
  new URL(r.url()).pathname === '/api/v1/instituicoes');
await tela.getByRole('button', { name: 'Cadastrar', exact: true }).click();
expect((await gravacao).ok()).toBeTruthy();
await expect(page.getByRole('status').filter({ hasText: 'Cadastro salvo.' })).toBeVisible();

const registro = tela.locator('.directory article.record').filter({
  has: page.getByRole('heading', { name: NOME, exact: true })
});
await expect(registro).toHaveCount(1);
await registro.getByRole('button', { name: 'Editar', exact: true }).click();
await expect(tela.locator('#cadastro-nome')).toHaveValue(NOME);
```

Esse exemplo assume banco de teste com a instituição visível na página atual; cadastro principal não oferece busca. Para bases maiores, percorrer paginação ou usar uma fixture isolada, em vez de presumir que a gravação sempre retorna à primeira página.

## Exemplo de seletor e transição

```typescript
const capacidades = page.locator('app-capacidades');
const categoria = capacidades.locator('app-referencia-capacidade').filter({
  has: page.locator('#categoria-ref-id')
});
await categoria.locator('#categoria-ref-busca').fill(NOME_CATEGORIA);
await categoria.getByRole('button', { name: 'Buscar referência', exact: true }).click();
await expect(categoria.locator('#categoria-ref-id')).toBeEnabled();
await categoria.locator('#categoria-ref-id').selectOption({ label: NOME_CATEGORIA });

// Em um cartão de atividade já salvo:
await atividade.getByRole('button', { name: 'Termos e sinônimos', exact: true }).click();
const termos = page.locator('app-termos');
await expect(termos.getByRole('heading', { name: `Termos e sinônimos · ${NOME_ATIVIDADE}` })).toBeVisible();
await termos.getByRole('button', { name: 'Voltar às atividades', exact: true }).click();
await expect(page.locator('#capacidade-codigo')).toBeVisible();
```

## Exemplo de desenho real no mapa

```typescript
const mapa = page.locator('app-mapa-areas');
await mapa.getByRole('button', { name: 'Desenhar nova delimitação', exact: true }).click();
const superficie = mapa.getByRole('region', { name: 'Mapa para delimitar áreas afetadas', exact: true });
await superficie.scrollIntoViewIfNeeded();
const caixa = await superficie.boundingBox();
if (!caixa) throw new Error('Mapa sem superfície visível');
for (const [x, y] of [[0.25, 0.30], [0.70, 0.30], [0.70, 0.75]]) {
  await superficie.click({ position: { x: caixa.width * x, y: caixa.height * y } });
}
await mapa.getByRole('button', { name: 'Concluir delimitação', exact: true }).click();
await expect(mapa.getByRole('status').filter({ hasText: 'Delimitação pronta para salvar' })).toBeVisible();
// A persistência ainda exige Salvar área no formulário ARE.
```

O harness deve operar pela superfície e pelos controles reais. Não injetar a geometria nos signals Angular para declarar que o desenho funciona. O cenário de polígono inválido deve usar ordem cruzada e conferir a recusa ao salvar. Falha do fundo externo e falha do componente são resultados diferentes.

## Viewports e teclado

Executar ao menos desktop 1440×1100 e celular 390×844. Em largura até 760 px, abrir Menu antes de escolher módulo; verificar `aria-expanded` e fechamento após seleção. Exercitar Menu por teclado com Espaço/Enter, tabulação e foco visível. Campos readonly/desabilitados devem permanecer protegidos sem `force` no teste.

Em outras larguras, verificar ausência de rolagem horizontal da página e controles visíveis dentro da área disponível. Esses checks não substituem auditoria completa de acessibilidade. Mapas podem receber gestos próprios; evitar usar rolagem/arraste do mapa como se fossem botões de navegação.

## Evidência e classificação de execução

Para cada cenário executado, registrar em diretório próprio do harness:

- ID da spec/ação/cenário e versão/hash de `catalogo.json`.
- Origem/versão da aplicação, viewport, navegador, horário e `RUN_ID`.
- Pré-condições/IDs das entidades de teste, sem credenciais.
- Ação executada, estado antes/depois, resposta relevante sanitizada e mensagem observada.
- Screenshot de sucesso quando útil; screenshot/trace na falha. Mascarar campos de token.
- Resultado **aprovado**, **falhou**, **bloqueado por pré-condição/infraestrutura** ou **não executado**.

Não marcar como aprovado um cenário de IA que deixou de executar por falta de modelo/chave/provedor, nem inferir persistência apenas de uma mensagem anterior. Separar teste com provedor HTTP controlado de avaliação com modelo externo real.
