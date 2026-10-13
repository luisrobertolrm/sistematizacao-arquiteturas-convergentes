from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from business.servico.qualificacoes import auditar
from business.servico.recursos import referencia
from business.view_models.desastres import AreaAfetadaVM
from business.view_models.operacao import DemandaInput, DemandaItemVM, DemandaVM
from core.entity.cadastros import Pessoa
from core.entity.capacidades import Atividade, UnidadeMedida
from core.entity.desastres import AreaAfetada, Desastre
from core.entity.operacao import Demanda, DemandaItem, SituacaoDemanda
from core.entity.recursos import TipoRecurso
from core.http.contratos import ErroNegocio
from infra.configurations.cadastros import pessoas
from infra.configurations.capacidades import atividades, unidades_medida
from infra.configurations.demandas import demanda_itens, demandas
from infra.configurations.desastres import areas_afetadas, desastres
from infra.configurations.recursos import tipos_recurso
from infra.database.operacao import OperacaoRepositorio


class DemandasService:
    def __init__(self, sessao: Session) -> None:
        self.sessao: Session = sessao
        self.repo = OperacaoRepositorio(sessao, Demanda, demandas)

    def listar(
        self,
        limite: int,
        deslocamento: int,
        busca: str | None,
        historico: bool,
        id_area_afetada: UUID | None,
    ) -> list[DemandaVM]:
        filtro = demandas.c.id_area_afetada == id_area_afetada if id_area_afetada else None
        return [
            self.visualizar(e, historico)
            for e in self.repo.listar(limite, deslocamento, busca, historico, filtro)
        ]

    def listar_areas_referencia(
        self, limite: int, deslocamento: int, busca: str | None
    ) -> list[AreaAfetadaVM]:
        q = (
            select(AreaAfetada)
            .join(desastres, areas_afetadas.c.id_desastre == desastres.c.id)
            .where(areas_afetadas.c.inativado_em.is_(None), desastres.c.inativado_em.is_(None))
        )
        if busca:
            q = q.where(areas_afetadas.c.nome.icontains(busca, autoescape=True))
        q = (
            q.order_by(areas_afetadas.c.nome, areas_afetadas.c.id)
            .limit(limite)
            .offset(deslocamento)
        )
        return [AreaAfetadaVM.model_validate(a) for a in self.sessao.scalars(q)]

    def itens(self, id: UUID, historico: bool = False) -> list[DemandaItem]:
        q = select(DemandaItem).where(demanda_itens.c.id_demanda == id)
        if not historico:
            q = q.where(demanda_itens.c.inativado_em.is_(None))
        return list(self.sessao.scalars(q.order_by(demanda_itens.c.criado_em, demanda_itens.c.id)))

    def visualizar(self, e: Demanda, historico: bool = False) -> DemandaVM:
        vm = DemandaVM.model_validate(e)
        area = self.sessao.get(AreaAfetada, e.id_area_afetada)
        pessoa = self.sessao.get(Pessoa, e.id_pessoa_solicitante)
        vm.area_nome = area.nome if area else ""
        vm.solicitante_nome = pessoa.nome if pessoa else ""
        for i in self.itens(e.id, historico):
            item = DemandaItemVM.model_validate(i)
            necessidade = (
                self.sessao.get(Atividade, i.id_atividade)
                if i.id_atividade
                else self.sessao.get(TipoRecurso, i.id_tipo_recurso)
            )
            unidade = self.sessao.get(UnidadeMedida, i.id_unidade_medida)
            item.necessidade_nome = necessidade.nome if necessidade else ""
            item.unidade_simbolo = unidade.simbolo if unidade else ""
            vm.itens.append(item)
        return vm

    def territorio(self, id_area: UUID) -> AreaAfetada:
        area = OperacaoRepositorio(self.sessao, AreaAfetada, areas_afetadas).exigir(id_area)
        # Mesma ordem das escritas territoriais: ocorrência, área, pedido.
        OperacaoRepositorio(self.sessao, Desastre, desastres).exigir(
            area.id_desastre, bloquear=True
        )
        return OperacaoRepositorio(self.sessao, AreaAfetada, areas_afetadas).exigir(
            id_area, bloquear=True
        )

    def salvar(self, id: UUID | None, dados: DemandaInput, sujeito: str) -> DemandaVM:
        with self.sessao.begin():
            self.territorio(dados.id_area_afetada)
            referencia(self.sessao, Pessoa, pessoas, dados.id_pessoa_solicitante)
            e = (
                self.repo.exigir(id, bloquear=True)
                if id
                else Demanda(
                    id_area_afetada=dados.id_area_afetada,
                    id_pessoa_solicitante=dados.id_pessoa_solicitante,
                    titulo=dados.titulo,
                    descricao=dados.descricao,
                    prioridade=dados.prioridade,
                    inicio_previsto_em=dados.inicio_previsto_em,
                    prazo_em=dados.prazo_em,
                    criado_por=sujeito,
                    atualizado_por=sujeito,
                )
            )
            if e.id_area_afetada != dados.id_area_afetada:
                raise ErroNegocio(409, "Área fixa", "Crie outro pedido para mudar a área.")
            if e.situacao == SituacaoDemanda.CANCELADA:
                raise ErroNegocio(
                    409, "Pedido cancelado", "Pedido cancelado não pode ser editado/reaberto."
                )
            if dados.situacao not in {SituacaoDemanda.ABERTA, SituacaoDemanda.CANCELADA}:
                raise ErroNegocio(
                    409, "Execução futura", "Atendimento/conclusão exigem registros de execução."
                )
            if id is None and dados.situacao != SituacaoDemanda.ABERTA:
                raise ErroNegocio(422, "Situação inicial", "Cadastre o pedido aberto.")
            e.titulo, e.descricao, e.prioridade = dados.titulo, dados.descricao, dados.prioridade
            e.inicio_previsto_em, e.prazo_em = dados.inicio_previsto_em, dados.prazo_em
            e.id_pessoa_solicitante, e.situacao = dados.id_pessoa_solicitante, dados.situacao
            auditar(e, sujeito)
            self.sessao.add(e)
            self.sessao.flush()
            anteriores = {i.id: i for i in self.itens(e.id)}
            mantidos: set[UUID] = set()
            for d in dados.itens:
                unidade = referencia(
                    self.sessao, UnidadeMedida, unidades_medida, d.id_unidade_medida
                )
                if d.id_atividade:
                    a = referencia(self.sessao, Atividade, atividades, d.id_atividade)
                    unidade_esperada = a.id_unidade_capacidade
                else:
                    assert d.id_tipo_recurso is not None
                    t = referencia(self.sessao, TipoRecurso, tipos_recurso, d.id_tipo_recurso)
                    unidade_esperada = t.id_unidade_medida
                if unidade.id != unidade_esperada:
                    raise ErroNegocio(
                        409, "Unidade incompatível", "Use a unidade cadastrada na necessidade."
                    )
                if d.id is not None:
                    if d.id not in anteriores:
                        raise ErroNegocio(
                            404, "Item não encontrado", "Item não pertence ao pedido vigente."
                        )
                    item = anteriores[d.id]
                    if (item.id_atividade, item.id_tipo_recurso, item.id_unidade_medida) != (
                        d.id_atividade,
                        d.id_tipo_recurso,
                        d.id_unidade_medida,
                    ):
                        raise ErroNegocio(
                            409,
                            "Necessidade fixa",
                            "Remova e crie outro item para mudar referências.",
                        )
                else:
                    item = DemandaItem(
                        id_demanda=e.id,
                        id_atividade=d.id_atividade,
                        id_tipo_recurso=d.id_tipo_recurso,
                        id_unidade_medida=d.id_unidade_medida,
                        quantidade_solicitada=d.quantidade_solicitada,
                        criado_por=sujeito,
                        atualizado_por=sujeito,
                    )
                item.quantidade_solicitada, item.observacoes = (
                    d.quantidade_solicitada,
                    d.observacoes,
                )
                auditar(item, sujeito)
                self.sessao.add(item)
                mantidos.add(item.id)
            for removido in anteriores.values():
                if removido.id not in mantidos:
                    auditar(removido, sujeito)
                    removido.inativado_em = removido.atualizado_em
            self.sessao.flush()
            resultado = self.visualizar(e)
        return resultado

    def inativar(self, id: UUID, sujeito: str) -> DemandaVM:
        with self.sessao.begin():
            e = self.repo.exigir(id, bloquear=True)
            auditar(e, sujeito)
            e.inativado_em = e.atualizado_em
            resultado = self.visualizar(e, True)
        return resultado
