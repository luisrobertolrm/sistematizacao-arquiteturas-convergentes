from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from uuid import UUID

from business.graphs.atendimento import ContextoRecuperado
from core.ia_operacao import (
    ClienteEmbedding,
    ClienteInferencia,
    ConfiguracaoModelo,
    InstituicaoSugerida,
    ItemSugerido,
    PessoaSugerida,
    PropostaDemanda,
    RecursoSugerido,
)


class EmbeddingFicticio:
    def __init__(self, dimensao: int, fabrica: FabricaFicticia) -> None:
        self.dimensao: int = dimensao
        self.fabrica: FabricaFicticia = fabrica

    def gerar(self, textos: list[str]) -> list[list[float]]:
        if self.fabrica.acao:
            self.fabrica.acao()
        if self.fabrica.falhar:
            raise RuntimeError("Detalhe privado de provedor: token-ficticio")
        return [[1.0] + [0.0] * (self.dimensao - 1) for _ in textos]


class InferenciaFicticia:
    def __init__(self, fabrica: FabricaFicticia) -> None:
        self.fabrica: FabricaFicticia = fabrica

    def gerar(self, contexto: str) -> PropostaDemanda:
        c = ContextoRecuperado.model_validate_json(contexto).dados
        itens: list[ItemSugerido] = []
        for d in c.demanda.itens:
            pessoas: list[PessoaSugerida] = []
            instituicoes: list[InstituicaoSugerida] = []
            bens: list[RecursoSugerido] = []
            quantidade = Decimal(0)
            for o in c.ofertas:
                if o.id_atividade == d.id_atividade:
                    if o.id_pessoa:
                        pessoas.append(
                            PessoaSugerida(
                                id_pessoa=o.id_pessoa,
                                id_oferta_atividade=o.id,
                                papel_sugerido="Apoio cadastral",
                            )
                        )
                    elif o.id_instituicao:
                        instituicoes.append(
                            InstituicaoSugerida(
                                id_instituicao=o.id_instituicao, id_oferta_atividade=o.id
                            )
                        )
            for r in c.recursos:
                if r.id_tipo_recurso == d.id_tipo_recurso and not bens:
                    quantidade = min(r.quantidade_total, d.quantidade_solicitada)
                    bens.append(RecursoSugerido(id_recurso=r.id, quantidade_sugerida=quantidade))
            itens.append(
                ItemSugerido(
                    id_demanda_item=d.id,
                    quantidade_sugerida=quantidade,
                    justificativa="Candidatos fictícios fornecidos pelo cenário",
                    pessoas=pessoas,
                    instituicoes=instituicoes,
                    recursos=bens,
                )
            )
        if self.fabrica.inventar:
            itens[0].id_demanda_item = UUID(int=999999)
        if self.fabrica.acao_texto:
            self.fabrica.acao_texto()
        return PropostaDemanda(
            justificativa="Análise fictícia para teste",
            pendencias=["Disponibilidade não verificada"],
            itens=itens,
        )


class FabricaFicticia:
    def __init__(self) -> None:
        self.acao: Callable[[], None] | None = None
        self.acao_texto: Callable[[], None] | None = None
        self.falhar: bool = False
        self.inventar: bool = False

    def embedding(self, config: ConfiguracaoModelo) -> ClienteEmbedding:
        assert config.dimensao is not None
        return EmbeddingFicticio(config.dimensao, self)

    def inferencia(self, config: ConfiguracaoModelo) -> ClienteInferencia:
        return InferenciaFicticia(self)
