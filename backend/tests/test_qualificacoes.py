from datetime import date
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from business.view_models.qualificacoes import (
    PessoaCursoInput,
    PessoaInstituicaoInput,
    PessoaProfissaoInput,
    ProfissaoInput,
)


@pytest.mark.parametrize(
    "caminho",
    [
        "/api/v1/profissoes",
        "/api/v1/cursos",
        f"/api/v1/pessoas/{UUID(int=1)}/instituicoes",
        f"/api/v1/pessoas/{UUID(int=1)}/profissoes",
        f"/api/v1/pessoas/{UUID(int=1)}/cursos",
    ],
)
def test_novas_rotas_exigem_admin(client: TestClient, caminho: str) -> None:
    assert client.get(caminho).status_code == 401


def test_hash_nao_e_editavel_e_formato_cbo() -> None:
    with pytest.raises(ValidationError):
        ProfissaoInput.model_validate_json(
            '{"nome":"Profissão","hash_conteudo_semantico":"forjado"}'
        )
    with pytest.raises(ValidationError):
        ProfissaoInput(nome="Profissão", codigo_cbo="abcdef")


def test_qualificacoes_datas_carga_uf_e_comprovante() -> None:
    with pytest.raises(ValidationError):
        PessoaInstituicaoInput(
            instituicao_id=UUID(int=1),
            tipo_vinculo="voluntario",
            inicio_em=date(2026, 2, 1),
            fim_em=date(2026, 1, 1),
        )
    with pytest.raises(ValidationError):
        PessoaProfissaoInput(profissao_id=UUID(int=1), uf_registro="XX")
    with pytest.raises(ValidationError):
        PessoaCursoInput(
            curso_id=UUID(int=1),
            instituicao_emissora="Escola",
            conclusao_em=date(2026, 1, 1),
            validade_em=date(2025, 1, 1),
        )
    with pytest.raises(ValidationError):
        PessoaCursoInput(
            curso_id=UUID(int=1),
            instituicao_emissora="Escola",
            conclusao_em=date(2026, 1, 1),
            carga_horaria="0",
        )
    with pytest.raises(ValidationError):
        PessoaCursoInput(
            curso_id=UUID(int=1),
            instituicao_emissora="Escola",
            conclusao_em=date(2026, 1, 1),
            comprovante_referencia="https://site.invalid?token=segredo",
        )
