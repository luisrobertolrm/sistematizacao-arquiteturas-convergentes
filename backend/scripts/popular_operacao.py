"""Script para popular massa de dados operacional e de demonstração na RedeSolidária.

Tabelas populadas (idempotente):
- pessoas
- pessoa_instituicao
- pessoa_profissao
- pessoa_curso
- recursos
- ofertas_atividade
- oferta_atividade_recurso
- desastres e desastre_tipo
- areas_afetadas (com polígonos GeoJSON para o mapa Leaflet)
- demandas e demanda_itens
"""

from __future__ import annotations

import sys
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DIR_BACKEND = Path(__file__).resolve().parent.parent
if str(DIR_BACKEND) not in sys.path:
    sys.path.insert(0, str(DIR_BACKEND))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from business.servico.cadastros import PessoaService
from business.servico.demandas import DemandasService
from business.servico.desastres import AreaAfetadaService, DesastreService
from business.servico.qualificacoes import (
    PessoaCursoService,
    PessoaInstituicaoService,
    PessoaProfissaoService,
)
from business.servico.recursos import (
    OfertaAtividadeService,
    OfertaRecursoService,
    RecursoService,
)
from business.view_models.cadastros import PessoaInput
from business.view_models.desastres import (
    AreaAfetadaInput,
    ClassificacaoInput,
    DesastreInput,
    GeometriaInput,
)
from business.view_models.operacao import DemandaInput, DemandaItemInput
from business.view_models.qualificacoes import (
    PessoaCursoInput,
    PessoaInstituicaoInput,
    PessoaProfissaoInput,
)
from business.view_models.recursos import (
    OfertaAtividadeInput,
    OfertaRecursoInput,
    RecursoInput,
)
from core.entity.cadastros import SituacaoCadastral
from core.entity.desastres import GravidadeArea, SituacaoArea, SituacaoDesastre
from core.entity.operacao import PrioridadeDemanda, SituacaoDemanda
from core.entity.qualificacoes import SituacaoValidacao, TipoVinculo
from core.entity.recursos import EstadoRecurso
from infra.configurations.cadastros import instituicoes, pessoas
from infra.configurations.capacidades import atividades, unidades_medida
from infra.configurations.demandas import demandas
from infra.configurations.desastres import areas_afetadas, desastres, tipos_desastre
from infra.configurations.qualificacoes import cursos, profissoes
from infra.configurations.recursos import ofertas_atividade, recursos, tipos_recurso
from infra.database.settings import DatabaseSettings

AUTOR = "seed-operacao"


def main() -> int:
    config = DatabaseSettings()
    engine = create_engine(config.database_url.get_secret_value(), pool_pre_ping=True)

    with Session(engine) as sessao:
        mapa_inst = {
            r.nome: r.id
            for r in sessao.execute(select(instituicoes.c.nome, instituicoes.c.id)).all()
        }
        mapa_prof = {
            r.nome: r.id
            for r in sessao.execute(select(profissoes.c.nome, profissoes.c.id)).all()
        }
        mapa_curso = {
            r.nome: r.id for r in sessao.execute(select(cursos.c.nome, cursos.c.id)).all()
        }
        mapa_ativ = {
            r.codigo: (r.id, r.id_unidade_capacidade)
            for r in sessao.execute(
                select(
                    atividades.c.codigo,
                    atividades.c.id,
                    atividades.c.id_unidade_capacidade,
                )
            ).all()
        }
        mapa_tipo_rec = {
            r.nome: (r.id, r.id_unidade_medida)
            for r in sessao.execute(
                select(
                    tipos_recurso.c.nome,
                    tipos_recurso.c.id,
                    tipos_recurso.c.id_unidade_medida,
                )
            ).all()
        }
        mapa_tipo_des = {
            r.codigo: r.id
            for r in sessao.execute(
                select(tipos_desastre.c.codigo, tipos_desastre.c.id)
            ).all()
        }
        mapa_unid = {
            r.codigo: r.id
            for r in sessao.execute(
                select(unidades_medida.c.codigo, unidades_medida.c.id)
            ).all()
        }

    inst_usp = mapa_inst["Universidade de São Paulo (USP)"]
    inst_unicamp = mapa_inst["Universidade Estadual de Campinas (UNICAMP)"]
    inst_unesp = mapa_inst["Universidade Estadual Paulista Júlio de Mesquita Filho (UNESP)"]
    inst_ifsp = mapa_inst["Instituto Federal de São Paulo (IFSP)"]
    inst_senai = mapa_inst["SENAI São Paulo"]
    inst_senac = mapa_inst["SENAC São Paulo"]

    # 1. Pessoas + Vínculos + Profissões + Cursos
    print("\n--- Populando Pessoas, Vínculos, Profissões e Cursos ---")
    dados_pessoas = [
        {
            "nome": "Dr. Carlos Eduardo Mendes",
            "municipio": "3550308",
            "uf": "SP",
            "email": "carlos.mendes@usp.br",
            "tel": "11988112233",
            "lat": Decimal("-23.5558000"),
            "lon": Decimal("-46.6396000"),
            "inst": inst_usp,
            "vinculo": TipoVinculo.FUNCIONARIO,
            "prof": "Médico Clínico",
            "reg": "CRM145890",
            "orgao": "CRMSP",
            "curso": "Primeiros Socorros e Suporte Básico de Vida",
        },
        {
            "nome": "Enf. Mariana Costa Silva",
            "municipio": "3550308",
            "uf": "SP",
            "email": "mariana.silva@usp.br",
            "tel": "11988223344",
            "lat": Decimal("-23.5614000"),
            "lon": Decimal("-46.6558000"),
            "inst": inst_usp,
            "vinculo": TipoVinculo.VOLUNTARIO,
            "prof": "Enfermeiro de Emergência",
            "reg": "COREN441200",
            "orgao": "CORENSP",
            "curso": "Técnico em Enfermagem de Emergência e Resgate",
        },
        {
            "nome": "Eng. Roberto Almeida Prado",
            "municipio": "3550308",
            "uf": "SP",
            "email": "roberto.prado@ifsp.edu.br",
            "tel": "11988334455",
            "lat": Decimal("-23.5329000"),
            "lon": Decimal("-46.6395000"),
            "inst": inst_ifsp,
            "vinculo": TipoVinculo.ASSOCIADO,
            "prof": "Engenheiro Civil",
            "reg": "CREA506987123",
            "orgao": "CREASP",
            "curso": "Avaliação e Percepção de Risco Geológico e Hidrológico",
        },
        {
            "nome": "João Pedro Ferreira",
            "municipio": "3550308",
            "uf": "SP",
            "email": "joao.ferreira@senai.br",
            "tel": "11988445566",
            "lat": Decimal("-23.5489000"),
            "lon": Decimal("-46.6388000"),
            "inst": inst_senai,
            "vinculo": TipoVinculo.VOLUNTARIO,
            "prof": "Motorista de Caminhão Pesado",
            "reg": "CNH99887766",
            "orgao": "DETRANSP",
            "curso": "Logística Humanitária e Gestão de Cadeia de Suprimentos",
        },
        {
            "nome": "Paula Regina Santos",
            "municipio": "3550308",
            "uf": "SP",
            "email": "paula.santos@senac.br",
            "tel": "11988556677",
            "lat": Decimal("-23.5670000"),
            "lon": Decimal("-46.6480000"),
            "inst": inst_senac,
            "vinculo": TipoVinculo.VOLUNTARIO,
            "prof": "Cozinheiro Geral",
            "reg": "CRN10293",
            "orgao": "CRNSP",
            "curso": "Gestão e Coordenação de Abrigos Temporários",
        },
        {
            "nome": "Lucas Gabriel Oliveira",
            "municipio": "3550308",
            "uf": "SP",
            "email": "lucas.oliveira@unesp.br",
            "tel": "11988667788",
            "lat": Decimal("-23.5400000"),
            "lon": Decimal("-46.6200000"),
            "inst": inst_unesp,
            "vinculo": TipoVinculo.VOLUNTARIO,
            "prof": "Bombeiro Civil",
            "reg": "CBSP77441",
            "orgao": "CBMSP",
            "curso": "Segurança e Operação de Embarcações de Resgate",
        },
        {
            "nome": "Dra. Beatriz Helena Rocha",
            "municipio": "3509502",
            "uf": "SP",
            "email": "beatriz.rocha@unicamp.br",
            "tel": "19988778899",
            "lat": Decimal("-22.8180000"),
            "lon": Decimal("-47.0640000"),
            "inst": inst_unicamp,
            "vinculo": TipoVinculo.VOLUNTARIO,
            "prof": "Psicólogo Clínico",
            "reg": "CRP06112233",
            "orgao": "CRPSP",
            "curso": "Apoio Psicossocial em Emergências e Desastres",
        },
        {
            "nome": "Fernanda Lima Gonçalves",
            "municipio": "3550308",
            "uf": "SP",
            "email": "fernanda.goncalves@senac.br",
            "tel": "11988990011",
            "lat": Decimal("-23.5505000"),
            "lon": Decimal("-46.6333000"),
            "inst": inst_senac,
            "vinculo": TipoVinculo.FUNCIONARIO,
            "prof": "Assistente Social",
            "reg": "CRESS33445",
            "orgao": "CRESSSP",
            "curso": "Gestão e Coordenação de Abrigos Temporários",
        },
    ]

    mapa_pessoas: dict[str, UUID] = {}
    for item in dados_pessoas:
        with Session(engine) as sessao:
            existente = sessao.scalar(
                select(pessoas.c.id).where(pessoas.c.nome == item["nome"]).limit(1)
            )
        if existente:
            mapa_pessoas[str(item["nome"])] = existente
            print(f"  [Já existe] Pessoa: {item['nome']}")
            continue

        with Session(engine) as sessao:
            p_vm = PessoaService(sessao).criar(
                PessoaInput(
                    nome=str(item["nome"]),
                    municipio_codigo_ibge=str(item["municipio"]),
                    uf=str(item["uf"]),
                    email_contato=str(item["email"]),
                    telefone_contato=str(item["tel"]),
                    latitude=item["lat"],
                    longitude=item["lon"],
                    situacao_cadastral=SituacaoCadastral.VALIDADA,
                ),
                AUTOR,
            )
            mapa_pessoas[str(item["nome"])] = p_vm.id
            print(f"  ✓ [Inserido] Pessoa: {p_vm.nome}")

        with Session(engine) as sessao:
            PessoaInstituicaoService(sessao).criar(
                p_vm.id,
                PessoaInstituicaoInput(
                    instituicao_id=item["inst"],
                    tipo_vinculo=item["vinculo"],
                    inicio_em=date(2024, 1, 15),
                    situacao_validacao=SituacaoValidacao.VALIDADA,
                ),
                AUTOR,
            )
        with Session(engine) as sessao:
            PessoaProfissaoService(sessao).criar(
                p_vm.id,
                PessoaProfissaoInput(
                    profissao_id=mapa_prof[str(item["prof"])],
                    registro_profissional=str(item["reg"]),
                    orgao_registro=str(item["orgao"]),
                    uf_registro="SP",
                    validade_em=date(2028, 12, 31),
                    situacao_validacao=SituacaoValidacao.VALIDADA,
                ),
                AUTOR,
            )
        with Session(engine) as sessao:
            PessoaCursoService(sessao).criar(
                p_vm.id,
                PessoaCursoInput(
                    curso_id=mapa_curso[str(item["curso"])],
                    instituicao_emissora="Escola Nacional de Defesa Civil",
                    conclusao_em=date(2025, 6, 10),
                    validade_em=date(2028, 6, 10),
                    carga_horaria=Decimal("40.00"),
                    comprovante_referencia=f"CERT-ENADEC-{p_vm.id.hex[:8].upper()}",
                    situacao_validacao=SituacaoValidacao.VALIDADA,
                ),
                AUTOR,
            )

    # 2. Recursos físicos e estoques
    print("\n--- Populando Recursos Físicos e Lotes ---")
    dados_recursos = [
        {
            "nome": "Caminhão Baú Logístico VUC-01",
            "tipo": "Caminhão Baú de Carga",
            "id_tag": "PLACA-BRA2E19",
            "qtd": Decimal("1"),
            "inst": inst_senai,
            "mun": "3550308",
        },
        {
            "nome": "Bote Inflável Resgate Rápido BR-04",
            "tipo": "Bote Inflável com Motor de Popa",
            "id_tag": "CAPITANIA-SP-402",
            "qtd": Decimal("1"),
            "inst": inst_unesp,
            "mun": "3550308",
        },
        {
            "nome": "Gerador Diesel Estacionário 10kVA GE-01",
            "tipo": "Gerador de Energia a Diesel 10kVA",
            "id_tag": "PAT-IFSP-9001",
            "qtd": Decimal("1"),
            "inst": inst_ifsp,
            "mun": "3550308",
        },
        {
            "nome": "Bomba Submersível de Drenagem BD-02",
            "tipo": "Bomba de Sucção e Drenagem de Água",
            "id_tag": "PAT-IFSP-9002",
            "qtd": Decimal("1"),
            "inst": inst_ifsp,
            "mun": "3550308",
        },
        {
            "nome": "Lote Água Potável Galões 20L — Depósito Central",
            "tipo": "Água Mineral Envasada em Galão de 20L",
            "id_tag": "LOTE-AGUA-2026-01",
            "qtd": Decimal("600"),
            "inst": inst_usp,
            "mun": "3550308",
        },
        {
            "nome": "Estoque Cestas Básicas Emergenciais",
            "tipo": "Cesta Básica de Alimentos Não Perecíveis",
            "id_tag": "LOTE-ALIM-2026-02",
            "qtd": Decimal("350"),
            "inst": inst_senac,
            "mun": "3550308",
        },
        {
            "nome": "Lote Colchões D33 para Abrigo Temporário",
            "tipo": "Colchão Solteiro de Espuma D33",
            "id_tag": "LOTE-COLCHAO-2026-03",
            "qtd": Decimal("200"),
            "inst": inst_senac,
            "mun": "3550308",
        },
        {
            "nome": "Lote Kits de Primeiros Socorros e Trauma",
            "tipo": "Kit de Primeiros Socorros e Curativos",
            "id_tag": "LOTE-SAUDE-2026-04",
            "qtd": Decimal("80"),
            "inst": inst_usp,
            "mun": "3550308",
        },
    ]

    mapa_recursos: dict[str, UUID] = {}
    for r_item in dados_recursos:
        with Session(engine) as sessao:
            existente = sessao.scalar(
                select(recursos.c.id).where(recursos.c.nome == r_item["nome"]).limit(1)
            )
        if existente:
            mapa_recursos[str(r_item["nome"])] = existente
            print(f"  [Já existe] Recurso: {r_item['nome']}")
            continue
        id_tipo, _ = mapa_tipo_rec[str(r_item["tipo"])]
        with Session(engine) as sessao:
            rec_vm = RecursoService(sessao).criar(
                RecursoInput(
                    tipo_recurso_id=id_tipo,
                    instituicao_id=r_item["inst"],
                    nome=str(r_item["nome"]),
                    descricao=f"Recurso operacional mantido para pronta resposta ({r_item['id_tag']}).",
                    identificacao=str(r_item["id_tag"]),
                    quantidade_total=r_item["qtd"],
                    estado_operacional=EstadoRecurso.OPERACIONAL,
                    municipio_codigo_ibge=str(r_item["mun"]),
                    latitude=Decimal("-23.5505000"),
                    longitude=Decimal("-46.6333000"),
                ),
                AUTOR,
            )
            mapa_recursos[str(r_item["nome"])] = rec_vm.id
            print(f"  ✓ [Inserido] Recurso: {rec_vm.nome}")

    # 3. Ofertas de Atividades e Recursos da Oferta
    print("\n--- Populando Ofertas de Atividades e Vínculos de Recursos ---")
    dados_ofertas = [
        {
            "cod_ativ": "resgate-aquatico",
            "inst": inst_unesp,
            "mun": "3550308",
            "cap": Decimal("25"),
            "desc": "Equipe de salvamento aquático com bote motorizado e coletes salva-vidas.",
            "recurso": "Bote Inflável Resgate Rápido BR-04",
            "qtd_rec": Decimal("1"),
        },
        {
            "cod_ativ": "primeiros-socorros",
            "inst": inst_usp,
            "mun": "3550308",
            "cap": Decimal("80"),
            "desc": "Posto médico avançado com médicos e enfermeiros de emergência.",
            "recurso": "Lote Kits de Primeiros Socorros e Trauma",
            "qtd_rec": Decimal("20"),
        },
        {
            "cod_ativ": "distribuicao-agua",
            "inst": inst_usp,
            "mun": "3550308",
            "cap": Decimal("500"),
            "desc": "Distribuição controlada de água potável para famílias desalojadas.",
            "recurso": "Lote Água Potável Galões 20L — Depósito Central",
            "qtd_rec": Decimal("200"),
        },
        {
            "cod_ativ": "refeicoes-comunitarias",
            "inst": inst_senac,
            "mun": "3550308",
            "cap": Decimal("400"),
            "desc": "Cozinha comunitária solidária com preparo diário de refeições quentes.",
            "recurso": "Estoque Cestas Básicas Emergenciais",
            "qtd_rec": Decimal("50"),
        },
        {
            "cod_ativ": "gestao-abrigo",
            "inst": inst_senac,
            "mun": "3550308",
            "cap": Decimal("150"),
            "desc": "Coordenação completa de abrigo emergencial, acolhimento e dormitório.",
            "recurso": "Lote Colchões D33 para Abrigo Temporário",
            "qtd_rec": Decimal("100"),
        },
        {
            "cod_ativ": "transporte-carga",
            "inst": inst_senai,
            "mun": "3550308",
            "cap": Decimal("8"),
            "desc": "Transporte rodoviário de donativos e equipamentos pesados até áreas afetadas.",
            "recurso": "Caminhão Baú Logístico VUC-01",
            "qtd_rec": Decimal("1"),
        },
    ]

    for of_item in dados_ofertas:
        id_ativ, _ = mapa_ativ[str(of_item["cod_ativ"])]
        with Session(engine) as sessao:
            existente = sessao.scalar(
                select(ofertas_atividade.c.id)
                .where(
                    ofertas_atividade.c.atividade_id == id_ativ,
                    ofertas_atividade.c.instituicao_id == of_item["inst"],
                )
                .limit(1)
            )
        if existente:
            print(f"  [Já existe] Oferta: {of_item['cod_ativ']}")
            continue
        with Session(engine) as sessao:
            of_vm = OfertaAtividadeService(sessao).criar(
                OfertaAtividadeInput(
                    atividade_id=id_ativ,
                    instituicao_id=of_item["inst"],
                    municipio_atendimento_codigo_ibge=str(of_item["mun"]),
                    descricao_complementar=str(of_item["desc"]),
                    capacidade_declarada=of_item["cap"],
                    situacao_validacao=SituacaoValidacao.VALIDADA,
                ),
                AUTOR,
            )
            print(f"  ✓ [Inserido] Oferta: {of_vm.atividade_nome} ({of_vm.responsavel_nome})")

        with Session(engine) as sessao:
            OfertaRecursoService(sessao, of_vm.id).criar(
                OfertaRecursoInput(
                    recurso_id=mapa_recursos[str(of_item["recurso"])],
                    quantidade_prevista=of_item["qtd_rec"],
                ),
                AUTOR,
            )

    # 4. Ocorrência de Desastre e Áreas Afetadas (GeoJSON)
    print("\n--- Populando Ocorrência de Desastre e Áreas Afetadas no Mapa ---")
    agora = datetime.now(UTC)
    titulo_desastre = "Operação Vale Azul — Chuvas Intensas, Enxurrada e Deslizamentos"
    with Session(engine) as sessao:
        id_desastre = sessao.scalar(
            select(desastres.c.id).where(desastres.c.titulo == titulo_desastre).limit(1)
        )
    if not id_desastre:
        with Session(engine) as sessao:
            des_vm = DesastreService(sessao).criar(
                DesastreInput(
                    titulo=titulo_desastre,
                    descricao=(
                        "Acumulado pluviométrico superior a 180 mm em 24h provocando transbordamento "
                        "do Rio Azul, alagamento da Várzea Baixa e escorregamentos na Encosta Norte."
                    ),
                    inicio_em=agora - timedelta(days=2),
                    situacao=SituacaoDesastre.EM_RESPOSTA,
                    id_instituicao_coordenadora=inst_usp,
                    classificacoes=[
                        ClassificacaoInput(
                            id_tipo_desastre=mapa_tipo_des["12200"], principal=True
                        ),
                        ClassificacaoInput(
                            id_tipo_desastre=mapa_tipo_des["13214"], principal=False
                        ),
                    ],
                ),
                AUTOR,
            )
            id_desastre = des_vm.id
            print(f"  ✓ [Inserido] Desastre: {des_vm.titulo}")
    else:
        print(f"  [Já existe] Desastre: {titulo_desastre}")

    dados_areas = [
        {
            "nome": "Setor 1 — Várzea Baixa (Zona Ribeirinha Inundada)",
            "desc": "Mais de 120 residências atingidas pela elevação brusca do nível do rio; acesso viário interrompido.",
            "gravidade": GravidadeArea.CRITICA,
            "situacao": SituacaoArea.EM_RESPOSTA,
            "coords": [
                [
                    (-46.6450, -23.5450),
                    (-46.6350, -23.5450),
                    (-46.6350, -23.5380),
                    (-46.6450, -23.5380),
                    (-46.6450, -23.5450),
                ]
            ],
        },
        {
            "nome": "Setor 2 — Encosta Norte (Risco Geológico Alto)",
            "desc": "Taludes instáveis e trincas em edificações; evacuação preventiva de 65 famílias.",
            "gravidade": GravidadeArea.ALTA,
            "situacao": SituacaoArea.EM_AVALIACAO,
            "coords": [
                [
                    (-46.6320, -23.5520),
                    (-46.6220, -23.5520),
                    (-46.6220, -23.5440),
                    (-46.6320, -23.5440),
                    (-46.6320, -23.5520),
                ]
            ],
        },
        {
            "nome": "Setor 3 — Ginásio Municipal Centro (Abrigo Base)",
            "desc": "Ponto de apoio logístico, triagem médica e acolhimento das famílias desabrigadas.",
            "gravidade": GravidadeArea.MODERADA,
            "situacao": SituacaoArea.EM_RESPOSTA,
            "coords": [
                [
                    (-46.6550, -23.5580),
                    (-46.6460, -23.5580),
                    (-46.6460, -23.5510),
                    (-46.6550, -23.5510),
                    (-46.6550, -23.5580),
                ]
            ],
        },
    ]

    mapa_areas: dict[str, UUID] = {}
    for a_item in dados_areas:
        with Session(engine) as sessao:
            existente = sessao.scalar(
                select(areas_afetadas.c.id)
                .where(
                    areas_afetadas.c.id_desastre == id_desastre,
                    areas_afetadas.c.nome == a_item["nome"],
                )
                .limit(1)
            )
        if existente:
            mapa_areas[str(a_item["nome"])] = existente
            print(f"  [Já existe] Área Afetada: {a_item['nome']}")
            continue
        with Session(engine) as sessao:
            area_vm = AreaAfetadaService(sessao, id_desastre).criar(
                AreaAfetadaInput(
                    nome=str(a_item["nome"]),
                    descricao=str(a_item["desc"]),
                    municipio_codigo_ibge="3550308",
                    gravidade=a_item["gravidade"],
                    situacao=a_item["situacao"],
                    geometria=GeometriaInput(
                        type="Polygon",
                        coordinates=a_item["coords"],
                    ),
                ),
                AUTOR,
            )
            mapa_areas[str(a_item["nome"])] = area_vm.id
            print(f"  ✓ [Inserido] Área Afetada: {area_vm.nome}")

    # 5. Demandas Emergenciais e Itens de Necessidade
    print("\n--- Populando Demandas Emergenciais e Itens ---")
    id_solicitante = mapa_pessoas["Fernanda Lima Gonçalves"]
    id_ativ_resgate, _ = mapa_ativ["resgate-aquatico"]
    id_ativ_agua, _ = mapa_ativ["distribuicao-agua"]
    id_ativ_refeicao, _ = mapa_ativ["refeicoes-comunitarias"]
    id_ativ_abrigo, _ = mapa_ativ["gestao-abrigo"]
    id_ativ_vistoria, _ = mapa_ativ["vistoria-estrutural"]
    id_tipo_agua, unid_agua = mapa_tipo_rec["Água Mineral Envasada em Galão de 20L"]
    id_tipo_colchao, unid_colchao = mapa_tipo_rec["Colchão Solteiro de Espuma D33"]
    id_tipo_gerador, unid_gerador = mapa_tipo_rec["Gerador de Energia a Diesel 10kVA"]

    dados_demandas = [
        {
            "area": "Setor 1 — Várzea Baixa (Zona Ribeirinha Inundada)",
            "titulo": "Resgate Aquático Urgente e Suprimento de Água Potável na Várzea",
            "desc": "Famílias ilhadas necessitam de evacuação por bote e abastecimento imediato de água potável.",
            "prio": PrioridadeDemanda.URGENTE,
            "itens": [
                DemandaItemInput(
                    id_atividade=id_ativ_resgate,
                    id_unidade_medida=mapa_unid["pessoa"],
                    quantidade_solicitada=Decimal("30"),
                    observacoes="Priorizar idosos e crianças em residências de 2 pavimentos.",
                ),
                DemandaItemInput(
                    id_tipo_recurso=id_tipo_agua,
                    id_unidade_medida=unid_agua,
                    quantidade_solicitada=Decimal("150"),
                    observacoes="Entrega no ponto seco da cabeceira da ponte.",
                ),
            ],
        },
        {
            "area": "Setor 2 — Encosta Norte (Risco Geológico Alto)",
            "titulo": "Vistoria Estrutural de Contenções e Energia de Emergência",
            "desc": "Inspeção de risco de novos deslizamentos nas ruas altas e gerador para iluminação do posto avançado.",
            "prio": PrioridadeDemanda.ALTA,
            "itens": [
                DemandaItemInput(
                    id_atividade=id_ativ_vistoria,
                    id_unidade_medida=mapa_unid["un"],
                    quantidade_solicitada=Decimal("25"),
                    observacoes="Laudo técnico para liberação ou interdição definitiva.",
                ),
                DemandaItemInput(
                    id_tipo_recurso=id_tipo_gerador,
                    id_unidade_medida=unid_gerador,
                    quantidade_solicitada=Decimal("1"),
                    observacoes="Necessário gerador diesel com autonomia mínima de 12 horas.",
                ),
            ],
        },
        {
            "area": "Setor 3 — Ginásio Municipal Centro (Abrigo Base)",
            "titulo": "Acolhimento, Alimentação e Dormitório para 120 Desabrigados",
            "desc": "Estruturação do abrigo municipal com fornecimento de refeições quentes e colchões.",
            "prio": PrioridadeDemanda.ALTA,
            "itens": [
                DemandaItemInput(
                    id_atividade=id_ativ_refeicao,
                    id_unidade_medida=mapa_unid["refeicao"],
                    quantidade_solicitada=Decimal("360"),
                    observacoes="Três refeições diárias para 120 pessoas acolhidas.",
                ),
                DemandaItemInput(
                    id_atividade=id_ativ_abrigo,
                    id_unidade_medida=mapa_unid["vaga"],
                    quantidade_solicitada=Decimal("120"),
                    observacoes="Equipe para triagem social e organização das alas.",
                ),
                DemandaItemInput(
                    id_tipo_recurso=id_tipo_colchao,
                    id_unidade_medida=unid_colchao,
                    quantidade_solicitada=Decimal("120"),
                    observacoes="Colchões D33 impermeabilizados.",
                ),
            ],
        },
    ]

    for d_item in dados_demandas:
        with Session(engine) as sessao:
            existente = sessao.scalar(
                select(demandas.c.id).where(demandas.c.titulo == d_item["titulo"]).limit(1)
            )
        if existente:
            print(f"  [Já existe] Demanda: {d_item['titulo']}")
            continue
        with Session(engine) as sessao:
            dem_vm = DemandasService(sessao).salvar(
                None,
                DemandaInput(
                    id_area_afetada=mapa_areas[str(d_item["area"])],
                    id_pessoa_solicitante=id_solicitante,
                    titulo=str(d_item["titulo"]),
                    descricao=str(d_item["desc"]),
                    prioridade=d_item["prio"],
                    inicio_previsto_em=agora + timedelta(hours=1),
                    prazo_em=agora + timedelta(days=3),
                    situacao=SituacaoDemanda.ABERTA,
                    itens=d_item["itens"],
                ),
                AUTOR,
            )
            print(f"  ✓ [Inserido] Demanda: {dem_vm.titulo} ({len(dem_vm.itens)} itens)")

    print("\n=================================================================")
    print(" ✓ Massa de dados operacional aplicada com sucesso!")
    print("=================================================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
