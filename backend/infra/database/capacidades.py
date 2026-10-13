from uuid import UUID

from sqlalchemy import Table, or_, select
from sqlalchemy.orm import Session

from core.entity.capacidades import AtividadeTermo, CatalogoComCodigo
from infra.configurations.capacidades import atividade_termos


class CatalogoCapacidadeRepositorio[T: CatalogoComCodigo]:
    def __init__(self, sessao: Session, tipo: type[T], tabela: Table) -> None:
        self.sessao: Session = sessao
        self.tipo: type[T] = tipo
        self.tabela: Table = tabela

    def obter(
        self,
        identificador: UUID,
        incluir_inativos: bool = False,
        bloquear: bool = False,
        compartilhado: bool = False,
    ) -> T | None:
        consulta = select(self.tipo).where(self.tabela.c.id == identificador)
        if not incluir_inativos:
            consulta = consulta.where(self.tabela.c.inativado_em.is_(None))
        if bloquear or compartilhado:
            consulta = consulta.with_for_update(read=compartilhado)
        return self.sessao.scalar(consulta.execution_options(populate_existing=True))

    def listar(
        self,
        limite: int,
        deslocamento: int,
        busca: str | None,
        incluir_inativos: bool,
    ) -> list[T]:
        consulta = select(self.tipo).order_by(self.tabela.c.nome, self.tabela.c.id)
        if not incluir_inativos:
            consulta = consulta.where(self.tabela.c.inativado_em.is_(None))
        if busca and busca.strip():
            trecho: str = busca.strip()
            filtro = or_(
                self.tabela.c.nome.icontains(trecho, autoescape=True),
                self.tabela.c.codigo.icontains(trecho, autoescape=True),
            )
            if self.tabela.name == "atividades":
                filtro = or_(
                    filtro,
                    self.tabela.c.descricao.icontains(trecho, autoescape=True),
                    select(atividade_termos.c.id)
                    .where(
                        atividade_termos.c.atividade_id == self.tabela.c.id,
                        atividade_termos.c.inativado_em.is_(None),
                        atividade_termos.c.termo.icontains(trecho, autoescape=True),
                    )
                    .exists(),
                )
            consulta = consulta.where(filtro)
        return list(self.sessao.scalars(consulta.limit(limite).offset(deslocamento)))


class TermosRepositorio:
    def __init__(self, sessao: Session) -> None:
        self.sessao: Session = sessao

    def listar(
        self,
        atividade_id: UUID,
        limite: int,
        deslocamento: int,
        incluir_inativos: bool,
    ) -> list[AtividadeTermo]:
        consulta = select(AtividadeTermo).where(atividade_termos.c.atividade_id == atividade_id)
        if not incluir_inativos:
            consulta = consulta.where(atividade_termos.c.inativado_em.is_(None))
        return list(
            self.sessao.scalars(
                consulta.order_by(atividade_termos.c.termo, atividade_termos.c.id)
                .limit(limite)
                .offset(deslocamento)
            )
        )

    def obter(
        self,
        atividade_id: UUID,
        identificador: UUID,
        incluir_inativos: bool,
    ) -> AtividadeTermo | None:
        consulta = select(AtividadeTermo).where(
            atividade_termos.c.id == identificador,
            atividade_termos.c.atividade_id == atividade_id,
        )
        if not incluir_inativos:
            consulta = consulta.where(atividade_termos.c.inativado_em.is_(None))
        return self.sessao.scalar(consulta)

    def textos_ativos(self, atividade_id: UUID) -> list[str]:
        return list(
            self.sessao.scalars(
                select(atividade_termos.c.termo).where(
                    atividade_termos.c.atividade_id == atividade_id,
                    atividade_termos.c.inativado_em.is_(None),
                )
            )
        )
