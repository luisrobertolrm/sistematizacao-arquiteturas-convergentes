"""Polígono local simples GeoJSON, sem anéis internos ou cruzamento do antimeridiano."""

from dataclasses import dataclass
from math import isfinite
from typing import Literal, Self, TypedDict

type Posicao = tuple[float, float]
EPSILON: float = 1e-12


class GeometriaJSON(TypedDict):
    type: Literal["Polygon"]
    coordinates: list[list[list[float]]]


def orientacao(a: Posicao, b: Posicao, c: Posicao) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def no_segmento(a: Posicao, b: Posicao, p: Posicao) -> bool:
    return (
        abs(orientacao(a, b, p)) <= EPSILON
        and min(a[0], b[0]) - EPSILON <= p[0] <= max(a[0], b[0]) + EPSILON
        and min(a[1], b[1]) - EPSILON <= p[1] <= max(a[1], b[1]) + EPSILON
    )


def intersectam(a: Posicao, b: Posicao, c: Posicao, d: Posicao) -> bool:
    ab_c, ab_d = orientacao(a, b, c), orientacao(a, b, d)
    cd_a, cd_b = orientacao(c, d, a), orientacao(c, d, b)
    return (
        ((ab_c > EPSILON and ab_d < -EPSILON) or (ab_c < -EPSILON and ab_d > EPSILON))
        and ((cd_a > EPSILON and cd_b < -EPSILON) or (cd_a < -EPSILON and cd_b > EPSILON))
    ) or any(
        (no_segmento(a, b, c), no_segmento(a, b, d), no_segmento(c, d, a), no_segmento(c, d, b))
    )


@dataclass(frozen=True, kw_only=True)
class GeometriaArea:
    coordinates: tuple[tuple[Posicao, ...], ...]
    type: Literal["Polygon"] = "Polygon"

    def __post_init__(self) -> None:
        if self.type != "Polygon" or len(self.coordinates) != 1:
            raise ValueError("Informe Polygon com um único anel exterior, sem furos")
        anel: tuple[Posicao, ...] = self.coordinates[0]
        if not 4 <= len(anel) <= 201 or anel[0] != anel[-1]:
            raise ValueError("Polígono exige 3 a 200 vértices e fechamento igual ao primeiro ponto")
        vertices: tuple[Posicao, ...] = anel[:-1]
        if len(set(vertices)) != len(vertices):
            raise ValueError("Vértices da área não podem ser repetidos")
        if any(
            not isfinite(x) or not isfinite(y) or not -180 <= x <= 180 or not -85 <= y <= 85
            for x, y in vertices
        ):
            raise ValueError("Use longitude entre -180/180 e latitude entre -85/85")
        if max(p[0] for p in vertices) - min(p[0] for p in vertices) >= 180:
            raise ValueError("O polígono local não pode atravessar o antimeridiano")
        n: int = len(vertices)
        for i in range(n):
            # Segmentos adjacentes também não podem voltar sobre si mesmos.
            a, b, c = vertices[i - 1], vertices[i], vertices[(i + 1) % n]
            if no_segmento(a, b, c) or no_segmento(b, c, a):
                raise ValueError("A borda não pode sobrepor segmentos adjacentes")
            for j in range(i + 1, n):
                if j == i + 1 or (i == 0 and j == n - 1):
                    continue
                if intersectam(
                    vertices[i], vertices[(i + 1) % n], vertices[j], vertices[(j + 1) % n]
                ):
                    raise ValueError("A borda da área não pode cruzar ou tocar a si mesma")
        # Usa origem local para reduzir cancelamento numérico em coordenadas próximas.
        area: float = sum(
            orientacao(vertices[0], vertices[i], vertices[i + 1]) for i in range(1, n - 1)
        )
        if abs(area) <= EPSILON:
            raise ValueError("A área deve ser maior que zero")
        if area < 0:
            object.__setattr__(self, "coordinates", (tuple(reversed(anel)),))

    def para_json(self) -> GeometriaJSON:
        return {
            "type": "Polygon",
            "coordinates": [[[x, y] for x, y in anel] for anel in self.coordinates],
        }

    @classmethod
    def de_json(cls, dados: GeometriaJSON) -> Self:
        if any(len(p) != 2 for anel in dados["coordinates"] for p in anel):
            raise ValueError("Cada posição deve conter somente longitude e latitude")
        return cls(
            type=dados["type"],
            coordinates=tuple(tuple((p[0], p[1]) for p in anel) for anel in dados["coordinates"]),
        )
