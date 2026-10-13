from datetime import UTC, datetime
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from business.view_models.desastres import ClassificacaoInput, DesastreInput, GeometriaInput
from core.entity.desastres import SituacaoDesastre
from core.geometria import GeometriaArea, Posicao
from tests.conftest import token_teste


@pytest.mark.parametrize(
    "rota", ["tipos-desastre", "desastres", "desastres/00000000-0000-0000-0000-000000000001/areas"]
)
def test_rotas_territoriais_exigem_admin(client: TestClient, rota: str) -> None:
    assert client.get(f"/api/v1/{rota}").status_code == 401
    client.headers["Authorization"] = f"Bearer {token_teste(role='voluntario')}"
    assert client.get(f"/api/v1/{rota}").status_code == 403


@pytest.mark.parametrize(
    "anel",
    [
        ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0)),
        ((0.0, 0.0), (1.0, 0.0), (1.0, 0.0), (0.0, 0.0)),
        ((0.0, 0.0), (1.0, 1.0), (0.0, 1.0), (1.0, 0.0), (0.0, 0.0)),
        ((0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (0.0, 0.0)),
        ((0.0, 0.0), (2.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0)),
        ((179.0, 0.0), (-179.0, 0.0), (-179.0, 1.0), (179.0, 0.0)),
        ((0.0, 86.0), (1.0, 0.0), (0.0, 1.0), (0.0, 86.0)),
        ((0.0, 0.0), (float("nan"), 0.0), (0.0, 1.0), (0.0, 0.0)),
    ],
)
def test_geometria_rejeita_bordas_invalidas(anel: tuple[Posicao, ...]) -> None:
    with pytest.raises(ValueError):
        GeometriaArea(coordinates=(anel,))


def test_geojson_longitude_latitude_fechamento_orientacao_e_limites() -> None:
    entrada = GeometriaInput(
        type="Polygon",
        coordinates=[
            [
                (-46.64, -23.55),
                (-46.64, -23.54),
                (-46.63, -23.54),
                (-46.63, -23.55),
                (-46.64, -23.55),
            ]
        ],
    )
    geometria = entrada.para_entidade()
    assert geometria.coordinates[0][1] == (-46.63, -23.55)
    assert GeometriaArea.de_json(geometria.para_json()) == geometria
    with pytest.raises(ValidationError):
        GeometriaInput(type="Polygon", coordinates=[entrada.coordinates[0], entrada.coordinates[0]])
    with pytest.raises(ValueError):
        GeometriaArea(coordinates=(tuple((float(i), 0.0) for i in range(201)) + ((0.0, 0.0),),))


def test_classificacoes_datas_fuso_e_encerramento() -> None:
    inicio = datetime(2026, 10, 9, tzinfo=UTC)
    dados = DesastreInput(
        titulo="Ocorrência",
        descricao="Cenário fictício",
        inicio_em=inicio,
        id_instituicao_coordenadora=UUID(int=1),
        classificacoes=[ClassificacaoInput(id_tipo_desastre=UUID(int=2), principal=True)],
    )
    assert dados.inicio_em.tzinfo == UTC
    dados.situacao = SituacaoDesastre.ENCERRADO
    with pytest.raises(ValidationError):
        DesastreInput.model_validate_json(dados.model_dump_json())
    dados.situacao = SituacaoDesastre.EM_RESPOSTA
    dados.inicio_em = inicio.replace(tzinfo=None)
    with pytest.raises(ValidationError):
        DesastreInput.model_validate_json(dados.model_dump_json())
    dados.inicio_em = inicio
    dados.classificacoes.append(ClassificacaoInput(id_tipo_desastre=UUID(int=3), principal=True))
    with pytest.raises(ValidationError):
        DesastreInput.model_validate_json(dados.model_dump_json())
