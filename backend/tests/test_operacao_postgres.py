from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import Engine, select, text, update
from sqlalchemy.orm import Session

from business.view_models.desastres import AreaAfetadaVM
from business.view_models.operacao import (
    ConexaoInput,
    ConexaoVM,
    DemandaInput,
    DemandaItemInput,
    DemandaVM,
    ModeloInput,
    ModeloVM,
    RecomendacaoVM,
)
from core.entity.operacao import ConexaoIA, FinalidadeModeloIA, SituacaoDemanda
from infra.configurations.capacidades import atividades
from infra.configurations.modelos_ia import modelo_ia
from infra.configurations.recursos import ofertas_atividade, recursos
from tests.conftest import token_teste
from tests.fakes_ia import FabricaFicticia
from tests.test_desastres_postgres import area_input, ocorrencia
from tests.test_recursos_postgres import (
    Cenario,
    cenario,
    criar,
)
from tests.test_recursos_postgres import (
    banco_recursos as banco_recursos,
)
from web.main import create_app
from web.settings import Settings

pytestmark = pytest.mark.postgres


@dataclass
class AmbienteIA:
    api: TestClient
    clientes: FabricaFicticia
    chave: bytes


@pytest.fixture
def ambiente(banco_recursos: Engine, settings: Settings) -> Iterator[AmbienteIA]:
    chave = Fernet.generate_key()
    config = settings.model_copy(
        update={
            "encryption_key": SecretStr(chave.decode("ascii")),
            "ia_urls_permitidas": ["https://provedor.invalid/v1"],
        }
    )
    fabrica = FabricaFicticia()
    with TestClient(
        create_app(config, banco_recursos, fabrica), raise_server_exceptions=False
    ) as api:
        api.headers["Authorization"] = f"Bearer {token_teste()}"
        yield AmbienteIA(api, fabrica, chave)


def conexao(api: TestClient, bearer: bool = False) -> ConexaoVM:
    resposta = api.post(
        "/api/v1/conexoes-ia",
        json={
            "nome": "Conexão fictícia",
            "url_base": "https://provedor.invalid/v1",
            "tipo_autenticacao": "bearer" if bearer else "nenhuma",
            "token": "token-ficticio" if bearer else None,
        },
    )
    assert resposta.status_code == 201, resposta.text
    return ConexaoVM.model_validate(resposta.json()["data"])


def modelo(
    api: TestClient,
    c: ConexaoVM,
    finalidade: FinalidadeModeloIA,
    dimensao: int | None = None,
    ativo: bool = False,
) -> ModeloVM:
    return criar(
        api,
        "modelos-ia",
        ModeloInput(
            id_conexao=c.id,
            identificador_modelo=f"ficticio-{finalidade.value}-{dimensao}",
            finalidade=finalidade,
            dimensao=dimensao,
            ativo=ativo,
        ),
        ModeloVM,
    )


def selecionar(api: TestClient, m: ModeloVM, ativo: bool = True) -> int:
    return api.put(
        f"/api/v1/modelos-ia/{m.id}",
        json=ModeloInput(
            id_conexao=m.id_conexao,
            identificador_modelo=m.identificador_modelo,
            finalidade=m.finalidade,
            dimensao=m.dimensao,
            ativo=ativo,
        ).model_dump(mode="json"),
    ).status_code


def indexar(api: TestClient, m: ModeloVM, c: Cenario) -> None:
    r = api.post(
        "/api/v1/indices-atividade/indexar",
        json={"id_modelo": str(m.id), "ids_atividades": [str(c.atividade.id)]},
    )
    assert r.status_code == 200, r.text


def pedido(api: TestClient, c: Cenario) -> tuple[DemandaVM, DemandaInput]:
    d, _, _ = ocorrencia(api)
    area = criar(api, f"desastres/{d.id}/areas", area_input(), AreaAfetadaVM)
    assert c.atividade.id_unidade_capacidade is not None
    inicio = datetime(2026, 10, 9, 9, tzinfo=UTC)
    dados = DemandaInput(
        id_area_afetada=area.id,
        id_pessoa_solicitante=c.pessoa.id,
        titulo="Pedido fictício",
        descricao="Transporte e equipamentos",
        prioridade="urgente",
        inicio_previsto_em=inicio,
        prazo_em=inicio + timedelta(hours=3),
        itens=[
            DemandaItemInput(
                id_atividade=c.atividade.id,
                id_unidade_medida=c.atividade.id_unidade_capacidade,
                quantidade_solicitada=Decimal(2),
            ),
            DemandaItemInput(
                id_tipo_recurso=c.tipo.id,
                id_unidade_medida=c.tipo.id_unidade_medida,
                quantidade_solicitada=Decimal(3),
            ),
        ],
    )
    return criar(api, "demandas", dados, DemandaVM), dados


def preparar(ambiente: AmbienteIA) -> tuple[Cenario, DemandaVM, ModeloVM, ModeloVM]:
    api = ambiente.api
    c = cenario(api, estoque=True)
    dados_pessoa = api.get(f"/api/v1/pessoas/{c.pessoa.id}").json()["data"]
    from business.view_models.cadastros import PessoaInput

    dados = {k: v for k, v in dados_pessoa.items() if k in PessoaInput.model_fields}
    dados["situacao_cadastral"] = "validada"
    assert api.put(f"/api/v1/pessoas/{c.pessoa.id}", json=dados).status_code == 200
    oferta = api.get(f"/api/v1/ofertas-atividade/{c.oferta.id}").json()["data"]
    from business.view_models.recursos import OfertaAtividadeInput

    dados_oferta = {k: v for k, v in oferta.items() if k in OfertaAtividadeInput.model_fields}
    dados_oferta["situacao_validacao"] = "validada"
    assert api.put(f"/api/v1/ofertas-atividade/{c.oferta.id}", json=dados_oferta).status_code == 200
    d, _ = pedido(api, c)
    con = conexao(api)
    me = modelo(api, con, FinalidadeModeloIA.EMBEDDING, 3)
    mt = modelo(api, con, FinalidadeModeloIA.TEXTO, ativo=True)
    indexar(api, me, c)
    assert selecionar(api, me) == 200
    return c, d, me, mt


def test_credencial_cifrada_nunca_retornada_rotacao_e_endpoint_estavel(
    ambiente: AmbienteIA,
    banco_recursos: Engine,
) -> None:
    api = ambiente.api
    c = conexao(api, True)
    assert c.tem_token
    resposta = api.get(f"/api/v1/conexoes-ia/{c.id}")
    assert "token-ficticio" not in resposta.text and "token_criptografado" not in resposta.text
    with Session(banco_recursos) as s:
        e = s.get(ConexaoIA, c.id)
        assert e is not None and e.token_criptografado is not None
        cifrado = e.token_criptografado
        assert b"token-ficticio" not in cifrado
        assert Fernet(ambiente.chave).decrypt(cifrado) == b"token-ficticio"
    assert (
        api.put(
            f"/api/v1/conexoes-ia/{c.id}",
            json={"nome": c.nome, "url_base": c.url_base, "tipo_autenticacao": "bearer"},
        ).status_code
        == 200
    )
    modelo(api, c, FinalidadeModeloIA.TEXTO, ativo=True)
    assert api.delete(f"/api/v1/conexoes-ia/{c.id}").status_code == 409
    assert (
        api.put(
            f"/api/v1/conexoes-ia/{c.id}",
            json={
                "nome": c.nome,
                "url_base": "https://outro.invalid/v1",
                "tipo_autenticacao": "bearer",
            },
        ).status_code
        == 409
    )
    assert (
        api.put(
            f"/api/v1/conexoes-ia/{c.id}",
            json={
                "nome": c.nome,
                "url_base": c.url_base,
                "tipo_autenticacao": "bearer",
                "token": "token-rotacionado",
            },
        ).status_code
        == 200
    )
    with Session(banco_recursos) as s:
        e = s.get(ConexaoIA, c.id)
        assert e is not None and e.token_criptografado != cifrado


def test_selecao_concorrente_unica_e_identidade_imutavel(
    ambiente: AmbienteIA, banco_recursos: Engine
) -> None:
    api = ambiente.api
    c = conexao(api)
    m1 = modelo(api, c, FinalidadeModeloIA.TEXTO)
    m2 = modelo(api, c, FinalidadeModeloIA.TEXTO)
    with ThreadPoolExecutor(2) as pool:
        resultados = list(pool.map(lambda m: selecionar(api, m), [m1, m2]))
    assert resultados == [200, 200]
    with banco_recursos.connect() as conn:
        assert len(list(conn.scalars(select(modelo_ia.c.id).where(modelo_ia.c.ativo)))) == 1
    dados = ModeloInput(
        id_conexao=c.id, identificador_modelo="alterado", finalidade=FinalidadeModeloIA.TEXTO
    )
    assert (
        api.put(f"/api/v1/modelos-ia/{m1.id}", json=dados.model_dump(mode="json")).status_code
        == 409
    )


def test_embedding_cobertura_dimensoes_e_inativacao(ambiente: AmbienteIA) -> None:
    api = ambiente.api
    c = cenario(api)
    con = conexao(api)
    m3 = modelo(api, con, FinalidadeModeloIA.EMBEDDING, 3)
    m4 = modelo(api, con, FinalidadeModeloIA.EMBEDDING, 4)
    assert selecionar(api, m3) == 409
    indexar(api, m3, c)
    assert selecionar(api, m3) == 200
    indexar(api, m4, c)
    assert selecionar(api, m4) == 200
    r = api.post("/api/v1/atividades/busca-semantica", json={"texto": "transporte"})
    assert r.status_code == 200, r.text
    assert r.json()["data"]["id_modelo"] == str(m4.id)
    assert len(api.get("/api/v1/indices-atividade").json()["data"]) == 2
    assert api.delete(f"/api/v1/modelos-ia/{m4.id}").status_code == 200
    assert (
        api.post("/api/v1/atividades/busca-semantica", json={"texto": "transporte"}).status_code
        == 409
    )


def test_invalida_hash_atomicamente_e_rejeita_publicacao_obsoleta(
    ambiente: AmbienteIA, banco_recursos: Engine
) -> None:
    api = ambiente.api
    c = cenario(api)
    m = modelo(api, conexao(api), FinalidadeModeloIA.EMBEDDING, 3)
    indexar(api, m, c)
    assert (
        api.post(f"/api/v1/atividades/{c.atividade.id}/termos", json={"termo": "carga"}).status_code
        == 201
    )
    assert not api.get("/api/v1/indices-atividade").json()["data"][0]["atualizado"]

    def alterar() -> None:
        with banco_recursos.begin() as conn:
            conn.execute(
                update(atividades)
                .where(atividades.c.id == c.atividade.id)
                .values(hash_conteudo_semantico="a" * 64)
            )

    ambiente.clientes.acao = alterar
    r = api.post(
        "/api/v1/indices-atividade/indexar",
        json={"id_modelo": str(m.id), "ids_atividades": [str(c.atividade.id)]},
    )
    assert r.status_code == 409, r.text


def test_falha_provedor_sanitizada_e_endpoint_nao_habilitado(ambiente: AmbienteIA) -> None:
    api = ambiente.api
    c = cenario(api)
    m = modelo(api, conexao(api), FinalidadeModeloIA.EMBEDDING, 3)
    ambiente.clientes.falhar = True
    r = api.post(
        "/api/v1/indices-atividade/indexar",
        json={"id_modelo": str(m.id), "ids_atividades": [str(c.atividade.id)]},
    )
    assert r.status_code == 502 and "token-ficticio" not in r.text
    assert api.get("/api/v1/indices-atividade").json()["data"] == []
    con = criar(
        api,
        "conexoes-ia",
        ConexaoInput(
            nome="Bloqueada", url_base="https://bloqueado.invalid/v1", tipo_autenticacao="nenhuma"
        ),
        ConexaoVM,
    )
    bloqueado = modelo(api, con, FinalidadeModeloIA.EMBEDDING, 3)
    r = api.post(
        "/api/v1/indices-atividade/indexar",
        json={"id_modelo": str(bloqueado.id), "ids_atividades": [str(c.atividade.id)]},
    )
    assert r.status_code == 503


def test_demanda_agregado_item_escopo_unidade_e_historico(ambiente: AmbienteIA) -> None:
    api = ambiente.api
    c = cenario(api)
    d, dados = pedido(api, c)
    assert len(d.itens) == 2 and d.prioridade == "urgente"
    dados.itens[0].id = d.itens[0].id
    dados.itens[1].id = UUID(int=99999)
    assert (
        api.put(f"/api/v1/demandas/{d.id}", json=dados.model_dump(mode="json")).status_code == 404
    )
    dados.itens = [dados.itens[0]]
    r = api.put(f"/api/v1/demandas/{d.id}", json=dados.model_dump(mode="json"))
    assert r.status_code == 200, r.text
    assert len(r.json()["data"]["itens"]) == 1
    assert (
        len(api.get(f"/api/v1/demandas/{d.id}?incluir_inativos=true").json()["data"]["itens"]) == 2
    )
    dados.situacao = SituacaoDemanda.CANCELADA
    assert (
        api.put(f"/api/v1/demandas/{d.id}", json=dados.model_dump(mode="json")).status_code == 200
    )
    dados.situacao = SituacaoDemanda.ABERTA
    assert (
        api.put(f"/api/v1/demandas/{d.id}", json=dados.model_dump(mode="json")).status_code == 409
    )


def test_demanda_unidade_protegida_e_estados_de_execucao_bloqueados(
    ambiente: AmbienteIA, banco_recursos: Engine
) -> None:
    api = ambiente.api
    c = cenario(api)
    d, dados = pedido(api, c)
    dados.situacao = SituacaoDemanda.CONCLUIDA
    assert (
        api.put(f"/api/v1/demandas/{d.id}", json=dados.model_dump(mode="json")).status_code == 409
    )
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError), banco_recursos.begin() as conn:
        conn.execute(
            update(atividades)
            .where(atividades.c.id == c.atividade.id)
            .values(id_unidade_capacidade=None)
        )
    assert api.delete(f"/api/v1/demandas/{d.id}").status_code == 200
    assert api.get(f"/api/v1/demandas/{d.id}").status_code == 404
    assert api.get(f"/api/v1/demandas/{d.id}?incluir_inativos=true").status_code == 200


def test_recomendacao_completa_decisao_preserva_pedido_e_estoque(
    ambiente: AmbienteIA, banco_recursos: Engine
) -> None:
    api = ambiente.api
    c, d, me, mt = preparar(ambiente)
    antes = api.get(f"/api/v1/demandas/{d.id}").json()
    r = api.post(f"/api/v1/demandas/{d.id}/recomendacoes")
    assert r.status_code == 201, r.text
    rec = RecomendacaoVM.model_validate(r.json()["data"])
    assert rec.id_modelo_embedding == me.id and rec.id_modelo_inferencia == mt.id
    assert (
        len(rec.itens) == 2
        and any(i.pessoas for i in rec.itens)
        and any(i.recursos for i in rec.itens)
    )
    assert str(c.pessoa.id) in r.json()["data"]["nomes_candidatos"]
    decisao = api.post(
        f"/api/v1/recomendacoes/{rec.id}/decisao",
        json={"situacao": "aprovada", "justificativa": "Revisado pelo administrador"},
    )
    assert decisao.status_code == 200, decisao.text
    assert decisao.json()["data"]["decidida_por"] == "administrador-teste"
    assert (
        api.post(
            f"/api/v1/recomendacoes/{rec.id}/decisao",
            json={"situacao": "rejeitada", "justificativa": "Não pode sobrescrever"},
        ).status_code
        == 409
    )
    assert api.get(f"/api/v1/demandas/{d.id}").json() == antes
    with banco_recursos.connect() as conn:
        assert conn.scalar(
            select(recursos.c.quantidade_total).where(recursos.c.id == c.recurso.id)
        ) == Decimal("20.5000")
    assert api.post(f"/api/v1/demandas/{d.id}/recomendacoes").status_code == 201
    assert len(api.get(f"/api/v1/recomendacoes?id_demanda={d.id}").json()["data"]) == 2


def test_recomendacao_inventada_nao_persistida(ambiente: AmbienteIA) -> None:
    _, d, _, _ = preparar(ambiente)
    ambiente.clientes.inventar = True
    r = ambiente.api.post(f"/api/v1/demandas/{d.id}/recomendacoes")
    assert r.status_code == 502, r.text
    assert ambiente.api.get("/api/v1/recomendacoes").json()["data"] == []


def test_candidato_alterado_durante_ia_rejeita_gravacao(
    ambiente: AmbienteIA, banco_recursos: Engine
) -> None:
    c, d, _, _ = preparar(ambiente)

    def alterar() -> None:
        with banco_recursos.begin() as conn:
            conn.execute(
                update(ofertas_atividade)
                .where(ofertas_atividade.c.id == c.oferta.id)
                .values(situacao_validacao="rejeitada", validado_em=None)
            )

    ambiente.clientes.acao_texto = alterar
    r = ambiente.api.post(f"/api/v1/demandas/{d.id}/recomendacoes")
    assert r.status_code == 409, r.text
    assert ambiente.api.get("/api/v1/recomendacoes").json()["data"] == []


def test_aprovacao_desatualizada_recusada_rejeicao_permitida(
    ambiente: AmbienteIA, banco_recursos: Engine
) -> None:
    api = ambiente.api
    c, d, _, _ = preparar(ambiente)
    r = api.post(f"/api/v1/demandas/{d.id}/recomendacoes")
    assert r.status_code == 201, r.text
    id = r.json()["data"]["id"]
    with banco_recursos.begin() as conn:
        conn.execute(
            update(recursos).where(recursos.c.id == c.recurso.id).values(quantidade_total=0)
        )
    assert (
        api.post(
            f"/api/v1/recomendacoes/{id}/decisao",
            json={"situacao": "aprovada", "justificativa": "Revisão"},
        ).status_code
        == 409
    )
    assert (
        api.post(
            f"/api/v1/recomendacoes/{id}/decisao",
            json={"situacao": "rejeitada", "justificativa": "Estoque mudou"},
        ).status_code
        == 200
    )


def test_sql_rejeita_vetor_com_dimensao_errada(
    ambiente: AmbienteIA, banco_recursos: Engine
) -> None:
    api = ambiente.api
    c = cenario(api)
    m = modelo(api, conexao(api), FinalidadeModeloIA.EMBEDDING, 3)
    indexar(api, m, c)
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError), banco_recursos.begin() as conn:
        conn.execute(text("UPDATE atividade_indice_semantico SET embedding = ARRAY[1.0, 2.0]"))
