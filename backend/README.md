# RedeSolidária API — cadastros, território, demandas e IA

Python `>=3.13,<3.14`, testado com 3.13.12. Camadas: `web → business → infra → core`. A aplicação usa FastAPI, SQLAlchemy 2 e PostgreSQL, com mapeamento imperativo em `infra/configurations`; entidades de domínio não dependem do ORM. Processamento de IA fica em `business/graphs`.

Implementado até o incremento 6: cadastros, vínculos/qualificações, capacidades, recursos/ofertas, território, conexões/modelos de IA, demandas/itens, índices de atividades e recomendações/decisões. As nove migrações criam **29 tabelas**, além da versão Alembic. Auditoria por `sub`, inativação, validação, busca/paginação, JWT administrativo, envelope da skill e ProblemDetails são preservados.

LangGraph executa recuperação → sugestão → validação; LangChain integra embeddings e saída estruturada de texto. Conexões/modelos são normalizados, tokens cifrados com Fernet/chave externa e índices guardam somente vetor/hash da origem. Geração e decisão são persistidas. [Configuração, rotas e limites](../docs/ia-demandas-recomendacoes.md). Nenhum provedor ou credencial real foi configurado na validação.

## Preparar

Na raiz do projeto, PowerShell, com Python 3.13, uv, Node 22 e Docker:

```powershell
cd backend
python scripts/sync_manifest.py
uv sync --frozen
.venv\Scripts\python.exe scripts/setup_local.py
cd ..
docker compose -p redesolidaria-dev up -d postgres
cd backend
.venv\Scripts\python.exe -m alembic upgrade head
.venv\Scripts\python.exe -m uvicorn web.main:app --host 127.0.0.1 --port 8000
```

`project.toml` é o arquivo editável. O primeiro comando gera `pyproject.toml`, ignorado pelo Git, para interoperabilidade com uv/PyPA. Após mudar dependências: sincronizar o manifesto, executar `uv lock` e versionar `uv.lock`. Não editar o arquivo gerado. Dependências diretas, de desenvolvimento e de build têm versões exatas; o lock resolve as transitivas.

O setup local gera senha, segredo JWT e chave Fernet aleatórios em dois arquivos `.env` ignorados. Ele não imprime valores e recusa sobrescrita. Alternativamente, copiar os exemplos e configurar manualmente. A conexão padrão sem senha não substitui essa configuração. Execute comandos da API dentro de `backend` para carregar seu `.env`.

O Compose fixa a imagem PostgreSQL 18.3 por digest, publica apenas `127.0.0.1:55432` e usa volume próprio. `docker compose -p redesolidaria-dev stop` interrompe o banco preservando dados. Nenhuma migração é aplicada no startup da API. Revise alterações de schema antes de executar Alembic em bancos com dados.

## Acesso e interface

Em outro terminal, dentro de `backend`, gerar uma credencial de desenvolvimento:

```powershell
.venv\Scripts\python.exe -m web.autenticacao.emitir_token --subject admin-local --minutes 60
```

Copiar o token para a tela Angular de acesso administrativo. O emissor CLI funciona somente com `REDE_ENVIRONMENT=development`; não há endpoint público de emissão nem login de produção. A API valida assinatura HS256, emissor, audiência, expiração, sujeito e perfil `admin`. Sem segredo configurado, recusa operações protegidas. O frontend mantém o token em memória e o perde ao sair/recarregar.

Frontend em outro terminal:

```powershell
cd frontend
npm ci --ignore-scripts
npm start
```

Abrir `http://localhost:4200`. O proxy encaminha `/api` para a API local. OpenAPI: `http://127.0.0.1:8000/docs`. `/health` é liveness público, sem verificar banco. Dados de demonstração podem ser cadastrados pela tela; nenhuma população automática é executada.

| Método / caminho | Operação |
|---|---|
| `GET /api/v1/instituicoes` e `/pessoas` | Listar ativos, com `limite` de 1–100 e `deslocamento` não negativo. |
| `GET /api/v1/{cadastro}/{id}` | Consultar cadastro ativo. |
| `POST /api/v1/{cadastro}` | Criar cadastro. |
| `PUT /api/v1/{cadastro}/{id}` | Substituir campos editáveis do cadastro. |
| `DELETE /api/v1/{cadastro}/{id}` | Inativar preservando registro/auditoria; resposta 200 com envelope. |

`{cadastro}` representa `instituicoes`, `pessoas`, `profissoes` ou `cursos`, com rotas concretas. Profissões/cursos oferecem as mesmas cinco operações. Instituições/pessoas/profissões/cursos aceitam `busca` por trecho literal do nome, com 2–200 caracteres, além da paginação.

Vínculos usam `GET/POST /api/v1/pessoas/{pessoa_id}/instituicoes`, `/profissoes` ou `/cursos`, e `GET/PUT/DELETE` com `/{id}`. Leituras aceitam `incluir_inativos=true` para consulta administrativa dos registros inativados e referências inativas. Todos exigem JWT administrativo. Pessoa e referência devem estar ativas para criar/editar; uma referência inativada preserva o vínculo no histórico. O `pessoa_id` vem da rota e um vínculo de outra pessoa retorna 404.

Na interface: **Profissões e cursos** mantém os catálogos; **Pessoas → Vínculos e formação** registra participação, qualificação, validade, validação e renovações. Seletores possuem busca e paginação. Encerrar vínculo institucional é preencher `fim_em`; inativar corrige/exclui da seleção sem apagar o registro.

Sucesso: `{ "data": ... }`, com `messages` omitido quando vazio e campos nulos preservados. Erros: `application/problem+json`, sem envelope. Logs registram método/status/duração e classe de erro inesperado; não registram corpos, tokens ou mensagens brutas de integração.

Profissões/cursos recebem hash SHA-256 canônico v1 calculado pelo servidor; o cliente não o informa. Não há índice ou chamada RAG desses catálogos neste incremento. Unicidade, datas e limites da validação estão em [D011](../docs/decisoes-modelagem.md#d011--vínculos-e-qualificações-incremento-2). Referência de comprovante é somente identificador textual: não há upload, download ou verificação de certificado implementados.

Para atualizar uma instalação anterior, parar a API, executar em `backend` `.venv\Scripts\python.exe -m alembic upgrade head` e reiniciar. A revisão `0002_qualificacoes` acrescenta cinco tabelas, `0003_capacidades` acrescenta quatro, `0004_recursos_ofertas` acrescenta quatro, `0005_desastres_areas` acrescenta quatro, `0006_modelos_ia` duas, `0007_demandas` duas, `0008_indices` uma e `0009_recomendacoes` cinco; preservam os cadastros anteriores. Não executar o gerador de `.env` novamente sobre uma configuração existente. Nenhuma migração é aplicada no startup.

### Unidades, categorias, atividades e termos

`/api/v1/unidades-medida`, `/api/v1/categorias-atividade` e `/api/v1/atividades` possuem GET/POST na coleção e GET/PUT/DELETE em `/{id}`. GET aceita `limite` 1–100, `deslocamento`, `busca` 2–200 caracteres e `incluir_inativos=true`; detalhe também permite histórico. Todas as operações exigem JWT administrativo.

Código único e estável, normalizado para minúsculas: até 50 caracteres ASCII, números, hífen/sublinhado. Categoria/unidade são FKs ativas na criação/edição da atividade; inativá-las preserva o cadastro com aviso na interface. Unidade não informa automaticamente período ou conversão.

Termos usam GET/POST em `/api/v1/atividades/{atividade_id}/termos` e GET/PUT/DELETE em `/{id}`. Normalização de minúsculas/espaços e unicidade por atividade entre termos ativos. A rota fixa a atividade; leituras com `incluir_inativos=true` preservam o histórico. Cada alteração atualiza o SHA-256 canônico da atividade na mesma transação, com bloqueio para alterações concorrentes. Entrada semântica v1 e limites em [D012](../docs/decisoes-modelagem.md#d012--catálogo-de-atividades-e-unidades-incremento-3).

No Angular: **Atividades e unidades → Unidades de medida / Categorias de atividade / Atividades → Termos e sinônimos**. Primeiro cadastrar as referências; depois a atividade e seus termos. Busca de atividades é textual literal por nome, código, descrição ou termo ativo. Essa consulta cadastral permanece textual; indexação e busca semântica têm operações próprias no incremento 6.

O CNPJ é normalizado e único, inclusive entre registros inativados. Há validação de formato numérico/alfanumérico, sem afirmar verificação dos dígitos. Email de pessoa não é identidade civil nem é único. Município é validado quanto ao formato de sete dígitos; não há consulta de existência no catálogo IBGE. Coordenadas cadastrais são pareadas e limitadas, sem análise de acesso. O mapa das áreas afetadas tem contrato próprio descrito abaixo.

### Recursos e ofertas

`/api/v1/tipos-recurso`, `/api/v1/recursos` e `/api/v1/ofertas-atividade` oferecem GET/POST na coleção e GET/PUT/DELETE em `/{id}`, com JWT administrativo, paginação, busca literal e histórico (`incluir_inativos=true`). Tipos buscam nome/descrição; recursos também identificação; ofertas buscam atividade/responsável/município/descrição complementar.

Vínculos usam `/api/v1/ofertas-atividade/{oferta_id}/recursos` e `/{id}`. O pai vem da rota; vínculo de outra oferta retorna 404. Oferta inativada permite histórico e inativação de vínculos, mas não criação/edição. Unicidade entre linhas ativas permite novo registro após inativação.

Responsável exclusivo entre pessoa/instituição; recursos individuais exigem quantidade 1 e estoque admite zero. Quantidades usam Decimal com até quatro casas. Capacidade de oferta positiva exige unidade da atividade. Unidade/modo do tipo utilizado e unidade da atividade com capacidades declaradas são protegidos contra troca. Referências principais de recurso/oferta/vínculo ficam fixas. Validação administrativa gera a data no servidor e não comprova aptidão.

No Angular, **Recursos e ofertas** reúne os cadastros e **Ofertas de atividades → Recursos da oferta**. Quantidade prevista não reserva/debita estoque; recurso pode pertencer a outro responsável, sem autorização de uso implícita. Contrato semântico de tipo de recurso e demais regras em [D013](../docs/decisoes-modelagem.md#d013--recursos-e-ofertas-incremento-4).

### Desastres e áreas afetadas

`/api/v1/tipos-desastre` e `/api/v1/desastres` possuem GET/POST na coleção e GET/PUT/DELETE em `/{id}`. Áreas usam `/api/v1/desastres/{id_desastre}/areas` e `/{id}`; o pai é fixado pela rota e uma área de outra ocorrência retorna 404. Todas as operações exigem JWT administrativo. Leituras aceitam paginação, busca literal e `incluir_inativos=true`.

POST/PUT da ocorrência recebem as classificações juntas: de 1 a 20 tipos distintos, exatamente um principal. A troca do principal ocorre atomicamente; remoções inativam a associação, preservando histórico. Coordenadora e tipos devem estar ativos ao criar/editar. Início/encerramento exigem fuso e são normalizados para UTC. Encerramento exige data coerente e preserva a ocorrência ativa; reabertura não está implementada. Inativação da ocorrência preserva as áreas, bloqueia criação/edição/avaliação e permite histórico/inativação de filhos.

Geometria é `Polygon` GeoJSON tipado em JSONB: um anel fechado, 3–200 vértices distintos, sem buracos, cruzamentos ou sobreposição de bordas. Longitude −180..180, latitude −85..85 e amplitude longitudinal menor que 180°. A API normaliza a orientação exterior. Não há PostGIS, geocodificação, verificação de limite municipal, área geodésica, rotas ou análise de acesso. O Angular usa Leaflet/OpenStreetMap e apresenta as áreas da página consultada.

`ultima_avaliacao_em` é gerada no servidor na criação e quando gravidade/situação mudam. Correções de nome, descrição, município ou geometria preservam essa data. `POST /api/v1/desastres/{id_desastre}/areas/{id}/avaliar` recebe gravidade/situação e registra nova avaliação mesmo com valores iguais. Não há tabela de versões das avaliações. Contratos, escalas e limites em [D014](../docs/decisoes-modelagem.md#d014--desastres-e-território-incremento-5).

### Conexões, modelos, demandas e recomendações

As revisões 0006–0009 e as telas **Configuração de IA** e **Demandas e recomendações** completam o fluxo inicial. Configurar `REDE_ENCRYPTION_KEY_ID` e `REDE_IA_URLS_PERMITIDAS` conforme [.env.example](.env.example); lista vazia bloqueia chamadas externas. O token entra pelo cadastro administrativo e nunca volta na resposta. Token nulo no PUT preserva o valor existente; identidade de conexão/modelo referenciada é estável.

Preparar embeddings de todas as atividades ativas antes de selecionar o modelo de busca; modelo de texto é selecionado separadamente. Demandas recebem cabeçalho/itens juntos, com unidades exatas e sem transições de execução. Índices usam arrays PostgreSQL, dimensão por modelo e busca exata até 5000 vetores. Mudanças semânticas invalidam vetores atomicamente.

Recomendação valida IDs, quantidades e contexto atual antes de gravar; decisão exige justificativa e conserva histórico. Aprovação não altera pedido/estoque. Contratos, todos os endpoints, sequência de operação e limitações em [IA, demandas e recomendações](../docs/ia-demandas-recomendacoes.md).

## Verificar

Dentro de `backend`:

```powershell
.venv\Scripts\ruff.exe check core infra business web scripts tests
.venv\Scripts\mypy.exe
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts/test_postgres.py
```

O pytest comum pula os 47 testes de persistência sem `TEST_DATABASE_URL`. O último comando cria PostgreSQL exclusivo em porta aleatória, verifica atualização de 0001/0002/0003 até 0009 com dados anteriores preservados, executa `alembic check` e **103 testes**, reverte/reaplica migrações e remove seu container/volume. Só aceita `redesolidaria_test`; não acessa a base de desenvolvimento. Requer a imagem fixada disponível no Docker; se necessário, obtê-la com `docker pull postgres@sha256:a9abf4275f9e99bff8e6aed712b3b7dfec9cac1341bba01c1ffdfce9ff9fc34a`.

Para incluir a interface integrada, executar `npm run build` em `frontend` e, em `backend`, `.venv\Scripts\python.exe scripts/test_postgres.py --frontend`. Inicia API temporária com segredo/token exclusivos e executa 17 cenários em Edge/Chrome headless com perfil próprio. O teste serve o build em porta aleatória local, simula os tiles do mapa e inicia provedor HTTP fictício para LangChain/LangGraph, fecha sua API/navegador/provedor e remove o banco temporário ao terminar. Não utiliza o perfil pessoal ou banco configurado em desenvolvimento. Evidências e limites em [frontend/verificacao](../frontend/verificacao/README.md).

Em `frontend`, `npm run build` compila aplicação e templates com verificação estrita; `npm run typecheck` faz apenas verificação. `package-lock.json` fixa dependências transitivas. Angular framework 21.2.25, CLI/build 21.2.26 e TypeScript 5.9.3 foram escolhidos para o Node 22.22.2 disponível, sem modificar o runtime global.

Execução validada: **103 testes com PostgreSQL real, schema sem divergências, dados anteriores preservados, ciclo de migração, mypy estrito/Ruff, build/typecheck Angular e 17 cenários de interface integrada**. Detalhes no [estado da implementação](../docs/implementacao-inicial.md).

Pendências do MVP e finalidade das tabelas: [controle de tarefas](../docs/controle-tarefas.md). Contexto complementar e exercício histórico: [simulações](../simulacoes/README.md).
