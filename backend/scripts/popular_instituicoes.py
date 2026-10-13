"""Script para popular 20 instituições de Ensino Superior e Profissionalizante no banco de dados.

Tabela populada:
- instituicoes

Uso:
  python backend/scripts/popular_instituicoes.py
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

# Garante saída UTF-8 no terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DIR_BACKEND = Path(__file__).resolve().parent.parent
if str(DIR_BACKEND) not in sys.path:
    sys.path.insert(0, str(DIR_BACKEND))

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from business.view_models.cadastros import InstituicaoInput
from core.entity.cadastros import SituacaoCadastral, TipoInstituicao
from infra.configurations.cadastros import instituicoes
from infra.database.settings import DatabaseSettings

AUTOR = "seed-instituicoes"

DADOS_INSTITUICOES = [
    {
        "nome": "Universidade de São Paulo (USP)",
        "razao_social": "Universidade de São Paulo",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "63025530000104",
        "municipio_codigo_ibge": "3550308",
        "uf": "SP",
        "email_contato": "faleconosco@usp.br",
        "telefone_contato": "1130913500",
        "latitude": Decimal("-23.5587000"),
        "longitude": Decimal("-46.7319000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Principal instituição pública estadual de ensino superior e pesquisa científica do "
            "Brasil, com ampla atuação em graduação, pós-graduação e extensão."
        ),
    },
    {
        "nome": "Universidade Estadual de Campinas (UNICAMP)",
        "razao_social": "Universidade Estadual de Campinas",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "46024364000144",
        "municipio_codigo_ibge": "3509502",
        "uf": "SP",
        "email_contato": "ouvidoria@unicamp.br",
        "telefone_contato": "1935212121",
        "latitude": Decimal("-22.8171000"),
        "longitude": Decimal("-47.0697000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Universidade pública paulista de referência internacional em ciência, tecnologia, "
            "medicina e inovação tecnológica."
        ),
    },
    {
        "nome": "Universidade Estadual Paulista Júlio de Mesquita Filho (UNESP)",
        "razao_social": "Universidade Estadual Paulista Júlio de Mesquita Filho",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "48031918000124",
        "municipio_codigo_ibge": "3550308",
        "uf": "SP",
        "email_contato": "comunicacao@unesp.br",
        "telefone_contato": "1156270200",
        "latitude": Decimal("-23.5255000"),
        "longitude": Decimal("-46.6664000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Universidade pública multicâmpus presente em mais de 20 cidades paulistas, com "
            "forte presença no ensino, pesquisa e extensão universitária."
        ),
    },
    {
        "nome": "Universidade Federal do Rio de Janeiro (UFRJ)",
        "razao_social": "Universidade Federal do Rio de Janeiro",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "33663683000116",
        "municipio_codigo_ibge": "3304557",
        "uf": "RJ",
        "email_contato": "centraldeatendimento@ufrj.br",
        "telefone_contato": "2139381000",
        "latitude": Decimal("-22.8612000"),
        "longitude": Decimal("-43.2307000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Tradicional universidade federal brasileira com histórico de pioneirismo e excelência "
            "em ciências exatas, da saúde e humanidades."
        ),
    },
    {
        "nome": "Universidade Federal de Minas Gerais (UFMG)",
        "razao_social": "Universidade Federal de Minas Gerais",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "17217985000104",
        "municipio_codigo_ibge": "3106200",
        "uf": "MG",
        "email_contato": "reitoria@ufmg.br",
        "telefone_contato": "3134095000",
        "latitude": Decimal("-19.8690000"),
        "longitude": Decimal("-43.9664000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Instituição federal de excelência em ensino superior, pesquisa científica e inovação "
            "tecnológica sediada em Belo Horizonte."
        ),
    },
    {
        "nome": "Universidade Federal do Rio Grande do Sul (UFRGS)",
        "razao_social": "Universidade Federal do Rio Grande do Sul",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "92969856000198",
        "municipio_codigo_ibge": "4314902",
        "uf": "RS",
        "email_contato": "ouvidoria@ufrgs.br",
        "telefone_contato": "5133083000",
        "latitude": Decimal("-30.0345000"),
        "longitude": Decimal("-51.2177000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Instituição pública federal de destaque no ensino superior e na pesquisa no sul do Brasil, "
            "com ampla infraestrutura acadêmica e hospitalar."
        ),
    },
    {
        "nome": "Universidade Federal de Santa Catarina (UFSC)",
        "razao_social": "Universidade Federal de Santa Catarina",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "83899526000182",
        "municipio_codigo_ibge": "4205407",
        "uf": "SC",
        "email_contato": "falecom@ufsc.br",
        "telefone_contato": "4837219000",
        "latitude": Decimal("-27.6014000"),
        "longitude": Decimal("-48.5186000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Instituição de ensino superior catarinense reconhecida internacionalmente pelo polo de "
            "engenharia, computação e ciências biológicas."
        ),
    },
    {
        "nome": "Universidade Federal do Paraná (UFPR)",
        "razao_social": "Universidade Federal do Paraná",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "75095679000149",
        "municipio_codigo_ibge": "4106902",
        "uf": "PR",
        "email_contato": "central.atendimento@ufpr.br",
        "telefone_contato": "4133605000",
        "latitude": Decimal("-25.4284000"),
        "longitude": Decimal("-49.2612000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Instituição centenária de ensino superior, pesquisa e extensão comunitária com atuação "
            "de liderança acadêmica no Paraná."
        ),
    },
    {
        "nome": "Universidade de Brasília (UnB)",
        "razao_social": "Fundação Universidade de Brasília",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "00038174000143",
        "municipio_codigo_ibge": "5300108",
        "uf": "DF",
        "email_contato": "ouvidoria@unb.br",
        "telefone_contato": "6131070000",
        "latitude": Decimal("-15.7631000"),
        "longitude": Decimal("-47.8706000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Universidade pública federal concebida no projeto original de Brasília, destacando-se na "
            "formação científica, política e cultural do país."
        ),
    },
    {
        "nome": "Universidade Federal de Pernambuco (UFPE)",
        "razao_social": "Universidade Federal de Pernambuco",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "24134488000108",
        "municipio_codigo_ibge": "2611606",
        "uf": "PE",
        "email_contato": "ouvidoria@ufpe.br",
        "telefone_contato": "8121268000",
        "latitude": Decimal("-8.0526000"),
        "longitude": Decimal("-34.9511000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Principal centro de formação superior e pesquisa científica do Nordeste, com forte "
            "destaque em ciências exatas, tecnologia da informação e medicina."
        ),
    },
    {
        "nome": "Universidade Federal da Bahia (UFBA)",
        "razao_social": "Universidade Federal da Bahia",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "15180714000104",
        "municipio_codigo_ibge": "2927408",
        "uf": "BA",
        "email_contato": "ouvidoria@ufba.br",
        "telefone_contato": "7132837000",
        "latitude": Decimal("-13.0003000"),
        "longitude": Decimal("-38.5088000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Mais antiga e tradicional instituição federal da Bahia, berço das ciências médicas e das "
            "artes na história do ensino superior nacional."
        ),
    },
    {
        "nome": "Universidade Federal do Ceará (UFC)",
        "razao_social": "Universidade Federal do Ceará",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "07272636000131",
        "municipio_codigo_ibge": "2304400",
        "uf": "CE",
        "email_contato": "reitoria@ufc.br",
        "telefone_contato": "8533667300",
        "latitude": Decimal("-3.7431000"),
        "longitude": Decimal("-38.5368000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Instituição federal de excelência em ciência e tecnologia, energias renováveis e ciências "
            "básicas e aplicadas no Ceará."
        ),
    },
    {
        "nome": "Universidade Federal do Amazonas (UFAM)",
        "razao_social": "Fundação Universidade do Amazonas",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "04378626000197",
        "municipio_codigo_ibge": "1302603",
        "uf": "AM",
        "email_contato": "reitoria@ufam.edu.br",
        "telefone_contato": "9233051490",
        "latitude": Decimal("-3.0984000"),
        "longitude": Decimal("-59.9868000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Principal instituição pública de ensino superior do bioma amazônico, com expressiva "
            "produção científica sobre biodiversidade e desenvolvimento sustentável."
        ),
    },
    {
        "nome": "Instituto Federal de São Paulo (IFSP)",
        "razao_social": "Instituto Federal de Educação, Ciência e Tecnologia de São Paulo",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "10882594000165",
        "municipio_codigo_ibge": "3550308",
        "uf": "SP",
        "email_contato": "reitoria@ifsp.edu.br",
        "telefone_contato": "1137754500",
        "latitude": Decimal("-23.5186000"),
        "longitude": Decimal("-46.6277000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Instituição federal de educação profissionalizante e tecnológica, oferecendo cursos "
            "técnicos integrados ao ensino médio, graduações tecnológicas e engenharias."
        ),
    },
    {
        "nome": "Instituto Federal do Rio de Janeiro (IFRJ)",
        "razao_social": "Instituto Federal de Educação, Ciência e Tecnologia do Rio de Janeiro",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "10952708000104",
        "municipio_codigo_ibge": "3304557",
        "uf": "RJ",
        "email_contato": "ouvidoria@ifrj.edu.br",
        "telefone_contato": "2139785900",
        "latitude": Decimal("-22.9103000"),
        "longitude": Decimal("-43.2185000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Rede pública federal fluminense de ensino profissionalizante de nível técnico e cursos "
            "superiores de tecnologia e pós-graduação."
        ),
    },
    {
        "nome": "Instituto Federal de Minas Gerais (IFMG)",
        "razao_social": "Instituto Federal de Educação, Ciência e Tecnologia de Minas Gerais",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "10626896000172",
        "municipio_codigo_ibge": "3106200",
        "uf": "MG",
        "email_contato": "comunicacao@ifmg.edu.br",
        "telefone_contato": "3125135150",
        "latitude": Decimal("-19.9248000"),
        "longitude": Decimal("-43.9431000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Rede mineira federal voltada à formação profissionalizante, técnica e tecnológica, com "
            "forte atuação no arranjo produtivo e comunitário local."
        ),
    },
    {
        "nome": "Centro Paula Souza (ETEC / FATEC)",
        "razao_social": "Centro Estadual de Educação Tecnológica Paula Souza",
        "tipo": TipoInstituicao.ORGAO_PUBLICO,
        "cnpj": "62823257000109",
        "municipio_codigo_ibge": "3550308",
        "uf": "SP",
        "email_contato": "faleconosco@cps.sp.gov.br",
        "telefone_contato": "1133243300",
        "latitude": Decimal("-23.5332000"),
        "longitude": Decimal("-46.6329000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Autarquia estadual de São Paulo gestora das Faculdades de Tecnologia (FATECs) e das "
            "Escolas Técnicas Estaduais (ETECs), referência nacional em ensino profissionalizante."
        ),
    },
    {
        "nome": "SENAI São Paulo",
        "razao_social": "Serviço Nacional de Aprendizagem Industrial - Departamento Regional de São Paulo",
        "tipo": TipoInstituicao.ASSOCIACAO,
        "cnpj": "03774819000102",
        "municipio_codigo_ibge": "3550308",
        "uf": "SP",
        "email_contato": "faleconosco@sp.senai.br",
        "telefone_contato": "1133220050",
        "latitude": Decimal("-23.5350000"),
        "longitude": Decimal("-46.6508000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Maior instituição de educação profissionalizante da América Latina com foco na indústria, "
            "oferecendo capacitações técnicas, certificações e soluções tecnológicas."
        ),
    },
    {
        "nome": "SENAC São Paulo",
        "razao_social": "Serviço Nacional de Aprendizagem Comercial - Departamento Regional de São Paulo",
        "tipo": TipoInstituicao.ASSOCIACAO,
        "cnpj": "03709814000130",
        "municipio_codigo_ibge": "3550308",
        "uf": "SP",
        "email_contato": "atendimento@sp.senac.br",
        "telefone_contato": "1140901030",
        "latitude": Decimal("-23.5658000"),
        "longitude": Decimal("-46.6534000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Instituição líder em formação profissionalizante nas áreas de comércio de bens, serviços, "
            "saúde, hospitalidade, gastronomia e tecnologia."
        ),
    },
    {
        "nome": "Pontifícia Universidade Católica de São Paulo (PUC-SP)",
        "razao_social": "Fundação São Paulo",
        "tipo": TipoInstituicao.ONG,
        "cnpj": "60990751000124",
        "municipio_codigo_ibge": "3550308",
        "uf": "SP",
        "email_contato": "ouvidoria@pucsp.br",
        "telefone_contato": "1136708000",
        "latitude": Decimal("-23.5377000"),
        "longitude": Decimal("-46.6713000"),
        "situacao_cadastral": SituacaoCadastral.VALIDADA,
        "descricao": (
            "Universidade comunitária e confessional sem fins lucrativos, referência em ensino superior, "
            "ciências jurídicas, ciências sociais e extensão comunitária."
        ),
    },
]


def obter_sessao() -> Session:
    env_path = DIR_BACKEND / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
    config = DatabaseSettings()
    url = config.database_url.get_secret_value()
    engine = create_engine(url, pool_pre_ping=True)
    return Session(engine)


def main() -> int:
    print("=" * 70)
    print(" POPULAR BANCO DE DADOS — 20 INSTITUIÇÕES DE ENSINO SUPERIOR E TÉCNICO")
    print("=" * 70)

    # 1. Validar todos os registros com Pydantic (InstituicaoInput)
    print("\n[Etapa 1] Validando dados com InstituicaoInput (Pydantic)...")
    for idx, item in enumerate(DADOS_INSTITUICOES, start=1):
        try:
            validado = InstituicaoInput(
                nome=item["nome"],
                municipio_codigo_ibge=item["municipio_codigo_ibge"],
                uf=item["uf"],
                email_contato=item["email_contato"],
                telefone_contato=item["telefone_contato"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                situacao_cadastral=item["situacao_cadastral"],
                tipo=item["tipo"],
                razao_social=item["razao_social"],
                cnpj=item["cnpj"],
                descricao=item["descricao"],
            )
        except Exception as e:
            print(f"✗ Erro de validação no item #{idx} ({item['nome']}): {e}")
            return 1
    print(f"✓ Todos os {len(DADOS_INSTITUICOES)} registros validados com sucesso no modelo Pydantic!")

    # 2. Conectar e executar no banco de dados
    print("\n[Etapa 2] Conectando ao PostgreSQL e inserindo registros...")
    sessao = obter_sessao()
    agora = datetime.now(timezone.utc)
    inseridos = 0
    existentes = 0

    try:
        for idx, item in enumerate(DADOS_INSTITUICOES, start=1):
            cnpj = item["cnpj"]
            stmt = select(instituicoes.c.id, instituicoes.c.nome).where(instituicoes.c.cnpj == cnpj)
            registro_existente = sessao.execute(stmt).first()

            if registro_existente:
                existentes += 1
                print(f"  [Já existe] #{idx:02d}: {item['nome']} (CNPJ: {cnpj})")
            else:
                novo_id = uuid4()
                sessao.execute(
                    instituicoes.insert().values(
                        id=novo_id,
                        nome=item["nome"],
                        municipio_codigo_ibge=item["municipio_codigo_ibge"],
                        uf=item["uf"],
                        situacao_cadastral=item["situacao_cadastral"].value,
                        email_contato=item["email_contato"],
                        telefone_contato=item["telefone_contato"],
                        latitude=item["latitude"],
                        longitude=item["longitude"],
                        criado_em=agora,
                        atualizado_em=agora,
                        inativado_em=None,
                        criado_por=AUTOR,
                        atualizado_por=AUTOR,
                        razao_social=item["razao_social"],
                        cnpj=cnpj,
                        descricao=item["descricao"],
                        tipo=item["tipo"].value,
                    )
                )
                inseridos += 1
                print(f"  ✓ [Inserido] #{idx:02d}: {item['nome']} (UF: {item['uf']})")

        sessao.commit()
        print("\n" + "=" * 70)
        print(f"✓ Concluído com sucesso! Inseridos: {inseridos} | Já existentes: {existentes}")
        print("=" * 70)
        return 0

    except Exception as e:
        sessao.rollback()
        print(f"\n✗ Erro ao inserir instituições no banco: {type(e).__name__}: {e}")
        return 2
    finally:
        sessao.close()


if __name__ == "__main__":
    raise SystemExit(main())
