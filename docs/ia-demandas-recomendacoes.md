# IA, demandas e recomendações — incremento 6

Implementação funcional do fluxo de apoio à decisão de D009, fora de `prototipo/`. As dez tabelas restantes foram acrescentadas, completando **29 tabelas iniciais**, com API, Angular e quatro revisões Alembic independentes:

| Revisão | Tabelas |
|---|---|
| `0006_modelos_ia` | `conexao_ia`, `modelo_ia` |
| `0007_demandas` | `demandas`, `demanda_itens` |
| `0008_indices` | `atividade_indice_semantico` |
| `0009_recomendacoes` | `recomendacoes`, `recomendacao_itens`, `recomendacao_pessoas`, `recomendacao_instituicoes`, `recomendacao_recursos` |

Decisões técnicas em D015–D017. Python `>=3.13,<3.14`, dependências exatas, `project.toml`, quatro camadas e domínio independente do ORM foram preservados. Grafos ficam em `business/graphs`, adaptadores em `infra/ia`, entidades em `core/entity` e rotas em `web/controllers`. Nenhuma migração é aplicada ao iniciar a API.

## Configuração e sequência de uso

Preparar ambiente, JWT administrativo e banco conforme [backend/README](../backend/README.md). Em instalações existentes, revisar e aplicar explicitamente `alembic upgrade head`; não executar novamente o gerador de segredos sobre arquivos existentes.

O backend precisa de chave Fernet externa e de uma lista explícita de endpoints permitidos para efetuar chamadas. Exemplo de configuração **sem credenciais reais**:

```dotenv
REDE_ENCRYPTION_KEY=<chave-Fernet-gerada-localmente>
REDE_ENCRYPTION_KEY_ID=fernet-v1
REDE_IA_URLS_PERMITIDAS=["https://provedor.example/v1"]
```

`REDE_IA_URLS_PERMITIDAS=[]` é o padrão: permite manter cadastros, mas recusa chamadas de IA. O endereço cadastrado precisa coincidir com um endereço da lista, desconsiderando a barra final. URLs não aceitam usuário/senha, query ou fragmento; HTTP é restrito a localhost/loopback. O endereço de exemplo não é um provedor utilizável. Reiniciar a API após alterar configuração de ambiente.

1. Cadastrar unidades, atividades, termos, pessoas/instituições, ofertas e recursos. Validar administrativamente os ofertantes e suas ofertas.
2. Em **Configuração de IA → Conexões**, cadastrar o endpoint compatível com OpenAI e autenticação `bearer` ou `nenhuma`.
3. Cadastrar um modelo de embeddings inicialmente sem seleção ativa, com dimensão correspondente à resposta do provedor, e um modelo de inferência de texto selecionado.
4. Em **Índices de atividades**, gerar embeddings de todas as atividades ativas, em lotes de até 50. Ativar o modelo de embeddings somente após cobertura atual de 100% desse catálogo.
5. Cadastrar ocorrência e área no mapa; em **Demandas e recomendações**, criar pedido e itens usando as unidades dos catálogos.
6. Solicitar análise, revisar candidatos, justificativas e pendências; aprovar ou rejeitar com justificativa. Nova análise gera outra recomendação e conserva decisões anteriores.

Não foi escolhido ou chamado um provedor real na validação. O provedor escolhido deverá suportar os contratos de embeddings e saída estruturada por ferramentas usados pelo adaptador.

## Conexões e modelos

`conexao_ia` centraliza nome, adaptador `openai_compativel`, URL, tipo de autenticação, token cifrado e identificador da chave. O token é entrada opcional protegida por `SecretStr`; a resposta devolve somente `tem_token` e identificação da chave, sem token ou cifra. Ao criar autenticação bearer, o token é obrigatório. No PUT, token ausente/nulo preserva a credencial; informar outro token a substitui. Autenticação `nenhuma` limpa a credencial e não aceita token informado.

A cifra Fernet usa `REDE_ENCRYPTION_KEY`, separada do banco. `REDE_ENCRYPTION_KEY_ID` identifica a chave atual. Chave ausente/inválida, cifra ilegível ou identificador incompatível geram erro explícito. Há substituição de token usando a chave corrente; keyring e migração automática de cifras entre chaves ficam pendentes. Hash não substitui criptografia reversível.

Endpoint, adaptador e autenticação ficam imutáveis depois que qualquer modelo referencia a conexão, inclusive inativado. Nome e token podem mudar. Para outra identidade semântica de endpoint, cadastrar outra conexão/modelo. Conexão com modelo selecionado não pode ser inativada.

`modelo_ia` guarda conexão, identificador exato enviado ao provedor, revisão descritiva, finalidade e dimensão. A dimensão é obrigatória de 1 a 16384 para `embedding` e nula para `inferencia_texto`. Identidade, revisão, finalidade, conexão e dimensão são imutáveis após criação; editar serve para selecionar/desselecionar. Mudanças de identidade exigem outro cadastro, preservando índices e recomendações anteriores. A revisão não é enviada como parâmetro separado: usar identificador do provedor que represente a versão desejada.

`ativo` significa seleção por finalidade. Índices únicos parciais e bloqueio transacional de configuração garantem no máximo um selecionado de cada finalidade. Ativar outro desmarca o anterior atomicamente. Modelo/conexão inativados não podem ser selecionados; inativar modelo também remove sua seleção. Embeddings exigem 100% das atividades ativas com índice pronto e hash atual; catálogo vazio satisfaz essa condição. Apenas atividades estão habilitadas para busca vetorial em D009.

Cada execução captura os dois modelos e a configuração correspondente. Trocar a seleção não mistura modelos dentro da execução. Se modelo/conexão capturados forem inativados antes da publicação, a operação é recusada. Trocar somente o modelo de texto não exige regenerar embeddings.

## Demandas e itens

Pedido pertence a uma área ativa de ocorrência ativa e referencia pessoa solicitante ativa. Área fica fixa após criação. Prioridade: `baixa`, `normal`, `alta` ou `urgente`, independente da gravidade territorial. Início e prazo exigem fuso, são normalizados para UTC e prazo não pode anteceder início. Encerrar uma ocorrência não a inativa; não há regra exigindo situação idêntica entre ocorrência, área e pedido.

POST/PUT recebem cabeçalho e **1 a 100 itens** juntos em uma transação. Cada item exige exatamente uma atividade ou um tipo de recurso, quantidade Decimal positiva de até quatro casas e unidade ativa exatamente igual à cadastrada na necessidade. Atividade sem unidade não pode ser solicitada numericamente. Não há conversão implícita nem dedução de taxa por IA.

IDs dos itens mantidos são preservados; removidos são inativados; novos usam ID nulo. IDs repetidos são recusados; ID de outro pedido ou de item já inativado retorna 404. Necessidade e unidade de item existente ficam fixas: remover/criar outro item para mudar seu significado. Não há CRUD isolado capaz de remover o último item. O banco protege a unidade de atividade/tipo já referenciado por qualquer item, inclusive inativado.

Criação exige `aberta`; edição permite manter aberta ou cancelar. Pedido cancelado não pode ser editado/reaberto. `em_atendimento` e `concluida` estão previstos no enum, mas a API recusa essas transições enquanto não houver registros de execução. Inativação é separada e preserva dados. `incluir_inativos=true` permite consultar itens removidos e pedidos inativados. PUT corretivo não constitui trilha imutável de todas as versões.

## Índices e busca semântica

O texto continua somente em `atividades` e `atividade_termos`. A entrada canônica v1 e o hash da origem seguem D012. `atividade_indice_semantico` contém FK de atividade/modelo, vetor, hash de origem, situação e data, sem duplicar descrição, dimensão ou conexão. O par atividade/modelo é único.

Armazenamento físico inicial: **`double precision[]`**, permitindo dimensões distintas por modelo na mesma tabela. A dimensão e a finalidade vêm de `modelo_ia`; aplicação e trigger SQL verificam dimensão, valores finitos, vetor não nulo e norma positiva antes de publicar. A busca usa cosseno exato em Python, filtra modelo/hash e aceita até **5000 vetores atuais**; acima disso recusa com 409, sem truncamento silencioso. Pgvector/ANN não foram instalados neste incremento. Referência do tipo: [PostgreSQL 18 — arrays](https://www.postgresql.org/docs/18/arrays.html).

Indexação síncrona em lotes de 1–50 IDs distintos:

1. Capturar conteúdo/hash consistentes e configuração do modelo em transação curta.
2. Gerar embeddings via LangChain fora da transação de banco.
3. Abrir outra transação, bloquear configuração/atividade/índice, verificar referências e hash, validar vetor e publicar todo o lote atomicamente.

Mudança da origem durante a geração retorna 409 e não publica o lote. Falha do provedor retorna erro sanitizado, sem gravar resultado parcial. Modelos ainda não selecionados podem ser preparados. O adaptador não envia parâmetro `dimensions`: o provedor deve retornar a dimensão configurada, validada pelo servidor.

Alteração do hash ou inativação da atividade invalida os índices na mesma transação, por trigger: limpa vetor e marca `pendente`; hash/data da última geração bem sucedida permanecem como referência. Situações implementadas: `pendente` e `pronta`. Não há fila, tarefa persistida, estado `processando` ou registro durável de falha neste fluxo síncrono. Outros escritores de textos/termos precisam cumprir o contrato canônico de atualização do hash de D012.

Busca exige modelo de embeddings selecionado e cobertura atual integral; utiliza somente seus índices atuais e atividades ativas. Resultado contém ID, nome e similaridade. Similaridade não estabelece equivalência entre atividades nem comprova capacidade, formação ou disponibilidade.

## Recomendações e decisão

O LangGraph executa **recuperar → sugerir → validar**, com estado e saída tipados. LangChain usa adaptadores de embeddings e `ChatOpenAI.with_structured_output`, método `function_calling`. Conteúdo cadastral é tratado como dado no prompt; a validação posterior impede publicação de IDs/quantidades inventados. Referências: [OpenAIEmbeddings — LangChain](https://reference.langchain.com/python/langchain-openai/embeddings/base/OpenAIEmbeddings) e [LangGraph — grafos](https://docs.langchain.com/oss/python/langgraph/graph-api).

Critérios implementados:

- Pedido aberto em território ativo; referências de necessidade/unidade ativas.
- Ofertas ativas e administrativamente validadas, da atividade exata solicitada e do mesmo município da área, com pessoa/instituição ativa e cadastro validado.
- Recursos ativos, operacionais, quantidade total positiva, tipo ativo e responsável ativo/validado, no mesmo município; tipo solicitado ou vínculo com oferta candidata.
- Até 30 ofertas e 30 recursos por análise, com limites informados nas pendências. Ordenação por ID torna a seleção reproduzível para o mesmo conjunto cadastral.
- Busca semântica recupera contexto de atividades. Ela não amplia automaticamente as ofertas elegíveis para atividades consideradas semelhantes.

Não são avaliados requisitos profissionais, cursos obrigatórios, agenda, rotas, composição de equipe ou capacidade por período. Vínculo institucional não prova participação numa oferta. Serviço pode indicar pessoas/instituições candidatas, mas sua quantidade sugerida permanece **zero**, pois cobertura numérica não foi definida. Recursos solicitados têm quantidades limitadas ao item/total cadastrado; individual exige 1. Recursos de apoio a serviço precisam estar vinculados a uma oferta indicada.

A saída deve conter exatamente todos os itens vigentes do pedido, com IDs válidos, relações coerentes e sem duplicação indevida de candidatos. Soma de recursos do item deve coincidir com quantidade sugerida e não exceder o solicitado. Uso do mesmo estoque em itens distintos pode exceder o total global: gera pendência explícita, sem resolver reserva/alocação.

Após a chamada de IA, o serviço abre outra transação, bloqueia território/pedido, recarrega candidatos e compara o SHA-256 do contexto. Mudança relevante durante a análise retorna 409 e não grava recomendação. Modelos capturados precisam continuar cadastrados/ativos. A proposta é revalidada e as cinco tabelas são gravadas juntas. Chamadas externas não mantêm transação de banco aberta.

O cabeçalho guarda demanda, modelos de embeddings/texto, hash do contexto, data, justificativa, pendências e situação. Itens guardam FK do item solicitado, quantidade e justificativa. Pessoas/instituições guardam FKs reais, oferta de origem e papel; recursos guardam FK real e quantidade. Nomes são consultados por relacionamento. Guarda-se hash e referências, sem cópia integral imutável de todos os dados de entrada; correções cadastrais podem alterar nomes exibidos no histórico.

Situações implementadas: `gerada`, `aprovada`, `rejeitada`. A decisão é final e única, exige justificativa e registra data do servidor e `sub` do JWT administrativo. Aprovação exige contexto ainda atual; rejeição pode registrar descarte de análise desatualizada. Nova análise cria outro registro, preservando o anterior, sem estado automático `substituida`.

**Aprovar não reserva pessoas/recursos, não altera quantidades do pedido/estoque e não cria missão ou entrega.** A aprovação atesta somente a avaliação administrativa da sugestão.

## Rotas acrescentadas

Todas exigem JWT administrativo. Sucesso segue `{data,messages?}`; erros seguem ProblemDetails.

| Caminho em `/api/v1` | Operações |
|---|---|
| `/conexoes-ia`, `/modelos-ia` | GET/POST na coleção, GET/PUT/DELETE em `/{id}`; DELETE inativa. |
| `/demandas` | GET/POST na coleção, GET/PUT/DELETE em `/{id}`; itens no agregado. |
| `/areas-afetadas` | GET de referências ativas, com busca e paginação. |
| `/indices-atividade` | GET paginado, filtro opcional `id_modelo`; sem vetores na resposta. |
| `/indices-atividade/indexar` | POST com `id_modelo` e `ids_atividades`. |
| `/atividades/busca-semantica` | POST com `texto` (2–4000 caracteres) e `limite` (1–30). |
| `/demandas/{id}/recomendacoes` | POST gera e persiste análise; resposta 201. |
| `/recomendacoes`, `/recomendacoes/{id}` | GET paginado, filtro `id_demanda`, consulta de detalhe. |
| `/recomendacoes/{id}/decisao` | POST com `situacao` (`aprovada`/`rejeitada`) e `justificativa`. |

Listagens usam `limite` 1–100 e `deslocamento`. Conexões/modelos/demandas aceitam busca literal e histórico; demandas também filtram área. Esquemas completos no OpenAPI local.

## Evidências e trabalho restante

Verificação: **103 testes Python com PostgreSQL, mypy estrito em 105 arquivos, Ruff, build/typecheck Angular e 17 cenários de navegador**. Alembic sem divergências, preservação dos dados de 0001/0002/0003 até 0009 e ciclo downgrade/upgrade. Credenciais fictícias tiveram cifra, recuperação exata, substituição e ausência em respostas verificadas.

O navegador percorreu conexão/modelos → indexação → busca → demanda → LangGraph → decisão → nova análise/histórico. Usou LangChain real contra provedor HTTP fictício local, embeddings artificiais e sugestões determinísticas. Isso valida integração/contratos, sem medir qualidade semântica, qualidade de um LLM externo ou indicador acadêmico. Capturas e resultados em [frontend/verificacao](../frontend/verificacao/README.md).

Faltam selecionar/configurar modelos reais, verificar compatibilidade e pertinência das respostas, preparar demonstração acadêmica e medir tempo/qualidade. Login/usuários/perfis de produção, rotação completa de chaves e infraestrutura de implantação continuam pendentes. As 21 tabelas futuras permanecem fora deste incremento. Banco de desenvolvimento e protótipo independente não foram migrados/populados/alterados automaticamente.
