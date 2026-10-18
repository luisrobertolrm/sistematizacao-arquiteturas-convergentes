from uuid import UUID

from sqlalchemy import Table, func, select
from sqlalchemy.orm import Session

from core.entity.cadastros import Entidade


class Repositorio[T: Entidade]:
    def __init__(self, sessao: Session, tipo: type[T], tabela: Table) -> None:
        self.sessao: Session = sessao
        self.tipo: type[T] = tipo
        self.tabela: Table = tabela

    def listar(self, limite: int, deslocamento: int, busca: str | None = None) -> list[T]:
        consulta = (
            select(self.tipo)
            .where(self.tabela.c.inativado_em.is_(None))
            .order_by(self.tabela.c.nome, self.tabela.c.id)
            .limit(limite)
            .offset(deslocamento)
        )
        if busca:
            consulta = consulta.where(self.tabela.c.nome.icontains(busca, autoescape=True))
        return list(self.sessao.scalars(consulta))

    def obter(self, identificador: UUID) -> T | None:
        entidade: T | None = self.sessao.get(self.tipo, identificador)
        return entidade if entidade is not None and entidade.inativado_em is None else None

    def obter_por_email(self, email: str) -> T | None:
        consulta = (
            select(self.tipo)
            .where(
                self.tabela.c.inativado_em.is_(None),
                func.lower(self.tabela.c.email_contato) == email.lower(),
            )
            .order_by(self.tabela.c.criado_em.desc(), self.tabela.c.id)
            .limit(1)
        )
        return self.sessao.scalar(consulta)

    def adicionar(self, entidade: T) -> None:
        self.sessao.add(entidade)

