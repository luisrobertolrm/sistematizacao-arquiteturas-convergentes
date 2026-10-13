import os
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy import Engine, create_engine, insert, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from business.view_models.cadastros import InstituicaoInput, InstituicaoVM, PessoaInput, PessoaVM
from business.view_models.qualificacoes import (
    CursoInput,
    CursoVM,
    PessoaCursoInput,
    PessoaCursoVM,
    PessoaInstituicaoInput,
    PessoaInstituicaoVM,
    PessoaProfissaoInput,
    PessoaProfissaoVM,
    ProfissaoInput,
    ProfissaoVM,
)
from core.entity.cadastros import Instituicao, agora_utc
from core.entity.qualificacoes import PessoaCurso, PessoaInstituicao, SituacaoValidacao, TipoVinculo
from core.http.contratos import ApiResponse, Problema
from infra.configurations.cadastros import instituicoes
from tests.conftest import token_teste
from web.main import create_app
from web.settings import Settings

pytestmark = pytest.mark.postgres


@pytest.fixture
def banco() -> Iterator[Engine]:
    url: str | None = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Executar scripts/test_postgres.py para testar PostgreSQL real.")
    if make_url(url).database != "redesolidaria_test":
        pytest.fail("Os testes só aceitam o banco dedicado redesolidaria_test.")
    engine: Engine = create_engine(url, hide_parameters=True)
    with engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE TABLE recomendacao_recursos, recomendacao_instituicoes, "
                "recomendacao_pessoas, recomendacao_itens, recomendacoes, "
                "atividade_indice_semantico, modelo_ia, conexao_ia, demanda_itens, demandas, "
                "areas_afetadas, desastre_tipo, desastres, tipos_desastre, "
                "oferta_atividade_recurso, ofertas_atividade, recursos, "
                "tipos_recurso, "
                "pessoa_curso, pessoa_profissao, pessoa_instituicao, "
                "cursos, profissoes, instituicoes, pessoas"
            )
        )
    yield engine
    engine.dispose()


@pytest.fixture
def api(banco: Engine, settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings, banco), raise_server_exceptions=False) as client:
        client.headers["Authorization"] = f"Bearer {token_teste()}"
        yield client


def instituicao_input() -> InstituicaoInput:
    return InstituicaoInput(
        nome="Associação de teste",
        municipio_codigo_ibge="3550308",
        uf="SP",
        tipo="associacao",
        cnpj="12.345.678/0001-95",
    )


def test_ciclo_instituicao_e_auditoria(api: TestClient, banco: Engine) -> None:
    dados: InstituicaoInput = instituicao_input()
    criada = api.post("/api/v1/instituicoes", json=dados.model_dump(mode="json"))
    assert criada.status_code == 201, criada.text
    assert "messages" not in criada.json()
    vm: InstituicaoVM = ApiResponse[InstituicaoVM].model_validate(criada.json()).data
    assert vm.cnpj == "12345678000195" and vm.criado_em.utcoffset() is not None
    assert api.get(f"/api/v1/instituicoes/{vm.id}").status_code == 200
    editada = api.put(
        f"/api/v1/instituicoes/{vm.id}",
        json=dados.model_copy(update={"nome": "Nome atualizado"}).model_dump(mode="json"),
    )
    assert editada.status_code == 200
    assert ApiResponse[InstituicaoVM].model_validate(editada.json()).data.nome == "Nome atualizado"
    assert api.delete(f"/api/v1/instituicoes/{vm.id}").status_code == 200
    assert api.get(f"/api/v1/instituicoes/{vm.id}").status_code == 404
    assert (
        ApiResponse[list[InstituicaoVM]].model_validate(api.get("/api/v1/instituicoes").json()).data
        == []
    )
    with Session(banco) as sessao:
        persistida: Instituicao | None = sessao.scalar(select(Instituicao))
        assert persistida is not None and persistida.inativado_em is not None
        assert persistida.criado_por == persistida.atualizado_por == "administrador-teste"


def test_pessoa_email_nao_e_identidade_e_inativacao(api: TestClient) -> None:
    dados: PessoaInput = PessoaInput(
        nome="Voluntária",
        municipio_codigo_ibge="3550308",
        uf="SP",
        email_contato="grupo@example.com",
    )
    primeira = api.post("/api/v1/pessoas", json=dados.model_dump(mode="json"))
    segunda = api.post("/api/v1/pessoas", json=dados.model_dump(mode="json"))
    assert primeira.status_code == segunda.status_code == 201
    vm: PessoaVM = ApiResponse[PessoaVM].model_validate(primeira.json()).data
    assert (
        api.put(
            f"/api/v1/pessoas/{vm.id}",
            json=dados.model_copy(update={"nome": "Nome novo"}).model_dump(mode="json"),
        ).status_code
        == 200
    )
    assert api.delete(f"/api/v1/pessoas/{vm.id}").status_code == 200
    assert api.get(f"/api/v1/pessoas/{vm.id}").status_code == 404
    assert (
        len(ApiResponse[list[PessoaVM]].model_validate(api.get("/api/v1/pessoas").json()).data) == 1
    )


def test_cnpj_duplicado_concorrente_rejeitado_no_banco(api: TestClient) -> None:
    dados: InstituicaoInput = instituicao_input()

    def criar(numero: int) -> int:
        return api.post("/api/v1/instituicoes", json=dados.model_dump(mode="json")).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        codigos: list[int] = list(pool.map(criar, range(2)))
    assert sorted(codigos) == [201, 409]
    assert (
        len(
            ApiResponse[list[InstituicaoVM]]
            .model_validate(api.get("/api/v1/instituicoes").json())
            .data
        )
        == 1
    )


def test_coordenadas_com_check_sql(banco: Engine) -> None:
    # Escreve direto no SQL para demonstrar a proteção além do validador HTTP.
    with pytest.raises(IntegrityError), banco.begin() as conn:
        conn.execute(
            insert(instituicoes).values(
                id=UUID(int=10),
                nome="Inválida",
                municipio_codigo_ibge="3550308",
                uf="SP",
                tipo="associacao",
                situacao_cadastral="pendente",
                latitude=-23,
                longitude=None,
                criado_em=agora_utc(),
                atualizado_em=agora_utc(),
                criado_por="teste",
                atualizado_por="teste",
            )
        )


def test_paginacao_e_problem_details(api: TestClient) -> None:
    dados: PessoaInput = PessoaInput(nome="Pessoa A", municipio_codigo_ibge="3550308", uf="SP")
    api.post("/api/v1/pessoas", json=dados.model_dump(mode="json"))
    api.post(
        "/api/v1/pessoas",
        json=dados.model_copy(update={"nome": "Pessoa B"}).model_dump(mode="json"),
    )
    resposta = api.get("/api/v1/pessoas?limite=1&deslocamento=1")
    assert ApiResponse[list[PessoaVM]].model_validate(resposta.json()).data[0].nome == "Pessoa B"
    invalid = api.get("/api/v1/pessoas?limite=1000")
    assert invalid.status_code == 422 and Problema.model_validate(invalid.json()).status == 422


def criar_vm[T: BaseModel](api: TestClient, caminho: str, dados: BaseModel, vm: type[T]) -> T:
    resposta = api.post(caminho, json=dados.model_dump(mode="json"))
    assert resposta.status_code == 201, resposta.text
    return vm.model_validate(resposta.json()["data"])


def pessoa_vm(api: TestClient, nome: str = "Pessoa de teste") -> PessoaVM:
    return criar_vm(
        api,
        "/api/v1/pessoas",
        PessoaInput(nome=nome, municipio_codigo_ibge="3550308", uf="SP"),
        PessoaVM,
    )


def profissao_vm(api: TestClient) -> ProfissaoVM:
    return criar_vm(
        api,
        "/api/v1/profissoes",
        ProfissaoInput(
            nome="Profissão ilustrativa", codigo_cbo="1234-56", descricao="Descrição do catálogo"
        ),
        ProfissaoVM,
    )


def curso_vm(api: TestClient) -> CursoVM:
    return criar_vm(
        api,
        "/api/v1/cursos",
        CursoInput(nome="Treinamento ilustrativo", tipo="treinamento"),
        CursoVM,
    )


def test_profissao_hash_busca_literal_e_auditoria(api: TestClient, banco: Engine) -> None:
    primeira: ProfissaoVM = profissao_vm(api)
    assert primeira.codigo_cbo == "123456" and len(primeira.hash_conteudo_semantico) == 64
    dados: ProfissaoInput = ProfissaoInput(
        nome=primeira.nome, descricao=primeira.descricao, codigo_cbo=primeira.codigo_cbo
    )
    mesma = api.put(f"/api/v1/profissoes/{primeira.id}", json=dados.model_dump(mode="json"))
    assert mesma.status_code == 200
    assert (
        ApiResponse[ProfissaoVM].model_validate(mesma.json()).data.hash_conteudo_semantico
        == primeira.hash_conteudo_semantico
    )
    alterada = api.put(
        f"/api/v1/profissoes/{primeira.id}",
        json=dados.model_copy(update={"descricao": "Escopo alterado"}).model_dump(mode="json"),
    )
    assert alterada.status_code == 200
    assert (
        ApiResponse[ProfissaoVM].model_validate(alterada.json()).data.hash_conteudo_semantico
        != primeira.hash_conteudo_semantico
    )
    assert (
        len(
            ApiResponse[list[ProfissaoVM]]
            .model_validate(api.get("/api/v1/profissoes?busca=ilustrativa").json())
            .data
        )
        == 1
    )
    assert (
        ApiResponse[list[ProfissaoVM]]
        .model_validate(api.get("/api/v1/profissoes?busca=%25%25").json())
        .data
        == []
    )
    assert api.get(f"/api/v1/profissoes/{primeira.id}").status_code == 200
    with banco.connect() as conexao:
        assert (
            conexao.scalar(text("SELECT atualizado_por FROM profissoes")) == "administrador-teste"
        )


def test_curso_hash_por_tipo_e_inativacao(api: TestClient) -> None:
    curso: CursoVM = curso_vm(api)
    nova = api.put(
        f"/api/v1/cursos/{curso.id}",
        json=CursoInput(nome=curso.nome, tipo="capacitacao").model_dump(mode="json"),
    )
    assert nova.status_code == 200
    assert (
        ApiResponse[CursoVM].model_validate(nova.json()).data.hash_conteudo_semantico
        != curso.hash_conteudo_semantico
    )
    assert api.delete(f"/api/v1/cursos/{curso.id}").status_code == 200
    assert api.get(f"/api/v1/cursos/{curso.id}").status_code == 404


def test_vinculo_institucional_periodos_renovacao_e_historico(api: TestClient) -> None:
    pessoa: PessoaVM = pessoa_vm(api)
    instituicao: InstituicaoVM = criar_vm(
        api, "/api/v1/instituicoes", instituicao_input(), InstituicaoVM
    )
    caminho: str = f"/api/v1/pessoas/{pessoa.id}/instituicoes"
    dados: PessoaInstituicaoInput = PessoaInstituicaoInput(
        instituicao_id=instituicao.id, tipo_vinculo="voluntario", inicio_em="2026-01-01"
    )
    vinculo: PessoaInstituicaoVM = criar_vm(api, caminho, dados, PessoaInstituicaoVM)
    assert vinculo.referencia_nome == instituicao.nome
    assert api.post(caminho, json=dados.model_dump(mode="json")).status_code == 409
    encerramento: PessoaInstituicaoInput = dados.model_copy(update={"fim_em": date(2026, 5, 31)})
    assert (
        api.put(f"{caminho}/{vinculo.id}", json=encerramento.model_dump(mode="json")).status_code
        == 200
    )
    sobreposto = encerramento.model_copy(
        update={"inicio_em": date(2026, 5, 31), "fim_em": date(2026, 6, 30)}
    )
    assert api.post(caminho, json=sobreposto.model_dump(mode="json")).status_code == 409
    renovacao = dados.model_copy(update={"inicio_em": date(2026, 6, 1)})
    novo: PessoaInstituicaoVM = criar_vm(api, caminho, renovacao, PessoaInstituicaoVM)
    assert novo.id != vinculo.id
    assert (
        len(ApiResponse[list[PessoaInstituicaoVM]].model_validate(api.get(caminho).json()).data)
        == 2
    )
    assert api.delete(f"{caminho}/{novo.id}").status_code == 200
    assert api.get(f"{caminho}/{novo.id}").status_code == 404
    historico = api.get(f"{caminho}/{novo.id}?incluir_inativos=true")
    assert (
        ApiResponse[PessoaInstituicaoVM].model_validate(historico.json()).data.inativado_em
        is not None
    )


def test_sobreposicao_institucional_concorrente(api: TestClient) -> None:
    pessoa: PessoaVM = pessoa_vm(api)
    instituicao: InstituicaoVM = criar_vm(
        api, "/api/v1/instituicoes", instituicao_input(), InstituicaoVM
    )
    caminho: str = f"/api/v1/pessoas/{pessoa.id}/instituicoes"
    dados: PessoaInstituicaoInput = PessoaInstituicaoInput(
        instituicao_id=instituicao.id,
        tipo_vinculo="associado",
        inicio_em="2026-01-01",
        fim_em="2026-12-31",
    )

    def criar(numero: int) -> int:
        return api.post(caminho, json=dados.model_dump(mode="json")).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados: list[int] = list(pool.map(criar, range(2)))
    assert sorted(resultados) == [201, 409]


def test_profissao_duplicada_com_nulos_concorrente_e_renovacao(api: TestClient) -> None:
    pessoa: PessoaVM = pessoa_vm(api)
    profissao: ProfissaoVM = profissao_vm(api)
    caminho: str = f"/api/v1/pessoas/{pessoa.id}/profissoes"
    dados: PessoaProfissaoInput = PessoaProfissaoInput(profissao_id=profissao.id)

    def criar(numero: int) -> int:
        return api.post(caminho, json=dados.model_dump(mode="json")).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados: list[int] = list(pool.map(criar, range(2)))
    assert sorted(resultados) == [201, 409]
    renovada: PessoaProfissaoVM = criar_vm(
        api,
        caminho,
        PessoaProfissaoInput(
            profissao_id=profissao.id,
            registro_profissional="ab-123",
            orgao_registro="teste",
            uf_registro="sp",
            validade_em="2027-12-31",
        ),
        PessoaProfissaoVM,
    )
    assert renovada.registro_profissional == "AB-123" and renovada.uf_registro == "SP"
    outra = api.post(
        caminho,
        json=PessoaProfissaoInput(
            profissao_id=profissao.id,
            registro_profissional="AB-123",
            orgao_registro="TESTE",
            uf_registro="SP",
            validade_em="2028-12-31",
        ).model_dump(mode="json"),
    )
    assert outra.status_code == 201
    assert (
        len(
            ApiResponse[list[PessoaProfissaoVM]]
            .model_validate(api.get(caminho + "?limite=1&deslocamento=1").json())
            .data
        )
        == 1
    )


def test_curso_renovacao_duplicidade_validacao_e_auditoria(api: TestClient, banco: Engine) -> None:
    pessoa: PessoaVM = pessoa_vm(api)
    curso: CursoVM = curso_vm(api)
    caminho: str = f"/api/v1/pessoas/{pessoa.id}/cursos"
    dados: PessoaCursoInput = PessoaCursoInput(
        curso_id=curso.id,
        instituicao_emissora="Escola Teste",
        conclusao_em="2025-01-10",
        validade_em="2026-01-10",
        carga_horaria="40.50",
        comprovante_referencia="documento:certificado-1",
    )
    vinculo: PessoaCursoVM = criar_vm(api, caminho, dados, PessoaCursoVM)
    duplicado = dados.model_copy(
        update={"instituicao_emissora": "escola teste", "validade_em": date(2028, 1, 10)}
    )
    assert api.post(caminho, json=duplicado.model_dump(mode="json")).status_code == 409
    renovacao = dados.model_copy(
        update={"conclusao_em": date(2026, 1, 10), "validade_em": date(2027, 1, 10)}
    )
    assert api.post(caminho, json=renovacao.model_dump(mode="json")).status_code == 201
    validado = api.put(
        f"{caminho}/{vinculo.id}",
        json=dados.model_copy(update={"situacao_validacao": SituacaoValidacao.VALIDADA}).model_dump(
            mode="json"
        ),
    )
    assert validado.status_code == 200
    vm: PessoaCursoVM = ApiResponse[PessoaCursoVM].model_validate(validado.json()).data
    assert vm.situacao_validacao == "validada" and str(vm.carga_horaria) == "40.50"
    # Mesmo vencido, o certificado permanece consultável; validação não concede aptidão.
    assert vm.validade_em == date(2026, 1, 10)
    with banco.connect() as conexao:
        assert (
            conexao.scalar(
                text("SELECT atualizado_por FROM pessoa_curso WHERE id = :id"), {"id": vinculo.id}
            )
            == "administrador-teste"
        )
    assert api.delete(f"{caminho}/{vinculo.id}").status_code == 200
    assert api.post(caminho, json=dados.model_dump(mode="json")).status_code == 201


def test_referencias_e_escopo_da_pessoa(api: TestClient) -> None:
    pessoa: PessoaVM = pessoa_vm(api)
    outra: PessoaVM = pessoa_vm(api, "Outra pessoa")
    profissao: ProfissaoVM = profissao_vm(api)
    caminho: str = f"/api/v1/pessoas/{pessoa.id}/profissoes"
    dados: PessoaProfissaoInput = PessoaProfissaoInput(profissao_id=profissao.id)
    vinculo: PessoaProfissaoVM = criar_vm(api, caminho, dados, PessoaProfissaoVM)
    alheio: str = f"/api/v1/pessoas/{outra.id}/profissoes/{vinculo.id}"
    assert api.get(alheio).status_code == 404
    assert api.put(alheio, json=dados.model_dump(mode="json")).status_code == 404
    assert api.delete(alheio).status_code == 404
    assert (
        api.post(
            caminho, json=PessoaProfissaoInput(profissao_id=UUID(int=987)).model_dump(mode="json")
        ).status_code
        == 404
    )
    assert api.delete(f"/api/v1/profissoes/{profissao.id}").status_code == 200
    assert api.post(caminho, json=dados.model_dump(mode="json")).status_code == 404
    assert ApiResponse[list[PessoaProfissaoVM]].model_validate(api.get(caminho).json()).data == []
    historico = (
        ApiResponse[list[PessoaProfissaoVM]]
        .model_validate(api.get(caminho + "?incluir_inativos=true").json())
        .data
    )
    assert historico[0].referencia_nome == profissao.nome
    assert api.delete(f"/api/v1/pessoas/{pessoa.id}").status_code == 200
    assert api.get(caminho).status_code == 404
    assert api.get(caminho + "?incluir_inativos=true").status_code == 200


def test_fk_e_periodo_protegidos_no_sql(api: TestClient, banco: Engine) -> None:
    pessoa: PessoaVM = pessoa_vm(api)
    instituicao: InstituicaoVM = criar_vm(
        api, "/api/v1/instituicoes", instituicao_input(), InstituicaoVM
    )
    with pytest.raises(IntegrityError), Session(banco) as sessao, sessao.begin():
        sessao.add(
            PessoaInstituicao(
                pessoa_id=pessoa.id,
                instituicao_id=instituicao.id,
                tipo_vinculo=TipoVinculo.VOLUNTARIO,
                inicio_em=date(2026, 5, 1),
                fim_em=date(2026, 4, 30),
                criado_por="teste",
                atualizado_por="teste",
            )
        )
        sessao.flush()
    with pytest.raises(IntegrityError), Session(banco) as sessao, sessao.begin():
        sessao.add(
            PessoaCurso(
                pessoa_id=pessoa.id,
                curso_id=UUID(int=999),
                instituicao_emissora="Escola Teste",
                conclusao_em=date(2026, 1, 1),
                criado_por="teste",
                atualizado_por="teste",
            )
        )
        sessao.flush()
