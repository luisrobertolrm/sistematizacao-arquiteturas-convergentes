import re
from datetime import date
from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from business.view_models.cadastros import UFS, AuditoriaVM
from core.entity.qualificacoes import SituacaoValidacao, TipoCurso, TipoVinculo


class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, from_attributes=True)


class CatalogoInput(Entrada):
    nome: str = Field(min_length=2, max_length=200)
    descricao: str | None = Field(default=None, max_length=4000)

    @field_validator("descricao")
    @classmethod
    def vazio_nulo(cls, valor: str | None) -> str | None:
        return valor or None


class ProfissaoInput(CatalogoInput):
    codigo_cbo: str | None = None

    @field_validator("codigo_cbo")
    @classmethod
    def normalizar_cbo(cls, valor: str | None) -> str | None:
        if not valor:
            return None
        normalizado: str = re.sub(r"[\s-]", "", valor)
        if not re.fullmatch(r"[0-9]{6}", normalizado):
            raise ValueError("Código CBO deve conter seis dígitos")
        return normalizado


class CursoInput(CatalogoInput):
    tipo: TipoCurso


class ProfissaoVM(ProfissaoInput, AuditoriaVM):
    hash_conteudo_semantico: str


class CursoVM(CursoInput, AuditoriaVM):
    hash_conteudo_semantico: str


class VinculoInput(Entrada):
    situacao_validacao: SituacaoValidacao = SituacaoValidacao.PENDENTE

    @property
    def id_referencia(self) -> UUID:
        raise NotImplementedError


class PessoaInstituicaoInput(VinculoInput):
    instituicao_id: UUID
    tipo_vinculo: TipoVinculo
    inicio_em: date
    fim_em: date | None = None

    @property
    def id_referencia(self) -> UUID:
        return self.instituicao_id

    @model_validator(mode="after")
    def datas_ordenadas(self) -> Self:
        if self.fim_em is not None and self.fim_em < self.inicio_em:
            raise ValueError("Fim do vínculo deve ser igual ou posterior ao início")
        return self


class PessoaProfissaoInput(VinculoInput):
    profissao_id: UUID
    registro_profissional: str | None = Field(default=None, max_length=100)
    orgao_registro: str | None = Field(default=None, max_length=100)
    uf_registro: str | None = None
    validade_em: date | None = None

    @property
    def id_referencia(self) -> UUID:
        return self.profissao_id

    @field_validator("registro_profissional", "orgao_registro", "uf_registro")
    @classmethod
    def normalizar_registro(cls, valor: str | None) -> str | None:
        return valor.upper() if valor else None

    @field_validator("uf_registro")
    @classmethod
    def validar_uf(cls, valor: str | None) -> str | None:
        if valor is not None and valor not in UFS:
            raise ValueError("UF de registro inválida")
        return valor


class PessoaCursoInput(VinculoInput):
    curso_id: UUID
    instituicao_emissora: str = Field(min_length=2, max_length=200)
    conclusao_em: date
    validade_em: date | None = None
    carga_horaria: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    comprovante_referencia: str | None = Field(default=None, max_length=500)

    @property
    def id_referencia(self) -> UUID:
        return self.curso_id

    @field_validator("comprovante_referencia")
    @classmethod
    def referencia_opaca(cls, valor: str | None) -> str | None:
        if not valor:
            return None
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:/-]*", valor):
            raise ValueError("Use uma referência de comprovante sem credenciais ou parâmetros")
        return valor

    @model_validator(mode="after")
    def datas_ordenadas(self) -> Self:
        if self.validade_em is not None and self.validade_em < self.conclusao_em:
            raise ValueError("Validade deve ser igual ou posterior à conclusão")
        return self


class VinculoVM(AuditoriaVM):
    pessoa_id: UUID
    referencia_nome: str = ""


class PessoaInstituicaoVM(PessoaInstituicaoInput, VinculoVM):
    pass


class PessoaProfissaoVM(PessoaProfissaoInput, VinculoVM):
    pass


class PessoaCursoVM(PessoaCursoInput, VinculoVM):
    pass
