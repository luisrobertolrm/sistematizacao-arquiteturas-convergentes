# RedeSolidária — protótipo navegável

Projeto Angular independente para visualizar e discutir todas as telas. Os dados fictícios ficam em memória durante a sessão. Não precisa executar backend, PostgreSQL, autenticação ou provedor de IA.

**Abrir:** [http://127.0.0.1:4300](http://127.0.0.1:4300), com o servidor iniciado.

## Executar

Node 22.22.2 está indicado em `.node-version`. Dependências diretas têm versão exata; transitivas estão fixadas em `package-lock.json`.

```powershell
cd 'C:\Git\Sistematizacao Arquiteruras Convergentes\prototipo'
npm ci
npm start
```

Em outro computador, entrar na pasta copiada antes dos comandos npm. Acessar a porta 4300; encerrar com Ctrl+C no terminal.

## Cobertura

- Visão geral, acesso demonstrativo, inventário e histórico.
- Instituições, pessoas, profissões, cursos, vínculos e qualificações individuais.
- Atividades, termos, ofertas, tipos de recursos, unidades e recursos concretos.
- Ocorrências com tipo principal e associados; áreas com desenho e avaliação no mapa esquemático.
- Demandas e itens, sugestões simuladas, candidatos e decisão administrativa justificada.
- Conexões/modelos de IA, seleção por finalidade e simulação de preparação dos índices.
- **29 tabelas iniciais e 21 futuras**, estas identificadas como rascunhos em discussão.

Cadastros possuem lista, busca, inclusão, edição, inativação e consulta de inativados. Associações também aparecem no detalhe do cadastro principal. Recomendações e índices são gerados por ações próprias, sem edição direta. A classificação é editada no desastre; áreas são desenhadas no mapa.

URLs usam `#/tela/id`, com links diretos e voltar/avançar do navegador. [TELAS.md](TELAS.md) relaciona todas as rotas.

## Percurso para conhecer o projeto

1. Na **Visão geral**, conhecer Vale Azul e seu cenário fictício.
2. Abrir **Pessoas → João** e consultar vínculos, profissões e cursos. Adicionar ou editar uma associação.
3. Consultar **Atividades**, **Ofertas de atividades** e **Recursos** para distinguir serviço, ofertante e bem concreto.
4. Em **Mapa e avaliação de áreas**, selecionar uma área, alterar sua avaliação ou desenhar outra com ao menos três pontos; salvar.
5. Abrir a demanda da área ou criar outra. Adicionar item de atividade ou tipo de recurso, com quantidade e unidade compatível.
6. Usar **Gerar recomendação simulada**; conferir candidatos, pendências e compartilhamentos. Aprovar ou rejeitar com motivo.
7. Gerar outra análise; consultar **Histórico de decisões**. A decisão anterior permanece, sem reduzir quantidades nem criar operações.
8. Consultar **Modelos de IA** e **Índices semânticos**. Preparar o modelo alternativo de embedding antes de selecioná-lo; alterar uma atividade/termo para observar o índice pendente.

Recarregar ou **Reiniciar cenário** restaura os dados iniciais. **Exportar dados da sessão** baixa um JSON de consulta, sem importação implementada. O acesso demonstrativo apenas identifica o responsável pelos eventos, sem autenticação.

## Repassar à outra IA

Entregar esta pasta com `src/`, `scripts/`, documentação, configurações e lock. `node_modules/`, `dist/`, `.angular/` e `.teste/` são gerados e podem ser omitidos da cópia.

Ler [ESTILIZACAO.md](ESTILIZACAO.md), [CONTEXTO.md](CONTEXTO.md) e [TELAS.md](TELAS.md). O CSS mínimo está em `src/styles.css`; todas as telas usam os mesmos dados e ações.

## Verificar

```powershell
npm test
npm run typecheck
npm run build
# Com npm start em outro terminal; usa Edge/Chrome instalado:
node scripts/testar-navegacao.mjs
```

O teste de navegador utiliza perfil exclusivo e grava evidências em [verificacao/](verificacao/README.md). Se necessário, definir `PROTOTIPO_BROWSER` com o caminho do executável.

## Limites

Sugestões determinísticas usam IDs e filtros locais. Não executam LLM, busca vetorial ou embeddings. O mapa SVG não possui georreferenciamento, ruas ou rotas. Credenciais são indicadores fictícios; não informar tokens reais.

Telas futuras guardam rascunhos locais, sem controlar agenda, reservas, estoque ou entregas. Seus campos/enums continuam em discussão. O backend Python e o frontend integrado permanecem separados; estes modelos não são DTOs finais da API.
