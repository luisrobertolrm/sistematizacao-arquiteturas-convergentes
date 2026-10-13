from decimal import Decimal
from hashlib import sha256
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from business.graphs.atendimento import (
    ContextoAnalise,
    ContextoRecuperado,
    GrafoAtendimento,
    OfertaCandidata,
    RecursoCandidato,
    validar_proposta,
)
from business.servico.demandas import DemandasService
from business.servico.indices import IndicesService
from business.servico.modelos_ia import ModelosIAService
from business.servico.qualificacoes import auditar
from business.servico.recursos import referencia
from business.view_models.operacao import (
    BuscaInput,
    DecisaoInput,
    RecomendacaoItemVM,
    RecomendacaoVM,
)
from core.entity.cadastros import Instituicao, Pessoa, SituacaoCadastral, agora_utc
from core.entity.capacidades import Atividade, UnidadeMedida
from core.entity.desastres import AreaAfetada, Desastre
from core.entity.operacao import (
    FinalidadeModeloIA,
    Recomendacao,
    RecomendacaoInstituicao,
    RecomendacaoItem,
    RecomendacaoPessoa,
    RecomendacaoRecurso,
    SituacaoDemanda,
    SituacaoRecomendacao,
)
from core.entity.qualificacoes import SituacaoValidacao
from core.entity.recursos import (
    EstadoRecurso,
    OfertaAtividade,
    OfertaAtividadeRecurso,
    Recurso,
    TipoRecurso,
)
from core.http.contratos import ErroNegocio
from core.ia_operacao import FabricaClientesIA, PropostaDemanda
from infra.configurations.cadastros import instituicoes, pessoas
from infra.configurations.capacidades import atividades, unidades_medida
from infra.configurations.recomendacoes import (
    recomendacao_instituicoes,
    recomendacao_itens,
    recomendacao_pessoas,
    recomendacao_recursos,
    recomendacoes,
)
from infra.configurations.recursos import (
    oferta_atividade_recurso,
    ofertas_atividade,
    recursos,
    tipos_recurso,
)
from infra.database.operacao import OperacaoRepositorio, bloquear_configuracao


def hash_contexto(contexto: ContextoAnalise) -> str:
    return sha256(contexto.model_dump_json().encode("utf-8")).hexdigest()


class RecomendacoesService:
    def __init__(
        self, sessao: Session, modelos: ModelosIAService, clientes: FabricaClientesIA
    ) -> None:
        self.sessao: Session = sessao
        self.modelos: ModelosIAService = modelos
        self.clientes: FabricaClientesIA = clientes
        self.demandas = DemandasService(sessao)
        self.indices = IndicesService(sessao, modelos, clientes)
        self.repo = OperacaoRepositorio(sessao, Recomendacao, recomendacoes)

    def listar(
        self, limite: int, deslocamento: int, id_demanda: UUID | None
    ) -> list[RecomendacaoVM]:
        filtro = recomendacoes.c.id_demanda == id_demanda if id_demanda else None
        return [
            self.visualizar(e) for e in self.repo.listar(limite, deslocamento, None, False, filtro)
        ]

    def contexto(self, id_demanda: UUID) -> ContextoAnalise:
        d = self.demandas.repo.exigir(id_demanda)
        area = self.sessao.get(AreaAfetada, d.id_area_afetada)
        assert area is not None
        desastre = self.sessao.get(Desastre, area.id_desastre)
        assert desastre is not None
        if d.situacao != SituacaoDemanda.ABERTA or area.inativado_em or desastre.inativado_em:
            raise ErroNegocio(
                409, "Pedido indisponível", "Análise requer pedido aberto e território ativo."
            )
        pedido = self.demandas.visualizar(d)
        fontes: dict[UUID, str] = {}
        for i in pedido.itens:
            unidade = referencia(self.sessao, UnidadeMedida, unidades_medida, i.id_unidade_medida)
            fontes[unidade.id] = unidade.atualizado_em.isoformat()
            if i.id_atividade:
                atividade = referencia(self.sessao, Atividade, atividades, i.id_atividade)
                fontes[atividade.id] = atividade.hash_conteudo_semantico
            elif i.id_tipo_recurso:
                tipo_pedido = referencia(self.sessao, TipoRecurso, tipos_recurso, i.id_tipo_recurso)
                fontes[tipo_pedido.id] = tipo_pedido.atualizado_em.isoformat()
        atividades_ids = [i.id_atividade for i in pedido.itens if i.id_atividade]
        tipos_ids = [i.id_tipo_recurso for i in pedido.itens if i.id_tipo_recurso]
        ofertas: list[OfertaCandidata] = []
        for o in self.sessao.scalars(
            select(OfertaAtividade)
            .where(
                ofertas_atividade.c.atividade_id.in_(atividades_ids),
                ofertas_atividade.c.municipio_atendimento_codigo_ibge == area.municipio_codigo_ibge,
                ofertas_atividade.c.situacao_validacao == SituacaoValidacao.VALIDADA,
                ofertas_atividade.c.inativado_em.is_(None),
            )
            .order_by(ofertas_atividade.c.id)
            .limit(30)
            .with_for_update(read=True)
        ):
            responsavel = (
                self.sessao.get(Pessoa, o.pessoa_id)
                if o.pessoa_id
                else self.sessao.get(Instituicao, o.instituicao_id)
            )
            if (
                responsavel is None
                or responsavel.inativado_em
                or responsavel.situacao_cadastral != SituacaoCadastral.VALIDADA
            ):
                continue
            if o.pessoa_id:
                referencia(self.sessao, Pessoa, pessoas, o.pessoa_id)
            elif o.instituicao_id:
                referencia(self.sessao, Instituicao, instituicoes, o.instituicao_id)
            ofertas.append(
                OfertaCandidata(
                    id=o.id,
                    id_atividade=o.atividade_id,
                    id_pessoa=o.pessoa_id,
                    id_instituicao=o.instituicao_id,
                    nome=responsavel.nome,
                    capacidade_declarada=o.capacidade_declarada,
                    atualizado_em=o.atualizado_em,
                    responsavel_atualizado_em=responsavel.atualizado_em,
                )
            )
        vinculos = list(
            self.sessao.scalars(
                select(OfertaAtividadeRecurso)
                .where(
                    oferta_atividade_recurso.c.oferta_atividade_id.in_([o.id for o in ofertas]),
                    oferta_atividade_recurso.c.inativado_em.is_(None),
                )
                .order_by(oferta_atividade_recurso.c.id)
                .with_for_update(read=True)
            )
        )
        for vinculo in vinculos:
            fontes[vinculo.id] = vinculo.atualizado_em.isoformat()
        bens: list[RecursoCandidato] = []
        for r in self.sessao.scalars(
            select(Recurso)
            .where(
                (
                    recursos.c.tipo_recurso_id.in_(tipos_ids)
                    | recursos.c.id.in_([v.recurso_id for v in vinculos])
                ),
                recursos.c.municipio_codigo_ibge == area.municipio_codigo_ibge,
                recursos.c.estado_operacional == EstadoRecurso.OPERACIONAL,
                recursos.c.quantidade_total > 0,
                recursos.c.inativado_em.is_(None),
            )
            .order_by(recursos.c.id)
            .limit(30)
            .with_for_update(read=True)
        ):
            responsavel = (
                self.sessao.get(Pessoa, r.pessoa_id)
                if r.pessoa_id
                else self.sessao.get(Instituicao, r.instituicao_id)
            )
            tipo = self.sessao.get(TipoRecurso, r.tipo_recurso_id)
            if (
                responsavel is None
                or responsavel.inativado_em
                or tipo is None
                or tipo.inativado_em
                or responsavel.situacao_cadastral != SituacaoCadastral.VALIDADA
            ):
                continue
            if r.pessoa_id:
                referencia(self.sessao, Pessoa, pessoas, r.pessoa_id)
            elif r.instituicao_id:
                referencia(self.sessao, Instituicao, instituicoes, r.instituicao_id)
            referencia(self.sessao, TipoRecurso, tipos_recurso, r.tipo_recurso_id)
            fontes[tipo.id] = tipo.atualizado_em.isoformat()
            bens.append(
                RecursoCandidato(
                    modo_controle=tipo.modo_controle.value,
                    id=r.id,
                    id_tipo_recurso=r.tipo_recurso_id,
                    id_unidade_medida=tipo.id_unidade_medida,
                    nome=r.nome,
                    quantidade_total=r.quantidade_total,
                    atualizado_em=r.atualizado_em,
                    responsavel_atualizado_em=responsavel.atualizado_em,
                    ofertas=sorted(
                        [v.oferta_atividade_id for v in vinculos if v.recurso_id == r.id]
                    ),
                )
            )
        return ContextoAnalise(
            fontes=fontes,
            demanda=pedido,
            municipio=area.municipio_codigo_ibge,
            area_atualizada_em=area.atualizado_em,
            desastre_atualizado_em=desastre.atualizado_em,
            ofertas=ofertas,
            recursos=bens,
        )

    def gerar(self, id_demanda: UUID, sujeito: str) -> RecomendacaoVM:
        with self.sessao.begin():
            bloquear_configuracao(self.sessao)
            me = self.modelos.ativo(FinalidadeModeloIA.EMBEDDING)
            mt = self.modelos.ativo(FinalidadeModeloIA.TEXTO)
            self.modelos.cobertura(me)
            ce, ct = self.modelos.configuracao(me.id), self.modelos.configuracao(mt.id)
            contexto = self.contexto(id_demanda)

        def recuperar() -> str:
            buscas = [
                self.indices.buscar_config(
                    BuscaInput(
                        texto=f"{i.necessidade_nome} {i.observacoes or ''}".strip(), limite=10
                    ),
                    ce,
                )
                for i in contexto.demanda.itens
                if i.id_atividade
            ]
            return ContextoRecuperado(
                dados=contexto, atividades_semanticas=buscas
            ).model_dump_json()

        try:
            p = GrafoAtendimento(
                recuperar,
                self.clientes.inferencia(ct),
                lambda proposta: validar_proposta(contexto, proposta),
            ).executar()
        except ErroNegocio:
            raise
        except Exception:
            raise ErroNegocio(
                502,
                "Falha de recomendação",
                "Provedor não produziu saída válida; nenhuma recomendação gravada.",
            ) from None
        with self.sessao.begin():
            bloquear_configuracao(self.sessao)
            self.modelos.modelos.exigir(ce.id_modelo)
            self.modelos.modelos.exigir(ct.id_modelo)
            self.modelos.conexoes.exigir(me.id_conexao)
            self.modelos.conexoes.exigir(mt.id_conexao)
            self.demandas.territorio(contexto.demanda.id_area_afetada)
            self.demandas.repo.exigir(id_demanda, bloquear=True)
            self.sessao.expire_all()
            atual = self.contexto(id_demanda)
            if hash_contexto(atual) != hash_contexto(contexto):
                raise ErroNegocio(
                    409,
                    "Contexto alterado",
                    "Pedido ou candidatos mudaram durante a análise; gere novamente.",
                )
            validar_proposta(atual, p)
            r = Recomendacao(
                id_demanda=id_demanda,
                id_modelo_embedding=ce.id_modelo,
                id_modelo_inferencia=ct.id_modelo,
                hash_contexto=hash_contexto(atual),
                justificativa=p.justificativa,
                pendencias=list(p.pendencias) + atual.limites,
                criado_por=sujeito,
                atualizado_por=sujeito,
            )
            self.sessao.add(r)
            self.sessao.flush()
            self.persistir_itens(r, p, sujeito)
            resultado = self.visualizar(r)
        return resultado

    def persistir_itens(self, r: Recomendacao, p: PropostaDemanda, sujeito: str) -> None:
        totais: dict[UUID, Decimal] = {}
        for i in p.itens:
            item = RecomendacaoItem(
                id_recomendacao=r.id,
                id_demanda_item=i.id_demanda_item,
                quantidade_sugerida=i.quantidade_sugerida,
                justificativa=i.justificativa,
                criado_por=sujeito,
                atualizado_por=sujeito,
            )
            self.sessao.add(item)
            self.sessao.flush()
            for pessoa in i.pessoas:
                self.sessao.add(
                    RecomendacaoPessoa(
                        id_recomendacao_item=item.id,
                        id_pessoa=pessoa.id_pessoa,
                        id_oferta_atividade=pessoa.id_oferta_atividade,
                        papel_sugerido=pessoa.papel_sugerido,
                        criado_por=sujeito,
                        atualizado_por=sujeito,
                    )
                )
            for instituicao in i.instituicoes:
                self.sessao.add(
                    RecomendacaoInstituicao(
                        id_recomendacao_item=item.id,
                        id_instituicao=instituicao.id_instituicao,
                        id_oferta_atividade=instituicao.id_oferta_atividade,
                        criado_por=sujeito,
                        atualizado_por=sujeito,
                    )
                )
            for recurso in i.recursos:
                self.sessao.add(
                    RecomendacaoRecurso(
                        id_recomendacao_item=item.id,
                        id_recurso=recurso.id_recurso,
                        quantidade_sugerida=recurso.quantidade_sugerida,
                        criado_por=sujeito,
                        atualizado_por=sujeito,
                    )
                )
                totais[recurso.id_recurso] = (
                    totais.get(recurso.id_recurso, Decimal(0)) + recurso.quantidade_sugerida
                )
        for id, total in totais.items():
            bem = self.sessao.get(Recurso, id)
            assert bem is not None
            if total > bem.quantidade_total:
                r.pendencias = [
                    *r.pendencias,
                    f"Recurso {bem.nome}: sugestões somam {total}, "
                    f"total cadastrado {bem.quantidade_total}; revise sobreposição.",
                ]
        self.sessao.flush()

    def visualizar(self, r: Recomendacao) -> RecomendacaoVM:
        vm = RecomendacaoVM.model_validate(r)
        from core.ia_operacao import InstituicaoSugerida, PessoaSugerida, RecursoSugerido

        for item in self.sessao.scalars(
            select(RecomendacaoItem)
            .where(recomendacao_itens.c.id_recomendacao == r.id)
            .order_by(recomendacao_itens.c.id)
        ):
            pessoas = list(
                self.sessao.scalars(
                    select(RecomendacaoPessoa).where(
                        recomendacao_pessoas.c.id_recomendacao_item == item.id
                    )
                )
            )
            instituicoes = list(
                self.sessao.scalars(
                    select(RecomendacaoInstituicao).where(
                        recomendacao_instituicoes.c.id_recomendacao_item == item.id
                    )
                )
            )
            bens = list(
                self.sessao.scalars(
                    select(RecomendacaoRecurso).where(
                        recomendacao_recursos.c.id_recomendacao_item == item.id
                    )
                )
            )
            for candidato in pessoas:
                pessoa = self.sessao.get(Pessoa, candidato.id_pessoa)
                if pessoa:
                    vm.nomes_candidatos[pessoa.id] = pessoa.nome
            for candidato_instituicao in instituicoes:
                instituicao = self.sessao.get(Instituicao, candidato_instituicao.id_instituicao)
                if instituicao:
                    vm.nomes_candidatos[instituicao.id] = instituicao.nome
            for candidato_recurso in bens:
                recurso = self.sessao.get(Recurso, candidato_recurso.id_recurso)
                if recurso:
                    vm.nomes_candidatos[recurso.id] = recurso.nome
            vm.itens.append(
                RecomendacaoItemVM(
                    id=item.id,
                    id_demanda_item=item.id_demanda_item,
                    quantidade_sugerida=item.quantidade_sugerida,
                    justificativa=item.justificativa,
                    pessoas=[
                        PessoaSugerida.model_validate(x, from_attributes=True) for x in pessoas
                    ],
                    instituicoes=[
                        InstituicaoSugerida.model_validate(x, from_attributes=True)
                        for x in instituicoes
                    ],
                    recursos=[
                        RecursoSugerido.model_validate(x, from_attributes=True) for x in bens
                    ],
                )
            )
        return vm

    def decidir(self, id: UUID, dados: DecisaoInput, sujeito: str) -> RecomendacaoVM:
        with self.sessao.begin():
            previa = self.repo.exigir(id)
            if dados.situacao == "aprovada":
                pedido = self.demandas.repo.exigir(previa.id_demanda)
                self.demandas.territorio(pedido.id_area_afetada)
                self.demandas.repo.exigir(pedido.id, bloquear=True)
            r = self.repo.exigir(id, bloquear=True)
            if r.situacao != SituacaoRecomendacao.GERADA:
                raise ErroNegocio(
                    409,
                    "Decisão registrada",
                    "A decisão é final; gere nova análise para reavaliar.",
                )
            if (
                dados.situacao == "aprovada"
                and hash_contexto(self.contexto(r.id_demanda)) != r.hash_contexto
            ):
                raise ErroNegocio(
                    409, "Análise desatualizada", "Pedido/candidatos mudaram; gere nova análise."
                )
            r.situacao = SituacaoRecomendacao(dados.situacao)
            r.justificativa_decisao, r.decidida_em, r.decidida_por = (
                dados.justificativa,
                agora_utc(),
                sujeito,
            )
            auditar(r, sujeito)
            resultado = self.visualizar(r)
        return resultado
