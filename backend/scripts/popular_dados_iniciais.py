"""Script para popular dados iniciais essenciais nas tabelas de catálogo da RedeSolidária.

Tabelas populadas:
- unidades_medida
- categorias_atividade
- atividades (com atividade_termos)
- cursos
- profissoes
- tipos_desastre
- tipos_recurso

Uso:
  python backend/scripts/popular_dados_iniciais.py
ou
  backend/.venv/Scripts/python.exe backend/scripts/popular_dados_iniciais.py
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4, UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# Garante saída UTF-8 no terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Adiciona o diretório do backend ao sys.path para importações locais
DIR_BACKEND = Path(__file__).resolve().parent.parent
if str(DIR_BACKEND) not in sys.path:
    sys.path.insert(0, str(DIR_BACKEND))

from core.entity.capacidades import (
    Atividade,
    AtividadeTermo,
    CategoriaAtividade,
    UnidadeMedida,
)
from core.entity.desastres import TipoDesastre
from core.entity.qualificacoes import Curso, Profissao, TipoCurso
from core.entity.recursos import CategoriaRecurso, ModoControleRecurso, TipoRecurso
from core.semantica import hash_atividade, hash_qualificacao, hash_tipo_recurso
from infra.configurations.cadastros import metadata
from infra.configurations.capacidades import (
    atividade_termos,
    atividades,
    categorias_atividade,
    unidades_medida,
)
from infra.configurations.desastres import tipos_desastre
from infra.configurations.qualificacoes import cursos, profissoes
from infra.configurations.recursos import tipos_recurso
from infra.database.settings import DatabaseSettings

AUTOR = "sistema-inicializacao"


def obter_sessao() -> Session:
    config = DatabaseSettings()
    url = config.database_url.get_secret_value()
    engine = create_engine(url, pool_pre_ping=True)
    return Session(engine)


def popular_unidades(sessao: Session) -> dict[str, UUID]:
    print("\n--- Populando Unidades de Medida ---")
    dados = [
        {"codigo": "un", "nome": "Unidade", "simbolo": "un"},
        {"codigo": "kg", "nome": "Quilograma", "simbolo": "kg"},
        {"codigo": "t", "nome": "Tonelada", "simbolo": "t"},
        {"codigo": "l", "nome": "Litro", "simbolo": "L"},
        {"codigo": "m3", "nome": "Metro cúbico", "simbolo": "m³"},
        {"codigo": "cx", "nome": "Caixa", "simbolo": "cx"},
        {"codigo": "fardo", "nome": "Fardo", "simbolo": "fdo"},
        {"codigo": "kit", "nome": "Kit", "simbolo": "kit"},
        {"codigo": "dose", "nome": "Dose", "simbolo": "ds"},
        {"codigo": "hora", "nome": "Hora", "simbolo": "h"},
        {"codigo": "diaria", "nome": "Diária", "simbolo": "d"},
        {"codigo": "refeicao", "nome": "Refeição", "simbolo": "ref"},
        {"codigo": "vaga", "nome": "Vaga", "simbolo": "vga"},
        {"codigo": "pessoa", "nome": "Pessoa", "simbolo": "pes"},
    ]

    mapa_ids: dict[str, UUID] = {}
    agora = datetime.now(timezone.utc)

    for item in dados:
        stmt = select(unidades_medida.c.id).where(unidades_medida.c.codigo == item["codigo"])
        existente = sessao.execute(stmt).scalar()
        if existente:
            mapa_ids[item["codigo"]] = existente
            print(f"  [Já existe] Unidade: {item['nome']} ({item['codigo']})")
        else:
            novo_id = uuid4()
            sessao.execute(
                unidades_medida.insert().values(
                    id=novo_id,
                    codigo=item["codigo"],
                    nome=item["nome"],
                    simbolo=item["simbolo"],
                    criado_em=agora,
                    atualizado_em=agora,
                    inativado_em=None,
                    criado_por=AUTOR,
                    atualizado_por=AUTOR,
                )
            )
            mapa_ids[item["codigo"]] = novo_id
            print(f"  ✓ [Inserido] Unidade: {item['nome']} ({item['simbolo']})")

    sessao.commit()
    return mapa_ids


def popular_categorias(sessao: Session) -> dict[str, UUID]:
    print("\n--- Populando Categorias de Atividade ---")
    dados = [
        {
            "codigo": "salvamento-resgate",
            "nome": "Busca, Salvamento e Resgate",
            "descricao": "Atividades operacionais de busca, resgate em águas, estruturas colapsadas e salvamento de pessoas e animais.",
        },
        {
            "codigo": "acolhimento-abrigo",
            "nome": "Acolhimento e Abrigamento Temporário",
            "descricao": "Gestão de abrigos emergenciais, alojamento temporário, acolhimento familiar e distribuição de itens de dormitório.",
        },
        {
            "codigo": "alimentacao-nutricao",
            "nome": "Alimentação e Nutrição",
            "descricao": "Fornecimento de água potável, cestas de alimentos e preparação de refeições comunitárias.",
        },
        {
            "codigo": "saude-apoio-psicossocial",
            "nome": "Saúde e Apoio Psicossocial",
            "descricao": "Atendimento pré-hospitalar, primeiros socorros, apoio psicológico e assistência básica de saúde a vítimas.",
        },
        {
            "codigo": "logistica-suprimentos",
            "nome": "Logística e Suprimentos",
            "descricao": "Armazenagem, triagem, transporte e distribuição de donativos, insumos e equipamentos operacionais.",
        },
        {
            "codigo": "engenharia-reconstrucao",
            "nome": "Engenharia, Avaliação Estrutural e Limpeza",
            "descricao": "Vistorias de risco, desobstrução de vias, limpeza urbana, drenagem e reabilitação de infraestrutura básica.",
        },
        {
            "codigo": "comunicacao-articulacao",
            "nome": "Comunicação, Triagem e Articulação Comunitária",
            "descricao": "Cadastro de famílias, radiocomunicação, divulgação de alertas e coordenação comunitária de voluntários.",
        },
    ]

    mapa_ids: dict[str, UUID] = {}
    agora = datetime.now(timezone.utc)

    for item in dados:
        stmt = select(categorias_atividade.c.id).where(categorias_atividade.c.codigo == item["codigo"])
        existente = sessao.execute(stmt).scalar()
        if existente:
            mapa_ids[item["codigo"]] = existente
            print(f"  [Já existe] Categoria: {item['nome']} ({item['codigo']})")
        else:
            novo_id = uuid4()
            sessao.execute(
                categorias_atividade.insert().values(
                    id=novo_id,
                    codigo=item["codigo"],
                    nome=item["nome"],
                    descricao=item["descricao"],
                    criado_em=agora,
                    atualizado_em=agora,
                    inativado_em=None,
                    criado_por=AUTOR,
                    atualizado_por=AUTOR,
                )
            )
            mapa_ids[item["codigo"]] = novo_id
            print(f"  ✓ [Inserido] Categoria: {item['nome']}")

    sessao.commit()
    return mapa_ids


def popular_atividades(sessao: Session, cats: dict[str, UUID], unids: dict[str, UUID]) -> dict[str, UUID]:
    print("\n--- Populando Atividades e Termos Sinônimos ---")
    dados = [
        {
            "codigo": "resgate-aquatico",
            "nome": "Resgate Aquático e em Áreas Inundadas",
            "categoria": "salvamento-resgate",
            "unidade": "pessoa",
            "descricao": "Busca e salvamento de pessoas isoladas por inundações, enxurradas e cheias com embarcações adequadas.",
            "orientacoes": "Exige equipe treinada com coletes salva-vidas e embarcações com motor e remo.",
            "restricoes": "Não operar em correntezas extremas sem ancoragem e apoio do Corpo de Bombeiros.",
            "termos": ["salvamento em barco", "bote salva vidas", "alagamento", "resgate barco", "evacuacao ilhados"],
        },
        {
            "codigo": "busca-escombros",
            "nome": "Busca e Resgate em Estruturas Colapsadas",
            "categoria": "salvamento-resgate",
            "unidade": "pessoa",
            "descricao": "Localização e extração de vítimas presas sob escombros ou soterramentos pós-deslizamento.",
            "orientacoes": "Avaliação prévia de estabilidade estrutural antes do ingresso de socorristas.",
            "restricoes": "Uso obrigatório de EPI completo e monitoramento geológico contínuo.",
            "termos": ["desabamento", "escombros", "soterramento", "deslizamento terra", "busca soterrados"],
        },
        {
            "codigo": "gestao-abrigo",
            "nome": "Montagem e Gestão de Abrigo Temporário",
            "categoria": "acolhimento-abrigo",
            "unidade": "vaga",
            "descricao": "Coordenação do espaço de acolhimento, cadastramento de desabrigados e garantia de convivência segura.",
            "orientacoes": "Seguir padrões mínimos do Projeto Esfera para ventilação, segurança e sanitários separados.",
            "restricoes": "Respeitar capacidade máxima declarada para evitar aglomerações e riscos sanitários.",
            "termos": ["alojamento provisorio", "centro de acolhida", "dormitorio emergencial", "abrigo municipal", "espaco desabrigados"],
        },
        {
            "codigo": "distribuicao-colchoes",
            "nome": "Distribuição de Colchões e Roupas de Cama",
            "categoria": "acolhimento-abrigo",
            "unidade": "kit",
            "descricao": "Entrega de colchões impermeáveis, cobertores térmicos e lençóis para famílias desabrigadas.",
            "orientacoes": "Priorizar crianças, idosos, gestantes e pessoas com deficiência.",
            "restricoes": "Garantir que os itens estejam secos e protegidos da chuva no transporte.",
            "termos": ["kit dormitorio", "cobertor", "lencol", "travesseiro", "agasalhos"],
        },
        {
            "codigo": "distribuicao-agua",
            "nome": "Distribuição de Água Potável",
            "categoria": "alimentacao-nutricao",
            "unidade": "l",
            "descricao": "Abastecimento emergencial de água tratada para consumo humano via caminhão pipa e água mineral envasada.",
            "orientacoes": "Monitorar teor de cloro e certificar potabilidade antes da entrega.",
            "restricoes": "Distribuir exclusivamente recipientes higienizados e vedados.",
            "termos": ["agua mineral", "caminhao pipa", "agua potavel", "hidratacao", "abastecimento emergencial"],
        },
        {
            "codigo": "refeicoes-comunitarias",
            "nome": "Preparação e Fornecimento de Refeições Prontas",
            "categoria": "alimentacao-nutricao",
            "unidade": "refeicao",
            "descricao": "Produção e distribuição de marmitas e refeições quentes balanceadas em cozinhas comunitárias.",
            "orientacoes": "Seguir normas de higiene alimentar e manter controle de temperatura das refeições prontas.",
            "restricoes": "Consumo em até duas horas após o preparo para prevenir intoxicações alimentares.",
            "termos": ["cozinha comunitaria", "quentinhas", "marmitex", "sopa", "alimentacao quente"],
        },
        {
            "codigo": "distribuicao-cestas",
            "nome": "Distribuição de Cestas Básicas",
            "categoria": "alimentacao-nutricao",
            "unidade": "cx",
            "descricao": "Entrega de kits de alimentos não perecíveis para famílias em situação de vulnerabilidade pós-desastre.",
            "orientacoes": "Registrar número do documento do responsável familiar e número de dependentes.",
            "restricoes": "Não incluir produtos perecíveis sem cadeia de refrigeração comprovada.",
            "termos": ["cesta de alimentos", "mantimentos", "generos alimenticios", "fardos comida", "rancho"],
        },
        {
            "codigo": "primeiros-socorros",
            "nome": "Atendimento Pré-Hospitalar e Primeiros Socorros",
            "categoria": "saude-apoio-psicossocial",
            "unidade": "pessoa",
            "descricao": "Atendimento emergencial a feridos, imobilizações, controle de hemorragias e triagem clínica.",
            "orientacoes": "Registrar prontuário de atendimento de emergência e transferir casos graves ao SAMU/hospital.",
            "restricoes": "Procedimentos invasivos restritos a profissionais habilitados.",
            "termos": ["APH", "socorrista", "curativos", "estabilizacao", "triagem medica"],
        },
        {
            "codigo": "apoio-psicossocial",
            "nome": "Acolhimento Psicológico e Social em Emergências",
            "categoria": "saude-apoio-psicossocial",
            "unidade": "pessoa",
            "descricao": "Suporte emocional, escuta ativa e intervenção em crise para pessoas impactadas por perdas e traumas.",
            "orientacoes": "Criar espaço reservado e acolhedor para escuta individual ou familiar.",
            "restricoes": "Evitar promessas irrealistas e respeitar o tempo emocional de cada afetado.",
            "termos": ["suporte emocional", "trauma", "acolhimento luto", "atendimento psicologico", "assistencia social"],
        },
        {
            "codigo": "distribuicao-higiene",
            "nome": "Distribuição de Kits de Higiene e Limpeza",
            "categoria": "saude-apoio-psicossocial",
            "unidade": "kit",
            "descricao": "Entrega de produtos de higiene pessoal e material sanitário para desinfecção de residências atingidas.",
            "orientacoes": "Instruir sobre diluição correta de hipoclorito para higienização de caixas d'água.",
            "restricoes": "Manter produtos químicos de limpeza afastados de embalagens de alimentos.",
            "termos": ["kit higiene pessoal", "sabonete", "escova dental", "absorvente", "material de desinfeccao"],
        },
        {
            "codigo": "transporte-carga",
            "nome": "Transporte Rodoviário de Cargas e Suprimentos",
            "categoria": "logistica-suprimentos",
            "unidade": "t",
            "descricao": "Movimentação rodoviária de donativos, água, equipamentos e mantimentos entre polos e áreas de desastre.",
            "orientacoes": "Conferência de rotas seguras e comunicação contínua com a base de operações.",
            "restricoes": "Não ultrapassar a capacidade técnica de carga dos veículos em estradas danificadas.",
            "termos": ["frete donativos", "caminhao de entrega", "carreta", "remocao suprimentos", "distribuicao regional"],
        },
        {
            "codigo": "triagem-donativos",
            "nome": "Triagem e Organização de Donativos",
            "categoria": "logistica-suprimentos",
            "unidade": "m3",
            "descricao": "Classificação, separação por gênero/tamanho, controle de validade e paletização de doações recebidas.",
            "orientacoes": "Descartar imediatamente itens rasgados, avariados ou medicamentos vencidos.",
            "restricoes": "Proibido armazenamento direto no piso; utilizar estrados ou paletes limpos.",
            "termos": ["galpao logistico", "separacao de roupas", "conferencia donativos", "estoque emergencial", "paletizacao"],
        },
        {
            "codigo": "vistoria-estrutural",
            "nome": "Vistoria e Avaliação de Risco Estrutural de Edificações",
            "categoria": "engenharia-reconstrucao",
            "unidade": "un",
            "descricao": "Inspeção visual e técnica de moradias e pontes para identificar trincas, risco de colapso e emissão de laudo.",
            "orientacoes": "Classificar em risco baixo, médio, alto ou muito alto, formalizando a interdição quando necessária.",
            "restricoes": "Não permitir retorno de moradores a imóveis com interdição formal da Defesa Civil.",
            "termos": ["interdicao casa", "pericia engenharia", "trincas rachaduras", "avaliacao geotecnica", "defesa civil laudo"],
        },
        {
            "codigo": "desobstrucao-vias",
            "nome": "Desobstrução de Vias e Remoção de Entulho",
            "categoria": "engenharia-reconstrucao",
            "unidade": "hora",
            "descricao": "Operação de retroescavadeiras e motosserras para corte de árvores e retirada de entulhos e lama de vias públicas.",
            "orientacoes": "Priorizar corredores de acesso a hospitais, abrigos e postos de comando.",
            "restricoes": "Desligamento e isolamento elétrico obrigatório caso haja cabos caídos na via.",
            "termos": ["retroescavadeira", "corte de arvores", "motosserra", "limpeza de ruas", "remoção de lama"],
        },
        {
            "codigo": "cadastro-familias",
            "nome": "Cadastro e Triagem de Famílias Afetadas",
            "categoria": "comunicacao-articulacao",
            "unidade": "pessoa",
            "descricao": "Levantamento censitário no território de famílias desabrigadas, desalojadas e suas necessidades emergenciais.",
            "orientacoes": "Identificar endereço de origem, perdas materiais e situação de saúde de cada membro familiar.",
            "restricoes": "Garantir confidencialidade e proteção de dados pessoais dos cidadãos cadastrados.",
            "termos": ["censo desabrigados", "ficha cadastral", "triagem social", "levantamento de perdas", "registro desabrigados"],
        },
    ]

    mapa_ids: dict[str, UUID] = {}
    agora = datetime.now(timezone.utc)

    for item in dados:
        stmt = select(atividades.c.id).where(atividades.c.codigo == item["codigo"])
        existente = sessao.execute(stmt).scalar()
        cat_id = cats[item["categoria"]]
        unid_id = unids.get(item["unidade"])

        if existente:
            mapa_ids[item["codigo"]] = existente
            print(f"  [Já existe] Atividade: {item['nome']} ({item['codigo']})")
        else:
            novo_id = uuid4()
            entidade_temp = Atividade(
                id=novo_id,
                codigo=item["codigo"],
                nome=item["nome"],
                descricao=item["descricao"],
                categoria_id=cat_id,
                id_unidade_capacidade=unid_id,
                orientacoes=item["orientacoes"],
                restricoes=item["restricoes"],
                hash_conteudo_semantico="",
                criado_em=agora,
                atualizado_em=agora,
                criado_por=AUTOR,
                atualizado_por=AUTOR,
            )
            hash_val = hash_atividade(entidade_temp, item["termos"])

            sessao.execute(
                atividades.insert().values(
                    id=novo_id,
                    codigo=item["codigo"],
                    nome=item["nome"],
                    descricao=item["descricao"],
                    categoria_id=cat_id,
                    id_unidade_capacidade=unid_id,
                    orientacoes=item["orientacoes"],
                    restricoes=item["restricoes"],
                    hash_conteudo_semantico=hash_val,
                    criado_em=agora,
                    atualizado_em=agora,
                    inativado_em=None,
                    criado_por=AUTOR,
                    atualizado_por=AUTOR,
                )
            )

            # Insere os termos sinônimos
            for termo_texto in item["termos"]:
                sessao.execute(
                    atividade_termos.insert().values(
                        id=uuid4(),
                        atividade_id=novo_id,
                        termo=termo_texto,
                        criado_em=agora,
                        atualizado_em=agora,
                        inativado_em=None,
                        criado_por=AUTOR,
                        atualizado_por=AUTOR,
                    )
                )

            mapa_ids[item["codigo"]] = novo_id
            print(f"  ✓ [Inserido] Atividade: {item['nome']} com {len(item['termos'])} termos")

    sessao.commit()
    return mapa_ids


def popular_cursos(sessao: Session) -> dict[str, UUID]:
    print("\n--- Populando Cursos de Qualificação e Certificação ---")
    dados = [
        {
            "nome": "Primeiros Socorros e Suporte Básico de Vida",
            "tipo": TipoCurso.CAPACITACAO,
            "descricao": "Procedimentos emergenciais de suporte básico de vida (SBV), reanimação cardiopulmonar e imobilizações em acidentes.",
        },
        {
            "nome": "Gestão e Coordenação de Abrigos Temporários",
            "tipo": TipoCurso.CAPACITACAO,
            "descricao": "Normas Esfera e diretrizes internacionais para organização, acolhimento e funcionamento digno de abrigos provisórios.",
        },
        {
            "nome": "Segurança e Operação de Embarcações de Resgate",
            "tipo": TipoCurso.TREINAMENTO,
            "descricao": "Condução segura de botes a motor e remo em correntezas, alagamentos e áreas submersas.",
        },
        {
            "nome": "Avaliação e Percepção de Risco Geológico e Hidrológico",
            "tipo": TipoCurso.CAPACITACAO,
            "descricao": "Identificação de sinais de instabilidade de taludes, encostas e risco iminente de deslizamentos e inundações.",
        },
        {
            "nome": "Apoio Psicossocial em Emergências e Desastres",
            "tipo": TipoCurso.CAPACITACAO,
            "descricao": "Primeiros cuidados psicológicos, acolhimento de luto e manejo de estresse em populações atingidas.",
        },
        {
            "nome": "Logística Humanitária e Gestão de Cadeia de Suprimentos",
            "tipo": TipoCurso.CAPACITACAO,
            "descricao": "Planejamento logístico, armazenagem de donativos e fluxos de distribuição equitativa em crises.",
        },
        {
            "nome": "Operação Segura de Motosserras no Corte de Árvores Caídas",
            "tipo": TipoCurso.TREINAMENTO,
            "descricao": "Técnicas de corte de árvores sob tensão e normas de segurança em desobstrução de vias públicas.",
        },
        {
            "nome": "Comunicação e Rádio Operador em Defesa Civil",
            "tipo": TipoCurso.TREINAMENTO,
            "descricao": "Protocolos de radiocomunicação VHF/HF e comunicação em rede para contingências em áreas isoladas.",
        },
        {
            "nome": "Técnico em Defesa Civil e Proteção Comunitária",
            "tipo": TipoCurso.TECNICO,
            "descricao": "Formação técnica abrangente em prevenção, mitigação, preparação, resposta e recuperação pós-desastre.",
        },
        {
            "nome": "Técnico em Enfermagem de Emergência e Resgate",
            "tipo": TipoCurso.TECNICO,
            "descricao": "Formação técnica para assistência pré-hospitalar, triagem e intervenções de urgência no território.",
        },
    ]

    mapa_ids: dict[str, UUID] = {}
    agora = datetime.now(timezone.utc)

    for item in dados:
        stmt = select(cursos.c.id).where(cursos.c.nome == item["nome"])
        existente = sessao.execute(stmt).scalar()
        if existente:
            mapa_ids[item["nome"]] = existente
            print(f"  [Já existe] Curso: {item['nome']}")
        else:
            novo_id = uuid4()
            entidade_temp = Curso(
                id=novo_id,
                nome=item["nome"],
                descricao=item["descricao"],
                tipo=item["tipo"],
                hash_conteudo_semantico="",
                criado_em=agora,
                atualizado_em=agora,
                criado_por=AUTOR,
                atualizado_por=AUTOR,
            )
            hash_val = hash_qualificacao(entidade_temp)

            sessao.execute(
                cursos.insert().values(
                    id=novo_id,
                    nome=item["nome"],
                    descricao=item["descricao"],
                    tipo=item["tipo"].value,
                    hash_conteudo_semantico=hash_val,
                    criado_em=agora,
                    atualizado_em=agora,
                    inativado_em=None,
                    criado_por=AUTOR,
                    atualizado_por=AUTOR,
                )
            )
            mapa_ids[item["nome"]] = novo_id
            print(f"  ✓ [Inserido] Curso: {item['nome']} ({item['tipo'].value})")

    sessao.commit()
    return mapa_ids


def popular_profissoes(sessao: Session) -> dict[str, UUID]:
    print("\n--- Populando Profissões do Catálogo (com CBO) ---")
    dados = [
        {
            "nome": "Médico Clínico",
            "cbo": "225125",
            "descricao": "Atendimento clínico geral, diagnóstico e prescrição médica em postos de triagem e abrigos.",
        },
        {
            "nome": "Enfermeiro de Emergência",
            "cbo": "223505",
            "descricao": "Coordenação de cuidados de enfermagem, triagem de feridos e curativos complexos.",
        },
        {
            "nome": "Técnico em Enfermagem",
            "cbo": "322205",
            "descricao": "Aplicação de medicação, aferição de sinais vitais e curativos sob supervisão de enfermagem.",
        },
        {
            "nome": "Psicólogo Clínico",
            "cbo": "251510",
            "descricao": "Atendimento psicológico de suporte e acolhimento emocional às vítimas e socorristas.",
        },
        {
            "nome": "Assistente Social",
            "cbo": "251605",
            "descricao": "Mapeamento socioeconômico das famílias, garantia de direitos e articulação com a rede socioassistencial.",
        },
        {
            "nome": "Engenheiro Civil",
            "cbo": "214205",
            "descricao": "Vistoria e emissão de laudos de estabilidade estrutural em imóveis afetados por desastres.",
        },
        {
            "nome": "Geólogo",
            "cbo": "213405",
            "descricao": "Avaliação geotécnica de encostas, mapeamento de risco de escorregamento de terra e comportamento do solo.",
        },
        {
            "nome": "Bombeiro Civil",
            "cbo": "517110",
            "descricao": "Prevenção e combate a princípios de incêndio, resgate aquático e evacuação de áreas de perigo.",
        },
        {
            "nome": "Motorista de Caminhão Pesado",
            "cbo": "782510",
            "descricao": "Transporte rodoviário de cargas de grande porte, suprimentos e maquinário pesado.",
        },
        {
            "nome": "Operador de Retroescavadeira",
            "cbo": "715115",
            "descricao": "Operação de maquinário pesado para remoção de terra, entulho e desobstrução de estradas.",
        },
        {
            "nome": "Cozinheiro Geral",
            "cbo": "513205",
            "descricao": "Preparo de refeições coletivas em cozinhas comunitárias e abrigos temporários.",
        },
        {
            "nome": "Logístico de Suprimentos",
            "cbo": "141410",
            "descricao": "Planejamento e controle de depósitos, inventário e fluxo de expedição de suprimentos humanitários.",
        },
    ]

    mapa_ids: dict[str, UUID] = {}
    agora = datetime.now(timezone.utc)

    for item in dados:
        stmt = select(profissoes.c.id).where(profissoes.c.nome == item["nome"])
        existente = sessao.execute(stmt).scalar()
        if existente:
            mapa_ids[item["nome"]] = existente
            print(f"  [Já existe] Profissão: {item['nome']} (CBO {item['cbo']})")
        else:
            novo_id = uuid4()
            entidade_temp = Profissao(
                id=novo_id,
                nome=item["nome"],
                descricao=item["descricao"],
                codigo_cbo=item["cbo"],
                hash_conteudo_semantico="",
                criado_em=agora,
                atualizado_em=agora,
                criado_por=AUTOR,
                atualizado_por=AUTOR,
            )
            hash_val = hash_qualificacao(entidade_temp)

            sessao.execute(
                profissoes.insert().values(
                    id=novo_id,
                    nome=item["nome"],
                    descricao=item["descricao"],
                    codigo_cbo=item["cbo"],
                    hash_conteudo_semantico=hash_val,
                    criado_em=agora,
                    atualizado_em=agora,
                    inativado_em=None,
                    criado_por=AUTOR,
                    atualizado_por=AUTOR,
                )
            )
            mapa_ids[item["nome"]] = novo_id
            print(f"  ✓ [Inserido] Profissão: {item['nome']} (CBO {item['cbo']})")

    sessao.commit()
    return mapa_ids


def popular_tipos_desastre(sessao: Session) -> dict[str, UUID]:
    print("\n--- Populando Tipos de Desastre (COBRADE) ---")
    dados = [
        {
            "codigo": "12100",
            "nome": "Inundação Gradual",
            "descricao": "Submersão progressiva de áreas fora dos limites normais de cursos d'água devido a precipitações prolongadas.",
        },
        {
            "codigo": "12200",
            "nome": "Enxurrada e Inundação Brusca",
            "descricao": "Escoamento superficial de alta velocidade provocado por chuvas intensas e concentradas com alto poder destrutivo.",
        },
        {
            "codigo": "12300",
            "nome": "Alagamento Urbano",
            "descricao": "Acúmulo momentâneo de água em áreas urbanas por deficiência no sistema de drenagem e impermeabilização do solo.",
        },
        {
            "codigo": "13214",
            "nome": "Deslizamento de Solo e Rochas",
            "descricao": "Movimento de massa em encostas, morros e encostas urbanas com risco iminente a vidas e edificações.",
        },
        {
            "codigo": "13215",
            "nome": "Corrida de Massa e Lama",
            "descricao": "Fluxo viscoso de solo saturado, água e detritos descendo encostas em alta velocidade.",
        },
        {
            "codigo": "14110",
            "nome": "Estiagem e Seca Prolongada",
            "descricao": "Período prolongado de escassez hídrica comprometendo abastecimento de água potável, agricultura e subsistência.",
        },
        {
            "codigo": "13111",
            "nome": "Vendaval e Tempestade de Vento",
            "descricao": "Ventos de forte intensidade causando destelhamento de habitações, queda de árvores e interrupção de serviços essenciais.",
        },
        {
            "codigo": "13112",
            "nome": "Granizo",
            "descricao": "Precipitação de pedras de gelo danificando telhados, estruturas frágeis, veículos e plantações.",
        },
        {
            "codigo": "14131",
            "nome": "Incêndio Florestal em Área Protegida ou Povoada",
            "descricao": "Propagação descontrolada do fogo em matas, vegetação e áreas de interface urbano-rural.",
        },
        {
            "codigo": "21110",
            "nome": "Colapso de Edificação ou Ponte",
            "descricao": "Ruptura ou queda parcial ou total de obras de engenharia civil afetando a circulação e segurança pública.",
        },
        {
            "codigo": "22210",
            "nome": "Contaminação de Manancial de Água Potável",
            "descricao": "Vazamento ou contaminação química e biológica em reservatórios ou redes de distribuição pública de água.",
        },
    ]

    mapa_ids: dict[str, UUID] = {}
    agora = datetime.now(timezone.utc)

    for item in dados:
        stmt = select(tipos_desastre.c.id).where(tipos_desastre.c.codigo == item["codigo"])
        existente = sessao.execute(stmt).scalar()
        if existente:
            mapa_ids[item["codigo"]] = existente
            print(f"  [Já existe] Tipo de Desastre: {item['nome']} ({item['codigo']})")
        else:
            novo_id = uuid4()
            sessao.execute(
                tipos_desastre.insert().values(
                    id=novo_id,
                    codigo=item["codigo"],
                    nome=item["nome"],
                    descricao=item["descricao"],
                    criado_em=agora,
                    atualizado_em=agora,
                    inativado_em=None,
                    criado_por=AUTOR,
                    atualizado_por=AUTOR,
                )
            )
            mapa_ids[item["codigo"]] = novo_id
            print(f"  ✓ [Inserido] Tipo de Desastre: {item['nome']} (Código {item['codigo']})")

    sessao.commit()
    return mapa_ids


def popular_tipos_recurso(sessao: Session, unids: dict[str, UUID]) -> dict[str, UUID]:
    print("\n--- Populando Tipos de Recurso ---")
    dados = [
        {
            "nome": "Caminhão Baú de Carga",
            "categoria": CategoriaRecurso.VEICULO,
            "modo": ModoControleRecurso.INDIVIDUAL,
            "unidade": "un",
            "descricao": "Caminhão fechado com capacidade mínima de 5 toneladas para transporte protegido de doações e mantimentos.",
        },
        {
            "nome": "Bote Inflável com Motor de Popa",
            "categoria": CategoriaRecurso.VEICULO,
            "modo": ModoControleRecurso.INDIVIDUAL,
            "unidade": "un",
            "descricao": "Embarcação para navegação em águas rasas e resgate de pessoas ilhadas.",
        },
        {
            "nome": "Gerador de Energia a Diesel 10kVA",
            "categoria": CategoriaRecurso.EQUIPAMENTO,
            "modo": ModoControleRecurso.INDIVIDUAL,
            "unidade": "un",
            "descricao": "Gerador portátil trifásico para fornecimento de eletricidade a postos médicos e abrigos temporários.",
        },
        {
            "nome": "Bomba de Sucção e Drenagem de Água",
            "categoria": CategoriaRecurso.EQUIPAMENTO,
            "modo": ModoControleRecurso.INDIVIDUAL,
            "unidade": "un",
            "descricao": "Motobomba de alta vazão para drenagem de porões, vias e áreas submersas.",
        },
        {
            "nome": "Motosserra a Gasolina",
            "categoria": CategoriaRecurso.EQUIPAMENTO,
            "modo": ModoControleRecurso.INDIVIDUAL,
            "unidade": "un",
            "descricao": "Motosserra profissional com sabre de 45cm para corte e desobstrução de árvores caídas.",
        },
        {
            "nome": "Colchão Solteiro de Espuma D33",
            "categoria": CategoriaRecurso.MATERIAL,
            "modo": ModoControleRecurso.ESTOQUE,
            "unidade": "un",
            "descricao": "Colchão impermeável e higienizável para uso em leitos de abrigo temporário.",
        },
        {
            "nome": "Kit Cobertor e Roupa de Cama",
            "categoria": CategoriaRecurso.MATERIAL,
            "modo": ModoControleRecurso.ESTOQUE,
            "unidade": "kit",
            "descricao": "Conjunto com cobertor térmico, lençol e fronha higienizados e embalados.",
        },
        {
            "nome": "Lona Plástica Impermeável 8x6m",
            "categoria": CategoriaRecurso.MATERIAL,
            "modo": ModoControleRecurso.ESTOQUE,
            "unidade": "un",
            "descricao": "Lona plástica reforçada com ilhoses para cobertura emergencial de telhados danificados.",
        },
        {
            "nome": "Cesta Básica de Alimentos Não Perecíveis",
            "categoria": CategoriaRecurso.INSUMO,
            "modo": ModoControleRecurso.ESTOQUE,
            "unidade": "cx",
            "descricao": "Cesta familiar padronizada com arroz, feijão, óleo, leite em pó, farinha e enlatados.",
        },
        {
            "nome": "Água Mineral Envasada em Galão de 20L",
            "categoria": CategoriaRecurso.INSUMO,
            "modo": ModoControleRecurso.ESTOQUE,
            "unidade": "l",
            "descricao": "Água potável certificada para distribuição em pontos de hidratação e acolhida.",
        },
        {
            "nome": "Kit de Higiene Pessoal Familiar",
            "categoria": CategoriaRecurso.INSUMO,
            "modo": ModoControleRecurso.ESTOQUE,
            "unidade": "kit",
            "descricao": "Kit familiar contendo sabonetes, cremes dentais, escovas de dente, xampu, papel higiênico e absorventes.",
        },
        {
            "nome": "Kit de Primeiros Socorros e Curativos",
            "categoria": CategoriaRecurso.INSUMO,
            "modo": ModoControleRecurso.ESTOQUE,
            "unidade": "kit",
            "descricao": "Caixa com gazes esterilizadas, ataduras, antissépticos, esparadrapos, luvas cirúrgicas e tesoura médica.",
        },
    ]

    mapa_ids: dict[str, UUID] = {}
    agora = datetime.now(timezone.utc)

    for item in dados:
        stmt = select(tipos_recurso.c.id).where(tipos_recurso.c.nome == item["nome"])
        existente = sessao.execute(stmt).scalar()
        unid_id = unids[item["unidade"]]

        if existente:
            mapa_ids[item["nome"]] = existente
            print(f"  [Já existe] Tipo de Recurso: {item['nome']}")
        else:
            novo_id = uuid4()
            entidade_temp = TipoRecurso(
                id=novo_id,
                nome=item["nome"],
                descricao=item["descricao"],
                categoria=item["categoria"],
                id_unidade_medida=unid_id,
                modo_controle=item["modo"],
                hash_conteudo_semantico="",
                criado_em=agora,
                atualizado_em=agora,
                criado_por=AUTOR,
                atualizado_por=AUTOR,
            )
            hash_val = hash_tipo_recurso(entidade_temp)

            sessao.execute(
                tipos_recurso.insert().values(
                    id=novo_id,
                    nome=item["nome"],
                    descricao=item["descricao"],
                    categoria=item["categoria"].value,
                    id_unidade_medida=unid_id,
                    modo_controle=item["modo"].value,
                    hash_conteudo_semantico=hash_val,
                    criado_em=agora,
                    atualizado_em=agora,
                    inativado_em=None,
                    criado_por=AUTOR,
                    atualizado_por=AUTOR,
                )
            )
            mapa_ids[item["nome"]] = novo_id
            print(f"  ✓ [Inserido] Tipo de Recurso: {item['nome']} ({item['categoria'].value})")

    sessao.commit()
    return mapa_ids


def main() -> None:
    print("=================================================================")
    print(" INICIALIZAÇÃO DE DADOS DE CATÁLOGO DA REDESOLIDÁRIA ")
    print("=================================================================")

    with obter_sessao() as sessao:
        # 1. Unidades de Medida
        unids = popular_unidades(sessao)

        # 2. Categorias de Atividade
        cats = popular_categorias(sessao)

        # 3. Atividades (com termos)
        popular_atividades(sessao, cats, unids)

        # 4. Cursos
        popular_cursos(sessao)

        # 5. Profissões
        popular_profissoes(sessao)

        # 6. Tipos de Desastre
        popular_tipos_desastre(sessao)

        # 7. Tipos de Recurso
        popular_tipos_recurso(sessao, unids)

    print("\n=================================================================")
    print(" ✓ Carga inicial concluída com sucesso em todas as tabelas!")
    print("=================================================================")


if __name__ == "__main__":
    main()
