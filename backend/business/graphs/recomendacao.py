from typing import Protocol, TypedDict, cast

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from core.http.contratos import ErroNegocio
from core.ia import CandidatoAtividade, ContextoIA, PropostaIA


class RecuperadorAtividades(Protocol):
    def buscar(self, necessidade: str) -> list[CandidatoAtividade]: ...


class GeradorProposta(Protocol):
    def gerar(self, contexto: ContextoIA) -> PropostaIA: ...


class EstadoIA(TypedDict):
    necessidade: str
    candidatos: list[CandidatoAtividade]
    proposta: PropostaIA | None


class AtualizacaoIA(TypedDict, total=False):
    candidatos: list[CandidatoAtividade]
    proposta: PropostaIA


class GrafoRecomendacao:
    def __init__(self, recuperador: RecuperadorAtividades, gerador: GeradorProposta) -> None:
        self.recuperador: RecuperadorAtividades = recuperador
        self.gerador: GeradorProposta = gerador
        grafo: StateGraph[EstadoIA, None, EstadoIA, EstadoIA] = StateGraph(EstadoIA)
        grafo.add_node("recuperar", self.recuperar)
        grafo.add_node("sugerir", self.sugerir)
        grafo.add_node("validar", self.validar)
        grafo.add_edge(START, "recuperar")
        grafo.add_edge("recuperar", "sugerir")
        grafo.add_edge("sugerir", "validar")
        grafo.add_edge("validar", END)
        self.compilado: CompiledStateGraph[EstadoIA, None, EstadoIA, EstadoIA] = grafo.compile()

    def recuperar(self, state: EstadoIA) -> AtualizacaoIA:
        return {"candidatos": self.recuperador.buscar(state["necessidade"])}

    def sugerir(self, state: EstadoIA) -> AtualizacaoIA:
        if not state["candidatos"]:
            return {
                "proposta": PropostaIA(
                    itens=[], pendencias=["Nenhuma atividade candidata encontrada."]
                )
            }
        return {
            "proposta": self.gerador.gerar(
                ContextoIA(
                    necessidade=state["necessidade"],
                    candidatos=state["candidatos"],
                )
            )
        }

    def validar(self, state: EstadoIA) -> AtualizacaoIA:
        proposta: PropostaIA | None = state["proposta"]
        if proposta is None:
            raise ErroNegocio(502, "Proposta ausente", "O modelo não produziu saída válida.")
        permitidos = {c.id_atividade for c in state["candidatos"]}
        escolhidos = [i.id_atividade for i in proposta.itens]
        if not set(escolhidos) <= permitidos or len(escolhidos) != len(set(escolhidos)):
            raise ErroNegocio(
                502, "Proposta inválida", "A saída contém candidatos inexistentes ou repetidos."
            )
        return {"proposta": proposta}

    def executar(self, necessidade: str) -> PropostaIA:
        if not necessidade.strip() or len(necessidade) > 4000:
            raise ErroNegocio(
                422, "Necessidade inválida", "Informe uma necessidade com até 4000 caracteres."
            )
        entrada: EstadoIA = {"necessidade": necessidade, "candidatos": [], "proposta": None}
        # Fronteira de biblioteca: domínio e estados permanecem explicitamente tipados.
        saida: EstadoIA = cast(EstadoIA, self.compilado.invoke(entrada))
        proposta: PropostaIA | None = saida["proposta"]
        if proposta is None:
            raise ErroNegocio(502, "Proposta ausente", "O modelo não produziu saída válida.")
        return proposta
