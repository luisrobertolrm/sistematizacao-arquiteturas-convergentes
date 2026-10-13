# Estado da implementação — até o incremento 6

Atualizado em 09/10/2026, aplicando a [skill dotnet-api-skill-cc](C:/Git/skills/dotnet-api-skill-cc/SKILL.md) com adaptação para Python e frontend Angular. O incremento 1 criou cadastros/infraestrutura, o 2 acrescentou qualificações/vínculos, o 3 implementou unidades, categorias, atividades e termos, o 4 acrescentou recursos/ofertas e o 5 implementou desastres e território. D009 mantém o escopo; D011–D017 detalham as implementações; o incremento 6 completa conexões/modelos, demandas, índices e recomendações.

**Visualização do projeto:** [prototipo/](../prototipo/README.md) contém Angular independente, com as 29 tabelas iniciais e 21 futuras em tela, mapa esquemático, demandas, sugestões simuladas e decisões. Futuras estão identificadas como rascunhos. Foram verificadas 16 regras/fluxos de domínio e cinco cenários de navegador, incluindo 50 listas, 39 formulários, 36 detalhes e seis telas complementares. [Evidências](../prototipo/verificacao/README.md) e [passagem para estilização](../prototipo/ESTILIZACAO.md). Não chama a API e não altera a contagem de tabelas implementadas no banco.

| Parte | Estado atual | Trabalho restante |
|---|---|---|
| Organização | `web → business → infra → core`; entidades sem ORM; IA em `business/graphs`. | Manter contratos tipados nas evoluções. |
| Configuração | Python >=3.13,<3.14, versões exatas, locks; `project.toml` como origem. | Atualizações deliberadas com verificações. |
| Banco/API | 29 tabelas iniciais, revisões 0001–0009; serviços e endpoints integrados. | 21 tabelas futuras fora do incremento. |
| HTTP | Envelope da skill, ProblemDetails, OpenAPI, CORS e validação. | Novos contratos conforme evolução. |
| Segurança/auditoria | JWT administrativo, auditoria por `sub`, decisão com data/justificativa, credenciais cifradas. | Login/usuários/perfis de produção e rotação completa de chaves. |
| IA | Conexões/modelos normalizados, embeddings, busca, LangGraph e recomendações persistidas. | Escolher/configurar provedor real, avaliar pertinência e indicador. |
| Angular | Todas as funcionalidades iniciais, incluindo mapa, configuração IA, índices, demandas e decisões. | Tema do protótipo aplicado; evolução geográfica futura. |

### Estilização da aplicação integrada

Em 09/10/2026, a pedido do usuário, o tema já desenvolvido no protótipo foi aplicado ao frontend integrado. Cabeçalho/marca, paleta azul, menu lateral agrupado, painéis, formulários, filtros, estados e decisões compartilham a identidade visual. Menu móvel recolhível, indicação de página ativa, foco visível e salto ao conteúdo foram acrescentados. A navegação continua usando os serviços e componentes funcionais; não há importação do cenário fictício do protótipo ou dependências novas.

### O que o incremento 6 acrescenta

- `0006_modelos_ia`: conexões e modelos, token cifrado/chave externa, seleção transacional por finalidade e identidade estável.
- `0007_demandas`: cabeçalho/itens atômicos, prioridade, datas, unidade exata, cancelamento e histórico de itens removidos.
- `0008_indices`: vetores por atividade/modelo, hash sem texto duplicado, invalidação transacional e publicação protegida contra origem alterada.
- `0009_recomendacoes`: análise, itens, pessoas/instituições/ofertas e recursos, com validação e decisão administrativa persistidas.
- Embeddings em arrays PostgreSQL com dimensão variável por modelo; cosseno exato até 5000 vetores. Ativação exige cobertura atual integral das atividades ativas.
- LangChain real com endpoint compatível e LangGraph recuperar → sugerir → validar; chamadas externas fora das transações. Mudanças no contexto impedem publicação/aprovação.
- Angular **Configuração de IA** e **Demandas e recomendações**; nova análise preserva anterior, sem alterar estoque ou pedido ao aprovar.

São **29 de 29 tabelas iniciais**, com 21 futuras mantidas fora do escopo. Contratos/limites em [D015–D017](decisoes-modelagem.md) e [IA, demandas e recomendações](ia-demandas-recomendacoes.md). Provedor real e qualidade não foram avaliados. Serviços indicam candidatos sem cobertura numérica presumida; agenda/reservas/requisitos avançados continuam futuros.

Os itens seguintes preservam o histórico de cada incremento; pendências descritas ali se referem àquela etapa.

### O que o incremento 5 acrescenta

- Tipos de desastre, ocorrências, classificações e áreas afetadas: **19 de 29 tabelas iniciais**, com API e migração 0005.
- Cadastro atômico com tipos distintos e exatamente um principal, com troca concorrente protegida, FKs e histórico das associações removidas.
- Início/encerramento com fuso, situação operacional e coordenadora; encerramento separado de inativação. Reabertura não implementada.
- Polígono GeoJSON tipado em JSONB, com limites de coordenadas/vértices e validação de borda, sem ORM no domínio ou dependência de PostGIS.
- Avaliação de gravidade/situação com data própria; correções de metadados/geometria preservam essa data. Confirmação explícita permite reavaliar valores iguais.
- Angular **Desastres e áreas → Ocorrências → Áreas e mapa**, com Leaflet 1.9.4/OpenStreetMap, desenho, consulta, edição, busca/paginação, avaliação e histórico.

Contrato e limites em [D014](decisoes-modelagem.md#d014--desastres-e-território-incremento-5). Mapa mostra as áreas da página; sem geocodificação, limite municipal, rotas, análise espacial ou trilha de avaliações. Tiles do teste são simulados; a disponibilidade do fundo externo não foi comprovada. Biblioteca/tipos têm versões exatas e lock atualizado; o protótipo independente permanece separado.

### O que o incremento 4 acrescenta

- Tipos de recurso, recursos, ofertas de atividades e seus vínculos com recursos, totalizando **15 de 29 tabelas iniciais**.
- Responsável exclusivo (pessoa ou instituição); quantidade Decimal, controle individual/estoque, localização e estado operacional.
- Ofertas únicas por atividade/ofertante/município; capacidade opcional na unidade da atividade e data de validação administrada pelo servidor.
- Vínculos com quantidade prevista, unicidade ativa e isolamento pela oferta da rota; preservação de histórico e encerramento de vínculos de oferta inativa.
- Proteção contra troca de unidade/modo já utilizados e contra alteração das referências principais, preservando o significado dos registros.
- Hash canônico v1 do tipo de recurso na origem, sem índice/embedding novo ou texto duplicado.
- Angular **Recursos e ofertas**, com três cadastros e recursos da oferta; seletores com busca/paginação, edição, inativação e histórico. Busca literal por nome também disponível para pessoas na API.

Quantidade prevista não reserva nem debita o total; pode superar estoque cadastrado. Vincular recurso de outro responsável não autoriza seu uso. Não somar capacidades institucionais/pessoais automaticamente. Regras, proteções entre tabelas e limites de auditoria estão em [D013](decisoes-modelagem.md#d013--recursos-e-ofertas-incremento-4).

### O que o incremento 3 acrescenta

- Quatro tabelas com auditoria, inativação, FKs, restrições e migração independente dos mapeamentos atuais.
- Códigos únicos e estáveis; unidade opcional na atividade, sem conversões/períodos implícitos. Referências inativas preservadas para consulta.
- Hash SHA-256 canônico v1 dos textos da atividade e termos ativos ordenados; descrição mantida na origem, sem `texto_busca` duplicado. Categoria/unidade são referências estruturadas excluídas da entrada semântica v1.
- Termos normalizados, únicos por atividade, escopo protegido pela rota e atualização do hash na mesma transação. Bloqueio da atividade impede perda de conteúdo em alterações concorrentes.
- CRUD administrativo, consulta de histórico e busca textual literal por código/nome/descrição/termos. Indexação vetorial e LLM permanecem pendentes.
- Interface Angular integrada, com três catálogos, referências paginadas e **Atividades → Termos e sinônimos**; segue o estilo existente.

SQL protege FKs/unicidades/formato; normalização, código imutável e manutenção do hash são regras do serviço. Outros escritores devem seguir esse contrato. PUT continua sem histórico imutável de todas as versões. Limites em [D012](decisoes-modelagem.md#d012--catálogo-de-atividades-e-unidades-incremento-3).

### O que o incremento 2 acrescenta

- Catálogos de profissões (CBO opcional) e cursos (técnico, capacitação ou treinamento), com hash canônico v1 calculado na origem, sem índices RAG adicionais.
- Participação em instituições com tipo, período e validação; bloqueio transacional e verificação de sobreposição, com teste de concorrência.
- Profissões individuais com registro/órgão/UF/validade; unicidade SQL com nulos equivalentes.
- Conclusões e renovações de cursos com emissor, datas, carga Decimal e referência textual de comprovante; unicidade por pessoa/curso/emissor/conclusão.
- Referências reais por FK e consultas administrativas de registros/parentes inativados, com isolamento por pessoa da rota. Nome exibido vem do catálogo relacionado.

Limites de D011: validação administrativa não garante aptidão ou agenda. SQL externo não deve contornar a regra de sobreposição dos períodos fechados implementada no serviço. Não há upload/download ou validação de comprovantes; somente referência textual. Renovações são preservadas como registros, enquanto PUT corretivo não mantém todas as versões anteriores dos campos.

No estado atual há operações administrativas de IA, indexação e geração persistida conforme D015–D017, sem provedor real escolhido. Mapa segue D014. Reserva, missão e entrega permanecem futuras.

## Verificação realizada

- **103 testes passaram com PostgreSQL 18.3 real**, em container/volume exclusivos removidos ao final. Incluem credenciais, seleção concorrente de modelos, dimensões distintas, cobertura, invalidação e corrida de indexação, demandas/itens, recomendações e contexto alterado, além dos cadastros anteriores.
- Alembic preservou dados criados nas revisões 0001, 0002 e 0003 ao aplicar até 0009; executou **check sem divergências → downgrade → upgrade**.
- **mypy estrito em 105 arquivos** e **Ruff** passaram.
- **Build e typecheck Angular** passaram: aproximadamente 570 kB, transferência estimada 131 kB, após aplicar o tema do protótipo.
- **17 cenários de interface integrada passaram**, com API/banco exclusivos, incluindo conexão/modelos, indexação/busca, demanda com atividade/recurso, LangGraph, aprovação e nova análise/rejeição com histórico. Capturas revistas em [frontend/verificacao](../frontend/verificacao/README.md).
- **21 verificações de layout passaram**, com viewports de 390 a 1920 px, sem rolagem horizontal ou controles fora da largura disponível. O menu móvel abriu pelo teclado e recolheu após navegar; [evidência](../frontend/verificacao/estilizacao.json).
- LangChain/LangGraph usaram provedor HTTP fictício local, vetores artificiais e respostas determinísticas. Não houve chamada a provedor de IA real. Tiles do mapa são simulados no teste; o componente Leaflet é real.

Esses testes verificam integração e regras, sem medir qualidade semântica, eficácia operacional ou indicador acadêmico. O banco de desenvolvimento não foi migrado/populado automaticamente. As quatro revisões novas e os comandos locais estão disponíveis para aplicação explícita.

## Executar e continuar

Seguir [backend/README.md](../backend/README.md) para ambiente, configuração local, PostgreSQL, migração, API, token e frontend. [frontend/README.md](../frontend/README.md) contém os comandos Angular. Para rever o negócio e as pendências, consultar o [controle de tarefas](controle-tarefas.md).

A próxima etapa é **configurar modelos reais, preparar a demonstração e medir pertinência/tempo**, além de definir autenticação de produção. O [pacote de simulação](../simulacoes/escopo_inicial/README.md) complementa D001–D009 e permanece separado da aplicação/testes PostgreSQL; não valida automaticamente os contratos novos.

Referências técnicas consultadas: [FastAPI — contratos de resposta](https://fastapi.tiangolo.com/tutorial/response-model/), [Angular — compatibilidade de versões](https://angular.dev/reference/versions) e [LangGraph — API de grafos](https://docs.langchain.com/oss/python/langgraph/graph-api).
