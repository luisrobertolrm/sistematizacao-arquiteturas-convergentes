"""Executa regras e fluxo D009 em memória; IA e embeddings são artificiais.

Uso: python simulacoes/escopo_inicial/simular_desastre.py [--salvar]
Sem --salvar, imprime o relatório. Com --salvar, grava artefatos nesta pasta.
"""

from __future__ import annotations

import json
import math
import platform
import sys
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from hashlib import sha256
from io import TextIOWrapper
from pathlib import Path
from typing import TypedDict
from uuid import UUID

from cenario import criar_cenario, uid
from modelos import (
    AdministradorSimulado, Atividade, Cenario, DecisaoSimulada, Demanda,
    DemandaItem, DesastreTipo, Finalidade, IndiceAtividade, ModeloIA,
    Recomendacao, RecomendacaoInstituicao, RecomendacaoItem, RecomendacaoPessoa,
    RecomendacaoRecurso, Recurso, SituacaoRecomendacao, Sugestao, Validacao,
)


class ErroValidacao(ValueError):
    """Rejeição esperada de uma entrada do exercício."""


def exigir(condicao: bool, mensagem: str) -> None:
    if not condicao:
        raise ErroValidacao(mensagem)


def exclusivo(primeiro: UUID | None, segundo: UUID | None) -> bool:
    return (primeiro is None) != (segundo is None)


def validar_classificacoes(c: Cenario, itens: tuple[DesastreTipo, ...]) -> None:
    exigir(bool(itens), "Classificação ausente")
    exigir(sum(i.principal for i in itens) == 1, "Exatamente um tipo principal")
    exigir(len({i.id_tipo_desastre for i in itens}) == len(itens), "Tipo duplicado")
    for i in itens:
        exigir(i.id_desastre == c.desastre.id, "FK desastre inválida")
        exigir(i.id_tipo_desastre in c.tipos_desastre, "FK tipo de desastre inválida")


def validar_modelos(c: Cenario) -> None:
    for finalidade in Finalidade:
        exigir(sum(m.ativo and m.finalidade == finalidade for m in c.modelos.values()) <= 1,
               "Mais de um modelo ativo por finalidade")
    for m in c.modelos.values():
        exigir(m.id_conexao in c.conexoes, "FK conexão inválida")
        if m.finalidade == Finalidade.EMBEDDING:
            exigir(m.dimensao is not None and m.dimensao > 0, "Dimensão de embedding inválida")
        else:
            exigir(m.dimensao is None, "Modelo de texto deve ter dimensão nula")


def selecionar_modelo(c: Cenario, finalidade: Finalidade) -> ModeloIA:
    validar_modelos(c)
    selecionados: list[ModeloIA] = [m for m in c.modelos.values() if m.ativo and m.finalidade == finalidade]
    exigir(len(selecionados) == 1, "Modelo ativo ausente")
    return selecionados[0]


def validar_demanda(c: Cenario, d: Demanda, itens: tuple[DemandaItem, ...]) -> None:
    exigir(d.id_area_afetada in c.areas_afetadas, "FK área inválida")
    exigir(d.id_pessoa_solicitante in c.pessoas, "FK solicitante inválida")
    exigir(d.inicio_previsto_em.utcoffset() is not None and d.prazo_em.utcoffset() is not None,
           "Datas devem ter fuso")
    exigir(d.prazo_em >= d.inicio_previsto_em, "Prazo anterior ao início")
    exigir(bool(itens), "Demanda sem itens")
    exigir(len({i.id for i in itens}) == len(itens), "Item duplicado")
    for i in itens:
        exigir(i.id_demanda == d.id, "Item pertence a outra demanda")
        exigir(exclusivo(i.id_atividade, i.id_tipo_recurso), "Item deve pedir atividade ou recurso")
        exigir(i.quantidade_solicitada.is_finite() and i.quantidade_solicitada > 0, "Quantidade inválida")
        exigir(i.id_unidade_medida in c.unidades_medida, "FK unidade inválida")
        if i.id_atividade is not None:
            exigir(i.id_atividade in c.atividades, "FK atividade inválida")
            exigir(i.id_unidade_medida == c.atividades[i.id_atividade].id_unidade_capacidade,
                   "Unidade incompatível")
        if i.id_tipo_recurso is not None:
            exigir(i.id_tipo_recurso in c.tipos_recurso, "FK tipo de recurso inválida")
            exigir(i.id_unidade_medida == c.tipos_recurso[i.id_tipo_recurso].id_unidade_medida,
                   "Unidade incompatível")


def validar_cadastros(c: Cenario) -> None:
    exigir(c.desastre.id_instituicao_coordenadora in c.instituicoes, "FK coordenadora inválida")
    validar_classificacoes(c, c.desastre_tipo)
    validar_modelos(c)
    for v in c.pessoa_instituicao:
        exigir(v.pessoa_id in c.pessoas and v.instituicao_id in c.instituicoes, "FK vínculo inválida")
    for p in c.pessoa_profissao:
        exigir(p.pessoa_id in c.pessoas and p.profissao_id in c.profissoes, "FK profissão inválida")
    for f in c.pessoa_curso:
        exigir(f.pessoa_id in c.pessoas and f.curso_id in c.cursos, "FK curso inválida")
    for a in c.atividades.values():
        exigir(a.categoria_id in c.categorias_atividade, "FK categoria inválida")
        exigir(a.id_unidade_capacidade in c.unidades_medida, "FK unidade de capacidade inválida")
    for termo in c.atividade_termos:
        exigir(termo.atividade_id in c.atividades and bool(termo.termo.strip()), "Termo inválido")
    for t in c.tipos_recurso.values():
        exigir(t.id_unidade_medida in c.unidades_medida, "FK unidade do recurso inválida")
    for r in c.recursos.values():
        exigir(r.tipo_recurso_id in c.tipos_recurso, "FK tipo de recurso inválida")
        exigir(exclusivo(r.pessoa_id, r.instituicao_id), "Responsável deve ser exclusivo")
        exigir(r.pessoa_id is None or r.pessoa_id in c.pessoas, "FK responsável pessoal inválida")
        exigir(r.instituicao_id is None or r.instituicao_id in c.instituicoes, "FK responsável institucional inválida")
        exigir(r.quantidade_total.is_finite() and r.quantidade_total >= 0, "Quantidade do recurso inválida")
        if c.tipos_recurso[r.tipo_recurso_id].modo_controle == "individual":
            exigir(r.quantidade_total == 1, "Bem individual deve ter quantidade um")
    for o in c.ofertas_atividade.values():
        exigir(o.atividade_id in c.atividades, "FK atividade da oferta inválida")
        exigir(exclusivo(o.pessoa_id, o.instituicao_id), "Ofertante deve ser exclusivo")
        exigir(o.pessoa_id is None or o.pessoa_id in c.pessoas, "FK ofertante pessoal inválida")
        exigir(o.instituicao_id is None or o.instituicao_id in c.instituicoes, "FK ofertante institucional inválida")
        exigir(o.capacidade_declarada.is_finite() and o.capacidade_declarada > 0, "Capacidade inválida")
    for v in c.oferta_atividade_recurso:
        exigir(v.oferta_atividade_id in c.ofertas_atividade and v.recurso_id in c.recursos, "FK oferta/recurso inválida")
        exigir(v.quantidade_prevista > 0, "Quantidade prevista inválida")
    exigir(len({(v.oferta_atividade_id, v.recurso_id) for v in c.oferta_atividade_recurso}) == len(c.oferta_atividade_recurso),
           "Associação oferta/recurso duplicada")
    for area in c.areas_afetadas.values():
        exigir(area.id_desastre == c.desastre.id, "FK desastre da área inválida")
        exigir(len(area.geometria) >= 4 and area.geometria[0] == area.geometria[-1], "Anel não fechado")
        exigir(all(-180 <= p.longitude <= 180 and -90 <= p.latitude <= 90 for p in area.geometria),
               "Coordenada fora do intervalo")
    for d in c.demandas.values():
        validar_demanda(c, d, tuple(i for i in c.demanda_itens.values() if i.id_demanda == d.id))
    exigir(all(i.id_demanda in c.demandas for i in c.demanda_itens.values()), "FK demanda inválida")
    exigir(len({(i.id_atividade, i.id_modelo) for i in c.indices}) == len(c.indices), "Índice duplicado")
    for i in c.indices:
        exigir(i.id_atividade in c.atividades and i.id_modelo in c.modelos, "FK índice inválida")
        exigir(indice_compativel(c.atividades[i.id_atividade], i, c.modelos[i.id_modelo]), "Índice incompatível")


def indice_compativel(a: Atividade, i: IndiceAtividade, m: ModeloIA) -> bool:
    return (
        m.finalidade == Finalidade.EMBEDDING and i.id_modelo == m.id
        and i.id_atividade == a.id and i.situacao_indexacao == "pronta"
        and i.hash_atividade_origem == a.hash_conteudo_semantico
        and i.embedding is not None and len(i.embedding) == m.dimensao
        and all(math.isfinite(v) for v in i.embedding)
        and any(v != 0 for v in i.embedding)
    )


def recuperar_atividade(c: Cenario, modelo: ModeloIA, consulta: tuple[float, ...]) -> UUID:
    exigir(modelo.finalidade == Finalidade.EMBEDDING, "Consulta exige modelo de embedding")
    exigir(len(consulta) == modelo.dimensao and all(math.isfinite(v) for v in consulta), "Consulta de dimensão inválida")
    norma: float = math.sqrt(sum(v * v for v in consulta))
    exigir(norma > 0, "Consulta com vetor nulo")
    pontuacoes: list[tuple[float, UUID]] = []
    for i in c.indices:
        if not indice_compativel(c.atividades[i.id_atividade], i, modelo) or i.embedding is None:
            continue
        norma_indice: float = math.sqrt(sum(v * v for v in i.embedding))
        similaridade: float = sum(a * b for a, b in zip(consulta, i.embedding, strict=True)) / (norma * norma_indice)
        pontuacoes.append((similaridade, i.id_atividade))
    exigir(bool(pontuacoes), "Nenhum índice atual para o modelo")
    pontuacoes.sort(key=lambda par: (-par[0], str(par[1])))
    exigir(pontuacoes[0][0] > 0, "Sem candidato na consulta artificial")
    return pontuacoes[0][1]


def candidatos_curso_demo(c: Cenario) -> tuple[UUID, ...]:
    # Critério fornecido manualmente pelo cenário; não é requisito cadastrado.
    return tuple(f.pessoa_id for f in c.pessoa_curso
                 if f.curso_id == c.id_curso_filtro_demo and f.situacao_validacao == Validacao.VALIDADA
                 and f.conclusao_em <= c.instante.date()
                 and (f.validade_em is None or f.validade_em >= c.instante.date())
                 and c.pessoas[f.pessoa_id].situacao_cadastral == Validacao.VALIDADA)


def gerar_sugestao_simulada(c: Cenario, id_demanda: UUID, numero: int) -> Sugestao:
    """Adaptador determinístico: nenhuma chamada de LLM ou LangGraph é feita."""
    embedding: ModeloIA = selecionar_modelo(c, Finalidade.EMBEDDING)
    texto: ModeloIA = selecionar_modelo(c, Finalidade.TEXTO)
    d: Demanda = c.demandas[id_demanda]
    municipio: str = c.areas_afetadas[d.id_area_afetada].municipio_codigo_ibge
    id_rec: UUID = uid(numero)
    itens: list[RecomendacaoItem] = []
    pessoas: list[RecomendacaoPessoa] = []
    instituicoes: list[RecomendacaoInstituicao] = []
    recursos: list[RecomendacaoRecurso] = []
    pendencias: list[str] = [
        "Sugestão simulada; disponibilidade, autorização de uso e acesso não verificados.",
        "Sugestões independentes podem usar o mesmo bem/estoque; aprovação não reserva.",
    ]
    for posicao, item in enumerate(i for i in c.demanda_itens.values() if i.id_demanda == d.id):
        id_item: UUID = uid(numero * 10 + posicao)
        quantidade: Decimal = Decimal(0)
        if item.id_atividade is not None:
            consulta: tuple[float, ...] = (1.0, 0.0, 0.0) if item.id_atividade == uid(70) else (0.0, 1.0, 0.0)
            recuperada: UUID = recuperar_atividade(c, embedding, consulta)
            exigir(recuperada == item.id_atividade, "Consulta artificial recuperou outra atividade")
            for o in c.ofertas_atividade.values():
                if o.atividade_id != recuperada or o.situacao_validacao != Validacao.VALIDADA or o.municipio_atendimento_codigo_ibge != municipio:
                    continue
                if o.instituicao_id is not None:
                    instituicoes.append(RecomendacaoInstituicao(id_item, o.instituicao_id, o.id))
                if o.pessoa_id is not None:
                    pessoas.append(RecomendacaoPessoa(id_item, o.pessoa_id, o.id, "Candidata; capacidade a confirmar"))
                if item.id_atividade == uid(70):
                    for p in candidatos_curso_demo(c):
                        pessoas.append(RecomendacaoPessoa(id_item, p, o.id, "Candidato por filtro manual; aptidão pendente"))
                    for v in c.oferta_atividade_recurso:
                        if v.oferta_atividade_id == o.id:
                            recursos.append(RecomendacaoRecurso(id_item, v.recurso_id, v.quantidade_prevista))
                    quantidade = Decimal(1)  # Uma viagem sugerida, sem comprovar execução.
            if item.id_atividade == uid(71):
                pendencias.append("Refeições: não somar cozinha 80 e Paula 40; composição e período-base pendentes. Cobertura quantitativa não validada.")
        elif item.id_tipo_recurso == uid(52):
            pendencias.append("Energia: gerador cadastrado descreve 2 kVA e pedido exige 5 kVA; não sugerido como compatível. Comparação estruturada pendente.")
        else:
            restantes: Decimal = item.quantidade_solicitada
            for r in c.recursos.values():
                if r.tipo_recurso_id == item.id_tipo_recurso and r.estado_operacional == "operacional" and r.municipio_codigo_ibge == municipio:
                    sugerida: Decimal = min(restantes, r.quantidade_total)
                    if sugerida > 0:
                        recursos.append(RecomendacaoRecurso(id_item, r.id, sugerida))
                        quantidade += sugerida
                        restantes -= sugerida
            pendencias.append("Água: total dos pedidos é 400 L para um lote de 300 L; há déficit global de 100 L. Sugestões por demanda não formam um plano reservado.")
        itens.append(RecomendacaoItem(id_item, id_rec, item.id, quantidade))
    justificativa: str = "Consulta aos cadastros fictícios e filtros do exercício. " + " ".join(pendencias)
    return Sugestao(
        Recomendacao(id_rec, d.id, embedding.id, texto.id, c.instante, justificativa, SituacaoRecomendacao.GERADA),
        tuple(itens), tuple(pessoas), tuple(instituicoes), tuple(recursos), tuple(pendencias),
    )


def validar_sugestao(c: Cenario, s: Sugestao) -> None:
    h: Recomendacao = s.cabecalho
    exigir(h.id_demanda in c.demandas, "FK demanda da recomendação inválida")
    exigir(h.id_modelo_embedding in c.modelos and h.id_modelo_inferencia in c.modelos, "FK modelo da recomendação inválida")
    exigir(c.modelos[h.id_modelo_embedding].finalidade == Finalidade.EMBEDDING
           and c.modelos[h.id_modelo_inferencia].finalidade == Finalidade.TEXTO, "Finalidade dos modelos inválida")
    exigir(bool(h.justificativa.strip()) and h.gerada_em.utcoffset() is not None, "Justificativa/data inválida")
    exigir(bool(s.itens) and len({i.id for i in s.itens}) == len(s.itens), "Itens da sugestão inválidos")
    itens: dict[UUID, RecomendacaoItem] = {i.id: i for i in s.itens}
    for i in s.itens:
        exigir(i.id_recomendacao == h.id, "Item pertence a outra recomendação")
        exigir(i.id_demanda_item in c.demanda_itens, "FK item de demanda inválida")
        pedido: DemandaItem = c.demanda_itens[i.id_demanda_item]
        exigir(pedido.id_demanda == h.id_demanda, "Item pertence a outra demanda")
        exigir(i.quantidade_sugerida.is_finite() and 0 <= i.quantidade_sugerida <= pedido.quantidade_solicitada,
               "Quantidade sugerida inválida")
    for p in s.pessoas:
        exigir(p.id_recomendacao_item in itens, "FK item da pessoa inválida")
        exigir(p.id_pessoa in c.pessoas, "Pessoa sugerida inexistente")
        exigir(c.pessoas[p.id_pessoa].situacao_cadastral == Validacao.VALIDADA, "Pessoa não validada")
        if p.id_oferta_atividade is not None:
            exigir(p.id_oferta_atividade in c.ofertas_atividade, "FK oferta da pessoa inválida")
            o = c.ofertas_atividade[p.id_oferta_atividade]
            pedido = c.demanda_itens[itens[p.id_recomendacao_item].id_demanda_item]
            exigir(o.atividade_id == pedido.id_atividade and o.situacao_validacao == Validacao.VALIDADA, "Oferta da pessoa incompatível")
            pertence: bool = o.pessoa_id == p.id_pessoa or any(
                v.pessoa_id == p.id_pessoa and v.instituicao_id == o.instituicao_id
                and v.situacao_validacao == Validacao.VALIDADA and v.inicio_em <= c.instante.date()
                and (v.fim_em is None or v.fim_em >= c.instante.date()) for v in c.pessoa_instituicao
            )
            exigir(pertence, "Pessoa sem vínculo com a oferta")
    for i in s.instituicoes:
        exigir(i.id_recomendacao_item in itens, "FK item da instituição inválida")
        exigir(i.id_instituicao in c.instituicoes and i.id_oferta_atividade in c.ofertas_atividade, "Instituição/oferta inexistente")
        o = c.ofertas_atividade[i.id_oferta_atividade]
        pedido = c.demanda_itens[itens[i.id_recomendacao_item].id_demanda_item]
        exigir(o.instituicao_id == i.id_instituicao, "Instituição não é dona da oferta")
        exigir(o.atividade_id == pedido.id_atividade and o.situacao_validacao == Validacao.VALIDADA, "Oferta institucional incompatível")
        exigir(c.instituicoes[i.id_instituicao].situacao_cadastral == Validacao.VALIDADA, "Instituição não validada")
    for r in s.recursos:
        exigir(r.id_recomendacao_item in itens, "FK item do recurso inválida")
        exigir(r.id_recurso in c.recursos, "Recurso sugerido inexistente")
        concreto = c.recursos[r.id_recurso]
        exigir(r.quantidade_sugerida.is_finite() and 0 < r.quantidade_sugerida <= concreto.quantidade_total,
               "Quantidade de recurso sugerida inválida")
        exigir(concreto.estado_operacional == "operacional", "Recurso não operacional")
        pedido = c.demanda_itens[itens[r.id_recomendacao_item].id_demanda_item]
        if pedido.id_tipo_recurso is not None:
            exigir(concreto.tipo_recurso_id == pedido.id_tipo_recurso, "Recurso de outro tipo")
        else:
            exigir(any(v.recurso_id == r.id_recurso and c.ofertas_atividade[v.oferta_atividade_id].atividade_id == pedido.id_atividade
                       for v in c.oferta_atividade_recurso), "Recurso sem oferta da atividade")


@dataclass(slots=True)
class Memoria:
    sugestoes: dict[UUID, Sugestao] = field(default_factory=dict)
    decisoes: list[DecisaoSimulada] = field(default_factory=list)

    def adicionar(self, c: Cenario, s: Sugestao) -> None:
        validar_sugestao(c, s)
        exigir(s.cabecalho.id not in self.sugestoes, "Recomendação já registrada")
        self.sugestoes[s.cabecalho.id] = s

    def decidir(self, id_rec: UUID, admin: AdministradorSimulado, situacao: SituacaoRecomendacao,
                momento: datetime, motivo: str) -> None:
        exigir(admin.autorizado, "Administrador não autorizado")
        exigir(id_rec in self.sugestoes, "Recomendação inexistente")
        s: Sugestao = self.sugestoes[id_rec]
        exigir(s.cabecalho.situacao == SituacaoRecomendacao.GERADA, "Recomendação já decidida")
        exigir(situacao in (SituacaoRecomendacao.APROVADA, SituacaoRecomendacao.REJEITADA), "Decisão inválida")
        exigir(momento.utcoffset() is not None and momento >= s.cabecalho.gerada_em, "Data da decisão inválida")
        exigir(bool(motivo.strip()), "Motivo ausente")
        self.sugestoes[id_rec] = replace(s, cabecalho=replace(s.cabecalho, situacao=situacao))
        self.decisoes.append(DecisaoSimulada(id_rec, admin.identificador, situacao, momento, motivo))


class VerificacaoJSON(TypedDict):
    cenario: str
    natureza: str
    resultado: str
    evidencia: str


class ItemJSON(TypedDict):
    id: str
    id_demanda_item: str
    quantidade_sugerida: str


class PessoaJSON(TypedDict):
    id_recomendacao_item: str
    id_pessoa: str
    id_oferta_atividade: str | None
    papel_sugerido: str


class InstituicaoJSON(TypedDict):
    id_recomendacao_item: str
    id_instituicao: str
    id_oferta_atividade: str


class RecursoJSON(TypedDict):
    id_recomendacao_item: str
    id_recurso: str
    quantidade_sugerida: str


class SugestaoJSON(TypedDict):
    id: str
    id_demanda: str
    id_modelo_embedding: str
    id_modelo_inferencia: str
    gerada_em: str
    situacao: str
    justificativa: str
    itens: list[ItemJSON]
    pessoas: list[PessoaJSON]
    instituicoes: list[InstituicaoJSON]
    recursos: list[RecursoJSON]
    pendencias: list[str]


class DecisaoJSON(TypedDict):
    id_recomendacao: str
    administrador: str
    situacao: str
    decidida_em: str
    motivo: str


class RelatorioJSON(TypedDict):
    versao_cenario: str
    executado_em_utc: str
    python: str
    fontes_sha256: dict[str, str]
    contagens: dict[str, int]
    verificacoes: list[VerificacaoJSON]
    recomendacoes: list[SugestaoJSON]
    decisoes: list[DecisaoJSON]


def checar(saida: list[VerificacaoJSON], nome: str, acao: Callable[[], object], evidencia: str,
           rejeicao: str | None = None) -> None:
    natureza: str = "Rejeição de entrada" if rejeicao else "Regra/fluxo"
    try:
        acao()
        if rejeicao:
            raise AssertionError(f"Entrada inválida foi aceita: {rejeicao}")
    except ErroValidacao as erro:
        if rejeicao and rejeicao in str(erro):
            saida.append({"cenario": nome, "natureza": natureza, "resultado": "OK", "evidencia": str(erro)})
            return
        saida.append({"cenario": nome, "natureza": natureza, "resultado": "FALHA", "evidencia": str(erro)})
        return
    except Exception as erro:
        saida.append({"cenario": nome, "natureza": natureza, "resultado": "FALHA", "evidencia": f"{type(erro).__name__}: {erro}"})
        return
    saida.append({"cenario": nome, "natureza": natureza, "resultado": "OK", "evidencia": evidencia})


def serializar_sugestao(s: Sugestao) -> SugestaoJSON:
    return {
        "id": str(s.cabecalho.id), "id_demanda": str(s.cabecalho.id_demanda),
        "id_modelo_embedding": str(s.cabecalho.id_modelo_embedding),
        "id_modelo_inferencia": str(s.cabecalho.id_modelo_inferencia),
        "gerada_em": s.cabecalho.gerada_em.isoformat(), "situacao": s.cabecalho.situacao.value,
        "justificativa": s.cabecalho.justificativa,
        "itens": [{"id": str(i.id), "id_demanda_item": str(i.id_demanda_item), "quantidade_sugerida": str(i.quantidade_sugerida)} for i in s.itens],
        "pessoas": [{"id_recomendacao_item": str(p.id_recomendacao_item), "id_pessoa": str(p.id_pessoa),
                     "id_oferta_atividade": str(p.id_oferta_atividade) if p.id_oferta_atividade else None,
                     "papel_sugerido": p.papel_sugerido} for p in s.pessoas],
        "instituicoes": [{"id_recomendacao_item": str(i.id_recomendacao_item), "id_instituicao": str(i.id_instituicao),
                          "id_oferta_atividade": str(i.id_oferta_atividade)} for i in s.instituicoes],
        "recursos": [{"id_recomendacao_item": str(r.id_recomendacao_item), "id_recurso": str(r.id_recurso),
                      "quantidade_sugerida": str(r.quantidade_sugerida)} for r in s.recursos],
        "pendencias": list(s.pendencias),
    }


def executar() -> RelatorioJSON:
    c: Cenario = criar_cenario()
    v: list[VerificacaoJSON] = []
    memoria: Memoria = Memoria()
    checar(v, "Cadastros e relações do cenário", lambda: validar_cadastros(c), "Relações verificadas em memória, incluindo qualificações, ofertas, unidades e modelos; não é teste de FKs SQL.")
    checar(v, "Município e três áreas", lambda: exigir(len(c.areas_afetadas) == 3 and len({a.municipio_codigo_ibge for a in c.areas_afetadas.values()}) == 1
                                                      and len({a.geometria for a in c.areas_afetadas.values()}) == 3, "Território inesperado"), "Três polígonos ilustrativos distintos em um município fictício; sem mapa ou análise espacial.")
    for nome, itens, mensagem in (
        ("Sem classificação", (), "Classificação ausente"),
        ("Sem tipo principal", tuple(replace(i, principal=False) for i in c.desastre_tipo), "Exatamente um"),
        ("Dois tipos principais", tuple(replace(i, principal=True) for i in c.desastre_tipo), "Exatamente um"),
        ("Tipo duplicado", c.desastre_tipo + (c.desastre_tipo[1],), "Tipo duplicado"),
        ("Tipo inexistente", (DesastreTipo(c.desastre.id, uid(999), True),), "FK tipo"),
    ):
        checar(v, nome, lambda itens=itens: validar_classificacoes(c, itens), "", mensagem)
    d: Demanda = c.demandas[uid(200)]
    item: DemandaItem = c.demanda_itens[uid(210)]
    checar(v, "Demanda com itens mistos", lambda: validar_demanda(c, d, (item, c.demanda_itens[uid(211)])), "Pedido contém uma viagem e 200 litros, cada item com uma referência exclusiva e unidade por FK.")
    checar(v, "Prioridade independente da gravidade", lambda: exigir(c.demandas[uid(202)].prioridade == "urgente"
           and c.areas_afetadas[uid(21)].gravidade == "moderada", "Prioridade indevida"), "Área moderada pode ter pedido urgente; escalas são convenções fictícias.")
    for nome, invalido, mensagem in (
        ("Item com atividade e recurso", replace(item, id_tipo_recurso=uid(50)), "atividade ou recurso"),
        ("Item sem objeto", replace(item, id_atividade=None), "atividade ou recurso"),
        ("Atividade inexistente", replace(item, id_atividade=uid(999)), "FK atividade"),
        ("Quantidade zero", replace(item, quantidade_solicitada=Decimal(0)), "Quantidade inválida"),
        ("Quantidade negativa", replace(item, quantidade_solicitada=Decimal(-1)), "Quantidade inválida"),
        ("Unidade incompatível", replace(item, id_unidade_medida=uid(101)), "Unidade incompatível"),
        ("Item de outra demanda", replace(item, id_demanda=uid(201)), "outra demanda"),
    ):
        checar(v, nome, lambda invalido=invalido: validar_demanda(c, d, (invalido,)), "", mensagem)
    checar(v, "Demanda sem itens", lambda: validar_demanda(c, d, ()), "", "sem itens")
    checar(v, "Prazo inválido", lambda: validar_demanda(c, replace(d, prazo_em=d.inicio_previsto_em - timedelta(minutes=1)), (item,)), "", "Prazo anterior")
    checar(v, "Solicitante inexistente", lambda: validar_demanda(c, replace(d, id_pessoa_solicitante=uid(999)), (item,)), "", "FK solicitante")
    checar(v, "Responsável ambíguo", lambda: validar_cadastros(replace(c, recursos={**c.recursos, uid(60): replace(c.recursos[uid(60)], pessoa_id=uid(30))})), "", "Responsável deve ser exclusivo")
    checar(v, "Ofertante ambíguo", lambda: validar_cadastros(replace(c, ofertas_atividade={**c.ofertas_atividade, uid(80): replace(c.ofertas_atividade[uid(80)], pessoa_id=uid(30))})), "", "Ofertante deve ser exclusivo")
    checar(v, "Filtro demonstrativo de formação", lambda: exigir(candidatos_curso_demo(c) == (uid(30),), "Filtro incorreto"), "João passa; Carlos tem curso vencido e Marta tem curso pendente. Requisito foi fornecido manualmente e não comprova aptidão.")
    modelo: ModeloIA = selecionar_modelo(c, Finalidade.EMBEDDING)
    indice: IndiceAtividade = c.indices[0]
    atividade: Atividade = c.atividades[uid(70)]
    checar(v, "Recuperação artificial", lambda: exigir(recuperar_atividade(c, modelo, (1.0, 0.0, 0.0)) == atividade.id, "Recuperação incorreta"), "Cosseno de vetores artificiais recupera transporte; qualidade semântica não avaliada.")
    checar(v, "Hash obsoleto", lambda: exigir(not indice_compativel(replace(atividade, descricao="Conteúdo alterado"), indice, modelo), "Índice obsoleto aceito"), "Alteração de conteúdo exclui a representação antiga; atomicidade no banco não foi exercitada.")
    checar(v, "Dimensão errada", lambda: exigir(not indice_compativel(atividade, replace(indice, embedding=(1.0, 0.0)), modelo), "Dimensão errada aceita"), "Vetor incompatível rejeitado.")
    checar(v, "Modelo diferente com mesma dimensão", lambda: exigir(not indice_compativel(atividade, indice, replace(modelo, id=uid(999))), "Mistura de modelos aceita"), "Dimensão igual não permite comparar modelos diferentes.")
    checar(v, "Modelo de texto no índice", lambda: exigir(not indice_compativel(atividade, indice, c.modelos[uid(91)]), "Texto aceito no índice"), "Finalidade de inferência não serve ao índice de embeddings.")
    checar(v, "Consulta de dimensão errada", lambda: recuperar_atividade(c, modelo, (1.0, 0.0)), "", "Consulta de dimensão")
    checar(v, "Mais de um modelo ativo", lambda: validar_modelos(replace(c, modelos={**c.modelos, uid(92): replace(c.modelos[uid(92)], ativo=True)})), "", "Mais de um modelo ativo")
    checar(v, "Ausência de modelo ativo", lambda: selecionar_modelo(replace(c, modelos={**c.modelos, uid(90): replace(modelo, ativo=False)}), Finalidade.EMBEDDING), "", "Modelo ativo ausente")
    checar(v, "Dimensões distintas armazenadas", lambda: exigir(indice_compativel(atividade, c.indices[2], c.modelos[uid(92)])
           and not indice_compativel(atividade, c.indices[2], modelo), "Índice de outro modelo aceito"), "Fixtures de 3 e 4 dimensões coexistem, com comparação limitada ao modelo; pgvector não foi usado.")
    checar(v, "Cobertura incompleta do modelo futuro", lambda: exigir({i.id_atividade for i in c.indices if i.id_modelo == uid(92)} != set(c.atividades), "Fixture de cobertura incorreta"), "Modelo de 4 dimensões cobre só transporte. Falta preparar refeições; critério formal de cobertura continua pendente.")
    sugestoes: tuple[Sugestao, ...] = tuple(gerar_sugestao_simulada(c, id_demanda, n) for n, id_demanda in enumerate(c.demandas, 300))
    for s in sugestoes:
        checar(v, f"Sugestão para {c.demandas[s.cabecalho.id_demanda].titulo}", lambda s=s: memoria.adicionar(c, s), "Itens, pessoas, instituições/ofertas, recursos e modelos referenciam registros reais do cenário.")
    primeira: Sugestao = sugestoes[0]
    for nome, invalida, mensagem in (
        ("Pessoa inventada", replace(primeira, pessoas=(replace(primeira.pessoas[0], id_pessoa=uid(999)),)), "Pessoa sugerida inexistente"),
        ("Instituição de outra oferta", replace(primeira, instituicoes=(replace(primeira.instituicoes[0], id_instituicao=uid(2)),)), "não é dona da oferta"),
        ("Recurso inventado", replace(primeira, recursos=(replace(primeira.recursos[0], id_recurso=uid(999)),)), "Recurso sugerido inexistente"),
        ("Item de pedido diferente", replace(primeira, itens=(replace(primeira.itens[0], id_demanda_item=uid(212)),)), "outra demanda"),
        ("Quantidade sugerida excessiva", replace(primeira, itens=(replace(primeira.itens[0], quantidade_sugerida=Decimal(99)),)), "Quantidade sugerida inválida"),
        ("Modelos trocados na recomendação", replace(primeira, cabecalho=replace(primeira.cabecalho, id_modelo_embedding=uid(91))), "Finalidade dos modelos"),
    ):
        checar(v, nome, lambda invalida=invalida: validar_sugestao(c, invalida), "", mensagem)
    checar(v, "Registro repetido", lambda: memoria.adicionar(c, primeira), "", "já registrada")
    antes_recursos: dict[UUID, Recurso] = c.recursos.copy()
    antes_demandas: dict[UUID, Demanda] = c.demandas.copy()
    antes_itens: dict[UUID, DemandaItem] = c.demanda_itens.copy()
    admin: AdministradorSimulado = AdministradorSimulado("admin-ficticio", True)
    momento: datetime = c.instante + timedelta(minutes=5)
    checar(v, "Aprovação administrativa", lambda: memoria.decidir(uid(300), admin, SituacaoRecomendacao.APROVADA, momento, "Sugestão pertinente; operação ainda exige confirmação"), "Decisão e motivo registrados no histórico auxiliar, sem alterar quantidades.")
    checar(v, "Rejeição administrativa", lambda: memoria.decidir(uid(301), admin, SituacaoRecomendacao.REJEITADA, momento, "Rever recurso compartilhado e energia"), "Rejeição preserva a sugestão e suas pendências.")
    checar(v, "Administrador não autorizado", lambda: memoria.decidir(uid(302), replace(admin, autorizado=False), SituacaoRecomendacao.APROVADA, momento, "Teste"), "", "não autorizado")
    checar(v, "Decisão repetida", lambda: memoria.decidir(uid(300), admin, SituacaoRecomendacao.REJEITADA, momento, "Teste"), "", "já decidida")
    checar(v, "Nova análise e histórico", lambda: memoria.adicionar(c, gerar_sugestao_simulada(c, uid(200), 303)), "Nova recomendação tem ID próprio; a anterior mantém sua decisão.")
    checar(v, "Preservação das decisões", lambda: exigir(len(memoria.sugestoes) == 4 and len(memoria.decisoes) == 2
           and memoria.sugestoes[uid(300)].cabecalho.situacao == SituacaoRecomendacao.APROVADA
           and memoria.sugestoes[uid(301)].cabecalho.situacao == SituacaoRecomendacao.REJEITADA, "Histórico incorreto"), "Quatro recomendações, duas decisões e duas análises ainda geradas.")
    checar(v, "Aprovação não altera estoque ou pedido", lambda: exigir(c.recursos == antes_recursos and c.demandas == antes_demandas and c.demanda_itens == antes_itens,
           "Aprovação alterou pedido/recurso"), "Lote continua com 300 L; quantidades e situações dos pedidos permanecem iguais. Missões/reservas não são modeladas neste exercício.")
    novo_texto: Cenario = replace(c, modelos={**c.modelos, uid(91): replace(c.modelos[uid(91)], ativo=False), uid(93): replace(c.modelos[uid(93)], ativo=True)})
    nova: Sugestao = gerar_sugestao_simulada(novo_texto, uid(200), 304)
    checar(v, "Novo LLM preserva embeddings", lambda: exigir(nova.cabecalho.id_modelo_inferencia == uid(93)
           and nova.cabecalho.id_modelo_embedding == primeira.cabecalho.id_modelo_embedding
           and novo_texto.indices == c.indices, "Troca de texto alterou embeddings"), "Seleção de configuração de inferência pode mudar sem reindexar; é verificação lógica, sem interface de troca ou chamada a provedor.")
    total_agua: Decimal = sum((i.quantidade_solicitada for i in c.demanda_itens.values() if i.id_tipo_recurso == uid(51)), Decimal(0))
    agua_sugerida: Decimal = sum((r.quantidade_sugerida for s in sugestoes for r in s.recursos if r.id_recurso == uid(61)), Decimal(0))
    checar(v, "Déficit global explícito", lambda: exigir(total_agua == Decimal(400) and total_agua - c.recursos[uid(61)].quantidade_total == Decimal(100)
           and agua_sugerida == Decimal(400), "Cenário de escassez não reproduzido"), "Cálculo confirma 400 L pedidos/sugeridos independentemente para 300 L cadastrados: déficit 100 L; não equivale a plano viável.")
    checar(v, "Bem compartilhado identificado", lambda: exigir(all(any(r.id_recurso == uid(60) for r in s.recursos) for s in sugestoes[:2])
           and c.demandas[uid(200)].inicio_previsto_em < c.demandas[uid(201)].prazo_em
           and c.demandas[uid(201)].inicio_previsto_em < c.demandas[uid(200)].prazo_em, "Conflito não reproduzido"), "As duas sugestões referenciam o mesmo caminhão em janelas sobrepostas; a pendência não é uma reserva resolvida.")
    checar(v, "Não somar capacidade dependente", lambda: exigir(sum((o.capacidade_declarada for o in c.ofertas_atividade.values() if o.atividade_id == uid(71)), Decimal(0)) == Decimal(120)
           and sugestoes[2].itens[0].quantidade_sugerida == 0, "Cobertura indevida de refeições"), "Embora a soma declarada seja 120, a sugestão não afirma cobertura quantitativa; membros da instituição não comprovam composição da oferta.")
    checar(v, "Item sem candidato mantém lacuna", lambda: exigir(any(i.id_demanda_item == uid(215) and i.quantidade_sugerida == 0 for i in sugestoes[1].itens)
           and not any(r.id_recurso == uid(62) for s in sugestoes for r in s.recursos), "Gerador declarado compatível"), "Energia permanece sem recurso sugerido pelo adaptador; nenhum recurso foi inventado para completar o pedido.")
    limites: tuple[tuple[str, str], ...] = (
        ("Estoque compartilhado", "Dois pedidos somam 400 L; lote possui 300 L. Sugestões independentes somam 400 L e explicitam déficit global de 100 L; não há reserva ou plano global executável."),
        ("Caminhão e agenda", "O mesmo caminhão e João aparecem nas duas demandas sobrepostas. Conflito fica como pendência; concorrência, agenda, aceite e reserva são evolução futura."),
        ("Capacidade compartilhada", "Cozinha declara 80 e Paula 40, mas ela integra a cozinha. A sugestão apresenta candidatos sem somar 120; cobertura quantitativa fica em zero, pendente de composição/período-base."),
        ("Compatibilidade técnica", "Gerador de 2 kVA e necessidade de 5 kVA constam em texto. O adaptador do cenário deixa o item sem sugestão; não existe validador técnico genérico de potência."),
        ("Geografia", "Somente fechamento de anel e intervalo de coordenadas foram checados. CRS, validade topológica, limites municipais, mapa e acesso seguro permanecem pendentes."),
        ("IA real", "Vetores e respostas são artificiais. Não há LangChain, LangGraph, provedor, qualidade de RAG ou medição do indicador de redução de tempo."),
        ("Banco e segurança", "FKs e regras foram exercitadas em Python; não há PostgreSQL, pgvector, Alembic, transações, JWT ou criptografia testados. Conexão fictícia não contém token."),
        ("Contratos posteriores", "O exercício mantém convenções D009 e não verifica os contratos implementados de escalas, auditoria, índices, quantidades e decisão em D015–D017. Requisitos avançados continuam futuros. Convenções do exercício não são novas decisões de modelagem."),
    )
    for nome, evidencia in limites:
        v.append({"cenario": nome, "natureza": "Limite do exercício", "resultado": "LIMITE", "evidencia": evidencia})
    raiz: Path = Path(__file__).resolve().parents[2]
    fontes: dict[str, str] = {
        str(p.relative_to(raiz)).replace("\\", "/"): sha256(p.read_bytes()).hexdigest()
        for p in (
            raiz / "docs/escopo-inicial.md", raiz / "docs/decisoes-modelagem.md",
            raiz / "docs/modelo-entidades.md", raiz / "docs/modelo-operacional-proposto.md",
            Path(__file__).resolve(), Path(__file__).with_name("modelos.py"), Path(__file__).with_name("cenario.py"),
        )
    }
    return {
        "versao_cenario": "escopo-inicial-d009-v2", "executado_em_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "fontes_sha256": fontes,
        "contagens": {estado: sum(i["resultado"] == estado for i in v) for estado in ("OK", "FALHA", "LIMITE")},
        "verificacoes": v, "recomendacoes": [serializar_sugestao(s) for s in memoria.sugestoes.values()],
        "decisoes": [{"id_recomendacao": str(d.id_recomendacao), "administrador": d.administrador,
                      "situacao": d.situacao.value, "decidida_em": d.decidida_em.isoformat(), "motivo": d.motivo}
                     for d in memoria.decisoes],
    }


def markdown(r: RelatorioJSON) -> str:
    linhas: list[str] = [
        "# Simulação do escopo inicial — resultado executado", "",
        f"Versão: `{r['versao_cenario']}`. Python {r['python']}. Execução UTC: {r['executado_em_utc']}.", "",
        "Cenário fictício fixo em 08/10/2026 às 09h UTC−03:00: um município (código fictício 0000001), uma ocorrência de inundação/deslizamento, três áreas distintas, três instituições, quatro pessoas, três demandas e seis itens. Recursos: um caminhão, 300 L de água e um gerador descrito como 2 kVA.", "",
        f"Resultado: **{r['contagens']['OK']} verificações OK, {r['contagens']['FALHA']} falhas e {r['contagens']['LIMITE']} limites documentados**. Limites não contam como testes aprovados.", "",
        "O fluxo de sugestão e avaliação administrativa foi exercitado em memória. Esse resultado não comprova aplicação, banco, IA real ou viabilidade de alocação. Demandas e recomendações já são representadas segundo D008/D009; execução operacional continua fora do recorte.", "",
        "| Cenário | Natureza | Resultado | Evidência |", "|---|---|---|---|",
    ]
    for i in r["verificacoes"]:
        celulas: list[str] = [i["cenario"], i["natureza"], i["resultado"], i["evidencia"]]
        linhas.append("| " + " | ".join(t.replace("|", "\\|").replace("\n", " ") for t in celulas) + " |")
    linhas.extend(["", "## Recomendações e histórico", "", "| ID (UUID abreviado) | Demanda | Situação | Itens |", "|---|---|---|---|"])
    for s in r["recomendacoes"]:
        linhas.append(f"| {s['id'][-8:]} | {s['id_demanda'][-8:]} | {s['situacao']} | {len(s['itens'])} |")
    linhas.extend([
        "", "Identificadores completos, candidatos, quantidades, justificativas, pendências e duas decisões estão em [resultado.json](resultado.json). Os dados de entrada estão em [cenario.py](../cenario.py), com tipos em [modelos.py](../modelos.py).", "",
        "Quantidade zero em refeição/energia significa cobertura quantitativa não validada ou ausência de candidato sugerido, conforme convenção deste exercício; não é entrega. As sugestões de água são independentes e não podem ser somadas como plano reservado.", "",
        "## Reprodução", "",
        "Na raiz do projeto, com Python >=3.13,<3.14: `python simulacoes/escopo_inicial/simular_desastre.py --salvar`. Sem `--salvar`, apenas imprime. Nenhuma dependência externa ou credencial é necessária; somente os artefatos de resultado são escritos.", "",
        "Os hashes das fontes usadas nesta execução constam no JSON. Alterar os arquivos não atualiza resultados antigos automaticamente; execute novamente. O relatório e o JSON são gerados pelo mesmo código e substituídos ao salvar.", "",
        "Consulte [o contexto da simulação](../README.md) e [o controle de tarefas](../../../docs/controle-tarefas.md).", "",
    ])
    return "\n".join(linhas)


def main() -> int:
    if isinstance(sys.stdout, TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.version_info[:2] != (3, 13):
        print("Este exercício requer Python >=3.13,<3.14.", file=sys.stderr)
        return 2
    if sys.argv[1:] not in ([], ["--salvar"]):
        print(__doc__, file=sys.stderr)
        return 2
    resultado: RelatorioJSON = executar()
    texto: str = markdown(resultado)
    if "--salvar" in sys.argv[1:]:
        pasta: Path = Path(__file__).resolve().parent / "resultados"
        pasta.mkdir(exist_ok=True)
        (pasta / "relatorio.md").write_text(texto, encoding="utf-8")
        (pasta / "resultado.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(texto)
    return 1 if resultado["contagens"]["FALHA"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
