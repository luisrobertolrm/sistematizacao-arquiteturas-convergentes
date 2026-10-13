from uuid import UUID

from sqlalchemy import Table, or_, select, text
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from core.entity.cadastros import Entidade
from core.http.contratos import ErroNegocio


def bloquear_configuracao(sessao: Session) -> None:
    sessao.execute(text("SELECT pg_advisory_xact_lock(72441809)"))


class OperacaoRepositorio[T: Entidade]:
    def __init__(self, sessao: Session, tipo: type[T], tabela: Table) -> None:
        self.sessao: Session = sessao
        self.tipo: type[T] = tipo
        self.tabela: Table = tabela

    def exigir(self, id: UUID, historico: bool = False, bloquear: bool = False) -> T:
        q = select(self.tipo).where(self.tabela.c.id == id)
        if not historico:
            q = q.where(self.tabela.c.inativado_em.is_(None))
        if bloquear:
            q = q.with_for_update()
        e = self.sessao.scalar(q.execution_options(populate_existing=True))
        if e is None:
            raise ErroNegocio(404, "Cadastro não encontrado", "Registro inexistente ou inativado.")
        return e

    def listar(
        self,
        limite: int,
        deslocamento: int,
        busca: str | None,
        historico: bool,
        filtro: ColumnElement[bool] | None = None,
    ) -> list[T]:
        q = select(self.tipo).order_by(self.tabela.c.criado_em.desc(), self.tabela.c.id)
        if not historico:
            q = q.where(self.tabela.c.inativado_em.is_(None))
        if filtro is not None:
            q = q.where(filtro)
        if busca:
            campos = [
                self.tabela.c[c].icontains(busca, autoescape=True)
                for c in ("nome", "titulo", "descricao", "identificador_modelo")
                if c in self.tabela.c
            ]
            if campos:
                q = q.where(or_(*campos))
        return list(self.sessao.scalars(q.limit(limite).offset(deslocamento)))
