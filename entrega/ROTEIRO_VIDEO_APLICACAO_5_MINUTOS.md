# Roteiro de Vídeo da Aplicação — RedeSolidária (Máximo de 5 Minutos)

**Duração Total:** Até 05:00 (300 segundos)  
**Formato:** Demonstração prática da aplicação (Screen Recording + Locução)  
**Foco:** Explicar **para que serve** a aplicação, **o que já existe implementado** (com tour pelas telas) e **o que falta** para evolução futura.

**Aplicação online:** <https://redesolidaria.myworklab.com.br/> — tela inicial com **Acesso administrativo** (login por token) e **cadastro de voluntário** pelo botão **Quero me voluntariar**.  
**Repositório (código-fonte):** <https://github.com/luisrobertolrm/sistematizacao-arquiteturas-convergentes/tree/main>

---

## Quadro-Resumo de Tempo

| Bloco | Tempo | Tema Principal | O que mostrar na tela |
|---|---|---|---|
| **1. Abertura e Para que Serve** | `00:00 – 00:55` | O problema da Defesa Civil, a Meta 3.1.3 do PN-PDC e o propósito da RedeSolidária | Tela inicial em `https://redesolidaria.myworklab.com.br/` |
| **2. O que Existe: Acesso e Cadastro Aberto** | `00:55 – 01:45` | Hero de incentivo ao voluntariado, autocadastro em tela própria, verificação por e-mail e botão **Gerar token admin** | Tela inicial (hero **Quero me voluntariar** + **Acesso administrativo**) → tela de **Cadastro de usuário** + **Verificação por e-mail** → **Gerar token admin** |
| **3. O que Existe: Rede, Capacidades e Mapa** | `01:45 – 02:50` | As 29 tabelas implementadas: Instituições, Pessoas/Qualificações, Atividades, Recursos e Mapa Leaflet | Navegação lateral: **Instituições**, **Pessoas**, **Atividades**, **Recursos** e **Desastres e áreas** (Mapa) |
| **4. O que Existe: IA (LangGraph) e Decisão** | `02:50 – 03:55` | Configuração de IA, Índices semânticos, Demandas e Recomendações com validação anti-alucinação | **Configuração de IA** → **Demandas e recomendações** (aprovar/rejeitar sugestão) |
| **5. O que Falta e Próximos Passos** | `03:55 – 05:00` | Limites atuais, as 21 tabelas operacionais futuras (missões/reservas), LLM de produção e autenticação final | Visão geral da aplicação / encerramento |

---

## Script Completo de Locução e Ações em Tela

### Bloco 1 — Para que serve a aplicação (`00:00 – 00:55`)

**[Cena em Tela]:** Abrir a tela inicial da **RedeSolidária** no navegador (`https://redesolidaria.myworklab.com.br/`).

**[Locução]:**
> "Olá! Neste vídeo vou apresentar a aplicação **RedeSolidária**, explicando **para que ela serve**, **o que já existe implementado** e **o que ainda falta** para as próximas etapas.
>
> **Para que serve a RedeSolidária?**  
> Durante desastres como enchentes e deslizamentos, a Defesa Civil recebe milhares de voluntários e doações, mas sofre com informações espalhadas em planilhas e grupos de mensagens. Isso atrasa a montagem de equipes qualificadas e gera envio duplicado ou inadequado de recursos.
>
> Alinhada à **Meta 3.1.3 do Plano Nacional de Proteção e Defesa Civil (PN-PDC 2025–2035)** — que prevê a criação de um cadastro nacional de voluntários institucionais —, a RedeSolidária serve como uma **plataforma de apoio à decisão**.  
> Ela conecta quatro pontas em um fluxo único: o cadastro prévio de instituições, pessoas e recursos; o mapeamento das áreas afetadas; a abertura de demandas emergenciais; e o cruzamento inteligente por Inteligência Artificial para sugerir ao gestor público quem e o que mobilizar, sempre com validação humana final."

---

### Bloco 2 — O que existe: Cadastro Aberto, Verificação por E-mail e Token Admin (`00:55 – 01:45`)

**[Cena em Tela]:** Na tela inicial pública (`https://redesolidaria.myworklab.com.br/`):
1. Mostrar o **hero de incentivo ao voluntariado** ("A sua vontade de ajudar pode salvar vidas.") ao lado do painel **Acesso administrativo**.
2. Clicar no botão **Quero me voluntariar** para abrir a tela de **Cadastro de usuário**.
3. Preencher rapidamente o formulário (Nome, E-mail, Município IBGE `3550308` — São Paulo/`SP`, o mesmo município da base de demonstração já carregada) e clicar em **Cadastrar usuário**; mostrar o cartão criado com o selo amarelo `pendente`.
4. Na seção **Verificação por e-mail simples**, clicar em **Verificar por e-mail** e mostrar o selo mudando para verde (`validada`).
5. Clicar em **← Voltar** para retornar à tela inicial e, no painel **Acesso administrativo**, clicar em **Gerar token admin** (que preenche o campo `#token`) e em **Acessar cadastros**.

**[Locução]:**
> "Vamos ver **o que já existe e funciona na aplicação integrada**, construída em **Angular 21**, **Python 3.13 com FastAPI**, **SQLAlchemy** e banco **PostgreSQL 18**, disponível online em `redesolidaria.myworklab.com.br`.
>
> Logo na tela inicial, sem precisar de login, a RedeSolidária convida o cidadão a participar: um **destaque incentiva o voluntariado** e, com um clique em **Quero me voluntariar**, abrimos a **tela de cadastro aberto**. Ali, qualquer voluntário ou solicitante informa nome, e-mail, município IBGE e UF; ao cadastrar, o registro nasce com situação **pendente**.  
> Na mesma tela, a **verificação por e-mail simples**: ao confirmar o e-mail cadastrado e clicar em **Verificar por e-mail**, a API valida o vínculo na hora e atualiza a situação cadastral para **validada**.
>
> De volta à tela inicial, no painel de **Acesso administrativo**, usamos o botão **Gerar token admin**: com um clique, o backend emite um token JWT assinado e preenche o campo de acesso, permitindo clicar em **Acessar cadastros** e entrar no painel de gestão. Esse emissor rápido existe apenas para demonstração — em produção será substituído por autenticação federada."

---

### Bloco 3 — O que existe: Cadastros da Rede, Capacidades, Recursos e Mapa (`01:45 – 02:50`)

**[Cena em Tela]:** Percorrer o menu lateral esquerdo:
1. Mostrar **Instituições** e **Pessoas** (clicar em *Vínculos e formação* de uma pessoa para exibir vínculos institucionais, profissões e cursos).
2. Clicar em **Atividades e unidades** e **Recursos e ofertas**.
3. Clicar em **Desastres e áreas**, abrir **Áreas e mapa** de uma ocorrência e mostrar o mapa interativo **Leaflet / OpenStreetMap** com os polígonos desenhados e a avaliação de gravidade.

**[Locução]:**
> "Dentro da área administrativa, já temos **todas as 29 tabelas do escopo inicial migradas no PostgreSQL via Alembic e 100% integradas no frontend**:
>
> - No grupo **Rede**, gerenciamos **Instituições** (ONGs, órgãos públicos, empresas com validação de CNPJ), **Pessoas** (incluindo quem acabou de se autocadastrar) e o catálogo de **Profissões e Cursos**. Dentro de cada pessoa, controlamos seus vínculos institucionais sem sobreposição de datas, seus registros profissionais e certificados de cursos.
> - No grupo **Capacidades**, temos **Unidades de medida**, **Categorias**, **Atividades** e seus **Termos e sinônimos**. Cada alteração recalcula automaticamente um hash SHA-256 canônico na origem.
> - Em **Recursos e ofertas**, separamos o catálogo da capacidade real: cadastramos lotes e equipamentos físicos — como caminhões, barcos e água potável — e as ofertas de serviços de cada instituição ou voluntário.
> - Em **Desastres e áreas**, registramos ocorrências com múltiplos tipos de desastre e abrimos o **Mapa interativo em Leaflet e OpenStreetMap**, onde o administrador desenha polígonos GeoJSON das áreas atingidas e registra a avaliação de gravidade."

---

### Bloco 4 — O que existe: IA com LangGraph, Demandas e Decisão Administrativa (`02:50 – 03:55`)

**[Cena em Tela]:**
1. Clicar em **Configuração de IA**: mostrar as **três abas** — *Conexões de IA*, *Modelos de IA* e *Índices de atividades*. Dentro da aba **Índices de atividades**, demonstrar também a **busca semântica** (campo *Necessidade* + botão **Buscar por significado**), que fica nessa mesma aba.
2. Clicar em **Demandas e recomendações**: selecionar uma demanda, abrir **Recomendações da demanda**, mostrar os candidatos sugeridos, as pendências apontadas e os botões **Aprovar sugestão** / **Rejeitar sugestão**.

**[Locução]:**
> "Na parte de inteligência e operação, temos dois módulos centrais prontos:
>
> - Em **Configuração de IA**, cadastramos conexões com credenciais criptografadas via Fernet, selecionamos modelos de *embedding* e de *inferência de texto*, preparamos os **índices vetoriais das atividades** e testamos a **busca semântica por cosseno**.
> - Em **Demandas e recomendações**, o gestor registra os itens de necessidade de uma área afetada e solicita uma recomendação. Nesse momento, um grafo em **LangGraph** executa três etapas: recupera atividades por similaridade semântica e candidatos por filtros estruturados; aciona o modelo via **LangChain**; e passa por um **validador determinístico anti-alucinação**. Esse guardrail garante que 100% dos IDs sugeridos existem no banco, evita aprovar análises se o pedido mudou e explicita déficits de estoque ou alertas de compartilhamento.
> - Por fim, o administrador analisa a justificativa e registra sua **decisão formal de aprovar ou rejeitar**, preservando todo o histórico de auditoria."

---

### Bloco 5 — O que falta: Limites Atuais e Evolução Futura (`03:55 – 05:00`)

**[Cena em Tela]:** Manter na tela de Recomendações ou voltar à visão geral da aplicação para o fechamento.

**[Locução]:**
> "E **o que falta** para completar a visão total do sistema? De forma transparente, mapeamos quatro frentes de evolução:
>
> 1. **Acoplamento das 21 tabelas operacionais de execução em campo**: das 50 tabelas modeladas no projeto, 29 estão prontas (focadas em apoio à decisão). Faltam as 21 tabelas de operação pós-aprovação: controle de **agenda e disponibilidade por horário**, requisitos técnicos detalhados de equipamentos, **reserva transacional de estoque**, abertura e despacho de **missões**, alocação de equipes e confirmação de **entrega efetiva** em campo.
> 2. **Provedor real de IA e medição empírica do indicador**: toda a tubulação LangChain/LangGraph já passa em mais de 100 testes automatizados usando provedor HTTP simulado; falta conectar uma chave de LLM comercial em produção e realizar o teste comparativo com usuários para aferir na prática a meta de 50% de redução no tempo de triagem.
> 3. **Autenticação de produção e servidor de e-mail real (SMTP)**: evoluir o emissor rápido de token admin e a verificação local de e-mail para autenticação federada com perfis granulares (coordenador, instituição e voluntário), disparo real de e-mails transacionais e upload de arquivos de comprovantes.
> 4. **Expansão geográfica e vetorial**: habilitar índices semânticos também para profissões, cursos e tipos de recurso com extensão `pgvector`, além de rotas e análise espacial avançada com PostGIS.
>
> Com isso, a RedeSolidária já entrega uma base arquitetural convergente sólida, testada de ponta a ponta e pronta para evoluir do apoio à decisão até a operação completa de resposta a desastres. Muito obrigado!"
