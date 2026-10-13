# Inventário das telas navegáveis

Todas as rotas abaixo são relativas a `http://127.0.0.1:4300`. A tela **Todas as telas e tabelas** contém os mesmos links. Um cadastro possui lista `#/tabela`, inclusão `#/tabela/novo`, detalhe `#/tabela/id` e edição `#/tabela/id?editar=1`, quando permitido.

As 50 tabelas possuem consulta própria. Associações também aparecem nos detalhes do cadastro principal, com referências e retorno ao contexto. Formulários das propostas futuras guardam somente rascunhos locais. Recomendações, componentes e índices não possuem CRUD manual.

## Telas complementares

| Tela | Rota | Ações |
|---|---|---|
| Visão geral | `#/inicio` | Contadores e percurso do cenário |
| Inventário | `#/projeto` | Acesso às 50 tabelas |
| Acesso demonstrativo | `#/acesso` | Identificar responsável da sessão |
| Mapa e avaliação | `#/mapa` | Selecionar ocorrência/área, desenhar, desfazer, redesenhar, salvar avaliação e abrir/criar demanda |
| Índices semânticos | `#/indices` | Selecionar catálogo/modelo e simular preparo; ver hashes/estado |
| Histórico de decisões | `#/historico` | Abrir análises anteriores e contexto dos eventos |

O cabeçalho oferece exportação JSON e reinício do cenário. A navegação por hash suporta links diretos e voltar/avançar do navegador.

## 29 tabelas do escopo inicial

| Tabela | Tela | Rota | Funcionamento |
|---|---|---|---|
| `instituicoes` | Instituições | `#/instituicoes` | Listar, cadastrar, editar e inativar |
| `pessoas` | Pessoas | `#/pessoas` | Listar, cadastrar, editar e inativar |
| `pessoa_instituicao` | Vínculos institucionais | `#/pessoa_instituicao` | Listar, cadastrar, editar e inativar |
| `profissoes` | Profissões | `#/profissoes` | Listar, cadastrar, editar e inativar |
| `pessoa_profissao` | Profissões das pessoas | `#/pessoa_profissao` | Listar, cadastrar, editar e inativar |
| `cursos` | Cursos | `#/cursos` | Listar, cadastrar, editar e inativar |
| `pessoa_curso` | Formações e renovações | `#/pessoa_curso` | Listar, cadastrar, editar e inativar |
| `unidades_medida` | Unidades de medida | `#/unidades_medida` | Listar, cadastrar, editar e inativar |
| `categorias_atividade` | Categorias de atividade | `#/categorias_atividade` | Listar, cadastrar, editar e inativar |
| `atividades` | Atividades | `#/atividades` | Listar, cadastrar, editar e inativar |
| `atividade_termos` | Termos de atividade | `#/atividade_termos` | Listar, cadastrar, editar e inativar |
| `ofertas_atividade` | Ofertas de atividades | `#/ofertas_atividade` | Listar, cadastrar, editar e inativar |
| `oferta_atividade_recurso` | Recursos de ofertas | `#/oferta_atividade_recurso` | Listar, cadastrar, editar e inativar |
| `tipos_recurso` | Tipos de recurso | `#/tipos_recurso` | Listar, cadastrar, editar e inativar |
| `recursos` | Recursos | `#/recursos` | Listar, cadastrar, editar e inativar |
| `tipos_desastre` | Tipos de desastre | `#/tipos_desastre` | Listar, cadastrar, editar e inativar |
| `desastres` | Desastres | `#/desastres` | Listar, cadastrar, editar e inativar |
| `desastre_tipo` | Classificações da ocorrência | `#/desastre_tipo` | Consultar; alterar tipos no formulário do desastre |
| `areas_afetadas` | Áreas afetadas | `#/areas_afetadas` | Desenhar/avaliar em `#/mapa`; consultar e editar dados |
| `demandas` | Demandas | `#/demandas` | Listar, cadastrar, editar e inativar |
| `demanda_itens` | Itens de demanda | `#/demanda_itens` | Listar, cadastrar, editar e inativar |
| `conexao_ia` | Conexões de IA | `#/conexao_ia` | Listar, cadastrar, editar e inativar |
| `modelo_ia` | Modelos de IA | `#/modelo_ia` | Listar, cadastrar, editar e inativar |
| `atividade_indice_semantico` | Índices de atividades | `#/atividade_indice_semantico` | Consultar; preparar em `#/indices` |
| `recomendacoes` | Recomendações | `#/recomendacoes` | Gerar na demanda; analisar/decidir/nova análise |
| `recomendacao_itens` | Itens da recomendação | `#/recomendacao_itens` | Consultar componentes gerados na análise |
| `recomendacao_pessoas` | Pessoas sugeridas | `#/recomendacao_pessoas` | Consultar componentes gerados na análise |
| `recomendacao_instituicoes` | Instituições sugeridas | `#/recomendacao_instituicoes` | Consultar componentes gerados na análise |
| `recomendacao_recursos` | Recursos sugeridos | `#/recomendacao_recursos` | Consultar componentes gerados na análise |

## 21 tabelas de evolução — rascunhos em discussão

| Tabela | Tela | Rota | Funcionamento |
|---|---|---|---|
| `profissao_indice_semantico` | Índices de profissões | `#/profissao_indice_semantico` | Consultar; preparar em `#/indices` |
| `curso_indice_semantico` | Índices de cursos | `#/curso_indice_semantico` | Consultar; preparar em `#/indices` |
| `tipo_recurso_indice_semantico` | Índices de tipos de recurso | `#/tipo_recurso_indice_semantico` | Consultar; preparar em `#/indices` |
| `atividade_requisito_profissao` | Profissões exigidas por atividade | `#/atividade_requisito_profissao` | Listar, cadastrar, editar e inativar rascunho |
| `atividade_requisito_curso` | Cursos exigidos por atividade | `#/atividade_requisito_curso` | Listar, cadastrar, editar e inativar rascunho |
| `demanda_item_requisito_profissao` | Profissões exigidas no pedido | `#/demanda_item_requisito_profissao` | Listar, cadastrar, editar e inativar rascunho |
| `demanda_item_requisito_curso` | Cursos exigidos no pedido | `#/demanda_item_requisito_curso` | Listar, cadastrar, editar e inativar rascunho |
| `caracteristicas_recurso` | Características técnicas | `#/caracteristicas_recurso` | Listar, cadastrar, editar e inativar rascunho |
| `tipo_recurso_caracteristica` | Características por tipo | `#/tipo_recurso_caracteristica` | Listar, cadastrar, editar e inativar rascunho |
| `recurso_caracteristica` | Valores técnicos dos recursos | `#/recurso_caracteristica` | Listar, cadastrar, editar e inativar rascunho |
| `demanda_item_requisito_recurso` | Características exigidas no pedido | `#/demanda_item_requisito_recurso` | Listar, cadastrar, editar e inativar rascunho |
| `oferta_atividade_pessoa` | Composição das ofertas | `#/oferta_atividade_pessoa` | Listar, cadastrar, editar e inativar rascunho |
| `disponibilidades_pessoa` | Disponibilidade de pessoas | `#/disponibilidades_pessoa` | Listar, cadastrar, editar e inativar rascunho |
| `disponibilidades_oferta` | Disponibilidade de ofertas | `#/disponibilidades_oferta` | Listar, cadastrar, editar e inativar rascunho |
| `missoes` | Missões | `#/missoes` | Listar, cadastrar, editar e inativar rascunho |
| `missao_itens` | Itens de missão | `#/missao_itens` | Listar, cadastrar, editar e inativar rascunho |
| `alocacoes_pessoa` | Alocações de pessoas | `#/alocacoes_pessoa` | Listar, cadastrar, editar e inativar rascunho |
| `reservas_recurso` | Reservas de recursos | `#/reservas_recurso` | Listar, cadastrar, editar e inativar rascunho |
| `atendimentos` | Atendimentos | `#/atendimentos` | Listar, cadastrar, editar e inativar rascunho |
| `atendimento_itens` | Itens atendidos | `#/atendimento_itens` | Listar, cadastrar, editar e inativar rascunho |
| `movimentacoes_recurso` | Movimentações de estoque | `#/movimentacoes_recurso` | Listar, cadastrar, editar e inativar rascunho |

## Associações nos cadastros principais

| Detalhe | Seções relacionadas |
|---|---|
| Instituições (`instituicoes`) | Pessoas vinculadas (`pessoa_instituicao`); Ofertas institucionais (`ofertas_atividade`); Recursos sob responsabilidade (`recursos`) |
| Pessoas (`pessoas`) | Instituições (`pessoa_instituicao`); Profissões (`pessoa_profissao`); Cursos e renovações (`pessoa_curso`); Ofertas pessoais (`ofertas_atividade`); Recursos sob responsabilidade (`recursos`) |
| Profissões (`profissoes`) | Qualificações individuais (`pessoa_profissao`) |
| Cursos (`cursos`) | Formações individuais (`pessoa_curso`) |
| Atividades (`atividades`) | Termos e sinônimos (`atividade_termos`); Quem oferece (`ofertas_atividade`); Índices por modelo (`atividade_indice_semantico`) |
| Ofertas de atividades (`ofertas_atividade`) | Recursos previstos (`oferta_atividade_recurso`) |
| Desastres (`desastres`) | Classificações (`desastre_tipo`); Áreas afetadas (`areas_afetadas`) |
| Áreas afetadas (`areas_afetadas`) | Demandas da área (`demandas`) |
| Demandas (`demandas`) | Itens solicitados (`demanda_itens`); Análises e decisões (`recomendacoes`) |
| Conexões de IA (`conexao_ia`) | Modelos da conexão (`modelo_ia`) |
| Modelos de IA (`modelo_ia`) | Índices de atividades (`atividade_indice_semantico`) |
| Recomendações (`recomendacoes`) | Itens sugeridos (`recomendacao_itens`) |
| Missões (`missoes`) | Itens (`missao_itens`); Pessoas (`alocacoes_pessoa`); Recursos (`reservas_recurso`) |
| Atendimentos (`atendimentos`) | Itens registrados (`atendimento_itens`) |

Todos os campos, referências e opções estão em `src/app/dominio/telas.ts`. Para revisar uma proposta futura, editar seus metadados e o cenário mantendo o contrato tipado; a apresentação acompanha o formulário genérico. Usuários/perfis reais ainda não têm tabelas definidas neste inventário; o acesso demonstrativo não representa um sistema de autenticação implementado.
