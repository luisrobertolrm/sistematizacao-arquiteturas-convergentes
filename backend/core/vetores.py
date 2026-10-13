from math import hypot, isfinite

from core.http.contratos import ErroNegocio


def validar_vetor(vetor: list[float], dimensao: int | None) -> None:
    if (
        len(vetor) != dimensao
        or not all(isfinite(x) for x in vetor)
        or not hypot(*vetor)
        or not isfinite(hypot(*vetor))
    ):
        raise ErroNegocio(
            502,
            "Embedding inválido",
            "Vetor deve ter dimensão correta, valores finitos e norma positiva.",
        )


def cosseno(a: list[float], b: list[float]) -> float:
    na, nb = hypot(*a), hypot(*b)
    return sum((x / na) * (y / nb) for x, y in zip(a, b, strict=True))
