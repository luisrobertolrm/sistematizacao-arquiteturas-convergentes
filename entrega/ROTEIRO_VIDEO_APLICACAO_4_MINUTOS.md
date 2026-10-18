# Roteiro de Vídeo da Aplicação — RedeSolidária (Máximo de 4 Minutos)

**Duração Total:** Até 04:00 (240 segundos)  
**Formato:** Demonstração prática da aplicação (Screen Recording + Locução)  
**Foco:** Explicar **para que serve** a aplicação, **o que já existe implementado** (com tour pelas telas) e **o que falta** para evolução futura.

**Aplicação online:** <https://redesolidaria.myworklab.com.br/> — tela inicial com **Acesso administrativo** (login por token) e **cadastro de voluntário** pelo botão **Quero me voluntariar**.  
**Repositório (código-fonte):** <https://github.com/luisrobertolrm/sistematizacao-arquiteturas-convergentes/tree/main>

---

## Quadro-Resumo de Tempo

| Bloco | Tempo | Tema Principal | O que mostrar na tela |
|---|---|---|---|
| **1. Abertura e Para que Serve** | `00:00 – 00:40` | O problema da Defesa Civil, a Meta 3.1.3 do PN-PDC e o propósito da RedeSolidária | Tela inicial em `https://redesolidaria.myworklab.com.br/` |
| **2. O que Existe: Acesso e Cadastro Aberto** | `00:40 – 01:20` | Hero de incentivo ao voluntariado, autocadastro em tela própria, verificação por e-mail e botão **Gerar token admin** | Tela inicial (hero **Quero me voluntariar** + **Acesso administrativo**) → tela de **Cadastro de usuário** + **Verificação por e-mail** → **Gerar token admin** |
| **3. O que Existe: Rede, Capacidades e Mapa** | `01:20 – 02:15` | As 29 tabelas implementadas: Instituições, Pessoas/Qualificações, Atividades, Recursos e Mapa Leaflet | Navegação lateral: **Instituições**, **Pessoas**, **Atividades**, **Recursos** e **Desastres e áreas** (Mapa) |
| **4. O que Existe: IA (LangGraph) e Decisão** | `02:15 – 03:10` | Configuração de IA, Índices semânticos, Demandas e Recomendações com validação anti-alucinação | **Configuração de IA** → **Demandas e recomendações** (aprovar/rejeitar sugestão) |
| **5. O que Falta e Próximos Passos** | `03:10 – 04:00` | Limites atuais, as 21 tabelas operacionais futuras (missões/reservas), LLM de produção e autenticação final | Visão geral da aplicação / encerramento |

> **Ritmo:** roteiro calibrado para até 4 minutos em locução natural (~155 palavras/min). Mantenha as ações em tela sincronizadas com a fala; trechos entre colchetes são apenas direção de cena, não são narrados.

---

## Script Completo de Locução e Ações em Tela

### Bloco 1 — Para que serve a aplicação (`00:00 – 00:40`)

**[Cena em Tela]:** Abrir a tela inicial da **RedeSolidária** no navegador (`https://redesolidaria.myworklab.com.br/`).

**[Locução]:**
> "Olá! Vou apresentar a **RedeSolidária** — para que serve, o que já existe e o que ainda falta.
>
> Durante enchentes e deslizamentos, a Defesa Civil recebe milhares de voluntários e doações, mas as informações ficam espalhadas em planilhas e grupos de mensagens, o que atrasa a montagem de equipes qualificadas e gera envio duplicado de recursos.
>
> Alinhada à **Meta 3.1.3 do PN-PDC 2025–2035** — o cadastro nacional de voluntários institucionais —, a RedeSolidária é uma **plataforma de apoio à decisão**: conecta o cadastro de instituições, pessoas e recursos, o mapa das áreas afetadas, as demandas emergenciais e o cruzamento por Inteligência Artificial, sempre com validação humana final."

---

### Bloco 2 — O que existe: Cadastro Aberto, Verificação por E-mail e Token Admin (`00:40 – 01:20`)

**[Cena em Tela]:** Na tela inicial pública (`https://redesolidaria.myworklab.com.br/`):
1. Mostrar o **hero de incentivo ao voluntariado** ("A sua vontade de ajudar pode salvar vidas.") ao lado do painel **Acesso administrativo**.
2. Clicar em **Quero me voluntariar** para abrir a tela de **Cadastro de usuário**.
3. Preencher o formulário (Nome, E-mail, Município IBGE `3550308` — São Paulo/`SP`) e clicar em **Cadastrar usuário**; mostrar o selo amarelo `pendente`.
4. Em **Verificação por e-mail simples**, clicar em **Verificar por e-mail** e mostrar o selo virando verde (`validada`).
5. Clicar em **← Voltar** e, no painel **Acesso administrativo**, clicar em **Gerar token admin** e em **Acessar cadastros**.

**[Locução]:**
> "A aplicação integrada foi construída em **Angular 21**, **Python 3.13 com FastAPI**, **SQLAlchemy** e **PostgreSQL 18**, e está online em `redesolidaria.myworklab.com.br`.
>
> Na tela inicial, sem login, um **destaque incentiva o voluntariado**: clicando em **Quero me voluntariar**, abrimos a **tela de cadastro aberto**, onde qualquer pessoa informa nome, e-mail, município e UF — o registro nasce **pendente** e, pela **verificação por e-mail**, passa na hora para **validada**.
>
> De volta ao início, o botão **Gerar token admin** emite um JWT e dá acesso ao painel de gestão. Esse emissor é apenas para demonstração; em produção, será substituído por autenticação federada."

---

### Bloco 3 — O que existe: Cadastros da Rede, Capacidades, Recursos e Mapa (`01:20 – 02:15`)

**[Cena em Tela]:** Percorrer o menu lateral esquerdo:
1. Mostrar **Instituições** e **Pessoas** (clicar em *Vínculos e formação* de uma pessoa).
2. Clicar em **Atividades e unidades** e **Recursos e ofertas**.
3. Clicar em **Desastres e áreas**, abrir **Áreas e mapa** e mostrar o mapa **Leaflet / OpenStreetMap** com os polígonos e a gravidade.

**[Locução]:**
> "Na área administrativa, já temos **as 29 tabelas do escopo inicial** migradas no PostgreSQL via Alembic e integradas no frontend:
>
> - Em **Rede**: **Instituições** (com validação de CNPJ), **Pessoas** — inclusive quem acabou de se autocadastrar — e **Profissões e Cursos**, com vínculos, registros profissionais e certificados.
> - Em **Capacidades**: **Unidades**, **Categorias**, **Atividades** e seus **Termos**, com hash SHA-256 canônico recalculado a cada alteração.
> - Em **Recursos e ofertas**: lotes e equipamentos físicos — caminhões, barcos, água — e as ofertas de serviço de cada instituição ou voluntário.
> - Em **Desastres e áreas**, abrimos o **Mapa Leaflet / OpenStreetMap**, onde o administrador desenha os polígonos GeoJSON das áreas atingidas e registra a gravidade."

---

### Bloco 4 — O que existe: IA com LangGraph, Demandas e Decisão Administrativa (`02:15 – 03:10`)

**[Cena em Tela]:**
1. Clicar em **Configuração de IA**: mostrar as **três abas** — *Conexões de IA*, *Modelos de IA* e *Índices de atividades*. Dentro de **Índices de atividades**, demonstrar a **busca semântica** (campo *Necessidade* + botão **Buscar por significado**).
2. Clicar em **Demandas e recomendações**: selecionar uma demanda, abrir **Recomendações**, mostrar candidatos e pendências e os botões **Aprovar** / **Rejeitar sugestão**.

**[Locução]:**
> "Na parte de inteligência e operação, dois módulos estão prontos:
>
> - Em **Configuração de IA**, cadastramos conexões com credenciais criptografadas via Fernet, selecionamos modelos de *embedding* e de *texto*, preparamos os **índices vetoriais das atividades** e testamos a **busca semântica por cosseno**.
> - Em **Demandas e recomendações**, o gestor registra as necessidades de uma área e pede uma recomendação. Um grafo em **LangGraph** executa três etapas: recupera atividades por similaridade e candidatos por filtros; aciona o modelo via **LangChain**; e passa por um **validador determinístico anti-alucinação**, que garante que 100% dos IDs existem no banco e aponta déficits de estoque e conflitos.
> - Por fim, o administrador **aprova ou rejeita**, preservando o histórico de auditoria."

---

### Bloco 5 — O que falta: Limites Atuais e Evolução Futura (`03:10 – 04:00`)

**[Cena em Tela]:** Manter na tela de Recomendações ou voltar à visão geral da aplicação para o fechamento.

**[Locução]:**
> "E o que falta? Mapeamos quatro frentes:
>
> 1. As **21 tabelas operacionais** restantes (das 50 modeladas, 29 estão prontas): agenda e disponibilidade, **reserva de estoque**, abertura de **missões**, alocação de equipes e **entrega em campo**.
> 2. **Provedor real de IA**: a tubulação LangChain/LangGraph já passa em mais de 100 testes com provedor simulado; falta a chave de LLM em produção e a medição empírica da meta de **50% de redução** no tempo de triagem.
> 3. **Autenticação de produção e e-mail real (SMTP)**, com perfis de coordenador, instituição e voluntário.
> 4. **Expansão geográfica e vetorial**, com `pgvector` e **PostGIS**.
>
> A RedeSolidária já entrega uma base convergente sólida, testada de ponta a ponta e pronta para evoluir do apoio à decisão até a operação completa de resposta a desastres. Muito obrigado!"
