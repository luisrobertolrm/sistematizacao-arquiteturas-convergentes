import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENTREGA_DIR = os.path.join(BASE_DIR, "entrega")
IMAGENS_DIR = os.path.join(ENTREGA_DIR, "imagens")

COLOR_NAVY = RGBColor(0x1F, 0x2A, 0x44)
COLOR_SLATE = RGBColor(0x2E, 0x3B, 0x55)
COLOR_STEEL = RGBColor(0x1F, 0x4D, 0x78)
COLOR_BODY = RGBColor(0x22, 0x22, 0x22)
COLOR_MUTED = RGBColor(0x66, 0x66, 0x66)

HEX_NAVY = "1F2A44"
HEX_LIGHT_GRAY = "F8FAFC"
HEX_BORDER = "D0D7DE"
HEX_CALLOUT_BG = "F0F4F9"
HEX_META_BG = "F0FDF4"
HEX_WARN_BG = "FFFBEB"

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''<w:tcMar {nsdecls("w")}>
        <w:top w:w="{top}" w:type="dxa"/>
        <w:bottom w:w="{bottom}" w:type="dxa"/>
        <w:left w:w="{left}" w:type="dxa"/>
        <w:right w:w="{right}" w:type="dxa"/>
    </w:tcMar>''')
    tcPr.append(tcMar)

def add_callout(doc, text_runs, hex_bg=HEX_CALLOUT_BG, border_color="1F2A44"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, hex_bg)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Left border only
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''<w:tcBorders {nsdecls("w")}>
        <w:top w:val="none"/>
        <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>
        <w:bottom w:val="none"/>
        <w:right w:val="none"/>
    </w:tcBorders>''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    for run_text, bold, italic, color in text_runs:
        r = p.add_run(run_text)
        r.bold = bold
        r.italic = italic
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
        if color:
            r.font.color.rgb = color
    
    # Space after table
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def format_table(tbl, col_widths, headers, rows_data):
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Header row
    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], HEX_NAVY)
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        for r in p.runs:
            r.font.name = "Calibri"
            r.font.size = Pt(9.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            
    # Body rows
    for r_idx, r_data in enumerate(rows_data):
        row_cells = tbl.add_row().cells
        bg = HEX_LIGHT_GRAY if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(r_data):
            row_cells[c_idx].text = val
            set_cell_background(row_cells[c_idx], bg)
            set_cell_margins(row_cells[c_idx], top=90, bottom=90, left=120, right=120)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9.5)
                r.font.color.rgb = COLOR_BODY

    # Set widths
    for row in tbl.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = Inches(width)

def gerar_docx_completo(output_path):
    doc = docx.Document()
    
    # Configure base section margins (2 cm = 0.787 in = 1134 dxa)
    sec0 = doc.sections[0]
    sec0.top_margin = Inches(0.8)
    sec0.bottom_margin = Inches(0.8)
    sec0.left_margin = Inches(0.8)
    sec0.right_margin = Inches(0.8)

    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = COLOR_BODY

    # ================= COVER PAGE =================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(24)
    p_inst.paragraph_format.space_after = Pt(2)
    r = p_inst.add_run("CENTRO UNIVERSITÁRIO DE BRASÍLIA")
    r.font.name = "Georgia"
    r.font.size = Pt(17)
    r.font.bold = True
    r.font.color.rgb = COLOR_NAVY

    p_sigla = doc.add_paragraph()
    p_sigla.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sigla.paragraph_format.space_before = Pt(0)
    p_sigla.paragraph_format.space_after = Pt(4)
    r = p_sigla.add_run("C E U B")
    r.font.name = "Georgia"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = COLOR_MUTED

    p_disc = doc.add_paragraph()
    p_disc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_disc.paragraph_format.space_before = Pt(0)
    p_disc.paragraph_format.space_after = Pt(16)
    r = p_disc.add_run("H3-AC — Arquiteturas Convergentes")
    r.font.name = "Calibri"
    r.font.size = Pt(12)
    r.font.color.rgb = COLOR_SLATE

    # Double divider line
    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_before = Pt(0)
    p_div.paragraph_format.space_after = Pt(60)
    r = p_div.add_run("═══════════════════════════════════════")
    r.font.color.rgb = COLOR_NAVY
    r.font.size = Pt(10)

    p_cat = doc.add_paragraph()
    p_cat.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cat.paragraph_format.space_before = Pt(0)
    p_cat.paragraph_format.space_after = Pt(14)
    r = p_cat.add_run("SISTEMATIZAÇÃO — DESAFIO DE COMPUTAÇÃO APLICADA À PROTEÇÃO E DEFESA CIVIL")
    r.font.name = "Calibri"
    r.font.size = Pt(10.5)
    r.font.bold = True
    r.font.color.rgb = COLOR_MUTED

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.space_before = Pt(0)
    p_tit.paragraph_format.space_after = Pt(12)
    r = p_tit.add_run("RedeSolidária")
    r.font.name = "Georgia"
    r.font.size = Pt(28)
    r.font.bold = True
    r.font.color.rgb = COLOR_NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(20)
    r = p_sub.add_run("Plataforma Integrada de Apoio à Decisão para Cadastramento e Mobilização Inteligente de Voluntários Institucionais e Recursos em Desastres")
    r.font.name = "Georgia"
    r.font.size = Pt(12)
    r.italic = True
    r.font.color.rgb = COLOR_BODY

    p_div2 = doc.add_paragraph()
    p_div2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div2.paragraph_format.space_before = Pt(0)
    p_div2.paragraph_format.space_after = Pt(80)
    r = p_div2.add_run("───────────────────────")
    r.font.color.rgb = COLOR_MUTED
    r.font.size = Pt(10)

    # Metadata bottom right
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(40)
    r = p_meta.add_run("Aluno: ")
    r.font.size = Pt(10.5)
    r.font.color.rgb = COLOR_MUTED
    r = p_meta.add_run("Luis Roberto de Moraes\n")
    r.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = COLOR_NAVY
    r = p_meta.add_run("Curso: ")
    r.font.size = Pt(10.5)
    r.font.color.rgb = COLOR_MUTED
    r = p_meta.add_run("Engenharia / Ciência da Computação\n")
    r.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = COLOR_NAVY
    r = p_meta.add_run("Disciplina: ")
    r.font.size = Pt(10.5)
    r.font.color.rgb = COLOR_MUTED
    r = p_meta.add_run("Arquiteturas Convergentes (H3-AC)")
    r.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = COLOR_NAVY

    p_local = doc.add_paragraph()
    p_local.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_local.paragraph_format.space_before = Pt(10)
    p_local.paragraph_format.space_after = Pt(0)
    r = p_local.add_run("BRASÍLIA\n2026")
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = COLOR_NAVY

    # Break to Page 2
    doc.add_page_break()

    # ================= HELPERS FOR BODY =================
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(20)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = COLOR_NAVY
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = COLOR_SLATE
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = COLOR_STEEL
        return p

    def add_body(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        r.font.color.rgb = COLOR_BODY
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r1 = p.add_run(bold_prefix + " ")
            r1.bold = True
            r1.font.color.rgb = COLOR_NAVY
        r2 = p.add_run(text)
        r2.font.color.rgb = COLOR_BODY

    def add_image_figure(img_rel_path, caption_text, width_inches=6.2):
        full_path = os.path.join(IMAGENS_DIR, img_rel_path)
        if os.path.exists(full_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(full_path, width=Inches(width_inches))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(0)
            p_cap.paragraph_format.space_after = Pt(10)
            r = p_cap.add_run(caption_text)
            r.italic = True
            r.font.size = Pt(9)
            r.font.color.rgb = COLOR_MUTED

    # ================= SUMÁRIO =================
    add_h1("Sumário")
    sumario_itens = [
        ("1. Identificação do Projeto e Integrante", "3"),
        ("2. Diagnóstico do Problema Real de Proteção e Defesa Civil", "3"),
        ("    2.1 O que está acontecendo?", "3"),
        ("    2.2 Quem é afetado?", "4"),
        ("    2.3 Onde o problema ocorre? (Cenários Reais e Município Fictício)", "4"),
        ("    2.4 Por que uma solução computacional pode contribuir para enfrentá-lo?", "4"),
        ("3. Vinculação Oficial ao Plano Nacional de Proteção e Defesa Civil (PN-PDC 2025–2035)", "5"),
        ("    3.1 Meta Selecionada: Meta 3.1.3", "5"),
        ("    3.2 Objetivo Estratégico (3.1) e Diretriz (3)", "5"),
        ("    3.3 Eixo de Atuação, Prazo (2031) e Indicador Oficial", "5"),
        ("4. Solução Computacional Proposta", "6"),
        ("    4.1 Visão Geral e Proposta de Valor", "6"),
        ("    4.2 Fluxo Operacional: Entrada, Processamento e Saída", "7"),
        ("    4.3 Governança Humana e Apoio à Tomada de Decisão (Human-in-the-Loop)", "7"),
        ("5. Arquitetura do Sistema e Engenharia de Software", "8"),
        ("    5.1 Padrão Arquitetural em Camadas (Web → Business → Infra → Core)", "8"),
        ("    5.2 Diagrama Arquitetural Completo", "8"),
        ("    5.3 Modelo de Entidades e Banco de Dados (29 Tabelas Iniciais)", "9"),
        ("6. Convergência Tecnológica", "10"),
        ("    6.1 Matriz de Componentes e Problemas Resolvidos", "10"),
        ("    6.2 Detalhamento dos Componentes Tecnológicos", "10"),
        ("7. Motor de Inteligência Artificial e Grafo Cognitivo", "10"),
        ("    7.1 Orquestração em Grafo com LangGraph", "10"),
        ("    7.2 Busca Semântica Vetorial de Atividades", "11"),
        ("    7.3 Guardrails Determinísticos e Validação Anti-Alucinação", "11"),
        ("8. Protótipo Funcional e Demonstração", "12"),
        ("    8.1 Telas Implementadas e Percurso Demonstrativo", "12"),
        ("    8.2 Evidências da Simulação e Validação em Memória (54 Verificações OK)", "14"),
        ("9. Indicador de Resultado da Solução", "15"),
        ("    9.1 Definição do Indicador Mensurável", "15"),
        ("    9.2 Protocolo Experimental (Manual vs. Assistido) e Fórmula", "15"),
        ("10. Benefícios Esperados", "16"),
        ("11. Limitações, Riscos e Estratégias de Mitigação", "17"),
        ("12. Roteiro e Estrutura do Pitch (Vídeo de até 5 Minutos)", "17"),
        ("13. Conclusão e Próximos Passos", "18"),
        ("14. Referências Oficiais e Bibliográficas", "19")
    ]
    for tit, pag in sumario_itens:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r1 = p.add_run(tit)
        r1.font.size = Pt(9.5)
        if not tit.startswith("    "):
            r1.bold = True
            r1.font.color.rgb = COLOR_NAVY
        r_dots = p.add_run(" " + "." * max(5, int(75 - len(tit) * 1.1)) + " ")
        r_dots.font.color.rgb = COLOR_MUTED
        r_dots.font.size = Pt(8.5)
        r2 = p.add_run(pag)
        r2.bold = True
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = COLOR_NAVY

    doc.add_page_break()

    # ================= SEÇÃO 1 =================
    add_h1("1. Identificação do Projeto e Integrante")
    add_body("Este documento consolida a entrega da atividade de Sistematização da disciplina H3-AC — Arquiteturas Convergentes do Centro Universitário de Brasília (CEUB), sob a temática Desafio de Computação Aplicada à Proteção e Defesa Civil.")
    add_callout(doc, [
        ("Projeto: ", True, False, COLOR_NAVY),
        ("RedeSolidária — Plataforma Integrada de Apoio à Decisão para Cadastramento e Mobilização Inteligente de Voluntários Institucionais e Recursos em Desastres\n", False, False, None),
        ("Integrante: ", True, False, COLOR_NAVY),
        ("Luis Roberto de Moraes\n", False, False, None),
        ("Instituição de Ensino: ", True, False, COLOR_NAVY),
        ("Centro Universitário de Brasília (CEUB)\n", False, False, None),
        ("Unidade Curricular: ", True, False, COLOR_NAVY),
        ("H3-AC — Arquiteturas Convergentes\n", False, False, None),
        ("Stack Tecnológica: ", True, False, COLOR_NAVY),
        ("Arquitetura em camadas Python (FastAPI/SQLAlchemy), Frontend Angular 21, PostgreSQL 18 e LangGraph/LangChain.", False, False, None)
    ])
    add_callout(doc, [
        ("Acesso ao Projeto\n", True, False, COLOR_STEEL),
        ("Aplicação online: ", True, False, COLOR_NAVY),
        ("https://redesolidaria.myworklab.com.br/\n", False, False, COLOR_STEEL),
        ("Tela inicial com acesso administrativo (login por token) e cadastro de voluntário pelo botão “Quero me voluntariar”.\n", False, True, COLOR_MUTED),
        ("Repositório (código-fonte): ", True, False, COLOR_NAVY),
        ("https://github.com/luisrobertolrm/sistematizacao-arquiteturas-convergentes/tree/main", False, False, COLOR_STEEL),
    ], hex_bg="E0F2FE", border_color="0284C7")

    # ================= SEÇÃO 2 =================
    add_h1("2. Diagnóstico do Problema Real de Proteção e Defesa Civil")
    add_body("O Brasil vivencia uma escalada na frequência e severidade de eventos climáticos extremos. Desastres hidrológicos (inundações bruscas e alagamentos) e geológicos (deslizamentos de terra em encostas urbanas) impõem desafios humanitários e logísticos sem precedentes à administração pública. Em conformidade com o edital de Sistematização, o diagnóstico é estruturado a partir de quatro questões fundamentais.")

    add_h2("2.1 O que está acontecendo?")
    add_body("Durante desastres deflagrados por chuvas torrenciais ou secas severas, observa-se uma comoção pública espontânea acompanhada pela mobilização voluntária de centenas de cidadãos, empresas e organizações da sociedade civil. No entanto, o ecossistema de resposta da Defesa Civil padece de uma crônica fragmentação de dados e desarticulação operacional:")
    add_bullet("Dispersão e perda de dados cadastrais:", "As inscrições de voluntários e instituições ocorrem através de formulários descentralizados, planilhas locais, anotações em papel ou grupos informais de aplicativos de mensagens.")
    add_bullet("Desconhecimento de competências técnicas reais:", "Não há uma validação prévia e estruturada sobre quem realmente possui capacitação comprovada (ex.: socorristas certificados, condutores náuticos, operadores de máquinas pesadas, médicos) versus voluntários gerais sem treinamento de autoproteção.")
    add_bullet("Sobrecarga cognitiva dos coordenadores:", "Nas salas de situação, agentes de Defesa Civil precisam cruzar manualmente listas estáticas com chamados urgentes, gerando lentidão extrema na montagem de equipes.")
    add_bullet("Gargalos e sobreposições logísticas:", "Recursos materiais e viaturas são frequentemente alocados em duplicidade para um local enquanto áreas adjacentes permanecem desassistidas, culminando no envio desordenado de pessoas para zonas de alto perigo sem equipamentos apropriados.")

    add_h2("2.2 Quem é afetado?")
    add_body("A desorganização das capacidades atinge múltiplos atores no cenário de emergência:")
    add_bullet("População e Comunidades Vulneráveis:", "Cidadãos isolados, famílias desabrigadas, idosos e crianças em áreas atingidas, cujo tempo de espera por socorro, água potável e atendimento médico é dilatado pela lentidão na triagem.")
    add_bullet("Agentes e Coordenadores da Defesa Civil:", "Gestores municipais e estaduais que atuam sob estresse extremo, carecendo de visibilidade situacional integrada e ferramentas de apoio à decisão.")
    add_bullet("Voluntários Institucionais e Comunitários:", "Profissionais dispostos a ajudar que sofrem com a ociosidade, frustração ou são expostos a riscos desnecessários em áreas instáveis por falta de triagem prévia.")
    add_bullet("Instituições Parceiras e Terceiro Setor:", "ONGs, cooperativas, igrejas, universidades e entidades privadas (como Cruz Vermelha e escoteiros) que não conseguem interoperar seus estoques e equipes com o plano municipal.")

    add_h2("2.3 Onde o problema ocorre? (Cenários Reais e Município Fictício)")
    add_body("Este gargalo é recorrente em todo o território nacional, tendo sido registrado criticamente em tragédias emblemáticas recentes:")
    add_bullet("Região Serrana do Rio de Janeiro (Petrópolis e Nova Friburgo):", "Enxurradas e deslizamentos soterraram acessos e demandaram equipes multidisciplinares com equipamentos pesados e treinamento de busca e resgate em estruturas colapsadas (BREC).")
    add_bullet("Litoral Norte de São Paulo (São Sebastião):", "Volumes pluviométricos históricos isolaram comunidades na serra, gerando gargalo logístico imediato de abastecimento aéreo e náutico.")
    add_bullet("Vale do Taquari e Região Metropolitana de Porto Alegre (Rio Grande do Sul):", "Inundações históricas de bacias hidrográficas inteiras que exigiram a coordenação simultânea de milhares de embarcações voluntárias civis e militares.")
    add_body("Para fins de experimentação controlada e validação rigorosa dos modelos implementados no projeto, adotou-se como cenário piloto o município de São Paulo (código IBGE 3550308), representativo de uma localidade brasileira densamente povoada e vulnerável, com uma ocorrência ilustrativa contendo três setores críticos: a Várzea (inundável), a Encosta (escorregamentos) e o Centro (concentração de abrigados).")

    add_h2("2.4 Por que uma solução computacional pode contribuir para enfrentá-lo?")
    add_body("A Ciência da Computação oferece respostas definitivas para superar o gargalo da gestão de emergências por meio da convergência tecnológica:")
    add_bullet("Centralização Relacional Íntegra:", "Substitui planilhas fragmentadas por um banco de dados relacional robusto (PostgreSQL), garantindo integridade referencial entre entidades, instituições, pessoas, certificações, vínculos e bens materiais.")
    add_bullet("Geoprocessamento Interativo (GIS):", "Permite aos gestores demarcar visualmente os polígonos das áreas impactadas diretamente no mapa sobreposto à cartografia municipal, correlacionando gravidade espacial e demandas.")
    add_bullet("Inteligência Artificial Cognitiva & RAG:", "O emprego de modelos de embeddings vetoriais possibilita buscar semanticamente intenções e necessidades expressas em linguagem natural não estruturada e associá-las imediatamente a atividades catalogadas.")
    add_bullet("Orquestração Determinística de Grafos (LangGraph):", "Em vez de confiar em caixas-pretas propensas a alucinações, o pipeline computacional emprega nós de validação estrita (guardrails) que filtram restrições de negócio, comprovam diplomas e verificam estoques físicos reais.")

    # ================= SEÇÃO 3 =================
    add_h1("3. Vinculação Oficial ao Plano Nacional de Proteção e Defesa Civil (PN-PDC 2025–2035)")
    add_body("O Plano Nacional de Proteção e Defesa Civil (PN-PDC 2025–2035), instituído no âmbito da Lei nº 12.608/2012 e regulamentado pelo Decreto nº 12.652/2025, estrutura-se em 5 eixos, 20 objetivos e 163 metas.")
    
    add_callout(doc, [
        ("Diretriz do Plano: ", True, False, COLOR_NAVY),
        ("Diretriz 3 — Gestão de desastres para o fortalecimento das ações de resposta aos desastres e da recuperação de áreas afetadas, com ênfase em reconstruir melhor e na adoção de infraestruturas resilientes.\n", False, False, None),
        ("Objetivo Estratégico: ", True, False, COLOR_NAVY),
        ("Objetivo 3.1 — Aprimorar as capacidades de atuação na resposta a desastres.\n", False, False, None),
        ("Meta Oficial Selecionada: ", True, False, COLOR_NAVY),
        ("Meta 3.1.3 — Criar cadastro nacional de voluntários institucionais para formar rede para atuar na resposta a desastres.\n", False, False, None),
        ("Eixo de Atuação: ", True, False, COLOR_NAVY),
        ("Resposta.\n", False, False, None),
        ("Prazo de Cumprimento: ", True, False, COLOR_NAVY),
        ("Médio Prazo (até 2031), conforme Decreto nº 12.652/2025.\n", False, False, None),
        ("Indicador Oficial da Meta: ", True, False, COLOR_NAVY),
        ("Cadastro nacional criado.\n", False, False, None),
        ("Órgão Responsável: ", True, False, COLOR_NAVY),
        ("Secretaria Nacional de Proteção e Defesa Civil (Sedec / MIDR).\n", False, False, None),
        ("Referência: ", True, False, COLOR_NAVY),
        ("PN-PDC 2025–2035, Quadro 6, páginas 114–115 (pág. 58 do PDF oficial).", False, False, None)
    ], hex_bg=HEX_META_BG, border_color="16A34A")

    # ================= SEÇÃO 4 =================
    add_h1("4. Solução Computacional Proposta")
    add_h2("4.1 Visão Geral e Proposta de Valor")
    add_body("A RedeSolidária é uma plataforma computacional full-stack convergente, orientada a microsserviços e apoio à tomada de decisão. A aplicação integra módulos de cadastros auditáveis, Sistema de Informação Geográfica (GIS), motor cognitivo com Inteligência Artificial generativa e orquestração de fluxos estruturados.")

    add_h2("4.2 Fluxo Operacional: Entrada, Processamento e Saída")
    t_ep_headers = ["Etapa", "Fluxo de Dados & Operações", "Módulos & Tecnologias"]
    t_ep_rows = [
        ["Entrada", "Cadastros de instituições e voluntários com vínculos; qualificações técnicas (cursos e profissões validados); catálogo de atividades e ofertas; recursos materiais; polígonos de áreas afetadas no mapa com gravidade; demandas emergenciais e prazos.", "Angular 21 (SPA responsiva)\nLeaflet 1.9 (GeoJSON)\nFastAPI / Pydantic (Validação)"],
        ["Processamento", "Validação de integridade referencial e contratos; geração de embeddings vetoriais para demandas e catálogo; busca por similaridade cosseno; filtragem estruturada relacional; orquestração LangGraph; inferência LLM para justificativas; guardrail determinístico anti-alucinação.", "Python 3.13 / FastAPI\nPostgreSQL 18 / SQLAlchemy\nLangGraph / LangChain\nTrigger SQL (Dimensões de vetores)"],
        ["Saída", "Mapa interativo com polígonos coloridos por gravidade; dossiê analítico de recomendação com justificativa textual contextualizada; alertas de sobreposição de agenda e déficit material; histórico auditável de decisões administrativas.", "Frontend Angular 21\nHistórico PostgreSQL (audit)\nLogs RFC 9457"]
    ]
    format_table(doc.add_table(rows=1, cols=3), [1.3, 3.4, 2.0], t_ep_headers, t_ep_rows)

    add_h2("4.3 Governança Humana e Apoio à Tomada de Decisão (Human-in-the-Loop)")
    add_body("Uma premissa de engenharia fundamental adotada no projeto é que a Inteligência Artificial não substitui a autoridade do gestor público de Defesa Civil. O sistema atua estritamente como um sistema de apoio à decisão (Decision Support System - DSS). O motor cognitivo elabora propostas fundamentadas, mas a decisão final de mobilização cabe indelevelmente ao administrador da sala de crise.")

    # ================= SEÇÃO 5 =================
    add_h1("5. Arquitetura do Sistema e Engenharia de Software")
    add_h2("5.1 Padrão Arquitetural em Camadas (Web → Business → Infra → Core)")
    add_body("O backend foi desenhado seguindo princípios de arquitetura limpa e inversão de dependências, garantindo que o núcleo do domínio permaneça desacoplado de bibliotecas de infraestrutura:")
    add_bullet("core/:", "Entidades centrais do domínio, definições de envelopes de resposta HTTP e tipos fundamentais. Não possui qualquer dependência de camadas superiores.")
    add_bullet("infra/:", "Mecanismos de persistência, conexão com PostgreSQL 18 via SQLAlchemy 2.1 e psycopg 3, mapeamento relacional (ORM) e migrações versionadas com Alembic.")
    add_bullet("business/:", "Serviços de aplicação, regras de negócio, validações de integridade, modelos de entrada/saída (DTOs/ViewModels) e o módulo business/graphs responsável pela orquestração do LangGraph.")
    add_bullet("web/:", "Controladores REST (FastAPI), middlewares de exceção global conforme RFC 9457 (ProblemDetails), filtros transversais e inicialização da aplicação (main.py).")

    add_h2("5.2 Diagrama Arquitetural Completo")
    add_image_figure("arquitetura_sistema.png", "Figura 1 — Diagrama arquitetural em camadas da plataforma RedeSolidária, destacando a integração entre Angular, FastAPI, LangGraph e PostgreSQL.")

    add_h2("5.3 Modelo de Entidades e Banco de Dados (29 Tabelas Iniciais)")
    add_body("O escopo inicial do projeto foi formalizado e implementado com 29 tabelas relacionais, contemplando migrações versionadas (Alembic 0001 a 0009):")
    add_bullet("Núcleo Cadastral:", "instituicoes, pessoas, pessoa_instituicoes (vínculo institucional com cargo/função).")
    add_bullet("Qualificações Formais:", "profissoes, cursos, pessoa_profissoes, pessoa_cursos (com data de emissão, validade e comprovação).")
    add_bullet("Capacidades e Ofertas:", "categorias_atividade, atividades, ofertas_atividades, unidades_medida.")
    add_bullet("Inventário Material:", "tipos_recurso, recursos, recurso_oferta.")
    add_bullet("Cartografia e Ocorrências:", "desastres, tipos_desastre, desastre_tipo, areas_afetadas (polígonos GeoJSON em JSONB e gravidade).")
    add_bullet("Demandas Emergenciais:", "demandas, demanda_itens (atividades ou recursos com quantidades e prioridades).")
    add_bullet("Infraestrutura Cognitiva & Vetorial:", "conexao_ia, modelo_ia, atividade_indice_semantico (vetores double precision[] com triggers), profissao_indice_semantico, curso_indice_semantico, tipo_recurso_indice_semantico.")
    add_bullet("Apoio à Decisão e Auditoria:", "recomendacoes, recomendacao_itens, recomendacao_pessoas, recomendacao_instituicoes, recomendacao_recursos, recomendacao_decisoes.")

    # ================= SEÇÃO 6 =================
    add_h1("6. Convergência Tecnológica")
    add_body("O edital estabelece a exigência de convergência de pelo menos 3 componentes tecnológicos estruturados. A solução RedeSolidária articula quatro componentes tecnológicos de ponta:")

    t_tech_headers = ["Componente Tecnológico", "Stack & Versões", "Problema Específico que Resolve na Arquitetura"]
    t_tech_rows = [
        ["1. Frontend Web SPA & Geoprocessamento", "Angular 21.2\nLeaflet 1.9\nOpenStreetMap", "Resolve a ausência de interface amigável e visualização espacial nas salas de crise. Permite desenhar zonas de risco diretamente no mapa, acompanhar níveis de gravidade por cores e operar cadastros complexos com validação reativa."],
        ["2. Backend & Engenharia de Serviços", "Python 3.13\nFastAPI 0.143\nSQLAlchemy 2.1\nPydantic / TypedDict", "Resolve a fragilidade e inconsistência de dados das planilhas manuais. Provê uma API assíncrona de alto desempenho, contratos fortemente tipados, validação de regras de negócio em tempo de execução e mensagens RFC 9457."],
        ["3. Banco de Dados Relacional e Georreferenciado", "PostgreSQL 18\nAlembic 1.20\nJSONB & Array Float", "Resolve o problema da dispersão, duplicidade e perda de histórico de cadastros. Assegura integridade referencial estrita entre 29 tabelas, versionamento auditável de esquemas via Alembic e armazenamento integrado de geometrias e vetores."],
        ["4. Inteligência Artificial & Orquestração Cognitiva", "LangGraph 1.2\nLangChain 1.4\nEmbeddings Cosseno\nLLM com Guardrails", "Resolve o gargalo cognitivo de cruzar centenas de chamados não-estruturados com voluntários e recursos. Realiza busca semântica veloz, balanceia ofertas, redige justificativas compreensíveis em português e filtra alucinações."]
    ]
    format_table(doc.add_table(rows=1, cols=3), [1.8, 1.8, 3.1], t_tech_headers, t_tech_rows)

    # ================= SEÇÃO 7 =================
    add_h1("7. Motor de Inteligência Artificial e Grafo Cognitivo")
    add_h2("7.1 Orquestração em Grafo com LangGraph")
    add_body("Para assegurar total controle sobre o fluxo de raciocínio da IA e impedir respostas caóticas, a recuperação e recomendação foram modeladas como um grafo acíclico dirigido (DAG) utilizando LangGraph:")
    add_image_figure("fluxo_cognitivo_langgraph.png", "Figura 2 — Grafo cognitivo LangGraph: busca semântica, filtragem estruturada, inferência LLM e guardrail determinístico.")

    add_h2("7.2 Busca Semântica Vetorial de Atividades")
    add_body("As demandas cadastradas nem sempre utilizam termos técnicos formais. Por meio de embeddings vetoriais com hash SHA-256 e cálculo de similaridade de cosseno exato, a plataforma associa pedidos em linguagem natural às atividades homologadas em tempo sub-segundo.")

    add_h2("7.3 Guardrails Determinísticos e Validação Anti-Alucinação")
    add_callout(doc, [
        ("Mecanismo de Guardrail Anti-Alucinação Implementado:\n", True, False, COLOR_NAVY),
        ("1. Validação de Chaves Estrangeiras: ", True, False, None),
        ("Qualquer ID sugerido pelo modelo inexistente no banco é sumariamente descartado;\n", False, False, None),
        ("2. Consistência de Quantidades: ", True, False, None),
        ("Quantidades sugeridas que excedem o estoque real ou negativas são normalizadas;\n", False, False, None),
        ("3. Detecção de Conflito de Janelas: ", True, False, None),
        ("O validador identifica se uma viatura ou voluntário foi indicado para outra demanda no mesmo horário;\n", False, False, None),
        ("4. Cálculo do Déficit Global: ", True, False, None),
        ("Se duas demandas pedem 200 L cada e o estoque tem 300 L, o sistema alerta para o déficit de 100 L.", False, False, None)
    ], hex_bg=HEX_WARN_BG, border_color="D97706")

    # ================= SEÇÃO 8 =================
    add_h1("8. Protótipo Funcional e Demonstração")
    add_h2("8.1 Telas Implementadas e Percurso Demonstrativo")
    add_body("A aplicação foi integralmente prototipada e integrada, contando com visual moderno, tema azul corporativo e navegação intuitiva em Angular.")
    add_image_figure("visao-geral.png", "Figura 3 — Visão Geral do Protótipo Funcional: menu lateral unificado, contadores das entidades da rede e percurso da operação.")
    add_body("O módulo de geoprocessamento permite ao gestor desenhar os polígonos das áreas impactadas diretamente no mapa:")
    add_image_figure("mapa.png", "Figura 4 — Módulo de Geoprocessamento: delimitação vetorial das áreas afetadas (Várzea, Encosta e Centro) e classificação de gravidade.")
    add_body("No painel de apoio à decisão, o gestor avalia as sugestões da IA com suas respectivas justificativas e alertas de conflito:")
    add_image_figure("recomendacao.png", "Figura 5 — Painel de Análise de Recomendação: modelo de IA acionado, justificativa textual, identificação de conflitos e registro da decisão administrativa.")

    add_h2("8.2 Evidências da Simulação e Validação em Memória (54 Verificações OK)")
    add_body("Para assegurar conformidade rigorosa com as regras de negócio, a simulação em memória (simular_desastre.py) validou 54 verificações OK, 0 falhas e 8 limites documentados:")

    t_sim_headers = ["Grupo de Teste", "Quantidade", "Resultado", "Evidência de Validação"]
    t_sim_rows = [
        ["Validação Cadastral e Relações", "6 cenários", "54 / 54 OK", "Vínculos institucionais, qualificações, modelos e entidades conferidos com rigor."],
        ["Rejeição de Entradas Inválidas", "18 cenários", "Aprovado", "Rejeição de demandas sem itens, quantidades negativas, prazos retroativos e FKs inválidas."],
        ["Integridade Semântica e Dimensões", "10 cenários", "Aprovado", "Rejeição de vetores incompatíveis, invalidação de hashes obsoletos e modelos múltiplos."],
        ["Guardrails Anti-Alucinação", "12 cenários", "Aprovado", "Descarte imediato de IDs de pessoas, instituições e recursos inexistentes sugeridos por IA."],
        ["Histórico e Decisão Administrativa", "8 cenários", "Aprovado", "Preservação de decisões anteriores, imutabilidade do histórico e integridade de estoques."]
    ]
    format_table(doc.add_table(rows=1, cols=4), [1.6, 1.0, 1.1, 3.0], t_sim_headers, t_sim_rows)

    # ================= SEÇÃO 9 =================
    add_h1("9. Indicador de Resultado da Solução")
    add_h2("9.1 Definição do Indicador Mensurável")
    add_callout(doc, [
        ("Indicador de Resultado da Solução:\n", True, False, COLOR_NAVY),
        ("Taxa de Redução no Tempo Médio de Triagem e Formação de Equipes Qualificadas para Atendimento a Demandas de Desastre.\n", True, True, None),
        ("Meta Operacional: ", True, False, COLOR_NAVY),
        ("Reduzir em pelo menos 50% o tempo necessário para que um coordenador identifique e valide voluntários e recursos pertinentes a uma demanda complexa, comparando busca manual em planilhas vs. busca assistida por IA na RedeSolidária.", False, False, None)
    ])

    add_h2("9.2 Protocolo Experimental (Manual vs. Assistido) e Fórmula")
    add_body("A mensuração é realizada comparando o tempo transcorrido desde a apresentação da necessidade até a finalização da equipe validada:")
    add_bullet("Cenário de Controle (Manual):", "Operador realiza buscas manuais em planilhas dispersas, verificando datas de validade de certificados e compatibilidade de equipamentos.")
    add_bullet("Cenário Experimental (Assistido):", "Operador insere a demanda no sistema, que executa busca semântica vetorial e apresenta sugestões validadas em segundos.")
    add_body("A fórmula de cálculo do indicador é expressa por:")
    add_body("Reducao_Tempo (%) = [ (Tempo_Medio_Manual - Tempo_Medio_Assistido) / Tempo_Medio_Manual ] * 100")
    add_body("Critério de controle: Taxa de Pertinência Cadastral ≥ 95%, garantindo que o ganho de tempo ocorra com 100% de conformidade com os cadastros reais e diplomas válidos.")

    # ================= SEÇÃO 10 =================
    add_h1("10. Benefícios Esperados")
    add_bullet("Agilidade nas Golden Hours de Resposta:", "Redução drástica no tempo de triagem nas primeiras 24 a 72 horas pós-desastre, acelerando o envio de socorro qualificado.")
    add_bullet("Segurança Operacional e Mitigação de Vítimas Secundárias:", "Filtro rigoroso de cursos válidos que impede o envio de voluntários despreparados para áreas perigosas.")
    add_bullet("Eficiência e Não-Desperdício Logístico:", "Cálculo de sobreposição de viaturas e estoques que evita duplicidades e assegura distribuição equitativa de mantimentos.")
    add_bullet("Transparência e Memória Institucional:", "Registro imutável de todas as decisões com pareceres auditáveis para órgãos de controle (TCU, Ministérios Públicos).")
    add_bullet("Alavancagem para Municípios Pequenos:", "Democratização de tecnologia de ponta para prefeituras com equipes reduzidas de Defesa Civil.")

    # ================= SEÇÃO 11 =================
    add_h1("11. Limitações, Riscos e Estratégias de Mitigação")
    t_risk_headers = ["Limitação ou Risco", "Impacto Potencial", "Estratégia de Mitigação Adotada / Prevista"]
    t_risk_rows = [
        ["1. Queda de Conectividade", "Interrupção do acesso à API na zona de impacto.", "Operação centralizada na sala de situação municipal com link redundante; evolução com PWA offline e cache local."],
        ["2. Alucinação de Modelos LLM", "IA propor pessoas ou recursos inexistentes.", "Guardrail determinístico no nó pós-LLM do LangGraph que descarta qualquer ID inexistente no banco relacional."],
        ["3. Desatualização Cadastral", "Cursos vencidos ou contatos desatualizados.", "Vínculo institucional obrigatório (Meta 3.1.3), delegando às instituições parceiras a revalidação periódica de quadros."],
        ["4. Desafio Topológico Viário", "Indicar recurso próximo em linha reta mas com via bloqueada.", "Apoio à decisão explicitando que proximidade não garante acesso seguro; evolução futura com camadas PostGIS de tráfego viário."],
        ["5. Autenticação em Modo de Demonstração", "O emissor rápido de token administrativo (endpoint /api/v1/autenticacao/token-admin, sem trava de ambiente) gera acesso administrativo sem login federado.", "Recurso destinado exclusivamente a testes e à demonstração acadêmica desta entrega — não será levado a produção. A versão produtiva substituirá o emissor por autenticação federada com perfis granulares (coordenador, instituição e voluntário), com emissão restrita ao ambiente de desenvolvimento."]
    ]
    format_table(doc.add_table(rows=1, cols=3), [1.8, 2.2, 2.7], t_risk_headers, t_risk_rows)

    # ================= SEÇÃO 12 =================
    add_h1("12. Roteiro e Estrutura do Pitch (Vídeo de até 5 Minutos)")
    add_body("Em conformidade com a Seção 11 do edital, foi estruturado o roteiro de pitch em vídeo respondendo obrigatoriamente às 5 perguntas:")

    t_pitch_headers = ["Tempo", "Pergunta Obrigatória", "Conteúdo e Telas a Projetar"]
    t_pitch_rows = [
        ["00:00 - 00:30", "Abertura e Identificação", "Apresentação do aluno Luis Roberto de Moraes, disciplina Arquiteturas Convergentes (CEUB) e introdução à RedeSolidária."],
        ["00:30 - 01:25", "1. Qual é o problema?", "Exposição da desorganização das capacidades em desastres climáticos, planilhas dispersas e tempo crítico nas salas de crise."],
        ["01:25 - 02:10", "2. Qual meta do PN-PDC está sendo trabalhada?", "Meta 3.1.3 (Criar cadastro nacional de voluntários institucionais para formar rede de resposta), Objetivo 3.1 e Eixo Resposta (prazo 2031)."],
        ["02:10 - 03:05", "3. Como a Computação contribui para a meta?", "Convergência Tecnológica: Angular + Leaflet (SIG), Python/FastAPI (engenharia de dados), PostgreSQL 18 e LangGraph/LangChain (IA explicada)."],
        ["03:05 - 04:15", "4. Como a solução funciona?", "Demonstração prática do protótipo: delimitação de área inundada no mapa, cadastro de demanda, recomendação inteligente da IA e decisão administrativa humana."],
        ["04:15 - 04:50", "5. Como será medido o resultado?", "Indicador de resultado: Redução de 50% no tempo médio de triagem com 100% de validação determinística de IDs (54 testes OK)."],
        ["04:50 - 05:00", "Encerramento", "Fechamento acadêmico, impacto humanitário e agradecimentos."]
    ]
    format_table(doc.add_table(rows=1, cols=3), [1.1, 2.2, 3.4], t_pitch_headers, t_pitch_rows)

    # ================= SEÇÃO 13 =================
    add_h1("13. Conclusão e Próximos Passos")
    add_body("O desenvolvimento da plataforma RedeSolidária demonstrou como conceitos fundamentais de Ciência da Computação e arquiteturas modernas de software podem transformar necessidades críticas de Proteção e Defesa Civil em soluções estruturadas, seguras e mensuráveis.")
    add_body("Ao conectar a Meta 3.1.3 do PN-PDC 2025–2035 à convergência entre geoprocessamento vetorial, microsserviços fortemente tipados e inteligência artificial governada por grafos cognitivos com guardrails determinísticos, o projeto supera os riscos de alucinação de modelos genéricos e oferece aos coordenadores públicos uma ferramenta confiável de apoio à decisão.")

    # ================= SEÇÃO 14 =================
    add_h1("14. Referências Oficiais e Bibliográficas")
    add_bullet("BRASIL.", "Ministério da Integração e do Desenvolvimento Regional. Secretaria Nacional de Proteção e Defesa Civil. Plano Nacional de Proteção e Defesa Civil (PN-PDC 2025–2035). Brasília: MIDR/Sedec, 2024.")
    add_bullet("BRASIL.", "Decreto nº 12.652, de 2025. Dispõe sobre as diretrizes, objetivos e metas da Política Nacional de Proteção e Defesa Civil. Diário Oficial da União, Brasília, DF, 2025.")
    add_bullet("BRASIL.", "Lei nº 12.608, de 10 de abril de 2012. Institui a Política Nacional de Proteção e Defesa Civil - PNPDEC e o SINPDEC. Brasília, DF, 2012.")
    add_bullet("FASTAPI.", "FastAPI framework, high performance, easy to learn, fast to code, ready for production. Disponível em: <https://fastapi.tiangolo.com/>. Acesso em: 2026.")
    add_bullet("ANGULAR.", "Angular Web Development Framework Documentation. Google LLC. Disponível em: <https://angular.dev/>. Acesso em: 2026.")
    add_bullet("LANGCHAIN / LANGGRAPH.", "Building resilient language agents as graphs. Disponível em: <https://langchain-ai.github.io/langgraph/>. Acesso em: 2026.")
    add_bullet("POSTGRESQL GLOBAL DEVELOPMENT GROUP.", "PostgreSQL 18 Documentation. Disponível em: <https://www.postgresql.org/docs/>. Acesso em: 2026.")
    add_bullet("INTERNET ENGINEERING TASK FORCE (IETF).", "RFC 9457: Problem Details for HTTP APIs. Disponível em: <https://datatracker.ietf.org/doc/html/rfc9457>. Acesso em: 2026.")

    doc.save(output_path)
    print(f"DOCX generated successfully at: {output_path}")

if __name__ == "__main__":
    out_docx = os.path.join(ENTREGA_DIR, "Entrega_Sistematizacao_RedeSolidaria.docx")
    gerar_docx_completo(out_docx)
