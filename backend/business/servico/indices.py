from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from business.graphs.indexacao import gerar_embeddings
from business.servico.modelos_ia import ModelosIAService
from business.servico.qualificacoes import auditar
from business.view_models.operacao import (
    BuscaInput,
    BuscaVM,
    IndexarInput,
    IndiceVM,
    ResultadoBusca,
)
from core.entity.cadastros import agora_utc
from core.entity.capacidades import Atividade
from core.entity.operacao import AtividadeIndiceSemantico, FinalidadeModeloIA, SituacaoIndexacao
from core.http.contratos import ErroNegocio
from core.ia_operacao import ConfiguracaoModelo, FabricaClientesIA
from core.semantica import conteudo_atividade
from core.vetores import cosseno
from infra.configurations.capacidades import atividade_termos, atividades
from infra.configurations.indices import atividade_indice_semantico as indices
from infra.database.operacao import OperacaoRepositorio, bloquear_configuracao


@dataclass(frozen=True)
class OrigemEmbedding:
    id: UUID
    hash: str
    texto: str


class IndicesService:
    def __init__(
        self, sessao: Session, modelos: ModelosIAService, clientes: FabricaClientesIA
    ) -> None:
        self.sessao: Session = sessao
        self.modelos: ModelosIAService = modelos
        self.clientes: FabricaClientesIA = clientes
        self.atividades = OperacaoRepositorio(sessao, Atividade, atividades)
        self.repo = OperacaoRepositorio(sessao, AtividadeIndiceSemantico, indices)

    def listar(self, limite: int, deslocamento: int, id_modelo: UUID | None) -> list[IndiceVM]:
        filtro = indices.c.id_modelo == id_modelo if id_modelo else None
        return [
            self.visualizar(e) for e in self.repo.listar(limite, deslocamento, None, False, filtro)
        ]

    def visualizar(self, e: AtividadeIndiceSemantico) -> IndiceVM:
        vm = IndiceVM.model_validate(e)
        a = self.atividades.exigir(e.id_atividade, True)
        vm.atualizado = (
            a.inativado_em is None
            and e.embedding is not None
            and e.hash_atividade_origem == a.hash_conteudo_semantico
            and e.situacao_indexacao == SituacaoIndexacao.PRONTA
        )
        vm.atividade_nome = a.nome
        return vm

    def indexar(self, dados: IndexarInput, sujeito: str) -> list[IndiceVM]:
        if len(set(dados.ids_atividades)) != len(dados.ids_atividades):
            raise ErroNegocio(422, "Atividades repetidas", "Informe IDs distintos.")
        with self.sessao.begin():
            bloquear_configuracao(self.sessao)
            m = self.modelos.modelos.exigir(dados.id_modelo)
            if m.finalidade != FinalidadeModeloIA.EMBEDDING or m.dimensao is None:
                raise ErroNegocio(409, "Finalidade incorreta", "Selecione modelo de embedding.")
            config = self.modelos.configuracao(m.id)
            id_conexao = m.id_conexao
            origens: list[OrigemEmbedding] = []
            for id in sorted(dados.ids_atividades):
                a = self.atividades.exigir(id, bloquear=True)
                termos = list(
                    self.sessao.scalars(
                        select(atividade_termos.c.termo).where(
                            atividade_termos.c.atividade_id == id,
                            atividade_termos.c.inativado_em.is_(None),
                        )
                    )
                )
                origens.append(
                    OrigemEmbedding(id, a.hash_conteudo_semantico, conteudo_atividade(a, termos))
                )
        try:
            vetores = gerar_embeddings(
                self.clientes.embedding(config), [o.texto for o in origens], config.dimensao or 0
            )
        except ErroNegocio:
            raise
        except Exception:
            raise ErroNegocio(
                502,
                "Falha de embedding",
                "Não foi possível gerar embeddings; nenhum vetor publicado.",
            ) from None
        with self.sessao.begin():
            bloquear_configuracao(self.sessao)
            self.modelos.modelos.exigir(config.id_modelo)
            self.modelos.conexoes.exigir(id_conexao)
            resultado: list[IndiceVM] = []
            for o, vetor in zip(origens, vetores, strict=True):
                a = self.atividades.exigir(o.id, bloquear=True)
                if a.hash_conteudo_semantico != o.hash:
                    raise ErroNegocio(
                        409,
                        "Origem alterada",
                        "Atividade mudou durante a geração; repita a indexação.",
                    )
                e = self.sessao.scalar(
                    select(AtividadeIndiceSemantico)
                    .where(indices.c.id_atividade == o.id, indices.c.id_modelo == config.id_modelo)
                    .with_for_update()
                )
                if e is None:
                    e = AtividadeIndiceSemantico(
                        id_atividade=o.id,
                        id_modelo=config.id_modelo,
                        hash_atividade_origem=o.hash,
                        criado_por=sujeito,
                        atualizado_por=sujeito,
                    )
                e.embedding, e.hash_atividade_origem = vetor, o.hash
                e.situacao_indexacao, e.indexado_em = SituacaoIndexacao.PRONTA, agora_utc()
                auditar(e, sujeito)
                self.sessao.add(e)
                self.sessao.flush()
                resultado.append(self.visualizar(e))
        return resultado

    def buscar_config(self, dados: BuscaInput, config: ConfiguracaoModelo) -> BuscaVM:
        assert config.dimensao is not None
        try:
            vetor = gerar_embeddings(
                self.clientes.embedding(config), [dados.texto], config.dimensao
            )[0]
        except ErroNegocio:
            raise
        except Exception:
            raise ErroNegocio(
                502, "Falha de busca", "Não foi possível gerar o vetor da consulta."
            ) from None
        with self.sessao.begin():
            self.modelos.modelos.exigir(config.id_modelo)
            # Limite explícito do MVP: busca exata, nunca trunca silenciosamente o catálogo.
            pares = list(
                self.sessao.execute(
                    select(AtividadeIndiceSemantico, Atividade)
                    .join(Atividade, indices.c.id_atividade == atividades.c.id)
                    .where(
                        indices.c.id_modelo == config.id_modelo,
                        indices.c.inativado_em.is_(None),
                        indices.c.situacao_indexacao == "pronta",
                        atividades.c.inativado_em.is_(None),
                        indices.c.hash_atividade_origem == atividades.c.hash_conteudo_semantico,
                    )
                    .limit(5001)
                )
            )
            if len(pares) > 5000:
                raise ErroNegocio(
                    409,
                    "Limite de busca",
                    "Catálogo excede 5000 vetores; configure índice vetorial escalável.",
                )
            resultados: list[ResultadoBusca] = []
            for indice, atividade in pares:
                if indice.embedding is not None:
                    resultados.append(
                        ResultadoBusca(
                            id_atividade=atividade.id,
                            nome=atividade.nome,
                            similaridade=cosseno(vetor, indice.embedding),
                        )
                    )
        resultados.sort(key=lambda r: (-r.similaridade, str(r.id_atividade)))
        return BuscaVM(id_modelo=config.id_modelo, resultados=resultados[: dados.limite])

    def buscar(self, dados: BuscaInput) -> BuscaVM:
        with self.sessao.begin():
            bloquear_configuracao(self.sessao)
            m = self.modelos.ativo(FinalidadeModeloIA.EMBEDDING)
            self.modelos.cobertura(m)
            config = self.modelos.configuracao(m.id)
        return self.buscar_config(dados, config)
