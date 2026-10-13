from uuid import UUID

from sqlalchemy import Table, or_, select
from sqlalchemy.orm import Session

from core.entity.cadastros import Entidade
from infra.configurations.cadastros import instituicoes, pessoas
from infra.configurations.capacidades import atividades
from infra.configurations.recursos import recursos


class RecursosRepositorio[T: Entidade]:
    def __init__(
        self, sessao: Session, tipo: type[T], tabela: Table, oferta_id: UUID | None = None
    ) -> None:
        self.sessao: Session = sessao
        self.tipo: type[T] = tipo
        self.tabela: Table = tabela
        self.oferta_id: UUID | None = oferta_id

    def obter(
        self,
        identificador: UUID,
        historico: bool = False,
        bloquear: bool = False,
        compartilhado: bool = False,
    ) -> T | None:
        consulta = select(self.tipo).where(self.tabela.c.id == identificador)
        if self.oferta_id is not None:
            consulta = consulta.where(self.tabela.c.oferta_atividade_id == self.oferta_id)
        if not historico:
            consulta = consulta.where(self.tabela.c.inativado_em.is_(None))
        if bloquear or compartilhado:
            consulta = consulta.with_for_update(read=compartilhado)
        return self.sessao.scalar(consulta.execution_options(populate_existing=True))

    def listar(
        self,
        limite: int,
        deslocamento: int,
        busca: str | None,
        historico: bool,
    ) -> list[T]:
        tabela: Table = self.tabela
        consulta = select(self.tipo)
        if self.oferta_id is not None:
            consulta = consulta.where(tabela.c.oferta_atividade_id == self.oferta_id)
        if not historico:
            consulta = consulta.where(tabela.c.inativado_em.is_(None))
        if busca and busca.strip():
            trecho: str = busca.strip()
            if tabela.name == "ofertas_atividade":
                filtro = or_(
                    tabela.c.descricao_complementar.icontains(trecho, autoescape=True),
                    tabela.c.municipio_atendimento_codigo_ibge.icontains(trecho, autoescape=True),
                    select(atividades.c.id)
                    .where(
                        atividades.c.id == tabela.c.atividade_id,
                        atividades.c.nome.icontains(trecho, autoescape=True),
                    )
                    .exists(),
                    select(pessoas.c.id)
                    .where(
                        pessoas.c.id == tabela.c.pessoa_id,
                        pessoas.c.nome.icontains(trecho, autoescape=True),
                    )
                    .exists(),
                    select(instituicoes.c.id)
                    .where(
                        instituicoes.c.id == tabela.c.instituicao_id,
                        instituicoes.c.nome.icontains(trecho, autoescape=True),
                    )
                    .exists(),
                )
            elif tabela.name == "oferta_atividade_recurso":
                filtro = (
                    select(recursos.c.id)
                    .where(
                        recursos.c.id == tabela.c.recurso_id,
                        recursos.c.nome.icontains(trecho, autoescape=True),
                    )
                    .exists()
                )
            else:
                filtro = or_(
                    tabela.c.nome.icontains(trecho, autoescape=True),
                    tabela.c.descricao.icontains(trecho, autoescape=True),
                )
                if tabela.name == "recursos":
                    filtro = or_(filtro, tabela.c.identificacao.icontains(trecho, autoescape=True))
            consulta = consulta.where(filtro)
        ordem = tabela.c.nome if "nome" in tabela.c else tabela.c.criado_em
        return list(
            self.sessao.scalars(
                consulta.order_by(ordem, tabela.c.id).limit(limite).offset(deslocamento)
            )
        )
