import os

svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 680" width="100%" height="100%" style="background: #fdfdfd; font-family: 'Segoe UI', Calibri, sans-serif;">
  <defs>
    <filter id="shadow" x="-4%" y="-4%" width="108%" height="108%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/>
    </filter>
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1F2A44" />
      <stop offset="100%" stop-color="#2E3B55" />
    </linearGradient>
    <linearGradient id="feGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" />
      <stop offset="100%" stop-color="#f0f4f9" />
    </linearGradient>
    <linearGradient id="aiGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fdf9f2" />
      <stop offset="100%" stop-color="#fef3d6" />
    </linearGradient>
  </defs>

  <!-- Title Banner -->
  <rect x="20" y="15" width="960" height="55" rx="8" fill="url(#headerGrad)" filter="url(#shadow)"/>
  <text x="40" y="43" fill="#ffffff" font-size="18" font-weight="bold" letter-spacing="0.5">RedeSolidária — Arquitetura Convergente de Apoio à Decisão</text>
  <text x="40" y="58" fill="#d2d9e5" font-size="11">Frontend Angular 21 • Backend Python 3.13 / FastAPI • LangGraph &amp; LangChain • PostgreSQL 18</text>

  <!-- Layer 1: Frontend -->
  <g transform="translate(20, 85)">
    <rect x="0" y="0" width="960" height="115" rx="8" fill="url(#feGrad)" stroke="#b5c4d6" stroke-width="1.5" filter="url(#shadow)"/>
    <rect x="0" y="0" width="960" height="28" rx="8" fill="#e1e9f2"/>
    <rect x="0" y="20" width="960" height="8" fill="#e1e9f2"/>
    <text x="20" y="19" fill="#1F2A44" font-size="13" font-weight="bold">CAMADA DE APRESENTAÇÃO (Frontend SPA — Angular 21 + Leaflet 1.9)</text>
    
    <!-- Module 1 -->
    <rect x="20" y="38" width="215" height="65" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="32" y="58" fill="#1F2A44" font-size="12" font-weight="bold">Cadastros Estruturados</text>
    <text x="32" y="74" fill="#475569" font-size="10.5">• Instituições e Voluntários</text>
    <text x="32" y="89" fill="#475569" font-size="10.5">• Qualificações e Recursos</text>

    <!-- Module 2 -->
    <rect x="255" y="38" width="215" height="65" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="267" y="58" fill="#1F2A44" font-size="12" font-weight="bold">Mapeamento GIS (Leaflet)</text>
    <text x="267" y="74" fill="#475569" font-size="10.5">• Desenho Vetorial GeoJSON</text>
    <text x="267" y="89" fill="#475569" font-size="10.5">• Marcação de Gravidade</text>

    <!-- Module 3 -->
    <rect x="490" y="38" width="215" height="65" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="502" y="58" fill="#1F2A44" font-size="12" font-weight="bold">Gestão de Demandas</text>
    <text x="502" y="74" fill="#475569" font-size="10.5">• Atividades Requeridas</text>
    <text x="502" y="89" fill="#475569" font-size="10.5">• Itens de Recursos / Prazos</text>

    <!-- Module 4 -->
    <rect x="725" y="38" width="215" height="65" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="737" y="58" fill="#1F2A44" font-size="12" font-weight="bold">Painel de Apoio à Decisão</text>
    <text x="737" y="74" fill="#475569" font-size="10.5">• Recomendações Explicadas</text>
    <text x="737" y="89" fill="#475569" font-size="10.5">• Aprovação / Rejeição Auditável</text>
  </g>

  <!-- Arrow Down 1 -->
  <g transform="translate(500, 203)">
    <line x1="0" y1="0" x2="0" y2="16" stroke="#1F2A44" stroke-width="2.5" stroke-dasharray="4,3"/>
    <polygon points="-5,16 5,16 0,23" fill="#1F2A44"/>
    <text x="10" y="14" fill="#475569" font-size="10" font-style="italic">REST / JSON (ProblemDetails RFC 9457)</text>
  </g>

  <!-- Layer 2: API & Core -->
  <g transform="translate(20, 230)">
    <rect x="0" y="0" width="960" height="95" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" filter="url(#shadow)"/>
    <rect x="0" y="0" width="960" height="28" rx="8" fill="#e2e8f0"/>
    <rect x="0" y="20" width="960" height="8" fill="#e2e8f0"/>
    <text x="20" y="19" fill="#1e293b" font-size="13" font-weight="bold">CAMADA DE SERVIÇOS &amp; CONTROLADORES (Python 3.13 / FastAPI)</text>
    
    <rect x="20" y="38" width="295" height="47" rx="5" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
    <text x="32" y="57" fill="#0f172a" font-size="11.5" font-weight="bold">Roteamento e Filtros (Web)</text>
    <text x="32" y="73" fill="#64748b" font-size="10">Controllers tipados, Envelope HTTP e RFC 9457</text>

    <rect x="332" y="38" width="295" height="47" rx="5" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
    <text x="344" y="57" fill="#0f172a" font-size="11.5" font-weight="bold">Serviços de Negócio (Business)</text>
    <text x="344" y="73" fill="#64748b" font-size="10">Validação de integridade, qualificações e demandas</text>

    <rect x="645" y="38" width="295" height="47" rx="5" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
    <text x="657" y="57" fill="#0f172a" font-size="11.5" font-weight="bold">Núcleo e Entidades (Core)</text>
    <text x="657" y="73" fill="#64748b" font-size="10">Contratos tipados, DTOs e entidades independentes</text>
  </g>

  <!-- Arrow Down 2 -->
  <g transform="translate(500, 328)">
    <line x1="0" y1="0" x2="0" y2="16" stroke="#1F2A44" stroke-width="2.5" stroke-dasharray="4,3"/>
    <polygon points="-5,16 5,16 0,23" fill="#1F2A44"/>
    <text x="10" y="14" fill="#b45309" font-size="10" font-weight="bold">Invocação de Grafo Cognitivo</text>
  </g>

  <!-- Layer 3: AI Cognitive Engine -->
  <g transform="translate(20, 355)">
    <rect x="0" y="0" width="960" height="135" rx="8" fill="url(#aiGrad)" stroke="#d97706" stroke-width="1.5" stroke-dasharray="6,3" filter="url(#shadow)"/>
    <rect x="0" y="0" width="960" height="28" rx="8" fill="#fed7aa"/>
    <rect x="0" y="20" width="960" height="8" fill="#fed7aa"/>
    <text x="20" y="19" fill="#7c2d12" font-size="13" font-weight="bold">MOTOR DE INTELIGÊNCIA ARTIFICIAL (Orquestração Cognitiva — LangGraph &amp; LangChain)</text>

    <!-- Node 1 -->
    <rect x="20" y="38" width="215" height="85" rx="6" fill="#ffffff" stroke="#f59e0b" stroke-width="1.2"/>
    <text x="32" y="57" fill="#78350f" font-size="11.5" font-weight="bold">1. Busca Semântica</text>
    <text x="32" y="74" fill="#451a03" font-size="10">• Embeddings vetoriais</text>
    <text x="32" y="90" fill="#451a03" font-size="10">• Similaridade cosseno</text>
    <text x="32" y="106" fill="#451a03" font-size="10">• Catálogo de atividades</text>

    <!-- Arrow node 1 to 2 -->
    <polygon points="250,77 257,80 250,83" fill="#d97706"/>

    <!-- Node 2 -->
    <rect x="257" y="38" width="215" height="85" rx="6" fill="#ffffff" stroke="#f59e0b" stroke-width="1.2"/>
    <text x="269" y="57" fill="#78350f" font-size="11.5" font-weight="bold">2. Filtro Estruturado</text>
    <text x="269" y="74" fill="#451a03" font-size="10">• Vínculo institucional ativo</text>
    <text x="269" y="90" fill="#451a03" font-size="10">• Cursos/profissões válidos</text>
    <text x="269" y="106" fill="#451a03" font-size="10">• Recursos disponíveis</text>

    <!-- Arrow node 2 to 3 -->
    <polygon points="482,77 489,80 482,83" fill="#d97706"/>

    <!-- Node 3 -->
    <rect x="489" y="38" width="215" height="85" rx="6" fill="#ffffff" stroke="#f59e0b" stroke-width="1.2"/>
    <text x="501" y="57" fill="#78350f" font-size="11.5" font-weight="bold">3. Inferência LLM</text>
    <text x="501" y="74" fill="#451a03" font-size="10">• Justificativa em linguagem</text>
    <text x="501" y="90" fill="#451a03" font-size="10">• Identificação de lacunas</text>
    <text x="501" y="106" fill="#451a03" font-size="10">• Alertas de sobreposição</text>

    <!-- Arrow node 3 to 4 -->
    <polygon points="714,77 721,80 714,83" fill="#d97706"/>

    <!-- Node 4 -->
    <rect x="721" y="38" width="218" height="85" rx="6" fill="#ffffff" stroke="#16a34a" stroke-width="1.5"/>
    <text x="733" y="57" fill="#14532d" font-size="11.5" font-weight="bold">4. Validador Guardrail</text>
    <text x="733" y="74" fill="#166534" font-size="10">• Verificação estrita de IDs</text>
    <text x="733" y="90" fill="#166534" font-size="10">• Rejeição de alucinações</text>
    <text x="733" y="106" fill="#166534" font-size="10">• Validação de quantidades</text>
  </g>

  <!-- Arrow Down 3 -->
  <g transform="translate(500, 493)">
    <line x1="0" y1="0" x2="0" y2="16" stroke="#1F2A44" stroke-width="2.5" stroke-dasharray="4,3"/>
    <polygon points="-5,16 5,16 0,23" fill="#1F2A44"/>
    <text x="10" y="14" fill="#0284c7" font-size="10" font-style="italic">SQLAlchemy / Psycopg 3</text>
  </g>

  <!-- Layer 4: Persistence & Database -->
  <g transform="translate(20, 520)">
    <rect x="0" y="0" width="960" height="125" rx="8" fill="#f8fafc" stroke="#0284c7" stroke-width="1.5" filter="url(#shadow)"/>
    <rect x="0" y="0" width="960" height="28" rx="8" fill="#bae6fd"/>
    <rect x="0" y="20" width="960" height="8" fill="#bae6fd"/>
    <text x="20" y="19" fill="#0369a1" font-size="13" font-weight="bold">CAMADA DE PERSISTÊNCIA &amp; BANCO DE DADOS (PostgreSQL 18 + Alembic)</text>

    <!-- DB Box 1 -->
    <rect x="20" y="38" width="215" height="75" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="32" y="57" fill="#0f172a" font-size="11.5" font-weight="bold">Cadastros &amp; Vínculos</text>
    <text x="32" y="73" fill="#475569" font-size="10">• instituicoes, pessoas</text>
    <text x="32" y="88" fill="#475569" font-size="10">• pessoa_instituicoes</text>
    <text x="32" y="103" fill="#475569" font-size="10">• profissoes, cursos</text>

    <!-- DB Box 2 -->
    <rect x="255" y="38" width="215" height="75" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="267" y="57" fill="#0f172a" font-size="11.5" font-weight="bold">Capacidades &amp; Recursos</text>
    <text x="267" y="73" fill="#475569" font-size="10">• atividades, ofertas</text>
    <text x="267" y="88" fill="#475569" font-size="10">• recursos, tipos_recurso</text>
    <text x="267" y="103" fill="#475569" font-size="10">• unidades_medida</text>

    <!-- DB Box 3 -->
    <rect x="490" y="38" width="215" height="75" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="502" y="57" fill="#0f172a" font-size="11.5" font-weight="bold">GIS &amp; Operação</text>
    <text x="502" y="73" fill="#475569" font-size="10">• desastres, tipos_desastre</text>
    <text x="502" y="88" fill="#475569" font-size="10">• areas_afetadas (JSONB)</text>
    <text x="502" y="103" fill="#475569" font-size="10">• demandas, demanda_itens</text>

    <!-- DB Box 4 -->
    <rect x="725" y="38" width="215" height="75" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="737" y="57" fill="#0f172a" font-size="11.5" font-weight="bold">IA, Índices &amp; Decisões</text>
    <text x="737" y="73" fill="#475569" font-size="10">• conexao_ia, modelo_ia</text>
    <text x="737" y="88" fill="#475569" font-size="10">• *_indice_semantico (vetor)</text>
    <text x="737" y="103" fill="#475569" font-size="10">• recomendacoes, decisoes</text>
  </g>

  <!-- Footer Info -->
  <text x="25" y="665" fill="#64748b" font-size="10.5">Sistema RedeSolidária — Arquiteturas Convergentes (H3-AC) — Aluno: Luis Roberto de Moraes (CEUB 2026)</text>
</svg>"""

with open("entrega/imagens/arquitetura_sistema.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)

print("Saved entrega/imagens/arquitetura_sistema.svg successfully")

fluxo_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 360" width="100%" height="100%" style="background: #ffffff; font-family: 'Segoe UI', Calibri, sans-serif;">
  <defs>
    <filter id="flShadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/>
    </filter>
  </defs>

  <!-- Title -->
  <rect x="20" y="15" width="860" height="42" rx="6" fill="#1F2A44" filter="url(#flShadow)"/>
  <text x="35" y="41" fill="#ffffff" font-size="15" font-weight="bold">Pipeline Cognitivo LangGraph &amp; Validação Anti-Alucinação</text>

  <!-- Step 1 -->
  <g transform="translate(30, 80)">
    <rect x="0" y="0" width="180" height="180" rx="8" fill="#f0f7ff" stroke="#0284c7" stroke-width="1.5" filter="url(#flShadow)"/>
    <rect x="0" y="0" width="180" height="32" rx="8" fill="#0284c7"/>
    <rect x="0" y="22" width="180" height="10" fill="#0284c7"/>
    <text x="12" y="21" fill="#ffffff" font-size="12" font-weight="bold">1. Demanda &amp; Embeddings</text>
    <text x="12" y="55" fill="#0f172a" font-size="11" font-weight="bold">Recuperação Vetorial</text>
    <text x="12" y="75" fill="#334155" font-size="10">• Análise do pedido de socorro</text>
    <text x="12" y="93" fill="#334155" font-size="10">• Geração de embedding (query)</text>
    <text x="12" y="111" fill="#334155" font-size="10">• Similaridade cosseno</text>
    <text x="12" y="129" fill="#334155" font-size="10">• Top-K atividades do catálogo</text>
    <rect x="10" y="145" width="160" height="24" rx="4" fill="#e0f2fe"/>
    <text x="16" y="161" fill="#0369a1" font-size="9.5" font-weight="bold">Saída: Atividades semânticas</text>
  </g>

  <!-- Arrow 1 -> 2 -->
  <g transform="translate(215, 160)">
    <line x1="0" y1="0" x2="25" y2="0" stroke="#0284c7" stroke-width="2.5"/>
    <polygon points="25,-5 35,0 25,5" fill="#0284c7"/>
  </g>

  <!-- Step 2 -->
  <g transform="translate(255, 80)">
    <rect x="0" y="0" width="180" height="180" rx="8" fill="#f8fafc" stroke="#475569" stroke-width="1.5" filter="url(#flShadow)"/>
    <rect x="0" y="0" width="180" height="32" rx="8" fill="#475569"/>
    <rect x="0" y="22" width="180" height="10" fill="#475569"/>
    <text x="12" y="21" fill="#ffffff" font-size="12" font-weight="bold">2. Filtro Estruturado</text>
    <text x="12" y="55" fill="#0f172a" font-size="11" font-weight="bold">Consulta ao PostgreSQL</text>
    <text x="12" y="75" fill="#334155" font-size="10">• Ofertas de pessoas/instituições</text>
    <text x="12" y="93" fill="#334155" font-size="10">• Cursos e profissões válidos</text>
    <text x="12" y="111" fill="#334155" font-size="10">• Recursos materiais associados</text>
    <text x="12" y="129" fill="#334155" font-size="10">• Filtragem por localidade</text>
    <rect x="10" y="145" width="160" height="24" rx="4" fill="#f1f5f9"/>
    <text x="16" y="161" fill="#334155" font-size="9.5" font-weight="bold">Saída: Candidatos pré-filtrados</text>
  </g>

  <!-- Arrow 2 -> 3 -->
  <g transform="translate(440, 160)">
    <line x1="0" y1="0" x2="25" y2="0" stroke="#d97706" stroke-width="2.5"/>
    <polygon points="25,-5 35,0 25,5" fill="#d97706"/>
  </g>

  <!-- Step 3 -->
  <g transform="translate(480, 80)">
    <rect x="0" y="0" width="180" height="180" rx="8" fill="#fffbeb" stroke="#d97706" stroke-width="1.5" filter="url(#flShadow)"/>
    <rect x="0" y="0" width="180" height="32" rx="8" fill="#d97706"/>
    <rect x="0" y="22" width="180" height="10" fill="#d97706"/>
    <text x="12" y="21" fill="#ffffff" font-size="12" font-weight="bold">3. Raciocínio LLM</text>
    <text x="12" y="55" fill="#0f172a" font-size="11" font-weight="bold">LangChain / Prompt Tipado</text>
    <text x="12" y="75" fill="#334155" font-size="10">• Cruzamento de perfis e demanda</text>
    <text x="12" y="93" fill="#334155" font-size="10">• Justificativa em linguagem</text>
    <text x="12" y="111" fill="#334155" font-size="10">• Apontamento de lacunas</text>
    <text x="12" y="129" fill="#334155" font-size="10">• Destaque de pendências</text>
    <rect x="10" y="145" width="160" height="24" rx="4" fill="#fef3c7"/>
    <text x="16" y="161" fill="#92400e" font-size="9.5" font-weight="bold">Saída: Proposta de alocação</text>
  </g>

  <!-- Arrow 3 -> 4 -->
  <g transform="translate(665, 160)">
    <line x1="0" y1="0" x2="25" y2="0" stroke="#16a34a" stroke-width="2.5"/>
    <polygon points="25,-5 35,0 25,5" fill="#16a34a"/>
  </g>

  <!-- Step 4 -->
  <g transform="translate(705, 80)">
    <rect x="0" y="0" width="170" height="180" rx="8" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.8" filter="url(#flShadow)"/>
    <rect x="0" y="0" width="170" height="32" rx="8" fill="#16a34a"/>
    <rect x="0" y="22" width="170" height="10" fill="#16a34a"/>
    <text x="10" y="21" fill="#ffffff" font-size="12" font-weight="bold">4. Guardrail Determinístico</text>
    <text x="10" y="55" fill="#14532d" font-size="11" font-weight="bold">Validação de Integridade</text>
    <text x="10" y="75" fill="#166534" font-size="10">• Rejeição de IDs alucinados</text>
    <text x="10" y="93" fill="#166534" font-size="10">• Checagem de quantidades</text>
    <text x="10" y="111" fill="#166534" font-size="10">• Detecção de sobreposição</text>
    <text x="10" y="129" fill="#166534" font-size="10">• Cálculo do déficit global</text>
    <rect x="8" y="145" width="154" height="24" rx="4" fill="#dcfce7"/>
    <text x="12" y="161" fill="#15803d" font-size="9" font-weight="bold">Auditável: Para análise humana</text>
  </g>

  <!-- Final Decision Footer Bar -->
  <g transform="translate(30, 280)">
    <rect x="0" y="0" width="845" height="55" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
    <text x="20" y="24" fill="#1F2A44" font-size="11.5" font-weight="bold">GOVERNANÇA &amp; APOIO À DECISÃO (Human-in-the-Loop):</text>
    <text x="20" y="42" fill="#475569" font-size="10.5">O gestor público analisa a recomendação, os alertas de conflito e as justificativas, registrando decisão administrativa (Aprovação / Rejeição) com parecer formal e data.</text>
  </g>
</svg>"""

with open("entrega/imagens/fluxo_cognitivo_langgraph.svg", "w", encoding="utf-8") as f:
    f.write(fluxo_svg)

print("Saved entrega/imagens/fluxo_cognitivo_langgraph.svg successfully")

