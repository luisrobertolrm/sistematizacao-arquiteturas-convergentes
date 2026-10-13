from dataclasses import replace
from decimal import Decimal
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from business.view_models.recursos import OfertaAtividadeInput, RecursoInput
from core.entity.recursos import CategoriaRecurso, ModoControleRecurso, TipoRecurso
from core.semantica import hash_tipo_recurso
from tests.conftest import token_teste


@pytest.mark.parametrize(
    "rota",
    [
        "tipos-recurso",
        "recursos",
        "ofertas-atividade",
        "ofertas-atividade/00000000-0000-0000-0000-000000000001/recursos",
    ],
)
def test_novas_rotas_exigem_administrador(client: TestClient, rota: str) -> None:
    assert client.get(f"/api/v1/{rota}").status_code == 401
    client.headers["Authorization"] = f"Bearer {token_teste(role='voluntario')}"
    assert client.get(f"/api/v1/{rota}").status_code == 403


def test_responsavel_exclusivo_coordenadas_e_precisao() -> None:
    with pytest.raises(ValidationError):
        RecursoInput(
            tipo_recurso_id=UUID(int=1),
            nome="Recurso",
            quantidade_total=Decimal(1),
            municipio_codigo_ibge="3550308",
        )
    with pytest.raises(ValidationError):
        OfertaAtividadeInput(
            atividade_id=UUID(int=1),
            municipio_atendimento_codigo_ibge="3550308",
            instituicao_id=UUID(int=2),
            pessoa_id=UUID(int=3),
        )
    with pytest.raises(ValidationError):
        RecursoInput(
            tipo_recurso_id=UUID(int=1),
            nome="Recurso",
            quantidade_total=Decimal(1),
            municipio_codigo_ibge="3550308",
            pessoa_id=UUID(int=3),
            latitude=Decimal(0),
        )
    with pytest.raises(ValidationError):
        RecursoInput(
            tipo_recurso_id=UUID(int=1),
            nome="Recurso",
            quantidade_total=Decimal("1.00001"),
            municipio_codigo_ibge="3550308",
            pessoa_id=UUID(int=3),
        )
    with pytest.raises(ValidationError):
        OfertaAtividadeInput(
            atividade_id=UUID(int=1),
            municipio_atendimento_codigo_ibge="3550308",
            pessoa_id=UUID(int=3),
            capacidade_declarada=Decimal(0),
        )


def test_hash_tipo_recurso_canonico_na_origem() -> None:
    tipo = TipoRecurso(
        nome="Gerador",
        descricao="Energia de apoio",
        categoria=CategoriaRecurso.EQUIPAMENTO,
        id_unidade_medida=UUID(int=1),
        modo_controle=ModoControleRecurso.INDIVIDUAL,
        hash_conteudo_semantico="",
        criado_por="teste",
        atualizado_por="teste",
    )
    original: str = hash_tipo_recurso(tipo)
    assert len(original) == 64
    assert (
        hash_tipo_recurso(replace(tipo, id_unidade_medida=UUID(int=2), atualizado_por="outro"))
        == original
    )
    assert hash_tipo_recurso(replace(tipo, descricao="Gerador de emergência")) != original
