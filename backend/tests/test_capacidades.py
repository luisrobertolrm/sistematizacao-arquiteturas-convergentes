from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from business.view_models.capacidades import AtividadeInput, AtividadeTermoInput, UnidadeMedidaInput
from core.entity.capacidades import Atividade
from core.semantica import conteudo_atividade, hash_atividade
from tests.conftest import token_teste


@pytest.mark.parametrize(
    "caminho",
    [
        "/api/v1/unidades-medida",
        "/api/v1/categorias-atividade",
        "/api/v1/atividades",
        f"/api/v1/atividades/{UUID(int=1)}/termos",
    ],
)
def test_capacidades_exigem_administrador(client: TestClient, caminho: str) -> None:
    assert client.get(caminho).status_code == 401
    assert (
        client.get(
            caminho, headers={"Authorization": f"Bearer {token_teste('voluntario')}"}
        ).status_code
        == 403
    )


def test_normalizacao_e_campos_exclusivos_do_servidor() -> None:
    assert UnidadeMedidaInput(codigo=" LITRO ", nome="Litro", simbolo="L").codigo == "litro"
    assert AtividadeTermoInput(termo="  REFEIÇÕES   Quentes  ").termo == "refeições quentes"
    with pytest.raises(ValidationError):
        UnidadeMedidaInput(codigo="Litro / hora", nome="Litro", simbolo="L")
    with pytest.raises(ValidationError):
        AtividadeInput.model_validate_json(
            '{"codigo":"transporte","nome":"Transporte","descricao":"Cargas",'
            '"categoria_id":"00000000-0000-0000-0000-000000000001",'
            '"hash_conteudo_semantico":"forjado"}'
        )
    with pytest.raises(ValidationError):
        AtividadeTermoInput.model_validate_json('{"termo":"Cargas","atividade_id":"outra"}')


def test_canonico_semantico_estavel_exclui_auditoria_e_referencias() -> None:
    atividade: Atividade = Atividade(
        codigo="transporte",
        nome="Transporte",
        descricao="Carga de suprimentos",
        categoria_id=UUID(int=1),
        hash_conteudo_semantico="",
        criado_por="teste",
        atualizado_por="teste",
    )
    primeiro: str = hash_atividade(atividade, ["suprimentos", "cargas"])
    assert primeiro == hash_atividade(atividade, ["cargas", "suprimentos", "cargas"])
    assert '"termos":["cargas","suprimentos"]' in conteudo_atividade(
        atividade, ["suprimentos", "cargas"]
    )
    atividade.categoria_id, atividade.id_unidade_capacidade = UUID(int=2), UUID(int=3)
    atividade.atualizado_por = "outro"
    assert primeiro == hash_atividade(atividade, ["cargas", "suprimentos"])
    atividade.restricoes = "Sem produtos inflamáveis"
    assert primeiro != hash_atividade(atividade, ["cargas", "suprimentos"])
