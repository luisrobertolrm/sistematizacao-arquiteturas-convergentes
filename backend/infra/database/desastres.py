from uuid import UUID

from sqlalchemy import Table, or_, select
from sqlalchemy.orm import Session

from core.entity.cadastros import Entidade
from core.entity.desastres import DesastreTipo
from infra.configurations.desastres import desastre_tipo


class TerritorioRepositorio[T: Entidade]:
    def __init__(
        self, sessao: Session, tipo: type[T], tabela: Table, id_desastre: UUID | None = None
    ) -> None:
        self.sessao: Session = sessao
        self.tipo: type[T] = tipo
        self.tabela: Table = tabela
        self.id_desastre: UUID | None = id_desastre

    def obter(
        self, identificador: UUID, historico: bool = False, bloquear: bool = False
    ) -> T | None:
        consulta = select(self.tipo).where(self.tabela.c.id == identificador)
        if self.id_desastre is not None:
            consulta = consulta.where(self.tabela.c.id_desastre == self.id_desastre)
        if not historico:
            consulta = consulta.where(self.tabela.c.inativado_em.is_(None))
        if bloquear:
            consulta = consulta.with_for_update()
        return self.sessao.scalar(consulta.execution_options(populate_existing=True))

    def listar(self, limite: int, deslocamento: int, busca: str | None, historico: bool) -> list[T]:
        tabela: Table = self.tabela
        consulta = select(self.tipo)
        if self.id_desastre is not None:
            consulta = consulta.where(tabela.c.id_desastre == self.id_desastre)
        if not historico:
            consulta = consulta.where(tabela.c.inativado_em.is_(None))
        nome = tabela.c.titulo if tabela.name == "desastres" else tabela.c.nome
        if busca and busca.strip():
            trecho: str = busca.strip()
            filtro = or_(
                nome.icontains(trecho, autoescape=True),
                tabela.c.descricao.icontains(trecho, autoescape=True),
            )
            if tabela.name == "areas_afetadas":
                filtro = or_(
                    filtro, tabela.c.municipio_codigo_ibge.icontains(trecho, autoescape=True)
                )
            consulta = consulta.where(filtro)
        return list(
            self.sessao.scalars(
                consulta.order_by(nome, tabela.c.id).limit(limite).offset(deslocamento)
            )
        )

    def classificacoes(self, id_desastre: UUID, historico: bool = False) -> list[DesastreTipo]:
        consulta = select(DesastreTipo).where(desastre_tipo.c.id_desastre == id_desastre)
        if not historico:
            consulta = consulta.where(desastre_tipo.c.inativado_em.is_(None))
        return list(
            self.sessao.scalars(consulta.order_by(desastre_tipo.c.criado_em, desastre_tipo.c.id))
        )
