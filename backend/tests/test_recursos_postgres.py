import os
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy import Engine, create_engine, insert, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from business.view_models.cadastros import InstituicaoInput, InstituicaoVM, PessoaInput, PessoaVM
from business.view_models.capacidades import AtividadeVM
from business.view_models.recursos import (
    OfertaAtividadeInput,
    OfertaAtividadeVM,
    OfertaRecursoInput,
    OfertaRecursoVM,
    RecursoInput,
    RecursoVM,
    TipoRecursoInput,
    TipoRecursoVM,
)
from core.entity.cadastros import TipoInstituicao, agora_utc
from core.entity.qualificacoes import SituacaoValidacao
from core.entity.recursos import CategoriaRecurso, ModoControleRecurso, Recurso
from core.http.contratos import ApiResponse
from infra.configurations.recursos import recursos
from tests.conftest import token_teste
from tests.test_capacidades_postgres import atividade, entrada_da_atividade
from web.main import create_app
from web.settings import Settings

pytestmark = pytest.mark.postgres


@pytest.fixture
def banco_recursos() -> Iterator[Engine]:
    url: str | None = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Use scripts/test_postgres.py para PostgreSQL isolado.")
    if make_url(url).database != "redesolidaria_test":
        pytest.fail("Somente o banco dedicado redesolidaria_test é permitido.")
    engine: Engine = create_engine(url, hide_parameters=True)
    with engine.begin() as conexao:
        conexao.execute(
            text(
                "TRUNCATE TABLE recomendacao_recursos, recomendacao_instituicoes, "
                "recomendacao_pessoas, recomendacao_itens, recomendacoes, "
                "atividade_indice_semantico, modelo_ia, conexao_ia, demanda_itens, demandas, "
                "areas_afetadas, desastre_tipo, desastres, tipos_desastre, "
                "oferta_atividade_recurso, ofertas_atividade, recursos, "
                "tipos_recurso, atividade_termos, atividades, categorias_atividade, "
                "unidades_medida, "
                "pessoa_curso, pessoa_profissao, pessoa_instituicao, cursos, profissoes, "
                "instituicoes, pessoas"
            )
        )
    yield engine
    engine.dispose()


@pytest.fixture
def api_recursos(banco_recursos: Engine, settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings, banco_recursos), raise_server_exceptions=False) as api:
        api.headers["Authorization"] = f"Bearer {token_teste()}"
        yield api


def criar[V: BaseModel](api: TestClient, rota: str, dados: BaseModel, vm: type[V]) -> V:
    resposta = api.post(f"/api/v1/{rota}", json=dados.model_dump(mode="json"))
    assert resposta.status_code == 201, resposta.text
    return vm.model_validate(resposta.json()["data"])


def entrada[I: BaseModel](vm: BaseModel, tipo: type[I]) -> I:
    return tipo.model_validate_json(vm.model_dump_json(include=set(tipo.model_fields)))


@dataclass
class Cenario:
    atividade: AtividadeVM
    pessoa: PessoaVM
    tipo: TipoRecursoVM
    recurso: RecursoVM
    oferta: OfertaAtividadeVM


def cenario(api: TestClient, estoque: bool = False) -> Cenario:
    a = atividade(api)
    assert a.id_unidade_capacidade is not None
    p = criar(
        api,
        "pessoas",
        PessoaInput(nome="Voluntário teste recursos", municipio_codigo_ibge="3550308", uf="SP"),
        PessoaVM,
    )
    t = criar(
        api,
        "tipos-recurso",
        TipoRecursoInput(
            nome="Gerador de teste",
            categoria=CategoriaRecurso.EQUIPAMENTO,
            modo_controle=ModoControleRecurso.ESTOQUE
            if estoque
            else ModoControleRecurso.INDIVIDUAL,
            id_unidade_medida=a.id_unidade_capacidade,
        ),
        TipoRecursoVM,
    )
    r = criar(
        api,
        "recursos",
        RecursoInput(
            tipo_recurso_id=t.id,
            nome="Gerador da pessoa",
            pessoa_id=p.id,
            quantidade_total=Decimal("20.5000") if estoque else Decimal(1),
            municipio_codigo_ibge="3550308",
        ),
        RecursoVM,
    )
    o = criar(
        api,
        "ofertas-atividade",
        OfertaAtividadeInput(
            atividade_id=a.id,
            pessoa_id=p.id,
            municipio_atendimento_codigo_ibge="3550308",
            capacidade_declarada=Decimal("2.5"),
        ),
        OfertaAtividadeVM,
    )
    return Cenario(a, p, t, r, o)


def test_tipo_unidade_modo_estaveis_hash_e_auditoria(
    api_recursos: TestClient, banco_recursos: Engine
) -> None:
    api = api_recursos
    c = cenario(api)
    url = f"/api/v1/tipos-recurso/{c.tipo.id}"
    dados = entrada(c.tipo, TipoRecursoInput)
    dados.modo_controle = ModoControleRecurso.ESTOQUE
    assert api.put(url, json=dados.model_dump(mode="json")).status_code == 409
    dados.modo_controle = ModoControleRecurso.INDIVIDUAL
    dados.descricao = "Gerador para energia de emergência"
    resposta = api.put(url, json=dados.model_dump(mode="json"))
    assert resposta.status_code == 200
    alterado = ApiResponse[TipoRecursoVM].model_validate(resposta.json()).data
    assert alterado.hash_conteudo_semantico != c.tipo.hash_conteudo_semantico
    assert len(api.get("/api/v1/tipos-recurso?busca=energia").json()["data"]) == 1
    assert api.get("/api/v1/tipos-recurso?limite=101").status_code == 422
    with Session(banco_recursos) as sessao:
        r = sessao.get(Recurso, c.recurso.id)
        assert r is not None and r.criado_por == "administrador-teste"
    assert api.delete(url).status_code == 200
    assert api.get(url).status_code == 404
    assert api.get(url + "?incluir_inativos=true").status_code == 200
    recurso_vm = (
        ApiResponse[RecursoVM]
        .model_validate(api.get(f"/api/v1/recursos/{c.recurso.id}").json())
        .data
    )
    assert recurso_vm.tipo_recurso_inativo and recurso_vm.tipo_recurso_nome == c.tipo.nome
    assert (
        api.put(
            f"/api/v1/recursos/{c.recurso.id}",
            json=entrada(c.recurso, RecursoInput).model_dump(mode="json"),
        ).status_code
        == 404
    )


def test_quantidades_individuais_estoque_e_ref_pessoa(api_recursos: TestClient) -> None:
    api = api_recursos
    c = cenario(api)
    dados = entrada(c.recurso, RecursoInput)
    dados.quantidade_total = Decimal(2)
    assert api.post("/api/v1/recursos", json=dados.model_dump(mode="json")).status_code == 422
    dados.quantidade_total = Decimal(1)
    dados.latitude, dados.longitude = Decimal("-23.5505000"), Decimal("-46.6333000")
    assert (
        api.put(f"/api/v1/recursos/{c.recurso.id}", json=dados.model_dump(mode="json")).status_code
        == 200
    )
    assert len(api.get("/api/v1/pessoas?busca=recursos").json()["data"]) == 1
    assert api.get("/api/v1/pessoas?busca=ninguém").json()["data"] == []
    assert api.delete(f"/api/v1/pessoas/{c.pessoa.id}").status_code == 200
    vm = (
        ApiResponse[RecursoVM]
        .model_validate(api.get(f"/api/v1/recursos/{c.recurso.id}").json())
        .data
    )
    assert vm.responsavel_inativo and vm.latitude == dados.latitude
    assert api.post("/api/v1/recursos", json=dados.model_dump(mode="json")).status_code == 404


def test_estoque_decimal_nao_e_saldo_reservado(api_recursos: TestClient) -> None:
    api = api_recursos
    c = cenario(api, estoque=True)
    rota = f"ofertas-atividade/{c.oferta.id}/recursos"
    v = criar(
        api,
        rota,
        OfertaRecursoInput(recurso_id=c.recurso.id, quantidade_prevista=Decimal("30.1250")),
        OfertaRecursoVM,
    )
    assert v.quantidade_prevista == Decimal("30.1250")
    r = (
        ApiResponse[RecursoVM]
        .model_validate(api.get(f"/api/v1/recursos/{c.recurso.id}").json())
        .data
    )
    assert r.quantidade_total == Decimal("20.5000")
    dados = entrada(r, RecursoInput)
    dados.quantidade_total = Decimal(0)
    assert (
        api.put(f"/api/v1/recursos/{r.id}", json=dados.model_dump(mode="json")).status_code == 200
    )


def test_responsavel_institucional_e_recurso_de_outro_ofertante(api_recursos: TestClient) -> None:
    api = api_recursos
    c = cenario(api)
    instituicao = criar(
        api,
        "instituicoes",
        InstituicaoInput(
            nome="Associação de apoio",
            municipio_codigo_ibge="3550308",
            uf="SP",
            tipo=TipoInstituicao.ASSOCIACAO,
        ),
        InstituicaoVM,
    )
    dados = entrada(c.oferta, OfertaAtividadeInput)
    dados.pessoa_id, dados.instituicao_id = None, instituicao.id
    oferta = criar(api, "ofertas-atividade", dados, OfertaAtividadeVM)
    assert oferta.responsavel_nome == instituicao.nome
    assert len(api.get("/api/v1/ofertas-atividade").json()["data"]) == 2
    assert (
        api.post("/api/v1/ofertas-atividade", json=dados.model_dump(mode="json")).status_code == 409
    )
    v = criar(
        api,
        f"ofertas-atividade/{oferta.id}/recursos",
        OfertaRecursoInput(
            recurso_id=c.recurso.id,
            quantidade_prevista=Decimal(1),
        ),
        OfertaRecursoVM,
    )
    assert v.recurso_responsavel_nome == c.pessoa.nome
    recurso = entrada(c.recurso, RecursoInput)
    recurso.pessoa_id, recurso.instituicao_id = None, instituicao.id
    resposta = api.put(f"/api/v1/recursos/{c.recurso.id}", json=recurso.model_dump(mode="json"))
    assert resposta.status_code == 200
    assert resposta.json()["data"]["responsavel_nome"] == instituicao.nome


def test_oferta_unica_validacao_e_unidade_da_capacidade(api_recursos: TestClient) -> None:
    api = api_recursos
    c = cenario(api)
    dados = entrada(c.oferta, OfertaAtividadeInput)
    assert c.oferta.validado_em is None
    assert (
        api.post("/api/v1/ofertas-atividade", json=dados.model_dump(mode="json")).status_code == 409
    )
    dados.situacao_validacao = SituacaoValidacao.VALIDADA
    url = f"/api/v1/ofertas-atividade/{c.oferta.id}"
    resposta = api.put(url, json=dados.model_dump(mode="json"))
    assert resposta.status_code == 200
    validada = ApiResponse[OfertaAtividadeVM].model_validate(resposta.json()).data
    assert validada.validado_em is not None
    dados.situacao_validacao = SituacaoValidacao.PENDENTE
    assert api.put(url, json=dados.model_dump(mode="json")).json()["data"]["validado_em"] is None
    assert len(api.get("/api/v1/ofertas-atividade?busca=Voluntário").json()["data"]) == 1
    a = entrada_da_atividade(c.atividade)
    a.id_unidade_capacidade = None
    assert (
        api.put(f"/api/v1/atividades/{c.atividade.id}", json=a.model_dump(mode="json")).status_code
        == 409
    )
    a.codigo, a.nome = "sem-unidade", "Atividade sem unidade"
    outra = criar(api, "atividades", a, AtividadeVM)
    dados.atividade_id = outra.id
    assert (
        api.post("/api/v1/ofertas-atividade", json=dados.model_dump(mode="json")).status_code == 422
    )
    dados.capacidade_declarada = None
    assert (
        api.post("/api/v1/ofertas-atividade", json=dados.model_dump(mode="json")).status_code == 201
    )
    assert api.delete(url).status_code == 200
    dados = entrada(c.oferta, OfertaAtividadeInput)
    assert (
        api.post("/api/v1/ofertas-atividade", json=dados.model_dump(mode="json")).status_code == 201
    )


def test_vinculo_escopo_unicidade_quantidade_historico(api_recursos: TestClient) -> None:
    api = api_recursos
    c = cenario(api)
    rota = f"ofertas-atividade/{c.oferta.id}/recursos"
    dados = OfertaRecursoInput(recurso_id=c.recurso.id, quantidade_prevista=Decimal(1))
    v = criar(api, rota, dados, OfertaRecursoVM)
    assert v.recurso_responsavel_nome == c.pessoa.nome
    assert api.post(f"/api/v1/{rota}", json=dados.model_dump(mode="json")).status_code == 409
    dados.quantidade_prevista = Decimal("0.5")
    assert api.put(f"/api/v1/{rota}/{v.id}", json=dados.model_dump(mode="json")).status_code == 422
    assert api.get(f"/api/v1/{rota}/{v.id}").json()["data"]["quantidade_prevista"] == "1.0000"
    oferta = entrada(c.oferta, OfertaAtividadeInput)
    oferta.municipio_atendimento_codigo_ibge = "3304557"
    outra = criar(api, "ofertas-atividade", oferta, OfertaAtividadeVM)
    for metodo in (api.get, api.delete):
        assert metodo(f"/api/v1/ofertas-atividade/{outra.id}/recursos/{v.id}").status_code == 404
    dados.quantidade_prevista = Decimal(1)
    # O mesmo ativo em duas ofertas não representa dupla reserva ou capacidade somável.
    criar(api, f"ofertas-atividade/{outra.id}/recursos", dados, OfertaRecursoVM)
    assert api.delete(f"/api/v1/{rota}/{v.id}").status_code == 200
    assert api.get(f"/api/v1/{rota}").json()["data"] == []
    assert api.get(f"/api/v1/{rota}/{v.id}?incluir_inativos=true").status_code == 200
    criar(api, rota, dados, OfertaRecursoVM)


def test_oferta_inativa_permite_historico_e_inativar_vinculos(api_recursos: TestClient) -> None:
    api = api_recursos
    c = cenario(api)
    rota = f"ofertas-atividade/{c.oferta.id}/recursos"
    dados = OfertaRecursoInput(recurso_id=c.recurso.id, quantidade_prevista=Decimal(1))
    v = criar(api, rota, dados, OfertaRecursoVM)
    assert api.delete(f"/api/v1/recursos/{c.recurso.id}").status_code == 200
    assert api.get(f"/api/v1/{rota}").json()["data"][0]["recurso_inativo"]
    assert api.put(f"/api/v1/{rota}/{v.id}", json=dados.model_dump(mode="json")).status_code == 404
    assert api.delete(f"/api/v1/ofertas-atividade/{c.oferta.id}").status_code == 200
    assert api.get(f"/api/v1/{rota}").status_code == 404
    assert api.get(f"/api/v1/{rota}?incluir_inativos=true").status_code == 200
    assert api.post(f"/api/v1/{rota}", json=dados.model_dump(mode="json")).status_code == 404
    assert api.delete(f"/api/v1/{rota}/{v.id}").status_code == 200


def test_sql_impede_responsavel_duplo_quantidade_negativa_fk(
    api_recursos: TestClient, banco_recursos: Engine
) -> None:
    c = cenario(api_recursos)
    with banco_recursos.connect() as conexao:
        for pessoa_id, instituicao_id, quantidade in (
            (None, None, Decimal(1)),
            (c.pessoa.id, UUID(int=999), Decimal(1)),
            (c.pessoa.id, None, Decimal(-1)),
            (UUID(int=999), None, Decimal(1)),
        ):
            with pytest.raises(IntegrityError), conexao.begin():
                conexao.execute(
                    insert(recursos).values(
                        id=UUID(int=999),
                        nome="Inválido",
                        tipo_recurso_id=c.tipo.id,
                        pessoa_id=pessoa_id,
                        instituicao_id=instituicao_id,
                        quantidade_total=quantidade,
                        estado_operacional="operacional",
                        municipio_codigo_ibge="3550308",
                        criado_em=agora_utc(),
                        atualizado_em=agora_utc(),
                        criado_por="teste",
                        atualizado_por="teste",
                    )
                )


def test_ofertas_concorrentes_unicas(
    api_recursos: TestClient, banco_recursos: Engine, settings: Settings
) -> None:
    c = cenario(api_recursos)
    app = create_app(settings, banco_recursos)
    dados = entrada(c.oferta, OfertaAtividadeInput)
    dados.municipio_atendimento_codigo_ibge = "3304557"

    def inserir(indice: int) -> int:
        with TestClient(app) as cliente:
            return cliente.post(
                "/api/v1/ofertas-atividade",
                json=dados.model_dump(mode="json"),
                headers={"Authorization": f"Bearer {token_teste()}"},
            ).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        respostas = list(executor.map(inserir, range(2)))
    assert sorted(respostas) == [201, 409]
