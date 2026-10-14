# Roteiro de Pitch — RedeSolidária (Vídeo de até 5 Minutos)

**Disciplina:** H3-AC — Arquiteturas Convergentes (CEUB)  
**Atividade:** Sistematização — Desafio de Computação Aplicada à Proteção e Defesa Civil  
**Aluno:** Luis Roberto de Moraes  
**Projeto:** RedeSolidária — Plataforma Integrada de Apoio à Decisão para Cadastramento e Mobilização Inteligente de Voluntários Institucionais e Recursos em Desastres  
**Duração Total:** 05 minutos (300 segundos)

---

## Estrutura do Roteiro e Cronograma

| Bloco | Minutagem | Foco da Fala | Pergunta Obrigatória do Edital | Tela / Slide Sugerido |
|---|---|---|---|---|
| **Bloco 1** | 00:00 – 00:30 | Introdução & Identificação | Apresentação pessoal e do projeto | Slide 1 (Capa Oficial) |
| **Bloco 2** | 00:30 – 01:25 | O Diagnóstico do Problema Real | **Pergunta 1: Qual é o problema?** | Slide 2 (Problema & Gargalos) |
| **Bloco 3** | 01:25 – 02:10 | Alinhamento com o PN-PDC 2025–2035 | **Pergunta 2: Qual meta está sendo trabalhada?** | Slide 3 (Meta Oficial 3.1.3) |
| **Bloco 4** | 02:10 – 03:05 | A Convergência Tecnológica | **Pergunta 3: Como a Computação contribui?** | Slide 4 & 5 (Arquitetura & Camadas) |
| **Bloco 5** | 03:05 – 04:15 | Funcionamento da Solução na Prática | **Pergunta 4: Como a solução funciona?** | Slide 6 / Telas do Protótipo (Mapa & IA) |
| **Bloco 6** | 04:15 – 04:50 | Mensuração e Indicador de Resultado | **Pergunta 5: Como será medido o resultado?** | Slide 7 (Indicador 50% & Testes) |
| **Bloco 7** | 04:50 – 05:00 | Conclusão & Encerramento | Fechamento institucional e humanitário | Slide 8 (Conclusão & Fechamento) |

---

## Transcrição Integral da Fala (Fala Sugerida Segundo a Segundo)

### [00:00 – 00:30] Abertura e Apresentação
> *(Câmera aberta ou Slide 1 projetado)*  
> "Olá a todos! Meu nome é **Luis Roberto de Moraes**, sou aluno de Computação no **Centro Universitário de Brasília (CEUB)**.  
> Apresento hoje o projeto **RedeSolidária**, desenvolvido para a disciplina de **Arquiteturas Convergentes** no âmbito da Sistematização sobre *Computação Aplicada à Proteção e Defesa Civil*.  
> A RedeSolidária é uma plataforma computacional convergente de apoio à tomada de decisão para o cadastramento estruturado e a mobilização inteligente de voluntários institucionais e recursos materiais durante situações de desastres socioambientais."

---

### [00:30 – 01:25] Pergunta 1: Qual é o problema?
> *(Projetar Slide 2 — O Problema Real)*  
> "Respondendo à primeira pergunta obrigatória: **Qual é o problema?**  
> Diante do agravamento das mudanças climáticas e da ocorrência de enchentes severas e deslizamentos de terra — como os presenciados em Petrópolis, no Litoral Norte de São Paulo e no Rio Grande do Sul —, presenciamos uma enorme comoção pública com milhares de voluntários e toneladas de doações chegando às áreas afetadas.  
> Porém, o grande gargalo da Proteção e Defesa Civil está na **crônica fragmentação de informações e na desorganização das capacidades**:  
> Os cadastros ficam espalhados em planilhas locais desconexas, fichas em papel e grupos de mensagens instantâneas;  
> Os coordenadores não sabem com antecedência quem realmente possui qualificação técnica comprovada — como socorristas, médicos, condutores náuticos ou operadores de maquinário pesado;  
> E o resultado é dramático: voluntários despreparados são enviados a áreas de alto risco, recursos materiais essenciais são alocados em duplicidade, e pedidos urgentes de socorro demoram horas ou dias para serem triados nas salas de crise."

---

### [01:25 – 02:10] Pergunta 2: Qual meta do PN-PDC está sendo trabalhada?
> *(Projetar Slide 3 — Alinhamento PN-PDC 2025–2035)*  
> "Para enfrentar esse desafio concreto, alinhamos nosso projeto à segunda pergunta: **Qual meta do Plano Nacional de Proteção e Defesa Civil estamos trabalhando?**  
> O projeto fundamenta-se na **Diretriz 3** e no **Objetivo 3.1** do PN-PDC 2025–2035 — que visa aprimorar a capacidade de resposta a desastres.  
> A meta específica escolhida é a **Meta 3.1.3: 'Criar cadastro nacional de voluntários institucionais para formar rede para atuar na resposta a desastres'**.  
> Esta meta pertence ao **Eixo de Resposta**, com prazo oficial de cumprimento até **2031** (médio prazo), sob responsabilidade da Secretaria Nacional de Proteção e Defesa Civil (Sedec/MIDR), tendo como indicador oficial a criação do cadastro nacional.  
> No nosso projeto, respeitamos estritamente a exigência do termo 'institucionais': todo voluntário possui vínculo com uma instituição parceira — seja Cruz Vermelha, universidade, cooperativa ou ONG —, garantindo governança, validação de diplomas e coordenação articulada em rede."

---

### [02:10 – 03:05] Pergunta 3: Como a Computação contribui para atingir essa meta?
> *(Projetar Slide 4 e 5 — Arquitetura Convergente & Pipeline LangGraph)*  
> "Terceira pergunta: **Como a Computação contribui para atingir essa meta?**  
> A computação transforma o cenário de crise através da **convergência tecnológica de quatro componentes fundamentais**:  
> Primeiro, um **Frontend Web SPA e Sistema de Informação Geográfica (Angular 21 + Leaflet)**, permitindo ao gestor visualizar a cartografia municipal e delimitar polígonos das áreas atingidas diretamente no mapa;  
> Segundo, um **Backend robusto e fortemente tipado (Python 3.13 com FastAPI e SQLAlchemy)** em arquitetura limpa em camadas, garantindo validação de integridade e mensagens padronizadas RFC 9457;  
> Terceiro, um **Banco de Dados Relacional e Georreferenciado (PostgreSQL 18 com Alembic)**, modelando 29 tabelas iniciais com integridade estrita e persistência auditável;  
> E quarto, um **Motor de Inteligência Artificial Cognitiva orquestrado com LangGraph e LangChain**, que combina busca vetorial por similaridade de cosseno com embeddings para compreender pedidos em linguagem natural e cruzar com as capacidades cadastradas em segundos, protegido por guardrails determinísticos que eliminam qualquer risco de alucinação."

---

### [03:05 – 04:15] Pergunta 4: Como a solução funciona?
> *(Projetar Slide 6 ou demonstração das telas do protótipo: mapa.png, visao-geral.png, recomendacao.png)*  
> "Quarta pergunta: **Como a solução funciona na prática?**  
> Vamos ao fluxo operacional da plataforma:  
> 1. Na etapa de **Entrada**, as instituições cadastram previamente seus voluntários, com comprovantes de profissões e cursos válidos, além do inventário de recursos físicos como caminhões, barcos e água potável.  
> 2. O coordenador abre o **Mapa da Ocorrência**, seleciona o município — exemplificado no piloto pelo município de *Vale Azul* — e desenha no mapa os polígonos das áreas impactadas, como a *Várzea* e a *Encosta*, atribuindo níveis de gravidade.  
> 3. Naquela área, o gestor registra a **Demanda Emergencial** — por exemplo: necessidade urgente de 300 litros de água potável e equipe para resgate.  
> 4. O motor de IA é acionado: o nó de busca semântica identifica as atividades compatíveis; o nó relacional consulta as ofertas de instituições locais com certificados válidos; e o LLM formula um **dossiê analítico com a sugestão fundamentada**.  
> 5. Crucial: o nó validador determinístico faz a checagem anti-alucinação — ele verifica se os IDs existem no banco real, calcula se há déficit de estoque e avisa se um caminhão está com horário sobreposto em outro chamado.  
> 6. Na **Saída**, o gestor público avalia as sugestões, lê as justificativas e as pendências, e registra sua **Decisão Administrativa** — aprovando ou rejeitando a recomendação com parecer formal e data, mantendo a governança humana no centro da resposta (*Human-in-the-loop*)."

---

### [04:15 – 04:50] Pergunta 5: Como será medido o resultado?
> *(Projetar Slide 7 — Indicador Mensurável & Validação)*  
> "Quinta pergunta: **Como será medido o resultado da solução?**  
> Definimos um indicador acadêmico rigoroso e mensurável: a **Taxa de Redução no Tempo Médio de Triagem e Formação de Equipes Qualificadas**.  
> A meta estabelecida é uma **redução de pelo menos 50% no tempo** necessário para que um coordenador monte e valide uma equipe compatível com uma demanda complexa, comparando o processo manual em planilhas dispersas contra a triagem assistida pela RedeSolidária.  
> A fórmula é direta: `Redução (%) = [(Tempo Médio Manual - Tempo Médio Assistido) / Tempo Médio Manual] * 100`.  
> E como salvaguarda operacional, adicionamos o critério de qualidade: **Taxa de Pertinência Cadastral superior a 95%**. Ganho de tempo com sugestões inválidas é computado como falha.  
> Na nossa bateria de validação e simulação em memória, executamos 54 cenários de teste automatizados com **54 verificações OK e zero falhas**, comprovando a robustez dos contratos, chaves estrangeiras e guardrails anti-alucinação."

---

### [04:50 – 05:00] Conclusão e Fechamento
> *(Projetar Slide 8 — Conclusão & Agradecimento)*  
> "Em conclusão, a RedeSolidária demonstra como a Ciência da Computação e as Arquiteturas Convergentes podem apoiar estrategicamente o Brasil no cumprimento do PN-PDC 2025–2035, transformando tecnologia em agilidade, segurança e vidas salvas na Proteção e Defesa Civil.  
> Muito obrigado!"
