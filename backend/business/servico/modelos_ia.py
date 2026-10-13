from uuid import UUID

from pydantic import SecretStr
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from business.servico.qualificacoes import auditar
from business.view_models.operacao import ConexaoInput, ConexaoVM, ModeloInput, ModeloVM
from core.entity.operacao import ConexaoIA, FinalidadeModeloIA, ModeloIA, TipoAutenticacaoIA
from core.http.contratos import ErroNegocio
from core.ia_operacao import ConfiguracaoModelo
from infra.configurations.capacidades import atividades
from infra.configurations.indices import atividade_indice_semantico as indices
from infra.configurations.modelos_ia import conexao_ia, modelo_ia
from infra.database.operacao import OperacaoRepositorio, bloquear_configuracao
from infra.ia.credenciais import CofreCredenciais


class ModelosIAService:
    def __init__(
        self,
        sessao: Session,
        chave: SecretStr | None,
        identificador_chave: str,
        urls_permitidas: list[str],
    ) -> None:
        self.sessao: Session = sessao
        self.chave: SecretStr | None = chave
        self.identificador_chave: str = identificador_chave
        self.urls_permitidas: list[str] = urls_permitidas
        self.conexoes = OperacaoRepositorio(sessao, ConexaoIA, conexao_ia)
        self.modelos = OperacaoRepositorio(sessao, ModeloIA, modelo_ia)

    def cofre(self) -> CofreCredenciais:
        if self.chave is None:
            raise ErroNegocio(
                503, "Cofre indisponível", "Configure a chave externa de criptografia."
            )
        try:
            return CofreCredenciais(self.chave)
        except ValueError:
            raise ErroNegocio(
                503, "Cofre indisponível", "Chave de criptografia inválida."
            ) from None

    def conexao_vm(self, e: ConexaoIA) -> ConexaoVM:
        vm = ConexaoVM.model_validate(e)
        vm.tem_token = e.token_criptografado is not None
        return vm

    def modelo_vm(self, e: ModeloIA) -> ModeloVM:
        vm = ModeloVM.model_validate(e)
        c = self.conexoes.exigir(e.id_conexao, True)
        vm.conexao_nome, vm.conexao_inativa = c.nome, c.inativado_em is not None
        return vm

    def salvar_conexao(self, id: UUID | None, dados: ConexaoInput, sujeito: str) -> ConexaoVM:
        with self.sessao.begin():
            bloquear_configuracao(self.sessao)
            e = (
                self.conexoes.exigir(id, bloquear=True)
                if id
                else ConexaoIA(
                    nome=dados.nome,
                    provedor=dados.provedor,
                    url_base=dados.url_base,
                    tipo_autenticacao=dados.tipo_autenticacao,
                    criado_por=sujeito,
                    atualizado_por=sujeito,
                )
            )
            usados = self.sessao.scalar(
                select(func.count()).select_from(modelo_ia).where(modelo_ia.c.id_conexao == e.id)
            )
            if usados and (e.provedor, e.url_base, e.tipo_autenticacao) != (
                dados.provedor,
                dados.url_base,
                dados.tipo_autenticacao,
            ):
                raise ErroNegocio(
                    409, "Conexão utilizada", "Crie outra conexão para mudar endpoint/adaptador."
                )
            e.nome, e.provedor, e.url_base = dados.nome, dados.provedor, dados.url_base
            e.tipo_autenticacao = dados.tipo_autenticacao
            if dados.tipo_autenticacao == TipoAutenticacaoIA.NENHUMA:
                if dados.token is not None:
                    raise ErroNegocio(
                        422, "Credencial incompatível", "Conexão sem autenticação não recebe token."
                    )
                e.token_criptografado, e.identificador_chave = None, None
            elif dados.token is not None:
                e.token_criptografado = self.cofre().criptografar(dados.token)
                e.identificador_chave = self.identificador_chave
            elif e.token_criptografado is None:
                raise ErroNegocio(
                    422, "Credencial obrigatória", "Informe token na criação da conexão bearer."
                )
            auditar(e, sujeito)
            self.sessao.add(e)
            self.sessao.flush()
            resultado = self.conexao_vm(e)
        return resultado

    def cobertura(self, modelo: ModeloIA) -> None:
        faltantes = self.sessao.scalar(
            select(func.count())
            .select_from(atividades)
            .where(
                atividades.c.inativado_em.is_(None),
                ~select(indices.c.id)
                .where(
                    indices.c.id_atividade == atividades.c.id,
                    indices.c.id_modelo == modelo.id,
                    indices.c.inativado_em.is_(None),
                    indices.c.situacao_indexacao == "pronta",
                    indices.c.hash_atividade_origem == atividades.c.hash_conteudo_semantico,
                )
                .exists(),
            )
        )
        if faltantes:
            raise ErroNegocio(
                409,
                "Cobertura incompleta",
                "Indexe todas as atividades ativas antes de selecionar.",
            )

    def selecionar(self, e: ModeloIA, sujeito: str) -> None:
        self.conexoes.exigir(e.id_conexao)
        if e.finalidade == FinalidadeModeloIA.EMBEDDING:
            # Impede mudança dos hashes durante a verificação de cobertura.
            list(
                self.sessao.scalars(
                    select(atividades.c.id).order_by(atividades.c.id).with_for_update(read=True)
                )
            )
            self.cobertura(e)
        anteriores = list(
            self.sessao.scalars(
                select(ModeloIA)
                .where(
                    modelo_ia.c.finalidade == e.finalidade,
                    modelo_ia.c.ativo.is_(True),
                    modelo_ia.c.id != e.id,
                )
                .with_for_update()
            )
        )
        for anterior in anteriores:
            anterior.ativo = False
            auditar(anterior, sujeito)
        self.sessao.flush()
        e.ativo = True

    def salvar_modelo(self, id: UUID | None, dados: ModeloInput, sujeito: str) -> ModeloVM:
        with self.sessao.begin():
            bloquear_configuracao(self.sessao)
            self.conexoes.exigir(dados.id_conexao)
            e = (
                self.modelos.exigir(id, bloquear=True)
                if id
                else ModeloIA(
                    id_conexao=dados.id_conexao,
                    identificador_modelo=dados.identificador_modelo,
                    revisao=dados.revisao,
                    finalidade=dados.finalidade,
                    dimensao=dados.dimensao,
                    criado_por=sujeito,
                    atualizado_por=sujeito,
                )
            )
            identidade = (e.id_conexao, e.identificador_modelo, e.revisao, e.finalidade, e.dimensao)
            if identidade != (
                dados.id_conexao,
                dados.identificador_modelo,
                dados.revisao,
                dados.finalidade,
                dados.dimensao,
            ):
                raise ErroNegocio(
                    409, "Modelo imutável", "Crie outro modelo para alterar sua identidade."
                )
            self.sessao.add(e)
            self.sessao.flush()
            if dados.ativo:
                self.selecionar(e, sujeito)
            else:
                e.ativo = False
            auditar(e, sujeito)
            self.sessao.flush()
            resultado = self.modelo_vm(e)
        return resultado

    def inativar_conexao(self, id: UUID, sujeito: str) -> ConexaoVM:
        with self.sessao.begin():
            bloquear_configuracao(self.sessao)
            e = self.conexoes.exigir(id, bloquear=True)
            if self.sessao.scalar(
                select(modelo_ia.c.id)
                .where(modelo_ia.c.id_conexao == id, modelo_ia.c.ativo.is_(True))
                .limit(1)
            ):
                raise ErroNegocio(
                    409, "Conexão selecionada", "Desmarque seus modelos ativos primeiro."
                )
            auditar(e, sujeito)
            e.inativado_em = e.atualizado_em
            resultado = self.conexao_vm(e)
        return resultado

    def inativar_modelo(self, id: UUID, sujeito: str) -> ModeloVM:
        with self.sessao.begin():
            bloquear_configuracao(self.sessao)
            e = self.modelos.exigir(id, bloquear=True)
            e.ativo = False
            auditar(e, sujeito)
            e.inativado_em = e.atualizado_em
            resultado = self.modelo_vm(e)
        return resultado

    def configuracao(self, id: UUID) -> ConfiguracaoModelo:
        e = self.modelos.exigir(id)
        c = self.conexoes.exigir(e.id_conexao)
        if c.url_base not in [url.rstrip("/") for url in self.urls_permitidas]:
            raise ErroNegocio(
                503, "Endpoint não habilitado", "Habilite a URL exata na configuração do servidor."
            )
        token = SecretStr("sem-autenticacao")
        if c.tipo_autenticacao == TipoAutenticacaoIA.BEARER:
            if c.identificador_chave != self.identificador_chave or c.token_criptografado is None:
                raise ErroNegocio(
                    503, "Chave incompatível", "Credencial requer a chave externa identificada."
                )
            try:
                token = self.cofre().descriptografar(c.token_criptografado)
            except ValueError:
                raise ErroNegocio(
                    503, "Cofre indisponível", "Não foi possível abrir a credencial."
                ) from None
        return ConfiguracaoModelo(
            id_modelo=e.id,
            identificador_modelo=e.identificador_modelo,
            revisao=e.revisao,
            dimensao=e.dimensao,
            url_base=c.url_base,
            token=token,
            sem_autenticacao=c.tipo_autenticacao == TipoAutenticacaoIA.NENHUMA,
        )

    def ativo(self, finalidade: FinalidadeModeloIA) -> ModeloIA:
        id = self.sessao.scalar(
            select(modelo_ia.c.id).where(
                modelo_ia.c.finalidade == finalidade,
                modelo_ia.c.ativo.is_(True),
                modelo_ia.c.inativado_em.is_(None),
            )
        )
        if id is None:
            raise ErroNegocio(
                409, "Modelo não selecionado", f"Selecione modelo de {finalidade.value}."
            )
        return self.modelos.exigir(id)
