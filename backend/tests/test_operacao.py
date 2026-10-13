from math import nan

import pytest
from pydantic import ValidationError

from business.view_models.operacao import ConexaoInput
from core.http.contratos import ErroNegocio
from core.vetores import cosseno, validar_vetor


@pytest.mark.parametrize(
    "vetor,dimensao", [([0.0, 0.0], 2), ([1.0], 2), ([nan], 1), ([float("inf")], 1)]
)
def test_rejeita_vetor_invalido(vetor: list[float], dimensao: int) -> None:
    with pytest.raises(ErroNegocio):
        validar_vetor(vetor, dimensao)


def test_cosseno_normalizado() -> None:
    assert cosseno([1, 0], [0, 1]) == 0
    assert cosseno([2, 0], [3, 0]) == 1


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "https://u:senha@exemplo.com",
        "https://exemplo.com?token=x",
        "http://exemplo.com",
    ],
)
def test_url_sem_credenciais_e_tls(url: str) -> None:
    with pytest.raises(ValidationError):
        ConexaoInput(nome="Teste", url_base=url)
