from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError

from business.view_models.cadastros import InstituicaoInput, PessoaInput
from core.http.contratos import ApiResponse, Problema
from infra.ia.credenciais import CofreCredenciais
from tests.conftest import token_teste


def test_health_publico_e_envelope(client: TestClient) -> None:
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"data": {"status": "ok"}}


@pytest.mark.parametrize(
    "token,status",
    [
        (None, 401),
        ("invalido", 401),
        (token_teste(role="consulta"), 403),
        (token_teste(issuer="outro"), 401),
        (token_teste(expira=-1), 401),
    ],
)
def test_rotas_exigem_jwt_admin(client: TestClient, token: str | None, status: int) -> None:
    resposta = client.get(
        "/api/v1/pessoas", headers={"Authorization": f"Bearer {token}"} if token else {}
    )
    assert resposta.status_code == status
    assert resposta.headers["content-type"].startswith("application/problem+json")
    problema: Problema = Problema.model_validate(resposta.json())
    assert problema.status == status
    assert "data" not in resposta.json()
    if status == 401:
        assert resposta.headers["www-authenticate"] == "Bearer"


def test_validacao_nao_vaza_input(client: TestClient) -> None:
    resposta = client.post(
        "/api/v1/pessoas",
        headers={"Authorization": f"Bearer {token_teste()}"},
        json={"nome": "segredo-nao-deve-ser-repetido", "api_token": "nao-vazar"},
    )
    assert resposta.status_code == 422
    assert "nao-vazar" not in resposta.text
    assert "segredo-nao-deve-ser-repetido" not in resposta.text
    assert Problema.model_validate(resposta.json()).status == 422


def test_normalizacao_e_cnpj_alfanumerico() -> None:
    dados: InstituicaoInput = InstituicaoInput(
        nome="  Associação  ",
        municipio_codigo_ibge="3550308",
        uf="sp",
        tipo="associacao",
        cnpj="AB.123.456/0001-95",
        telefone_contato="(11) 99999-8888",
    )
    assert dados.nome == "Associação" and dados.uf == "SP"
    assert dados.cnpj == "AB123456000195" and dados.telefone_contato == "11999998888"


def test_coordenadas_pareadas_e_limites() -> None:
    with pytest.raises(ValidationError):
        PessoaInput(nome="Pessoa", municipio_codigo_ibge="3550308", uf="SP", latitude="-23")
    with pytest.raises(ValidationError):
        PessoaInput(
            nome="Pessoa", municipio_codigo_ibge="3550308", uf="SP", latitude="100", longitude="-46"
        )


def test_campos_nulos_preservados_sem_mensagens() -> None:
    assert ApiResponse(data=None).model_dump(mode="json") == {"data": None}


def test_criptografia_autenticada() -> None:
    from cryptography.fernet import Fernet

    cofre: CofreCredenciais = CofreCredenciais(SecretStr(Fernet.generate_key().decode("ascii")))
    segredo: SecretStr = SecretStr("credencial-ficticia")
    cifrado: bytes = cofre.criptografar(segredo)
    assert b"credencial-ficticia" not in cifrado
    assert cofre.descriptografar(cifrado).get_secret_value() == segredo.get_secret_value()
    assert cofre.criptografar(segredo) != cifrado
    with pytest.raises(ValueError, match="Credencial protegida"):
        cofre.descriptografar(cifrado[:-5] + b"xxxxx")


def test_dependencias_entre_camadas() -> None:
    import ast

    raiz: Path = Path(__file__).resolve().parents[1]
    restricoes: dict[str, set[str]] = {
        "core": {"infra", "business", "web"},
        "infra": {"business", "web"},
        "business": {"web"},
    }
    for camada, proibidas in restricoes.items():
        for arquivo in (raiz / camada).rglob("*.py"):
            arvore: ast.Module = ast.parse(arquivo.read_text(encoding="utf-8"))
            for no in ast.walk(arvore):
                if isinstance(no, ast.ImportFrom) and no.module:
                    assert no.module.split(".")[0] not in proibidas, str(arquivo)
                if isinstance(no, ast.Import):
                    assert not {n.name.split(".")[0] for n in no.names} & proibidas, str(arquivo)
