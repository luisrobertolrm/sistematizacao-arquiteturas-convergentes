# Decisões de modelagem

## D001 — Conteúdo semântico e rastreabilidade do embedding

**Estado: aprovada pelo usuário.**

- Descrições e demais conteúdos de domínio permanecem na tabela `atividades`.
- Remover `texto_busca` da proposta de `atividade_indice_semantico`. O texto para geração será composto em memória a partir do conteúdo de origem.
- Manter o hash atual do conteúdo semântico em `atividades.hash_conteudo_semantico`.
- Manter `hash_atividade_origem` no índice para identificar a versão do conteúdo que originou o embedding.
- O hash considera o conteúdo usado na geração, sem datas de auditoria. A serialização e a composição exata serão especificadas antes da implementação.
- Alterações do conteúdo atualizam o hash e invalidam os índices na mesma transação.
- A publicação do embedding compara atomicamente o hash atual com o hash capturado na geração. Resultado obsoleto não será publicado.

Motivo: evitar duplicação do texto de domínio e impedir uso de um embedding incompatível com a versão corrente da atividade.

## D002 — Cadastro comum de modelos de IA e conexões

**Estado: consolidada a pedido do usuário após discussão.**

- Usar `modelo_ia` para modelos de embeddings e de inferência de texto, diferenciados por `finalidade` (`embedding` ou `inferencia_texto`).
- Separar dados de conexão em `conexao_ia`: provedor, URL base, autenticação e credencial protegida. Uma conexão pode atender a vários modelos.
- `modelo_ia` identifica conexão, nome do modelo no provedor, revisão quando disponível, finalidade, dimensão e seleção ativa.
- `dimensao` é obrigatória e positiva para embeddings, e nula para inferência de texto.
- No primeiro recorte, manter a dimensão em `modelo_ia`. Tabelas adicionais para parâmetros específicos só serão detalhadas quando houver necessidade concreta.
- Preservar a identidade das configurações que geram embeddings. Mudar modelo/revisão/dimensão ou parâmetros que alterem a representação exige um novo cadastro de modelo; não reinterpretar vetores existentes.
- Rotacionar o token não altera a identidade semântica do modelo. Troca de URL exige confirmar se o modelo servido permanece equivalente.

## D003 — Seleção por finalidade

**Estado: consolidada a pedido do usuário após discussão.**

- O campo `modelo_ia.ativo` seleciona o modelo utilizado para a finalidade cadastrada.
- Permitir no máximo um modelo ativo por finalidade, com restrição de unicidade no banco. Assim, um modelo de embeddings e outro de inferência de texto podem estar ativos simultaneamente.
- `ativo = false` significa que o modelo não está selecionado; seu cadastro e seus embeddings permanecem armazenados. Inativação cadastral é tratada separadamente e não pode deixar um modelo selecionado.
- A troca desativa o anterior e ativa o novo em uma única transação.
- Gerar e validar a cobertura dos embeddings do novo modelo antes de selecioná-lo, em todos os catálogos habilitados para busca: atividades, profissões, cursos e tipos de recurso. O critério de cobertura será especificado antes da implementação.
- Uma busca precisa de modelo de embeddings ativo; uma recomendação por LLM precisa de modelo de inferência ativo. Ausência de configuração deve produzir uma falha explícita para a operação dependente.
- Uma execução captura os IDs dos modelos selecionados no início e os mantém durante aquela execução, para evitar mistura em uma troca concorrente.
- Trocar apenas o LLM de inferência não exige regenerar embeddings. Trocar o modelo de embeddings exige novas representações dos catálogos habilitados e consultas com esse modelo.

## D004 — Embeddings por atividade e modelo

**Estado: consolidada a pedido do usuário após discussão.**

- `atividade_indice_semantico` terá FKs `id_atividade` e `id_modelo`, com unicidade no par.
- O índice só pode referenciar `modelo_ia` com finalidade `embedding`.
- Uma atividade poderá ter embeddings de vários modelos. Provedor, nome do modelo e dimensão não serão duplicados no índice; serão obtidos por relacionamento.
- Toda consulta vetorial filtra pelo modelo selecionado e verifica o hash atual da atividade. Vetores de modelos distintos não são comparados, mesmo com dimensão igual.
- O backend valida se a dimensão do vetor corresponde ao modelo vinculado. A implementação da garantia correspondente no banco será detalhada com o mapeamento físico.
- O armazenamento permanece em uma única tabela lógica por catálogo, conforme a extensão D006. Se adotado pgvector, usar `vector` sem dimensão fixa e, quando necessário, índices vetoriais parciais por modelo com dimensão explícita em cada tabela.
- Busca exata pode atender ao protótipo inicial; índices aproximados serão definidos conforme necessidade de desempenho e limitações do modelo escolhido.

O uso de pgvector continua candidato. Sua versão, tipo de índice, métrica e DDL ainda serão definidos. Referência técnica: [pgvector — vetores de dimensões diferentes](https://github.com/pgvector/pgvector#can-i-store-vectors-with-different-dimensions-in-the-same-column).

## D005 — Credencial da conexão

**Estado: consolidada a pedido do usuário após discussão.**

- A credencial pertence à conexão, e não à atividade, ao embedding ou a cada modelo individualmente.
- Para tokens persistidos no banco, usar criptografia reversível autenticada. Hash isolado não permite recuperar o token para autenticar chamadas ao provedor.
- Manter a chave de criptografia fora do banco que armazena o token e registrar sua identificação/versão para permitir rotação.
- Não expor token descriptografado em respostas da API, logs ou frontend. A descriptografia ocorre somente no backend para uso autorizado.
- Conexões sem token podem existir, conforme o mecanismo de autenticação definido.

O incremento D010 prepara Fernet com `cryptography` 50.0.2 e chave externa. Persistência, rotação e fornecimento em implantação permanecem pendentes; gerenciador de segredos continua alternativa. Referência: [OWASP — Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html).

## D006 — Busca semântica nos catálogos de capacidades

**Estado: aprovada pelo usuário.**

- Ampliar a recuperação semântica/RAG para os catálogos `profissoes`, `cursos` e `tipos_recurso`, além de `atividades`.
- Criar tabelas específicas: `profissao_indice_semantico`, `curso_indice_semantico` e `tipo_recurso_indice_semantico`. Cada uma referencia sua entidade com FK real e `modelo_ia` por `id_modelo`.
- Garantir unicidade no par entidade/modelo em cada tabela. Evitar uma tabela polimórfica com `tipo_entidade/id_entidade` sem integridade referencial.
- Conteúdo descritivo e `hash_conteudo_semantico` permanecem na entidade de origem. Índices guardam embedding, hash da origem, situação e data da indexação, sem copiar descrições.
- Aplicar a todos os catálogos as regras de invalidação transacional, publicação condicionada ao hash atual, validação de dimensão e seleção por modelo definidas para atividades.
- Reutilizar o cadastro `modelo_ia`, as conexões e a infraestrutura de geração/consulta. O código compartilhado preservará contratos tipados e não exigirá duplicar configurações de provedores por catálogo.
- Para recursos, buscar primeiro o tipo e depois consultar bens/estoques disponíveis por relações e filtros estruturados. Embeddings de recursos individuais ficam como extensão futura, condicionada a uma necessidade concreta de busca por características próprias.
- Recuperação semântica retorna candidatos; não comprova equivalência de cursos, habilitação profissional ou compatibilidade de equipamentos. Requisitos, características técnicas, validade e disponibilidade continuam sujeitos às regras estruturadas.
- A troca do modelo de embeddings deve verificar cobertura em todos os catálogos habilitados, sem misturar representações de modelos diferentes.

## D007 — Desastres, classificações e áreas afetadas

**Estado: aprovada pelo usuário.**

- `desastres` representa uma ocorrência concreta que organiza a operação, suas áreas afetadas, demandas e missões.
- Manter o catálogo `tipos_desastre` separado da ocorrência.
- Um desastre poderá ter vários tipos, relacionados por `desastre_tipo`, com um deles marcado como principal. Não manter um campo único `id_tipo_desastre` em `desastres`.
- Garantir unicidade do par desastre/tipo e exatamente um tipo principal entre as classificações vigentes de cada ocorrência. A troca do principal será transacional.
- Registrar título, descrição, início, encerramento, situação operacional e instituição coordenadora na ocorrência.
- Separar o usuário que cadastra/atualiza da instituição que coordena a operação. O vínculo de auditoria ao usuário depende do modelo de autenticação.
- A situação operacional contempla monitoramento, resposta, recuperação e encerramento; não se confunde com inativação cadastral.
- Uma ocorrência poderá abranger vários municípios por suas áreas afetadas. Não limitar `desastres` a um único município ou coordenada.
- `areas_afetadas` pertence a uma ocorrência e registra nome, descrição, município de referência, geometria marcada pelo administrador, gravidade, situação e data da última avaliação.
- A necessidade de geometria faz parte do domínio. O recorte geográfico e o mapa inicial foram detalhados no incremento 5, em D014.
- Demandas serão registros próprios vinculados à área afetada, com necessidades, quantidades e prioridades. A gravidade da área e a prioridade de cada demanda são conceitos separados.
- O fluxo será desastre → áreas afetadas → demandas → recomendações → missões aprovadas. Demandas e itens foram detalhados em D008; as demais etapas permanecem em discussão.
- Encerrar uma ocorrência preserva seu histórico para consulta e avaliação.

## D008 — Demandas, itens e unidades de medida

**Estado: aprovada pelo usuário.**

- Uma demanda é um pedido de atendimento de uma área afetada, com título, descrição, prioridade, janela de atendimento, pessoa solicitante e situação.
- A pessoa solicitante pode ser diferente do usuário autenticado que registra o pedido; manter essa distinção na auditoria.
- Separar o cabeçalho `demandas` de seus registros `demanda_itens`, permitindo várias necessidades em um pedido.
- Cada item referencia exatamente uma atividade ou um tipo de recurso, com FKs reais e restrição de exclusividade.
- Cada item informa quantidade positiva usando `Decimal`, unidade de medida e observações. Quantidade e unidade devem ser compatíveis com o serviço ou recurso solicitado.
- Criar o catálogo `unidades_medida`, normalizando as unidades utilizadas nos pedidos e nos catálogos de capacidades/recursos. Conversões e capacidades por período precisam de regra explícita; não comparar automaticamente unidades distintas ou taxas com quantidades absolutas.
- Prioridade da demanda não substitui gravidade da área. A situação prevista é aberta, em atendimento, concluída ou cancelada.
- Separar pedido, recomendação, aprovação, missão/reservas e atendimento efetivamente realizado.
- Somente atendimento confirmado reduz o saldo pendente do item; recomendação, planejamento ou reserva não comprovam entrega.
- Preservar registros de atendimentos parciais para calcular o saldo, sem um contador de atendimento editado independentemente do histórico. O esquema de atendimento ainda será discutido.
- Requisitos de habilitação, formação e características técnicas serão estruturados, sem depender somente de observações ou interpretação do LLM. Suas tabelas ainda serão discutidas.

Sugestões para as etapas seguintes estão em [Modelo operacional proposto](modelo-operacional-proposto.md). Essas sugestões não são decisões aprovadas.

## D009 — Primeira entrega de apoio à decisão

**Estado: registrado a pedido do usuário, conforme o escopo reduzido proposto.**

- A primeira entrega cobre cadastro de capacidades, ocorrência/áreas no mapa, demandas e geração de recomendações por IA para análise administrativa.
- Demonstrar uma ocorrência fictícia, em um município, com três áreas afetadas. O modelo mantém suporte às cardinalidades mais amplas já aprovadas.
- Incluir `recomendacoes`, `recomendacao_itens`, `recomendacao_pessoas`, `recomendacao_instituicoes` e `recomendacao_recursos`, com referências estruturadas e justificativas da IA.
- Aprovação/rejeição registra a decisão sobre a sugestão e preserva seu histórico. Nova análise gera outra recomendação.
- Aprovação não cria missão, não reserva pessoas/recursos, não movimenta estoque e não reduz saldo de demanda nesta etapa.
- Implementar inicialmente recuperação semântica por atividades e usar relações/filtros estruturados nos demais cadastros. Índices de profissões, cursos e tipos de recurso ficam para a etapa seguinte; D006 permanece válida para o modelo completo.
- Disponibilidade por horário, composição detalhada de equipes/ofertas, requisitos avançados, missões, reservas, entregas, estoque e rotas ficam para evolução futura.
- Preservar cadastros normalizados de modelos e conexões, sem exigir troca de modelos durante a operação na primeira entrega.
- Avaliar tempo e pertinência da identificação de candidatos; a simulação não garante alocação ou aptidão além dos critérios efetivamente verificados.

O [escopo inicial](escopo-inicial.md) detalha funcionalidades, inventário de tabelas, telas, indicador e critérios de conclusão. O [modelo operacional](modelo-operacional-proposto.md) registra as tabelas restantes como evolução futura, sem aprovar automaticamente seus contratos finais.

## D010 — Implementação inicial em Python e Angular

**Estado: incremento implementado a pedido do usuário.**

- Aplicar a skill informada com quatro pastas/pacotes e direção `web → business → infra → core`; entidades de domínio não importam SQLAlchemy, e mapeamentos ficam em `infra/configurations`.
- Usar FastAPI, SQLAlchemy/psycopg, Pydantic, mypy estrito e Ruff, com versões exatas e locks. Preservar Python `>=3.13,<3.14`.
- Manter `project.toml` como origem; gerar `pyproject.toml` explicitamente para interoperabilidade. Arquivo gerado não deve ser editado nem versionado.
- Iniciar com instituições e pessoas: UUID v4, UTC, CRUD, inativação e auditoria pelo `sub` do JWT. Cadastro de usuários/login de produção permanece pendente; voluntário não é usuário autenticado.
- Validar JWT HS256, emissor, audiência, expiração e perfil administrativo. Emissão local somente por CLI de desenvolvimento, sem endpoint público de login. Segredos aleatórios externos ao código.
- Preparar grafo LangGraph tipado, adaptador LangChain e Fernet com chave externa. Recuperação vetorial, persistência normalizada dos modelos/conexões e recomendação administrativa ainda não estão integradas.
- Criar Angular com telas dos dois cadastros, token em memória e versões compatíveis com o Node disponível. Biblioteca de mapa e provedor/modelos reais não foram escolhidos.
- Validar schema e API com PostgreSQL real exclusivo de testes. Nunca aplicar migração automaticamente ao iniciar a API.

O [estado da implementação](implementacao-inicial.md) e o [controle de tarefas](controle-tarefas.md) indicam o que foi entregue e o restante de D009.

## D011 — Vínculos e qualificações, incremento 2

**Estado: detalhamento implementado para continuar o escopo autorizado.** D006 e D009 permanecem válidas; este incremento não habilita RAG de profissões/cursos.

- Acrescentar `profissoes`, `cursos`, `pessoa_instituicao`, `pessoa_profissao` e `pessoa_curso`, com a mesma identidade, auditoria e inativação do incremento 1. Migração 0002 independente dos modelos atuais; cadastros anteriores são preservados.
- Catálogos mantêm nome/descrição na origem. O servidor calcula SHA-256 do JSON v1 ordenado por chaves, sem espaços entre elementos, UTF-8 e caracteres não escapados. Profissão inclui `versao`, `catalogo`, `nome`, `descricao` e `codigo_cbo`; curso inclui os quatro primeiros e `tipo`. Auditoria, IDs, qualificações e comprovantes individuais não integram o hash. Nenhum texto de busca é duplicado.
- CBO opcional normalizado para seis dígitos, sem consulta a uma classificação oficial. Nomes/CBO não têm unicidade presumida: consolidação de conceitos e equivalência permanecem trabalho administrativo. Valores de `TipoCurso`: técnico, capacitação e treinamento.
- Participação institucional usa voluntário, funcionário, associado ou representante. Datas têm granularidade de dia, com início/fim inclusivos. Rejeitar fim anterior ao início e períodos sobrepostos da mesma pessoa/instituição/tipo, inclusive quando ambos têm encerramento informado. Período seguinte pode começar no dia posterior ao encerramento.
- A API verifica sobreposição em transação com bloqueio da pessoa, serializando alterações concorrentes dos seus vínculos. O banco protege FKs, ordem das datas e unicidade do vínculo aberto (`fim_em IS NULL`) não inativado. A restrição de sobreposição de períodos fechados está no serviço; SQL externo não deve contorná-lo. Uma eventual garantia por exclusão SQL será avaliada antes de permitir outros escritores.
- Qualificação profissional não inativada é única por pessoa, profissão, registro, órgão, UF e validade. Nulos contam como iguais; registro/órgão/UF são normalizados em maiúsculas na API. Validade diferente permite renovação em outro registro. Não inferir habilitação de registros ausentes ou da situação administrativa.
- Formação não inativada é única por pessoa, curso, emissor sem distinção de maiúsculas/minúsculas/espaços externos e data de conclusão. Alterar validade/carga/comprovante não cria uma segunda conclusão. Renovação com outra data de conclusão cria outro registro. Carga horária, quando informada, é Decimal positiva com duas casas; validade não precede conclusão.
- Novos vínculos e edições exigem pessoa/referência ativas. `pessoa_id` vem da rota e não pode ser trocado pelo payload. Consulta administrativa com `incluir_inativos=true` inclui registros e referências inativadas, retornando nome por relacionamento, sem copiá-lo para a associação. Inativação não apaga FKs nem cascata registros.
- A listagem cadastral pode mostrar vínculos encerrados e formações vencidas, preservando entendimento do histórico. Situação de validação é independente de validade/agenda. A seleção operacional futura deverá verificar esses critérios; marcar `validada` não declara aptidão.
- `comprovante_referencia` é um identificador textual opcional sem credenciais/parâmetros. Não há envio, obtenção remota, download, conteúdo de documento ou verificação de certificado implementados. A leitura exige o mesmo JWT administrativo dos vínculos.
- Renovações e encerramentos preservam registros; correção via PUT atualiza campos e auditoria. Isso não é uma trilha imutável de todas as versões de uma edição. Evidências e auditoria completa de validação permanecem pendentes.
- Angular oferece catálogos e a ação **Pessoas → Vínculos e formação**, com consulta paginada, busca de referências, edição, encerramento, inativação e consulta de histórico.

Referências técnicas: [PostgreSQL 18 — unicidade e NULLS NOT DISTINCT](https://www.postgresql.org/docs/18/indexes-unique.html) e [SQLAlchemy — índices PostgreSQL](https://docs.sqlalchemy.org/en/21/dialects/postgresql.html).

## D012 — Catálogo de atividades e unidades, incremento 3

**Estado: detalhamento técnico implementado para continuar o escopo autorizado.** Mantém D001–D009; geração de embeddings e publicação de índices pertencem ao próximo fluxo de IA.

- Acrescentar `unidades_medida`, `categorias_atividade`, `atividades` e `atividade_termos`, com UUID, auditoria e inativação. Revisão 0003 independente dos mapeamentos atuais; dados dos incrementos 1 e 2 são preservados.
- Códigos têm 1–50 caracteres: letras ASCII minúsculas, números, hífen ou sublinhado, começando por letra/número. A API remove espaços externos e converte maiúsculas. Código é único por tabela inclusive entre inativados e não é alterado por PUT. Nome/símbolo/descrições podem ser corrigidos. Não presumir equivalência de unidades pelo nome ou símbolo.
- Atividade exige descrição e categoria. Unidade de capacidade é opcional, por FK. Criação/edição exige referências ativas, protegidas por bloqueio compartilhado até o commit. Inativar categoria/unidade preserva atividades, que continuam consultáveis com aviso de referência inativa; novas edições exigem referências ativas. Sem cascata de inativação.
- Entrada semântica v1 é JSON com `versao=1`, `catalogo="atividades"`, `codigo`, `nome`, `descricao`, `orientacoes`, `restricoes` e `termos`. Textos opcionais vazios viram null; termos ativos normalizados são únicos e ordenados. Serialização UTF-8, chaves ordenadas, caracteres não escapados e separadores sem espaços; SHA-256 calculado pelo servidor.
- IDs, auditoria, inativação e dados de categoria/unidade ficam fora dessa entrada v1. São referências estruturadas; mudar o nome da categoria ou símbolo da unidade não altera o hash da atividade. Caso outro contrato semântico inclua esses dados, terá de versionar a composição e implementar atualização das atividades afetadas.
- Termo normalizado usa palavras separadas por um espaço e letras minúsculas, mantendo acentos. Unicidade de `(atividade_id, termo)` entre não inativados; permite outra linha após inativação. `atividade_id` vem da rota e não é alterado pelo corpo. Leitura/edição de termo de outra atividade retorna 404.
- Cadastro, edição e inativação de termos atualizam o hash e auditoria da atividade na mesma transação. Bloqueio exclusivo da atividade serializa alterações de seus textos e termos, inclusive concorrentes. Conflito reverte toda a transação. A consulta do hash usa todos os termos ativos, sem limite de paginação.
- SQL garante FKs, formato básico, códigos únicos e termos ativos únicos. Normalização, imutabilidade de códigos e manutenção do hash são regras do serviço; outros escritores devem aplicar o mesmo contrato e bloqueio, sem alterar textos/termos diretamente ignorando o hash.
- Consulta administrativa com `incluir_inativos=true` preserva cadastros/termos e referências históricas. Termos de atividade inativada são consultáveis no histórico e podem ser inativados, mas não criados/editados. Correções via PUT continuam sem uma trilha imutável de todas as versões.
- Angular oferece **Atividades e unidades**, três catálogos, busca/paginação de referências e **Atividades → Termos e sinônimos**. A busca por atividades é literal por nome, código, descrição e termos ativos. Não executa busca vetorial ou LLM.
- Não criar `texto_busca`, embeddings ou tabelas de índices neste incremento. A futura indexação deverá capturar conteúdo/hash consistentes e publicar somente se ainda corresponderem à origem; sua invalidação/publicação não está implementada nesta etapa.

## D013 — Recursos e ofertas, incremento 4

**Estado: detalhamento técnico implementado no escopo autorizado.** Acrescenta `tipos_recurso`, `recursos`, `ofertas_atividade` e `oferta_atividade_recurso`, mantendo D001–D009. Migração 0004 independente dos mapeamentos atuais, UUID, auditoria pelo sujeito autenticado e inativação sem cascata.

- Tipo de recurso define categoria (`veiculo`, `equipamento`, `material`, `insumo`), unidade obrigatória e controle `individual` ou `estoque`. Não foi acrescentado código de negócio que não constava do modelo. Nomes não são identidade nem têm unicidade presumida.
- Entrada semântica v1 de tipo de recurso: JSON com `versao=1`, `catalogo="tipos_recurso"`, `nome`, `descricao` e `categoria`, serializado como D012 e resumido em SHA-256 pelo servidor. Unidade, modo de controle, IDs e auditoria são referências/metadados estruturados fora do hash. Nenhuma descrição é duplicada em índice. Embeddings de tipos e recursos individuais não são implementados aqui.
- Um recurso tem exatamente um responsável, instituição ou pessoa, com FKs e `CHECK` de exclusividade. Quantidade total é Decimal de até 18 dígitos, quatro casas, não negativa. Individual exige exatamente 1; estoque admite zero. Identificação é opcional e não presume unicidade global. Coordenadas são pareadas e limitadas; município valida formato de sete dígitos, sem consulta IBGE ou mapa.
- Estado operacional é `operacional`, `em_manutencao` ou `indisponivel`. Cadastro não calcula disponibilidade por período. Não há saldo disponível independente, reserva ou movimentação neste incremento.
- Unidade/modo do tipo ficam estáveis após qualquer recurso referenciá-lo, inclusive inativado. O tipo de um recurso, a atividade de uma oferta e o recurso de um vínculo não são trocados por PUT; inativar/criar outro registro preserva o significado das relações. Nomes, descrições e demais campos editáveis podem ser corrigidos.
- Oferta exige exatamente um ofertante e permite no máximo uma linha ativa por atividade/ofertante/município, com índices parciais separados para pessoa e instituição. Após inativação, outra linha pode ser criada. Não somar automaticamente ofertas institucionais e pessoais; composição de equipe e detecção de sobreposição continuam futuras.
- Capacidade declarada é opcional e positiva quando informada; exige unidade ativa na atividade, sem taxa/período ou conversão implícitos. A unidade da atividade não pode mudar enquanto existir oferta, inclusive inativada, com capacidade declarada. Essa proteção complementa D012.
- Validação é administrativa: `pendente`, `validada` ou `rejeitada`. O servidor preenche `validado_em` ao salvar uma versão validada e limpa ao salvar pendente/rejeitada. PUT em uma oferta validada renova essa data. Inativação preserva a data; não constitui comprovação de aptidão ou uma trilha imutável de versões.
- Vínculo oferta/recurso é único entre linhas ativas; após inativação admite outra linha. Quantidade prevista é positiva, quatro casas; recurso individual exige 1. Quantidade prevista de estoque pode superar o total cadastrado: é planejamento, sem promessa de disponibilidade, débito ou reserva. Um bem pode constar de mais de uma oferta; isso não autoriza somar capacidades nem alocar simultaneamente.
- O recurso pode ter responsável diferente do ofertante. O vínculo não prova propriedade, consentimento ou autorização de uso. O responsável pelo recurso é exibido; confirmação de disponibilidade e autorização pertencem à futura operação.
- Criação/edição exige referências ativas, com bloqueios compartilhados; alteração do próprio registro usa bloqueio exclusivo. Vínculos usam também bloqueio da oferta, e seu ID vem da rota. Vínculo de outra oferta retorna 404. Oferta inativa permite consultar histórico e inativar vínculos, mas não criá-los/editá-los. Referências inativas permanecem consultáveis, sem cascata.
- SQL garante FKs, exclusividade do responsável, limites básicos, unicidades e coerência situação/data de validação. Regras entre tabelas (quantidade individual, unidade estável), imutabilidade de referências e hash são do serviço: escritores externos devem seguir o mesmo contrato e bloqueios.
- Angular integrado oferece **Recursos e ofertas → Tipos de recurso / Recursos / Ofertas de atividades → Recursos da oferta**, com edição, inativação, histórico e seletores paginados. Pessoas também passam a aceitar busca literal por nome na API, para selecionar responsáveis.

## D014 — Desastres e território, incremento 5

**Estado: detalhamento técnico implementado para continuar o escopo autorizado.** Acrescenta `tipos_desastre`, `desastres`, `desastre_tipo` e `areas_afetadas`, com migração 0005, auditoria pelo `sub` e inativação sem cascata. Mantém as cardinalidades de D007 e o recorte de D009.

- Tipos usam o contrato de código estável de D012, com nome e descrição obrigatórios. É catálogo local: não foi carregada nem presumida classificação oficial ou equivalência automática.
- Ocorrência exige coordenadora ativa, título, descrição, início com fuso e de 1 a 20 classificações distintas, exatamente uma principal. Datas recebidas são normalizadas para UTC; a interface mostra e recebe horário local do navegador.
- Cadastro e PUT enviam as classificações vigentes junto do cabeçalho, em uma transação. Tipos vigentes mantidos preservam IDs; removidos são inativados; uma associação anteriormente inativada pode gerar nova linha. A rota/serviço fixa o desastre, sem CRUD isolado capaz de remover a última classificação.
- O banco garante unicidade ativa do par e no máximo um principal por ocorrência. O serviço garante ao menos uma classificação/principal, com bloqueio exclusivo do desastre. A troca libera a marca anterior antes de promover a nova, na mesma transação. Concorrência não produz estado parcialmente publicado; erro reverte cabeçalho e classificações. Escritores SQL externos devem seguir o contrato, pois a existência de principal não é uma restrição SQL diferida.
- Situação é `em_monitoramento`, `em_resposta`, `em_recuperacao` ou `encerrado`. Entre estados abertos admite correção administrativa. Encerrado exige data igual ou posterior ao início; outros estados não aceitam data de encerramento. Reabertura fica pendente e é recusada com 409. Encerramento mantém cadastro consultável; não inativa nem encerra áreas automaticamente. Correções cadastrais, classificações e avaliações de áreas continuam possíveis em ocorrência encerrada e ativa.
- Coordenadora/tipos inativados permanecem visíveis com identificação; criação/edição exige referências ativas. Inativação da ocorrência preserva classificações/áreas. Áreas de ocorrência inativa podem ser lidas no histórico e inativadas, mas não criadas, editadas ou reavaliadas.
- Área pertence à ocorrência da rota, por FK imutável no corpo. A leitura/edição/inativação/avaliação de área de outra ocorrência retorna 404. Cada operação de escrita bloqueia primeiro o desastre, depois a área; não há troca de município ou classificação no cabeçalho do desastre para substituir suas áreas.
- Gravidade administrativa: `baixa`, `moderada`, `alta`, `critica`; situação da área: `em_avaliacao`, `em_resposta`, `em_recuperacao`, `encerrada`. São escalas locais deste incremento, sem certificação técnica e sem determinar automaticamente a prioridade de demandas. Não é necessário manter a situação da área igual à da ocorrência.
- O servidor gera `ultima_avaliacao_em` na inclusão. PUT que muda gravidade/situação atualiza essa data; alterações de nome/descrição/município/geometria e inativação preservam a avaliação anterior. `POST .../areas/{id}/avaliar` confirma gravidade/situação, inclusive iguais, atualizando a data. Na interface, **Confirmar avaliação atual** confirma os valores já registrados; edite a área para alterá-los. Não existe tabela/trilha de todas as avaliações ou versões nesta etapa.
- Geometria de domínio é `Polygon` GeoJSON em longitude/latitude WGS84, com um anel exterior, de 3 a 200 vértices distintos mais fechamento. Sem altitude, furos, MultiPolygon ou cruzamento do antimeridiano. Longitude entre -180 e 180; latitude entre -85 e 85, no recorte visual do mapa. Números finitos, borda simples sem cruzamentos/toques próprios ou sobreposição de segmentos e área planar positiva; orientação exterior normalizada para anti-horário. A validação usa tolerância de 1e-12 em graus quadrados, adequada a polígonos locais, sem cálculo de superfície geodésica.
- Persistência JSONB com conversor tipado separado do domínio. SQL garante formato básico do objeto e FKs; serviço/conversor validam coordenadas e borda. Não há PostGIS, consulta espacial, teste contra limite municipal, acesso seguro ou rota. Código IBGE é somente formato de sete dígitos. Município é referência declarada; cobertura que atravesse municípios precisa de revisão administrativa, sem validação cartográfica automática.
- Mapa inicial: Leaflet **1.9.4**, tipos **1.9.22**, versões exatas e lock atualizado; distribuição ESM integrada ao Angular. OpenStreetMap fornece o fundo, com atribuição visível e requisições normais do navegador, sem download em massa/cache offline. Delimitação fica independente da biblioteca. Vista inicial de referência em São Paulo, centralização por coordenadas e enquadramento das áreas consultadas; sem geocodificação automática.
- Mapa exibe áreas da página consultada (até 50), cores por gravidade e bordas tracejadas para inativadas. Seleção/delimitação em edição é azul. Desenho por cliques, desfazer ponto, concluir e redesenhar; servidor valida antes de persistir. Sem fundo cartográfico carregado, as geometrias/controles permanecem disponíveis e há aviso. O teste automatizado substitui tiles por imagens locais simuladas e não comprova disponibilidade ou exatidão cartográfica de terceiros.
- Angular oferece **Desastres e áreas → Tipos de desastre / Ocorrências → Áreas e mapa**, com busca/paginação, troca de principal, edição, histórico e avaliações. Demandas e recomendações permanecem no próximo incremento.

Referências: [GeoJSON — RFC 7946](https://www.rfc-editor.org/rfc/rfc7946.html), [Leaflet — versão estável](https://leafletjs.com/download.html) e [OpenStreetMap — política de tiles](https://operations.osmfoundation.org/policies/tiles/).

## D015 — Conexões e modelos de IA, incremento 6

**Estado: detalhamento técnico implementado na continuação solicitada pelo usuário.** Revisão 0006 acrescenta `conexao_ia` e `modelo_ia`, preservando D002–D005. Não representa escolha de provedor real.

- Adaptador inicial `openai_compativel`; autenticação `bearer` ou `nenhuma`. URL validada, sem credenciais/query/fragmento; HTTP somente local. Chamadas dependem de URL explicitamente permitida na configuração do servidor.
- Token cifrado com Fernet e chave externa; API nunca devolve token/cifra. Token nulo no PUT preserva a credencial; outro token a substitui. Identificador da chave acompanha a cifra. Keyring/rotação automática de chaves permanecem futuros.
- Endpoint/adaptador/autenticação ficam fixos quando houver qualquer modelo referenciando a conexão. Nome/token podem mudar. Identidade, finalidade, revisão, dimensão e conexão de modelo são imutáveis; alterações semânticas exigem novo cadastro.
- `ativo` seleciona no máximo um modelo por finalidade, com índice único parcial e bloqueio transacional. Inativar modelo desmarca seleção; conexão com modelo selecionado não pode ser inativada.
- Ativação de embeddings exige 100% das atividades ativas com índice pronto/hash atual. Somente atividades estão habilitadas em D009; catálogo vazio satisfaz cobertura. Modelo não selecionado pode ser indexado previamente.
- Cada execução captura modelos/configuração e mantém seus IDs. Seleção administrativa de outro modelo não mistura representações; publicação recusa modelos/conexões capturados que tenham sido inativados. Revisão é descritiva; o identificador exato do provedor deve representar a versão pretendida.
- Angular oferece configuração administrativa de conexões/modelos e preparação dos índices, atendendo à continuação pedida. A limitação original de D009 não exige troca em operação; agora há gestão administrativa explícita, sem substituição automática dentro do grafo.

## D016 — Demandas e itens, incremento 6

**Estado: detalhamento técnico implementado no recorte D008–D009.** Revisão 0007 acrescenta `demandas` e `demanda_itens`.

- Pedido pertence a área fixa, com território/solicitante ativos. Prioridade `baixa`, `normal`, `alta`, `urgente`; datas com fuso, normalizadas para UTC e prazo não anterior ao início.
- Cabeçalho e 1–100 itens são gravados juntos. Cada item solicita exatamente uma atividade ou tipo de recurso, com quantidade Decimal positiva e unidade exatamente igual à necessidade. Atividade sem unidade não admite item quantitativo; sem conversões implícitas.
- Itens mantidos preservam IDs; removidos são inativados; novos têm ID nulo. IDs repetidos, de outro pedido ou inativados são recusados. Necessidade/unidade de item existente ficam fixas. Não há CRUD isolado capaz de deixar pedido sem itens.
- Unidades de atividade/tipo já utilizadas em qualquer item, inclusive inativado, são protegidas no banco contra alteração de significado.
- Criar somente `aberta`; editar para manter aberta ou cancelar. Cancelada não é reaberta/editada. Estados `em_atendimento`/`concluida` ficam previstos, mas suas transições são recusadas sem registros de execução. Inativação é separada.
- Consulta histórica inclui itens removidos; PUT corretivo não mantém todas as versões antigas dos campos. Alterações após análise tornam seu contexto desatualizado e impedem aprovação.

## D017 — Índices de atividades e recomendações, incremento 6

**Estado: fluxo funcional implementado em D009.** Revisões 0008 e 0009 acrescentam índice e cinco tabelas de recomendações. Contratos e sequência de operação em [IA, demandas e recomendações](ia-demandas-recomendacoes.md).

- Vetor inicial em `double precision[]`, dimensão obtida do modelo, com validação na aplicação e trigger SQL de finalidade, dimensão e valores. Par atividade/modelo único. Pgvector/ANN fica para escala; cosseno exato em Python aceita até 5000 vetores, com erro explícito acima disso.
- Não há `texto_busca` duplicado. Conteúdo/hash canônicos seguem D012. Mudança de hash/inativação invalida vetor na mesma transação. Lote síncrono de até 50 captura origem, chama provedor fora da transação e publica atomicamente somente se hash/referências continuarem válidos.
- Estados de índice implementados: `pendente` e `pronta`. Falha não publica lote nem grava tarefa durável; `processando`/`falhou` ficam para eventual fila futura. Último hash/data de sucesso permanecem quando o vetor é invalidado.
- LangGraph em `business/graphs` executa recuperar → sugerir → validar; LangChain integra embeddings e texto estruturado. Busca semântica fornece contexto, sem considerar atividades semelhantes automaticamente equivalentes às solicitadas.
- Candidatos: ofertas validadas da atividade exata e recursos operacionais, no mesmo município, com responsáveis ativos/validados. Até 30 ofertas e 30 recursos; limites informados. Sem agenda, requisitos avançados, composição de equipe ou conversão de capacidade por período.
- Saída deve corresponder aos itens vigentes e usar IDs/relações/quantidades válidos. Serviços indicam candidatos com quantidade sugerida zero, sem cobertura numérica presumida. Sobreposição global de estoque em itens distintos gera pendência, sem reserva automática.
- Recarregar e comparar hash do contexto após a chamada; mudança relevante impede gravação. Persistência das cinco tabelas é atômica. Guardar modelos/hash/referências e resultado, sem cópia integral imutável de todas as entradas. Nomes históricos vêm dos cadastros relacionados.
- Estados `gerada`, `aprovada`, `rejeitada`; decisão única/final com justificativa, data do servidor e `sub` do JWT. Aprovação exige contexto atual; rejeição pode descartar análise desatualizada. Nova análise cria outro registro, sem apagar anterior ou marcar substituição automaticamente.
- Aprovação não altera pedido/estoque, não reserva nem registra entrega. Validação com provedor HTTP fictício testa integração, sem comprovar qualidade de LLM externo ou resultado do indicador.

## Estado da implementação e pendências

As **29 tabelas iniciais** têm entidades, migrações, API e Angular. Conexões/modelos, indexação, recuperação e recomendações/decisões estão integrados conforme D015–D017. Passaram 103 testes PostgreSQL e 17 cenários de navegador, com IA HTTP fictícia. A [simulação em memória](../simulacoes/escopo_inicial/README.md) continua como complemento separado de D001–D009; não verifica automaticamente os contratos posteriores.

Permanecem escolher/configurar provedores reais, avaliar qualidade/indicador, definir login/usuários/perfis de produção e implantação. Keyring, parâmetros adicionais tipados e índice vetorial para escala serão evoluções deliberadas. Dependências permanecem fixadas. [Estado detalhado](implementacao-inicial.md).