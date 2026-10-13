# Controle de tarefas e finalidade das tabelas

Atualizado em 09/10/2026. Referências: [escopo inicial](escopo-inicial.md), [modelo de entidades](modelo-entidades.md), [modelo operacional](modelo-operacional-proposto.md), decisões D001–D017 e [estado da implementação](implementacao-inicial.md).

O negócio pensado é manter uma rede de capacidades: uma instituição reúne pessoas e bens; pessoas possuem qualificações; uma atividade descreve um serviço e a oferta identifica quem o fornece. Um desastre atinge áreas; cada área registra demandas. A IA consulta capacidades e sugere candidatos, e o administrador avalia a sugestão. Execução e entrega são uma evolução posterior.

**Estados:** Concluída = artefato disponível; Em andamento = parte implementada, ainda com trabalho restante; Pendente = trabalho da primeira entrega; Em discussão = proposta futura ainda sem contrato final; Adiada = modelagem registrada, implementação posterior. Documentação e simulação não significam aplicação implementada. Os IDs abaixo são apenas referências de acompanhamento.

## Tarefas gerais

| ID | Tarefa | Etapa | Estado |
|---|---|---|---|
| TG01 | Registrar escopo, decisões e finalidade de cada tabela. | Planejamento | Concluída |
| TG02 | Atualizar e executar simulação em memória; guardar código, contexto e resultados para outra IA. | Planejamento | Concluída |
| TG03 | Campos, estados e integridade das recomendações/decisões definidos e implementados em D017. | Inicial | Concluída |
| TG04 | FastAPI, SQLAlchemy/psycopg, mypy/Ruff e versões fixas definidos; provedor/modelos reais pendentes. | Inicial | Em andamento |
| TG05 | Compatibilidade de `project.toml`, quatro camadas e configuração Alembic criadas. | Inicial | Concluída |
| TG06 | Todas as 29 tabelas iniciais migradas e testadas, revisões 0001–0009. | Inicial | Concluída |
| TG07 | JWT, auditoria por sujeito e decisão administrativa implementados; login/usuários/perfis de produção pendentes. | Inicial | Em andamento |
| TG08 | Serviços/API de todos os cadastros iniciais, demandas/itens, índices e recomendações/decisões implementados. | Inicial | Concluída |
| TG09 | Leaflet/OSM e Polygon GeoJSON definidos para o mapa inicial; delimitação, validação local e avaliação administrativa implementadas. Limites geográficos em D014. | Inicial | Concluída |
| TG10 | LangChain/LangGraph, recuperação e persistência integrados/testados com HTTP fictício; configuração e avaliação de provedor real pendentes. | Inicial | Em andamento |
| TG11 | Angular integrado para todo o escopo inicial, incluindo conexões/modelos, índices, demandas e recomendações. Protótipo independente em TG15. | Inicial | Concluída |
| TG12 | Fluxo fictício integrado verificado; preparar demonstração acadêmica e medir tempo/pertinência das sugestões. | Inicial | Em andamento |
| TG13 | Caracterizar problema/localidade, informar integrantes e preparar pitch de até cinco minutos. | Entrega acadêmica | Pendente |
| TG14 | Discutir e detalhar tabelas operacionais futuras antes de implementá-las. | Futuro | Em discussão |
| TG15 | Criar protótipo Angular independente das 50 tabelas e telas complementares, com navegação, ações locais, cenário e passagem para outra IA estilizar; domínio e navegador verificados. | Visualização | Concluída |

Aplicação integrada estilizada com o visual do protótipo: tema claro azul, menu lateral, formulários, mensagens e recomendações responsivos. Implementação em `frontend/`; referência independente em `prototipo/`. Evidências em [verificação de interface](../frontend/verificacao/README.md).

## Tarefas por tabela

Há **29 tabelas na primeira entrega** e **21 previstas para evolução**, totalizando **50** no inventário atual. Cada linha representa a tarefa de detalhar/implementar a tabela na etapa indicada. Usuários/perfis e outros assuntos sem nome de tabela definido não estão incluídos nessa contagem.

| ID | Tabela | Etapa | Por que existe / negócio pensado | Estado |
|---|---|---|---|---|
| TB01 | `instituicoes` | Inicial | Identificar organizações da rede, contatos e responsabilidade institucional pela coordenação ou oferta de capacidades. | Concluída |
| TB02 | `pessoas` | Inicial | Identificar voluntários e solicitantes, sem confundir pessoa cadastrada com usuário autenticado. | Concluída |
| TB03 | `pessoa_instituicao` | Inicial | Registrar participação e histórico de vínculo; uma pessoa pode integrar várias instituições, sem duplicar seu cadastro. | Concluída |
| TB04 | `profissoes` | Inicial | Padronizar profissões para consulta e relacionamentos, evitando nomes livres diferentes para o mesmo conceito. | Concluída |
| TB05 | `pessoa_profissao` | Inicial | Registrar qualificação individual, registro profissional, validade e validação; profissão do catálogo não prova habilitação da pessoa. | Concluída |
| TB06 | `cursos` | Inicial | Catalogar cursos técnicos, treinamentos e capacitações independentemente de quem os concluiu. | Concluída |
| TB07 | `pessoa_curso` | Inicial | Registrar conclusão, emissor, referência de comprovante, validade e renovações de cada formação individual; envio/consulta de arquivos permanece pendente. | Concluída |
| TB08 | `unidades_medida` | Inicial | Compartilhar unidades entre pedidos, recursos e capacidades; cadastro implementado, sem conversões ou período implícitos. | Concluída |
| TB09 | `categorias_atividade` | Inicial | Organizar serviços por grupos como logística e alimentação para navegação e filtros. | Concluída |
| TB10 | `atividades` | Inicial | Descrever o que pode ser feito, com conteúdo e hash canônico na origem; não repetir a atividade para cada ofertante. Indexação vetorial em TB24. | Concluída |
| TB11 | `atividade_termos` | Inicial | Associar sinônimos/termos normalizados em linhas próprias e atualizar o hash da atividade na mesma transação. | Concluída |
| TB12 | `ofertas_atividade` | Inicial | Dizer quem oferece uma atividade, onde e em quais condições; separar serviço do catálogo e capacidade declarada do ofertante. | Concluída |
| TB13 | `oferta_atividade_recurso` | Inicial | Indicar bens previstos para uma oferta, sem presumir propriedade, autorização de uso ou reserva automática. | Concluída |
| TB14 | `tipos_recurso` | Inicial | Classificar bens/insumos, definir unidade e controle individual/estoque, permitindo localizar a classe antes do recurso concreto. | Concluída |
| TB15 | `recursos` | Inicial | Cadastrar cada bem ou lote com responsável exclusivo, localização, quantidade e condição operacional. | Concluída |
| TB16 | `tipos_desastre` | Inicial | Manter catálogo de fenômenos, separado das ocorrências e de suas operações. | Concluída |
| TB17 | `desastres` | Inicial | Reunir coordenação, período e situação de uma ocorrência concreta, preservando seu histórico. | Concluída |
| TB18 | `desastre_tipo` | Inicial | Associar vários fenômenos à mesma ocorrência e indicar exatamente um principal, sem duplicar o desastre. | Concluída |
| TB19 | `areas_afetadas` | Inicial | Delimitar impactos no mapa por ocorrência e município, com gravidade, situação e última avaliação administrativa. | Concluída |
| TB20 | `demandas` | Inicial | Registrar pedido de uma área, solicitante, prioridade e prazo, separando urgência do pedido e gravidade territorial. | Concluída |
| TB21 | `demanda_itens` | Inicial | Detalhar cada necessidade mensurável de atividade ou tipo de recurso; uma demanda pode combinar vários itens. | Concluída |
| TB22 | `conexao_ia` | Inicial | Centralizar provedor, endpoint e credencial protegida para vários modelos, mantendo a chave de criptografia fora do banco. | Concluída |
| TB23 | `modelo_ia` | Inicial | Identificar finalidade, revisão, dimensão e seleção ativa dos modelos; separar inferência de texto e embeddings. | Concluída |
| TB24 | `atividade_indice_semantico` | Inicial | Guardar vetor e hash de origem por atividade/modelo; detectar conteúdo desatualizado sem duplicar a descrição da atividade. | Concluída |
| TB25 | `recomendacoes` | Inicial | Registrar análise da demanda, modelos usados, justificativa e situação administrativa; nova análise preserva a anterior. | Concluída |
| TB26 | `recomendacao_itens` | Inicial | Relacionar cada parte da sugestão ao item solicitado, permitindo explicar cobertura sugerida e lacunas por necessidade. | Concluída |
| TB27 | `recomendacao_pessoas` | Inicial | Identificar pessoas concretas sugeridas e seu papel, preservando FKs em vez de nomes inventados em texto livre. | Concluída |
| TB28 | `recomendacao_instituicoes` | Inicial | Identificar instituições sugeridas e a oferta que fundamenta a indicação, sem confundir vínculo de voluntário com oferta institucional. | Concluída |
| TB29 | `recomendacao_recursos` | Inicial | Identificar bens/lotes e quantidades sugeridas; sugestão não constitui reserva nem entrega. | Concluída |
| TB30 | `atividade_requisito_profissao` | Futuro | Definir profissões exigidas para um serviço, permitindo verificação estruturada além da similaridade textual. | Em discussão |
| TB31 | `atividade_requisito_curso` | Futuro | Definir formações exigidas para o serviço; regras de alternativas e combinações ainda precisam ser fechadas. | Em discussão |
| TB32 | `demanda_item_requisito_profissao` | Futuro | Acrescentar exigências profissionais do atendimento concreto sem enfraquecer requisitos gerais da atividade. | Em discussão |
| TB33 | `demanda_item_requisito_curso` | Futuro | Acrescentar capacitações exigidas pelo contexto do item solicitado. | Em discussão |
| TB34 | `caracteristicas_recurso` | Futuro | Catalogar propriedades técnicas tipadas e unidades, como potência, capacidade de carga ou refrigeração. | Em discussão |
| TB35 | `tipo_recurso_caracteristica` | Futuro | Definir quais características se aplicam a cada classe de recurso e quais são obrigatórias. | Em discussão |
| TB36 | `recurso_caracteristica` | Futuro | Informar valores técnicos de um bem concreto, permitindo comparar o gerador disponível e a potência necessária. | Em discussão |
| TB37 | `demanda_item_requisito_recurso` | Futuro | Expressar limites e comparações técnicas do pedido, evitando aceitar qualquer bem apenas por ter o mesmo tipo. | Em discussão |
| TB38 | `oferta_atividade_pessoa` | Futuro | Identificar pessoas que compõem uma oferta institucional e detectar capacidade compartilhada com ofertas pessoais. | Em discussão |
| TB39 | `disponibilidades_pessoa` | Futuro | Declarar janelas de disponibilidade; qualificação e vínculo não garantem presença em determinado horário. | Em discussão |
| TB40 | `disponibilidades_oferta` | Futuro | Declarar capacidade da oferta por período; capacidade geral não garante atendimento em qualquer janela. | Em discussão |
| TB41 | `missoes` | Futuro | Organizar uma operação autorizada com responsáveis, período e situação de execução. | Em discussão |
| TB42 | `missao_itens` | Futuro | Relacionar o planejamento da missão aos itens de demanda; um item pode ser atendido por várias missões. | Em discussão |
| TB43 | `alocacoes_pessoa` | Futuro | Registrar compromisso de participação por período e impedir sobreposição incompatível entre operações. | Em discussão |
| TB44 | `reservas_recurso` | Futuro | Comprometer bens/quantidades para uma missão com controle transacional, sem considerar reserva como consumo físico. | Em discussão |
| TB45 | `atendimentos` | Futuro | Registrar execução/entrega efetiva, distinta do que foi sugerido, aprovado ou planejado. | Em discussão |
| TB46 | `atendimento_itens` | Futuro | Quantificar atendimento confirmado de cada item e calcular saldo pendente, com proteção contra duplicidade e correções rastreáveis. | Em discussão |
| TB47 | `movimentacoes_recurso` | Futuro | Registrar entradas, saídas e devoluções de estoque vinculadas à operação, evitando saldo e histórico independentes. | Em discussão |
| TB48 | `profissao_indice_semantico` | Futuro | Recuperar profissões por significado, com FK real e hash do catálogo, sem indexar registros profissionais individuais. | Adiada |
| TB49 | `curso_indice_semantico` | Futuro | Recuperar cursos pertinentes preservando modelo/hash; encontrar curso não comprova certificado nem equivalência. | Adiada |
| TB50 | `tipo_recurso_indice_semantico` | Futuro | Recuperar classes de bens/insumos por significado antes de consultar recursos concretos e compatibilidade. | Adiada |

## Assuntos ainda sem tabela definida

Login/usuários/perfis de produção precisam ser resolvidos. Decisões administrativas já registram sujeito, data e justificativa; uma trilha completa de versões cadastrais continua pendente. Histórico de avaliações das áreas, cobertura territorial ampliada, rotas e equipes permanentes permanecem para discussão futura. Não há nomes ou contratos finais aprovados para essas tabelas.

O protótipo continua limitado a sugestões e avaliação administrativa. As linhas futuras não ampliam automaticamente o escopo D009. Os contratos detalhados permanecem nas referências; este arquivo serve para controle e entendimento do negócio.
