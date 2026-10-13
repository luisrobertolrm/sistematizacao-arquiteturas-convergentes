from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from business.view_models.cadastros import InstituicaoVM
from business.view_models.desastres import (
    AreaAfetadaInput,
    AreaAfetadaVM,
    AvaliacaoAreaInput,
    ClassificacaoInput,
    DesastreInput,
    DesastreVM,
    GeometriaInput,
    TipoDesastreInput,
    TipoDesastreVM,
)
from core.entity.cadastros import agora_utc
from core.entity.desastres import AreaAfetada, GravidadeArea, SituacaoArea, SituacaoDesastre
from core.http.contratos import ApiResponse
from infra.configurations.desastres import desastre_tipo
from tests.conftest import token_teste
from tests.test_api_postgres import instituicao_input
from tests.test_recursos_postgres import banco_recursos as banco_recursos
from tests.test_recursos_postgres import criar
from web.main import create_app
from web.settings import Settings

pytestmark = pytest.mark.postgres


@pytest.fixture
def api_desastres(banco_recursos: Engine, settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings, banco_recursos), raise_server_exceptions=False) as api:
        api.headers["Authorization"] = f"Bearer {token_teste()}"
        yield api


def tipo(api: TestClient, codigo: str) -> TipoDesastreVM:
    return criar(
        api,
        "tipos-desastre",
        TipoDesastreInput(
            codigo=codigo, nome=codigo.title(), descricao="Fenômeno fictício de teste"
        ),
        TipoDesastreVM,
    )


def ocorrencia(api: TestClient) -> tuple[DesastreVM, DesastreInput, TipoDesastreVM]:
    instituicao = criar(api, "instituicoes", instituicao_input(), InstituicaoVM)
    inundacao, deslizamento = tipo(api, "inundacao"), tipo(api, "deslizamento")
    entrada = DesastreInput(
        titulo="Ocorrência de teste",
        descricao="Inundação fictícia e deslizamento",
        inicio_em=datetime(2026, 10, 9, 9, tzinfo=UTC),
        id_instituicao_coordenadora=instituicao.id,
        situacao=SituacaoDesastre.EM_RESPOSTA,
        classificacoes=[
            ClassificacaoInput(id_tipo_desastre=inundacao.id, principal=True),
            ClassificacaoInput(id_tipo_desastre=deslizamento.id, principal=False),
        ],
    )
    return criar(api, "desastres", entrada, DesastreVM), entrada, deslizamento


def area_input() -> AreaAfetadaInput:
    return AreaAfetadaInput(
        nome="Várzea de teste",
        descricao="Área fictícia inundada",
        municipio_codigo_ibge="3550308",
        gravidade=GravidadeArea.ALTA,
        situacao=SituacaoArea.EM_RESPOSTA,
        geometria=GeometriaInput(
            type="Polygon",
            coordinates=[[(-46.64, -23.55), (-46.63, -23.55), (-46.63, -23.54), (-46.64, -23.55)]],
        ),
    )


def test_tipo_codigo_estavel_e_classificacao_atomica(api_desastres: TestClient) -> None:
    api = api_desastres
    d, entrada, secundario = ocorrencia(api)
    assert sum(c.principal for c in d.classificacoes) == 1
    assert len(api.get("/api/v1/desastres?busca=fictícia").json()["data"]) == 1
    assert api.get("/api/v1/desastres?limite=101").status_code == 422
    t = TipoDesastreInput(codigo="outro", nome=secundario.nome, descricao=secundario.descricao)
    assert (
        api.put(
            f"/api/v1/tipos-desastre/{secundario.id}", json=t.model_dump(mode="json")
        ).status_code
        == 409
    )
    assert (
        api.post(
            "/api/v1/tipos-desastre",
            json=TipoDesastreInput(
                codigo="DESLIZAMENTO", nome="Outro", descricao="Duplicado"
            ).model_dump(mode="json"),
        ).status_code
        == 409
    )
    entrada.titulo = "Não deve persistir"
    entrada.classificacoes[1].id_tipo_desastre = UUID(int=999)
    assert api.post("/api/v1/desastres", json=entrada.model_dump(mode="json")).status_code == 404
    assert api.get("/api/v1/desastres?busca=persistir").json()["data"] == []


def test_troca_principal_remocao_e_historico_classificacao(api_desastres: TestClient) -> None:
    api = api_desastres
    d, entrada, secundario = ocorrencia(api)
    url = f"/api/v1/desastres/{d.id}"
    for c in entrada.classificacoes:
        c.principal = c.id_tipo_desastre == secundario.id
    resposta = api.put(url, json=entrada.model_dump(mode="json"))
    assert resposta.status_code == 200, resposta.text
    vm = ApiResponse[DesastreVM].model_validate(resposta.json()).data
    assert next(c for c in vm.classificacoes if c.principal).id_tipo_desastre == secundario.id
    assert {c.id for c in vm.classificacoes} == {c.id for c in d.classificacoes}
    entrada.classificacoes = [entrada.classificacoes[1]]
    assert api.put(url, json=entrada.model_dump(mode="json")).status_code == 200
    assert len(api.get(url).json()["data"]["classificacoes"]) == 1
    historico = (
        ApiResponse[DesastreVM].model_validate(api.get(url + "?incluir_inativos=true").json()).data
    )
    assert len(historico.classificacoes) == 2
    assert sum(c.inativado_em is not None for c in historico.classificacoes) == 1


def test_encerramento_distinto_inativacao_reabertura_e_referencias(
    api_desastres: TestClient,
) -> None:
    api = api_desastres
    d, entrada, secundario = ocorrencia(api)
    entrada.situacao, entrada.encerramento_em = (
        SituacaoDesastre.ENCERRADO,
        entrada.inicio_em + timedelta(days=1),
    )
    url = f"/api/v1/desastres/{d.id}"
    assert api.put(url, json=entrada.model_dump(mode="json")).status_code == 200
    assert api.get(url).json()["data"]["inativado_em"] is None
    entrada.situacao, entrada.encerramento_em = SituacaoDesastre.EM_RESPOSTA, None
    assert api.put(url, json=entrada.model_dump(mode="json")).status_code == 409
    assert api.delete(f"/api/v1/tipos-desastre/{secundario.id}").status_code == 200
    vm = ApiResponse[DesastreVM].model_validate(api.get(url).json()).data
    assert next(c for c in vm.classificacoes if c.id_tipo_desastre == secundario.id).tipo_inativo
    assert api.delete(f"/api/v1/instituicoes/{d.id_instituicao_coordenadora}").status_code == 200
    assert api.get(url).json()["data"]["coordenadora_inativa"]
    assert api.delete(url).status_code == 200
    assert api.get(url).status_code == 404
    assert api.get(url + "?incluir_inativos=true").status_code == 200


def test_area_geojson_persistencia_e_avaliacao_separada(
    api_desastres: TestClient, banco_recursos: Engine
) -> None:
    api = api_desastres
    d, _, _ = ocorrencia(api)
    rota = f"desastres/{d.id}/areas"
    entrada = area_input()
    a = criar(api, rota, entrada, AreaAfetadaVM)
    assert a.geometria == entrada.geometria
    with Session(banco_recursos) as sessao:
        entidade = sessao.get(AreaAfetada, a.id)
        assert entidade is not None
        assert entidade.geometria == entrada.geometria.para_entidade()
        assert entidade.criado_por == "administrador-teste"
    entrada.nome = "Nome corrigido"
    entrada.geometria = GeometriaInput(
        type="Polygon",
        coordinates=[[(-46.65, -23.55), (-46.63, -23.55), (-46.63, -23.54), (-46.65, -23.55)]],
    )
    url = f"/api/v1/{rota}/{a.id}"
    corrigida = (
        ApiResponse[AreaAfetadaVM]
        .model_validate(api.put(url, json=entrada.model_dump(mode="json")).json())
        .data
    )
    assert corrigida.ultima_avaliacao_em == a.ultima_avaliacao_em
    assert corrigida.atualizado_em > a.atualizado_em
    entrada.gravidade = GravidadeArea.CRITICA
    avaliada = (
        ApiResponse[AreaAfetadaVM]
        .model_validate(api.put(url, json=entrada.model_dump(mode="json")).json())
        .data
    )
    assert avaliada.ultima_avaliacao_em > corrigida.ultima_avaliacao_em
    resposta = api.post(
        url + "/avaliar",
        json=AvaliacaoAreaInput(gravidade=entrada.gravidade, situacao=entrada.situacao).model_dump(
            mode="json"
        ),
    )
    confirmada = ApiResponse[AreaAfetadaVM].model_validate(resposta.json()).data
    assert confirmada.ultima_avaliacao_em > avaliada.ultima_avaliacao_em
    assert len(api.get(f"/api/v1/{rota}?busca=3550308").json()["data"]) == 1


def test_area_escopo_e_historico_ocorrencia_inativa(api_desastres: TestClient) -> None:
    api = api_desastres
    d, entrada, _ = ocorrencia(api)
    rota = f"desastres/{d.id}/areas"
    a = criar(api, rota, area_input(), AreaAfetadaVM)
    entrada.titulo = "Outra ocorrência"
    outra = criar(api, "desastres", entrada, DesastreVM)
    outra_url = f"/api/v1/desastres/{outra.id}/areas/{a.id}"
    assert api.get(outra_url).status_code == 404
    assert api.delete(outra_url).status_code == 404
    assert api.put(outra_url, json=area_input().model_dump(mode="json")).status_code == 404
    assert (
        api.post(
            outra_url + "/avaliar",
            json=AvaliacaoAreaInput(
                gravidade=GravidadeArea.ALTA, situacao=SituacaoArea.EM_RESPOSTA
            ).model_dump(mode="json"),
        ).status_code
        == 404
    )
    assert api.delete(f"/api/v1/desastres/{d.id}").status_code == 200
    assert api.get(f"/api/v1/{rota}").status_code == 404
    assert api.get(f"/api/v1/{rota}?incluir_inativos=true").status_code == 200
    assert api.post(f"/api/v1/{rota}", json=area_input().model_dump(mode="json")).status_code == 404
    assert api.delete(f"/api/v1/{rota}/{a.id}").status_code == 200


def test_classificacao_concorrente_sempre_um_principal(
    api_desastres: TestClient, banco_recursos: Engine, settings: Settings
) -> None:
    d, entrada, secundario = ocorrencia(api_desastres)
    app = create_app(settings, banco_recursos)

    def alterar(principal: UUID) -> int:
        dados = DesastreInput.model_validate_json(entrada.model_dump_json())
        for c in dados.classificacoes:
            c.principal = c.id_tipo_desastre == principal
        with TestClient(app) as api:
            return api.put(
                f"/api/v1/desastres/{d.id}",
                json=dados.model_dump(mode="json"),
                headers={"Authorization": f"Bearer {token_teste()}"},
            ).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        respostas = list(
            executor.map(alterar, [entrada.classificacoes[0].id_tipo_desastre, secundario.id])
        )
    assert respostas == [200, 200]
    vm = (
        ApiResponse[DesastreVM]
        .model_validate(api_desastres.get(f"/api/v1/desastres/{d.id}").json())
        .data
    )
    assert len(vm.classificacoes) == 2 and sum(c.principal for c in vm.classificacoes) == 1


def test_sql_no_maximo_um_principal_e_fk(api_desastres: TestClient, banco_recursos: Engine) -> None:
    d, _, secundario = ocorrencia(api_desastres)
    extra = tipo(api_desastres, "incendio")
    with banco_recursos.connect() as conexao:
        for id_tipo, principal in (
            (extra.id, True),
            (UUID(int=999), False),
            (secundario.id, False),
        ):
            with pytest.raises(IntegrityError), conexao.begin():
                conexao.execute(
                    insert(desastre_tipo).values(
                        id=UUID(int=998),
                        id_desastre=d.id,
                        id_tipo_desastre=id_tipo,
                        principal=principal,
                        criado_em=agora_utc(),
                        atualizado_em=agora_utc(),
                        criado_por="teste",
                        atualizado_por="teste",
                    )
                )
        assert (
            len(
                conexao.scalars(
                    select(desastre_tipo.c.id).where(desastre_tipo.c.id_desastre == d.id)
                ).all()
            )
            == 2
        )
