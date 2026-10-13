from uuid import UUID

import pytest

from business.graphs.recomendacao import GrafoRecomendacao
from core.http.contratos import ErroNegocio
from core.ia import CandidatoAtividade, ContextoIA, ItemPropostaIA, PropostaIA


class RecuperadorTeste:
    def __init__(self, vazio: bool = False) -> None:
        self.vazio: bool = vazio

    def buscar(self, necessidade: str) -> list[CandidatoAtividade]:
        return (
            []
            if self.vazio
            else [
                CandidatoAtividade(
                    id_atividade=UUID(int=1), nome="Transporte", descricao="Levar itens"
                )
            ]
        )


class GeradorTeste:
    def __init__(self, inventar: bool = False) -> None:
        self.inventar: bool = inventar
        self.chamadas: int = 0

    def gerar(self, contexto: ContextoIA) -> PropostaIA:
        self.chamadas += 1
        identificador: UUID = (
            UUID(int=999) if self.inventar else contexto.candidatos[0].id_atividade
        )
        return PropostaIA(
            itens=[
                ItemPropostaIA(id_atividade=identificador, justificativa="Candidato pertinente")
            ],
            pendencias=["Disponibilidade a confirmar"],
        )


def test_grafo_percorre_nos_e_preserva_ids() -> None:
    gerador: GeradorTeste = GeradorTeste()
    proposta: PropostaIA = GrafoRecomendacao(RecuperadorTeste(), gerador).executar("Levar água")
    assert proposta.itens[0].id_atividade == UUID(int=1)
    assert gerador.chamadas == 1 and proposta.pendencias


def test_grafo_rejeita_id_inventado() -> None:
    with pytest.raises(ErroNegocio, match="inexistentes"):
        GrafoRecomendacao(RecuperadorTeste(), GeradorTeste(inventar=True)).executar("Levar água")


def test_sem_candidatos_nao_chama_modelo() -> None:
    gerador: GeradorTeste = GeradorTeste()
    proposta: PropostaIA = GrafoRecomendacao(RecuperadorTeste(vazio=True), gerador).executar(
        "Levar água"
    )
    assert proposta.itens == [] and proposta.pendencias and gerador.chamadas == 0
