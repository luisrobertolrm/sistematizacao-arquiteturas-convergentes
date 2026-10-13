import os
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, insert, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from business.view_models.capacidades import (
    AtividadeInput,
    AtividadeTermoVM,
    AtividadeVM,
    CategoriaAtividadeInput,
    CategoriaAtividadeVM,
    UnidadeMedidaInput,
    UnidadeMedidaVM,
)
from core.entity.capacidades import Atividade, UnidadeMedida
from core.http.contratos import ApiResponse
from core.semantica import hash_atividade
from infra.configurations.capacidades import atividade_termos
from infra.database.capacidades import TermosRepositorio
from tests.conftest import token_teste
from web.main import create_app
from web.settings import Settings

pytestmark = pytest.mark.postgres


@pytest.fixture
def banco_capacidades() -> Iterator[Engine]:
    url: str | None = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Executar scripts/test_postgres.py para testar PostgreSQL real.")
    if make_url(url).database != "redesolidaria_test":
        pytest.fail("Os testes só aceitam redesolidaria_test.")
    engine: Engine = create_engine(url, hide_parameters=True)
    with engine.begin() as conexao:
        conexao.execute(
            text(
                "TRUNCATE TABLE recomendacao_recursos, recomendacao_instituicoes, "
                "recomendacao_pessoas, recomendacao_itens, recomendacoes, "
                "atividade_indice_semantico, modelo_ia, conexao_ia, demanda_itens, demandas, "
                "areas_afetadas, desastre_tipo, desastres, tipos_desastre, "
                "oferta_atividade_recurso, ofertas_atividade, recursos, "
                "tipos_recurso, "
                "atividade_termos, atividades, categorias_atividade, unidades_medida"
            )
        )
    yield engine
    engine.dispose()


@pytest.fixture
def api_capacidades(banco_capacidades: Engine, settings: Settings) -> Iterator[TestClient]:
    with TestClient(
        create_app(settings, banco_capacidades), raise_server_exceptions=False
    ) as cliente:
        cliente.headers["Authorization"] = f"Bearer {token_teste()}"
        yield cliente


def referencias(api: TestClient) -> tuple[CategoriaAtividadeVM, UnidadeMedidaVM]:
    categoria = api.post(
        "/api/v1/categorias-atividade",
        json=CategoriaAtividadeInput(
            codigo="logistica",
            nome="Logística",
            descricao="Apoio logístico",
        ).model_dump(mode="json"),
    )
    unidade = api.post(
        "/api/v1/unidades-medida",
        json=UnidadeMedidaInput(
            codigo="viagem",
            nome="Viagem",
            simbolo="viagem",
        ).model_dump(mode="json"),
    )
    assert categoria.status_code == unidade.status_code == 201
    return (
        ApiResponse[CategoriaAtividadeVM].model_validate(categoria.json()).data,
        ApiResponse[UnidadeMedidaVM].model_validate(unidade.json()).data,
    )


def atividade(api: TestClient) -> AtividadeVM:
    categoria, unidade = referencias(api)
    resposta = api.post(
        "/api/v1/atividades",
        json=AtividadeInput(
            codigo="transporte",
            nome="Transporte",
            descricao="Transportar itens de apoio",
            categoria_id=categoria.id,
            id_unidade_capacidade=unidade.id,
            orientacoes="Confirmar condições de acesso",
        ).model_dump(mode="json"),
    )
    assert resposta.status_code == 201, resposta.text
    assert "messages" not in resposta.json()
    return ApiResponse[AtividadeVM].model_validate(resposta.json()).data


def obter(api: TestClient, id_atividade: UUID) -> AtividadeVM:
    resposta = api.get(f"/api/v1/atividades/{id_atividade}")
    assert resposta.status_code == 200
    return ApiResponse[AtividadeVM].model_validate(resposta.json()).data


def entrada_da_atividade(vm: AtividadeVM) -> AtividadeInput:
    return AtividadeInput(
        codigo=vm.codigo,
        nome=vm.nome,
        descricao=vm.descricao,
        categoria_id=vm.categoria_id,
        id_unidade_capacidade=vm.id_unidade_capacidade,
        orientacoes=vm.orientacoes,
        restricoes=vm.restricoes,
    )


def test_catalogos_codigo_global_estavel_e_historico(
    api_capacidades: TestClient,
    banco_capacidades: Engine,
) -> None:
    api = api_capacidades
    categoria, unidade = referencias(api)
    assert (
        api.put(
            f"/api/v1/unidades-medida/{unidade.id}",
            json=UnidadeMedidaInput(
                codigo="outro",
                nome="Viagem",
                simbolo="v",
            ).model_dump(mode="json"),
        ).status_code
        == 409
    )
    assert (
        api.put(
            f"/api/v1/categorias-atividade/{categoria.id}",
            json=CategoriaAtividadeInput(
                codigo=categoria.codigo,
                nome="Apoio logístico",
                descricao=None,
            ).model_dump(mode="json"),
        ).status_code
        == 200
    )
    assert api.get("/api/v1/categorias-atividade?busca=apoio").json()["data"][0]["id"] == str(
        categoria.id
    )
    assert api.get("/api/v1/categorias-atividade?limite=101").status_code == 422
    assert api.delete(f"/api/v1/unidades-medida/{unidade.id}").status_code == 200
    assert api.get(f"/api/v1/unidades-medida/{unidade.id}").status_code == 404
    historico = api.get(f"/api/v1/unidades-medida/{unidade.id}?incluir_inativos=true")
    vm = ApiResponse[UnidadeMedidaVM].model_validate(historico.json()).data
    assert vm.inativado_em is not None
    with Session(banco_capacidades) as sessao:
        entidade = sessao.get(UnidadeMedida, unidade.id)
        assert entidade is not None and entidade.atualizado_por == "administrador-teste"
    assert api.get("/api/v1/unidades-medida").json()["data"] == []
    assert len(api.get("/api/v1/unidades-medida?incluir_inativos=true").json()["data"]) == 1
    assert (
        api.post(
            "/api/v1/unidades-medida",
            json=UnidadeMedidaInput(
                codigo="VIAGEM",
                nome="Duplicado",
                simbolo="v",
            ).model_dump(mode="json"),
        ).status_code
        == 409
    )


def test_atividade_ciclo_hash_textual_e_sem_nome_duplicado(api_capacidades: TestClient) -> None:
    api = api_capacidades
    criada = atividade(api)
    assert len(criada.hash_conteudo_semantico) == 64
    assert criada.categoria_nome == "Logística" and criada.unidade_nome == "Viagem"
    entrada = entrada_da_atividade(criada)
    # Busca descritiva literal, sem transformar '%' e '_' em curingas.
    assert len(api.get("/api/v1/atividades?busca=itens").json()["data"]) == 1
    assert api.get("/api/v1/atividades?busca=%25%25").json()["data"] == []
    assert (
        api.put(
            f"/api/v1/atividades/{criada.id}",
            json=entrada.model_copy(update={"codigo": "outro"}).model_dump(mode="json"),
        ).status_code
        == 409
    )
    resposta = api.put(
        f"/api/v1/atividades/{criada.id}",
        json=entrada.model_copy(update={"restricoes": "Somente carga seca"}).model_dump(
            mode="json"
        ),
    )
    alterada = ApiResponse[AtividadeVM].model_validate(resposta.json()).data
    assert alterada.hash_conteudo_semantico != criada.hash_conteudo_semantico
    assert api.delete(f"/api/v1/atividades/{criada.id}").status_code == 200
    assert api.get(f"/api/v1/atividades/{criada.id}").status_code == 404
    assert api.get(f"/api/v1/atividades/{criada.id}?incluir_inativos=true").status_code == 200


def test_termos_normalizados_hash_atomico_escopo_e_rollback(api_capacidades: TestClient) -> None:
    api = api_capacidades
    criada = atividade(api)
    url = f"/api/v1/atividades/{criada.id}/termos"
    resposta = api.post(url, json={"termo": "  AJUDA   Comunitária "})
    termo = ApiResponse[AtividadeTermoVM].model_validate(resposta.json()).data
    assert resposta.status_code == 201 and termo.termo == "ajuda comunitária"
    hash_com_termo = obter(api, criada.id).hash_conteudo_semantico
    assert hash_com_termo != criada.hash_conteudo_semantico
    assert api.post(url, json={"termo": "Ajuda comunitária"}).status_code == 409
    assert obter(api, criada.id).hash_conteudo_semantico == hash_com_termo
    outra = api.post(
        "/api/v1/atividades",
        json=AtividadeInput(
            codigo="outra",
            nome="Outra atividade",
            descricao="Outra necessidade",
            categoria_id=criada.categoria_id,
        ).model_dump(mode="json"),
    )
    id_outra = ApiResponse[AtividadeVM].model_validate(outra.json()).data.id
    for metodo in (api.get, api.delete):
        assert metodo(f"/api/v1/atividades/{id_outra}/termos/{termo.id}").status_code == 404
    assert api.put(f"{url}/{termo.id}", json={"termo": "Entrega de suprimentos"}).status_code == 200
    assert obter(api, criada.id).hash_conteudo_semantico != hash_com_termo
    assert len(api.get("/api/v1/atividades?busca=suprimentos").json()["data"]) == 1
    assert api.delete(f"{url}/{termo.id}").status_code == 200
    assert obter(api, criada.id).hash_conteudo_semantico == criada.hash_conteudo_semantico
    assert api.get(url).json()["data"] == []
    assert api.get(f"{url}/{termo.id}").status_code == 404
    assert api.get(f"{url}/{termo.id}?incluir_inativos=true").status_code == 200
    assert len(api.get(f"{url}?incluir_inativos=true").json()["data"]) == 1


def test_referencias_inativas_preservadas_novas_operacoes_bloqueadas(
    api_capacidades: TestClient,
) -> None:
    api = api_capacidades
    criada = atividade(api)
    antes = criada.hash_conteudo_semantico
    assert api.delete(f"/api/v1/categorias-atividade/{criada.categoria_id}").status_code == 200
    assert api.delete(f"/api/v1/unidades-medida/{criada.id_unidade_capacidade}").status_code == 200
    vm = obter(api, criada.id)
    assert vm.categoria_inativa and vm.unidade_inativa
    assert vm.categoria_nome == "Logística" and vm.unidade_nome == "Viagem"
    assert vm.hash_conteudo_semantico == antes
    entrada = entrada_da_atividade(criada)
    assert (
        api.put(f"/api/v1/atividades/{criada.id}", json=entrada.model_dump(mode="json")).status_code
        == 404
    )
    assert (
        api.post(
            "/api/v1/atividades",
            json=entrada.model_copy(update={"codigo": "nova"}).model_dump(mode="json"),
        ).status_code
        == 404
    )
    assert api.delete(f"/api/v1/atividades/{criada.id}").status_code == 200
    assert (
        api.post(f"/api/v1/atividades/{criada.id}/termos", json={"termo": "Novo termo"}).status_code
        == 404
    )
    assert (
        api.get(f"/api/v1/atividades/{criada.id}/termos?incluir_inativos=true").status_code == 200
    )


def test_termos_concorrentes_preservam_todos_no_hash(
    api_capacidades: TestClient,
    banco_capacidades: Engine,
    settings: Settings,
) -> None:
    criada = atividade(api_capacidades)

    aplicacao = create_app(settings, banco_capacidades)

    def inserir(termo: str) -> int:
        with TestClient(aplicacao) as cliente:
            return cliente.post(
                f"/api/v1/atividades/{criada.id}/termos",
                json={"termo": termo},
                headers={"Authorization": f"Bearer {token_teste()}"},
            ).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(inserir, ["carga seca", "suprimentos"]))
    assert resultados == [201, 201]
    with Session(banco_capacidades) as sessao:
        entidade = sessao.get(Atividade, criada.id)
        assert entidade is not None
        termos = TermosRepositorio(sessao).textos_ativos(criada.id)
        assert sorted(termos) == ["carga seca", "suprimentos"]
        assert entidade.hash_conteudo_semantico == hash_atividade(entidade, termos)


def test_fk_e_unicidade_sql_dos_termos(
    api_capacidades: TestClient, banco_capacidades: Engine
) -> None:
    criada = atividade(api_capacidades)
    resposta = api_capacidades.post(
        f"/api/v1/atividades/{criada.id}/termos", json={"termo": "carga seca"}
    )
    termo = ApiResponse[AtividadeTermoVM].model_validate(resposta.json()).data
    with banco_capacidades.connect() as conexao:
        with pytest.raises(IntegrityError), conexao.begin():
            conexao.execute(
                insert(atividade_termos).values(
                    id=UUID(int=999),
                    atividade_id=UUID(int=999),
                    termo="inexistente",
                    criado_em=termo.criado_em,
                    atualizado_em=termo.atualizado_em,
                    criado_por="teste",
                    atualizado_por="teste",
                )
            )
        with pytest.raises(IntegrityError), conexao.begin():
            conexao.execute(
                insert(atividade_termos).values(
                    id=UUID(int=998),
                    atividade_id=criada.id,
                    termo=termo.termo,
                    criado_em=termo.criado_em,
                    atualizado_em=termo.atualizado_em,
                    criado_por="teste",
                    atualizado_por="teste",
                )
            )
