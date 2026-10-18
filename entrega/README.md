# Pacote Oficial de Entrega — Sistematização H3-AC

**Instituição:** Centro Universitário de Brasília (CEUB)  
**Disciplina:** H3-AC — Arquiteturas Convergentes  
**Aluno:** Luis Roberto de Moraes  
**Projeto:** RedeSolidária — Plataforma Integrada de Apoio à Decisão para Cadastramento e Mobilização Inteligente de Voluntários Institucionais e Recursos em Desastres  
**Tema Geral:** Desafio de Computação Aplicada à Proteção e Defesa Civil (PN-PDC 2025–2035)

---

## 1. Visão Geral dos Arquivos Disponibilizados na Pasta `entrega/`

Esta pasta reúne a totalidade dos artefatos técnicos, relatórios formais, apresentações, roteiros e diagramas exigidos pelo edital de Sistematização:

| Arquivo | Formato | Descrição e Finalidade |
|---|---|---|
| [`Entrega_Sistematizacao_RedeSolidaria.pdf`](Entrega_Sistematizacao_RedeSolidaria.pdf) | PDF (Vetor) | **Documento Principal Oficial da Entrega (19 páginas).** Formatado estritamente com base no padrão visual do curso anterior (Capa com brasão/padrão CEUB, títulos `#1F2A44` e `#2E3B55`, fontes Calibri/Consolas, sumário estruturado, tabelas corporativas, diagramas de alta resolução e evidências de simulação). |
| [`Entrega_Sistematizacao_RedeSolidaria.docx`](Entrega_Sistematizacao_RedeSolidaria.docx) | Word DOCX | Versão editável completa em Microsoft Word do documento principal, preservando estilos, tabelas, formatação de capa e imagens incorporadas. |
| [`documento_entrega.html`](documento_entrega.html) | HTML5 / CSS3 | Fonte original do documento formatado para impressão (`@page A4`), compatível com qualquer navegador web. |
| [`ROTEIRO_PITCH_5_MINUTOS.md`](ROTEIRO_PITCH_5_MINUTOS.md) | Markdown | **Roteiro completo do Pitch de até 5 minutos.** Estruturado segundo a segundo (00:00 a 05:00), respondendo obrigatoriamente às 5 perguntas exigidas pelo edital, com texto integral da fala e indicação de slides/telas. |
| [`ROTEIRO_PITCH_5_MINUTOS.pdf`](ROTEIRO_PITCH_5_MINUTOS.pdf) | PDF | Versão diagramada em PDF do roteiro de gravação do pitch. |
| [`SLIDES_APRESENTACAO_PITCH.html`](SLIDES_APRESENTACAO_PITCH.html) | Apresentação Web | **Apresentação de Slides Executiva (8 slides)** em HTML interativo (formato 16:9 paisagem). Pronta para ser projetada ou gravada durante o vídeo de pitch. |
| [`SLIDES_APRESENTACAO_PITCH.pdf`](SLIDES_APRESENTACAO_PITCH.pdf) | PDF (A4 Paisagem) | Versão em PDF dos slides para projeção ou anexação acadêmica. |
| [`imagens/`](imagens/) | Pasta | Diretório com todos os diagramas arquiteturais e telas do protótipo (`arquitetura_sistema.svg`, `fluxo_cognitivo_langgraph.svg`, `visao-geral.png`, `mapa.png`, `recomendacao.png`). |
| [`Entrega_Sistematizacao_Luis_Roberto_Moraes.zip`](Entrega_Sistematizacao_Luis_Roberto_Moraes.zip) | Arquivo ZIP | **Pacote unificado da entrega** contendo todos os artefatos, conforme solicitado no Item 10 do edital. |

---

## 2. Matriz de Conformidade com os 17 Itens Exigidos no Edital

O edital de Sistematização (Seção 10, pág. 6) estabelece que a entrega deve contemplar obrigatoriamente 17 tópicos. Abaixo demonstra-se onde cada um foi abordado:

| Nº | Item Obrigatório do Edital | Onde está documentado | Resumo do Conteúdo |
|:---:|---|---|---|
| **1** | Nome do projeto | Capa e Seção 1 do PDF/DOCX | **RedeSolidária** |
| **2** | Integrante | Capa e Seção 1 do PDF/DOCX | **Luis Roberto de Moraes** (CEUB) |
| **3** | Problema | Seção 2 do PDF/DOCX | Responde às 4 perguntas: O que está acontecendo? Quem é afetado? Onde ocorre? Por que a computação ajuda? |
| **4** | Público afetado | Seção 2.2 do PDF/DOCX | População atingida, agentes de Defesa Civil, voluntários e instituições parceiras. |
| **5** | Meta do PN-PDC selecionada | Seção 3.1 do PDF/DOCX | **Meta 3.1.3:** *"Criar cadastro nacional de voluntários institucionais para formar rede para atuar na resposta a desastres."* |
| **6** | Objetivo do PN-PDC relacionado | Seção 3.2 do PDF/DOCX | **Objetivo 3.1:** *"Aprimorar as capacidades de atuação na resposta a desastres"* (vinculado à Diretriz 3). |
| **7** | Eixo de atuação | Seção 3.3 do PDF/DOCX | **Resposta** |
| **8** | Prazo da meta | Seção 3.3 do PDF/DOCX | **Médio Prazo (até 2031)**, conforme Decreto nº 12.652/2025. |
| **9** | Indicador da meta | Seção 3.3 do PDF/DOCX | *"Cadastro nacional criado"* (indicador oficial do MIDR/Sedec). |
| **10** | Solução proposta | Seção 4 do PDF/DOCX | Plataforma integrada com módulos de cadastro, GIS, IA generativa e apoio à decisão. |
| **11** | Entrada, processamento e saída | Seção 4.2 do PDF/DOCX | Tabela detalhada de entradas cadastrais/cartográficas, processamento vetorial/LangGraph e saídas justificadas. |
| **12** | Arquitetura | Seção 5 do PDF/DOCX | Arquitetura em camadas (Web &rarr; Business &rarr; Infra &rarr; Core) com diagrama completo (Figura 1). |
| **13** | Tecnologias utilizadas | Seção 6 do PDF/DOCX | Mínimo de 3 componentes: Angular 21/Leaflet, FastAPI/Python 3.13, PostgreSQL 18 e LangGraph/LangChain. |
| **14** | Protótipo (mock / funcional) | Seção 8 do PDF/DOCX | Demonstração do protótipo navegável com 3 telas reais (Figuras 3, 4 e 5) e percurso da operação. |
| **15** | Indicador de resultado da solução | Seção 9 do PDF/DOCX | Redução de pelo menos **50% no tempo médio de triagem** com &ge; 95% de pertinência cadastral. |
| **16** | Benefício esperado | Seção 10 do PDF/DOCX | Agilidade nas Golden Hours, segurança operacional, eliminação de duplicidades e memória institucional. |
| **17** | Limitação ou risco | Seção 11 do PDF/DOCX | Matriz de 5 riscos (conectividade, alucinação de LLM, validade cadastral, bloqueios viários e autenticação em modo de demonstração) e mitigações. |

---

## 3. Matriz de Conformidade com as 5 Perguntas do Pitch (Vídeo até 5 min)

A Seção 11 do edital define que o pitch deve responder obrigatoriamente a cinco perguntas. O arquivo [`ROTEIRO_PITCH_5_MINUTOS.md`](ROTEIRO_PITCH_5_MINUTOS.md) e a apresentação [`SLIDES_APRESENTACAO_PITCH.html`](SLIDES_APRESENTACAO_PITCH.html) cobrem cada uma com precisão:

1. **Qual é o problema?** (Respondido no Bloco 2 / Slide 2 — 00:30 a 01:25)
   - Dispersão de cadastros em planilhas e grupos informais, falta de triagem técnica de qualificações, sobrecarga cognitiva e envio desordenado de voluntários para áreas perigosas.
2. **Qual meta do PN-PDC está sendo trabalhada?** (Respondido no Bloco 3 / Slide 3 — 01:25 a 02:10)
   - Meta 3.1.3: Criar cadastro nacional de voluntários institucionais para formar rede de resposta (Diretriz 3, Objetivo 3.1, Eixo Resposta, prazo 2031).
3. **Como a Computação contribui para atingir essa meta?** (Respondido no Bloco 4 / Slides 4 e 5 — 02:10 a 03:05)
   - Convergência de Angular + Leaflet (mapa interativo), Python/FastAPI (validação tipada e integridade), PostgreSQL 18 (29 tabelas relacionais) e LangGraph/LangChain (busca semântica por embeddings e guardrails determinísticos).
4. **Como a solução funciona?** (Respondido no Bloco 5 / Slide 6 — 03:05 a 04:15)
   - Percurso prático demonstrado: delimitação de área inundada no mapa, cadastro de demanda, busca semântica em catálogo de atividades, validação de certificados, geração de recomendação com justificativas e decisão administrativa humana auditável.
5. **Como será medido o resultado?** (Respondido no Bloco 6 / Slide 7 — 04:15 a 04:50)
   - Indicador de resultado: Redução de 50% no tempo médio de triagem assistida vs. manual, com validação de 100% dos IDs cadastrais (evidenciado por 54 testes automatizados sem falhas).

---

## 4. Orientações para Gravação do Pitch em Vídeo

1. **Abrir a Apresentação de Slides:**
   - Abra [`entrega/SLIDES_APRESENTACAO_PITCH.html`](SLIDES_APRESENTACAO_PITCH.html) no navegador (Chrome ou Edge) e pressione `F11` para tela cheia.
2. **Software de Gravação:**
   - Utilize ferramentas como OBS Studio, Loom, Clipchamp ou gravação de tela nativa do Windows (`Win + G` ou `Win + Alt + R`).
3. **Guia de Fala:**
   - Mantenha o arquivo [`entrega/ROTEIRO_PITCH_5_MINUTOS.pdf`](ROTEIRO_PITCH_5_MINUTOS.pdf) aberto como guia de fala. A transcrição foi calibrada para uma leitura natural em aproximadamente 4 minutos e 45 segundos, respeitando o limite máximo de 5 minutos do edital.
4. **Após Gravar:**
   - Adicione o vídeo (`video_pitch.mp4` ou o link do YouTube/Google Drive no documento) e recompacte o arquivo ZIP se necessário.
