from datetime import date
from typing import cast
from uuid import UUID

from sqlalchemy import Table, or_, select
from sqlalchemy.orm import Session

from core.entity.qualificacoes import TipoVinculo, VinculoPessoa
from core.http.contratos import ErroNegocio
from infra.configurations.cadastros import pessoas
from infra.configurations.qualificacoes import pessoa_instituicao


class VinculosRepositorio[T: VinculoPessoa]:
    def __init__(
        self,
        sessao: Session,
        tipo: type[T],
        tabela: Table,
        referencia: Table,
        coluna_referencia: str,
    ) -> None:
        self.sessao: Session = sessao
        self.tipo: type[T] = tipo
        self.tabela: Table = tabela
        self.referencia: Table = referencia
        self.coluna_referencia: str = coluna_referencia

    def exigir_pessoa(self, pessoa_id: UUID, ativo: bool = True, bloquear: bool = False) -> None:
        self.exigir_registro(pessoas, pessoa_id, ativo, bloquear)

    def exigir_referencia(self, identificador: UUID) -> None:
        self.exigir_registro(self.referencia, identificador, True, True)

    def exigir_registro(
        self, tabela: Table, identificador: UUID, ativo: bool, bloquear: bool
    ) -> None:
        consulta = select(tabela.c.id).where(tabela.c.id == identificador)
        if ativo:
            consulta = consulta.where(tabela.c.inativado_em.is_(None))
        if bloquear:
            consulta = consulta.with_for_update()
        if self.sessao.scalar(consulta) is None:
            raise ErroNegocio(404, "Referência não encontrada", "Cadastro inexistente ou inativo.")

    def listar(
        self, pessoa_id: UUID, limite: int, deslocamento: int, incluir_inativos: bool
    ) -> list[tuple[T, str]]:
        consulta = (
            select(self.tipo, self.referencia.c.nome)
            .join(self.referencia, self.tabela.c[self.coluna_referencia] == self.referencia.c.id)
            .where(self.tabela.c.pessoa_id == pessoa_id)
            .order_by(self.tabela.c.criado_em.desc(), self.tabela.c.id)
            .limit(limite)
            .offset(deslocamento)
        )
        if not incluir_inativos:
            consulta = consulta.where(
                self.tabela.c.inativado_em.is_(None), self.referencia.c.inativado_em.is_(None)
            )
        return [(cast(T, linha[0]), cast(str, linha[1])) for linha in self.sessao.execute(consulta)]

    def obter(self, pessoa_id: UUID, identificador: UUID, incluir_inativos: bool = False) -> T:
        entidade: T | None = self.sessao.get(self.tipo, identificador)
        if (
            entidade is None
            or entidade.pessoa_id != pessoa_id
            or (not incluir_inativos and entidade.inativado_em is not None)
        ):
            raise ErroNegocio(404, "Vínculo não encontrado", "Vínculo inexistente ou inativo.")
        return entidade

    def nome_referencia(self, entidade: T) -> str:
        nome: str | None = self.sessao.scalar(
            select(self.referencia.c.nome).where(self.referencia.c.id == entidade.id_referencia)
        )
        if nome is None:
            raise ErroNegocio(404, "Referência não encontrada", "Cadastro inexistente.")
        return nome

    def ha_sobreposicao(
        self,
        pessoa_id: UUID,
        instituicao_id: UUID,
        tipo: TipoVinculo,
        inicio: date,
        fim: date | None,
        exceto: UUID,
    ) -> bool:
        t: Table = pessoa_instituicao
        consulta = select(t.c.id).where(
            t.c.pessoa_id == pessoa_id,
            t.c.instituicao_id == instituicao_id,
            t.c.tipo_vinculo == tipo,
            t.c.inativado_em.is_(None),
            t.c.id != exceto,
            or_(t.c.fim_em.is_(None), t.c.fim_em >= inicio),
        )
        if fim is not None:
            consulta = consulta.where(t.c.inicio_em <= fim)
        return self.sessao.scalar(consulta.limit(1)) is not None
