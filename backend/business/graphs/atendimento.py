from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import Literal, TypedDict, cast
from uuid import UUID

from langgraph.graph import END, START, StateGraph
from pydantic import Field

from business.view_models.operacao import BuscaVM, DemandaVM
from business.view_models.qualificacoes import Entrada
from core.http.contratos import ErroNegocio
from core.ia_operacao import ClienteInferencia, PropostaDemanda


class OfertaCandidata(Entrada):
    id: UUID
    id_atividade: UUID
    id_pessoa: UUID | None
    id_instituicao: UUID | None
    nome: str
    capacidade_declarada: Decimal | None
    atualizado_em: datetime
    responsavel_atualizado_em: datetime


class RecursoCandidato(Entrada):
    modo_controle: Literal["individual", "estoque"]
    id: UUID
    id_tipo_recurso: UUID
    id_unidade_medida: UUID
    nome: str
    quantidade_total: Decimal
    atualizado_em: datetime
    responsavel_atualizado_em: datetime
    ofertas: list[UUID]


class ContextoAnalise(Entrada):
    demanda: DemandaVM
    fontes: dict[UUID, str] = Field(default_factory=dict)
    municipio: str
    area_atualizada_em: datetime
    desastre_atualizado_em: datetime
    ofertas: list[OfertaCandidata]
    recursos: list[RecursoCandidato]
    limites: list[str] = Field(
        default_factory=lambda: [
            "Sugestão não reserva nem entrega; disponibilidade e acesso não verificados.",
            "Validação cadastral não comprova aptidão; requisitos avançados não implementados.",
            "Não somar capacidades pessoais/institucionais ou supor período da capacidade.",
            "Até 30 ofertas e 30 recursos por consulta; candidatos podem estar limitados.",
        ]
    )


class ContextoRecuperado(Entrada):
    dados: ContextoAnalise
    atividades_semanticas: list[BuscaVM]


def validar_proposta(contexto: ContextoAnalise, p: PropostaDemanda) -> None:
    def exigir(condicao: bool) -> None:
        if not condicao:
            raise ErroNegocio(
                502,
                "Recomendação inválida",
                "Saída contém IDs, relações ou quantidades não permitidos.",
            )

    pedidos = {i.id: i for i in contexto.demanda.itens if i.inativado_em is None}
    ofertas = {o.id: o for o in contexto.ofertas}
    recursos = {r.id: r for r in contexto.recursos}
    ids = [i.id_demanda_item for i in p.itens]
    exigir(len(ids) == len(set(ids)) and set(ids) == set(pedidos))
    for item in p.itens:
        d = pedidos[item.id_demanda_item]
        exigir(item.quantidade_sugerida <= d.quantidade_solicitada)
        exigir(len({x.id_pessoa for x in item.pessoas}) == len(item.pessoas))
        exigir(len({x.id_oferta_atividade for x in item.instituicoes}) == len(item.instituicoes))
        exigir(len({x.id_recurso for x in item.recursos}) == len(item.recursos))
        if d.id_atividade:
            exigir(item.quantidade_sugerida == 0)
        else:
            exigir(not item.pessoas and not item.instituicoes)
            exigir(
                sum((x.quantidade_sugerida for x in item.recursos), Decimal(0))
                == item.quantidade_sugerida
            )
        ofertas_escolhidas: set[UUID] = set()
        for pessoa in item.pessoas:
            o = ofertas.get(pessoa.id_oferta_atividade)
            exigir(
                o is not None
                and o.id_pessoa == pessoa.id_pessoa
                and o.id_atividade == d.id_atividade
            )
            ofertas_escolhidas.add(pessoa.id_oferta_atividade)
        for instituicao in item.instituicoes:
            o = ofertas.get(instituicao.id_oferta_atividade)
            exigir(
                o is not None
                and o.id_instituicao == instituicao.id_instituicao
                and o.id_atividade == d.id_atividade
            )
            ofertas_escolhidas.add(instituicao.id_oferta_atividade)
        for recurso in item.recursos:
            r = recursos.get(recurso.id_recurso)
            exigir(r is not None and recurso.quantidade_sugerida <= r.quantidade_total)
            assert r is not None
            if r.modo_controle == "individual":
                exigir(recurso.quantidade_sugerida == 1)
            if d.id_tipo_recurso:
                exigir(
                    r.id_tipo_recurso == d.id_tipo_recurso
                    and r.id_unidade_medida == d.id_unidade_medida
                )
            else:
                exigir(bool(set(r.ofertas) & ofertas_escolhidas))


class EstadoAtendimento(TypedDict):
    contexto: str
    proposta: PropostaDemanda | None


class AtualizacaoAtendimento(TypedDict, total=False):
    contexto: str
    proposta: PropostaDemanda


class GrafoAtendimento:
    def __init__(
        self,
        recuperar: Callable[[], str],
        cliente: ClienteInferencia,
        validar: Callable[[PropostaDemanda], None],
    ) -> None:
        self.recuperar_contexto: Callable[[], str] = recuperar
        self.cliente: ClienteInferencia = cliente
        self.validar_proposta: Callable[[PropostaDemanda], None] = validar
        g: StateGraph[EstadoAtendimento, None, EstadoAtendimento, EstadoAtendimento] = StateGraph(
            EstadoAtendimento
        )
        g.add_node("recuperar", self.recuperar)
        g.add_node("sugerir", self.sugerir)
        g.add_node("validar", self.validar)
        g.add_edge(START, "recuperar")
        g.add_edge("recuperar", "sugerir")
        g.add_edge("sugerir", "validar")
        g.add_edge("validar", END)
        self.compilado = g.compile()

    def recuperar(self, state: EstadoAtendimento) -> AtualizacaoAtendimento:
        return {"contexto": self.recuperar_contexto()}

    def sugerir(self, state: EstadoAtendimento) -> AtualizacaoAtendimento:
        return {"proposta": self.cliente.gerar(state["contexto"])}

    def validar(self, state: EstadoAtendimento) -> AtualizacaoAtendimento:
        assert state["proposta"] is not None
        self.validar_proposta(state["proposta"])
        return {"proposta": state["proposta"]}

    def executar(self) -> PropostaDemanda:
        entrada: EstadoAtendimento = {"contexto": "", "proposta": None}
        saida = cast(EstadoAtendimento, self.compilado.invoke(entrada))
        assert saida["proposta"] is not None
        return saida["proposta"]
