"""Cria PostgreSQL descartável, migra, testa e remove somente o container criado.

Requer Docker local. Usa imagem fixada por digest; não acessa bancos do usuário.
"""

import argparse
import json
import os
import re
import secrets
import socket
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import monotonic, sleep
from urllib.error import URLError
from urllib.request import urlopen
from uuid import UUID, uuid4

import jwt
import psycopg
from cryptography.fernet import Fernet

from core.entity.capacidades import Atividade
from core.semantica import hash_atividade
from tests.provedor_http import provedor_ficticio
from web.autenticacao.emitir_token import ClaimsEmitidos

IMAGEM: str = "postgres@sha256:a9abf4275f9e99bff8e6aed712b3b7dfec9cac1341bba01c1ffdfce9ff9fc34a"


def docker(argumentos: list[str], ambiente: dict[str, str], timeout: int = 45) -> str:
    resultado: subprocess.CompletedProcess[str] = subprocess.run(
        ["docker", *argumentos],
        check=True,
        capture_output=True,
        text=True,
        env=ambiente,
        timeout=timeout,
    )
    return resultado.stdout.strip()


def executar_python(argumentos: list[str], ambiente: dict[str, str], raiz: Path) -> None:
    subprocess.run([sys.executable, *argumentos], check=True, env=ambiente, cwd=raiz)


def testar_frontend_com_provedor(ambiente: dict[str, str], raiz: Path, url_ia: str) -> None:
    """API com segredo temporário e build Angular servido pelo teste local de navegador."""
    with socket.socket() as reserva:
        reserva.bind(("127.0.0.1", 0))
        porta: int = reserva.getsockname()[1]
    segredo: str = secrets.token_urlsafe(40)
    instante: datetime = datetime.now(UTC)
    claims: ClaimsEmitidos = {
        "sub": "administrador-browser-teste",
        "role": "admin",
        "iss": "ui-teste",
        "aud": "ui-api",
        "iat": int(instante.timestamp()),
        "exp": int((instante + timedelta(minutes=5)).timestamp()),
    }
    ambiente_ui: dict[str, str] = {
        **ambiente,
        "REDE_ENVIRONMENT": "test",
        "REDE_IA_URLS_PERMITIDAS": json.dumps([url_ia]),
        "REDE_ENCRYPTION_KEY": Fernet.generate_key().decode("ascii"),
        "REDE_ENCRYPTION_KEY_ID": "fernet-v1",
        "UI_TEST_IA_URL": url_ia,
        "REDE_JWT_SECRET": segredo,
        "REDE_JWT_ISSUER": "ui-teste",
        "REDE_JWT_AUDIENCE": "ui-api",
        "UI_TEST_API": f"http://127.0.0.1:{porta}",
        "UI_TEST_TOKEN": jwt.encode(dict(claims), segredo, algorithm="HS256"),
    }
    processo: subprocess.Popen[bytes] = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "web.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(porta),
        ],
        cwd=raiz,
        env=ambiente_ui,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        limite: float = monotonic() + 20
        while True:
            try:
                with urlopen(f"http://127.0.0.1:{porta}/health", timeout=2) as resposta:
                    if resposta.status == 200:
                        break
            except (URLError, TimeoutError):
                if processo.poll() is not None or monotonic() >= limite:
                    raise RuntimeError(
                        "A API temporária para o teste de interface não iniciou."
                    ) from None
                sleep(0.2)
        print("API temporária pronta; verificando Angular com PostgreSQL real.", flush=True)
        subprocess.run(
            ["node", "scripts/testar-capacidades.mjs"],
            check=True,
            env=ambiente_ui,
            cwd=raiz.parent / "frontend",
            timeout=120,
        )
    finally:
        processo.terminate()
        try:
            processo.wait(timeout=10)
        except subprocess.TimeoutExpired:
            processo.kill()
            processo.wait(timeout=5)


def testar_frontend(ambiente: dict[str, str], raiz: Path) -> None:
    with provedor_ficticio() as url_ia:
        testar_frontend_com_provedor(ambiente, raiz, url_ia)


def main() -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--frontend", action="store_true", help="Verificar também o build Angular no navegador."
    )
    verificar_frontend: bool = bool(parser.parse_args().frontend)
    raiz: Path = Path(__file__).resolve().parents[1]
    senha: str = secrets.token_hex(24)
    ambiente: dict[str, str] = {**os.environ, "POSTGRES_PASSWORD": senha}
    nome: str = "redesolidaria-test-" + uuid4().hex[:12]
    identificador: str | None = None
    try:
        identificador = docker(
            [
                "run",
                "--pull=never",
                "--detach",
                "--name",
                nome,
                "--env",
                "POSTGRES_PASSWORD",
                "--env",
                "POSTGRES_USER=redesolidaria",
                "--env",
                "POSTGRES_DB=redesolidaria_test",
                "--publish",
                "127.0.0.1::5432",
                IMAGEM,
            ],
            ambiente,
        )
        if not re.fullmatch(r"[a-f0-9]{64}", identificador):
            raise RuntimeError("Identificador inesperado do container criado.")
        porta: str = docker(["port", identificador, "5432/tcp"], ambiente).split(":")[-1]
        url: str = f"postgresql://redesolidaria:{senha}@127.0.0.1:{porta}/redesolidaria_test"
        limite: float = monotonic() + 45
        while True:
            try:
                with psycopg.connect(url, connect_timeout=2):
                    break
            except psycopg.OperationalError:
                if monotonic() >= limite:
                    raise RuntimeError("PostgreSQL de teste não ficou pronto.") from None
                sleep(0.5)
        ambiente["REDE_DATABASE_URL"] = url.replace("postgresql://", "postgresql+psycopg://", 1)
        ambiente["TEST_DATABASE_URL"] = ambiente["REDE_DATABASE_URL"]
        print(
            "PostgreSQL isolado pronto; verificando atualização dos incrementos anteriores.",
            flush=True,
        )
        executar_python(["-m", "alembic", "upgrade", "0001_cadastros"], ambiente, raiz)
        with psycopg.connect(url) as conexao:
            conexao.execute(
                "INSERT INTO pessoas (id, nome, municipio_codigo_ibge, uf, situacao_cadastral, "
                "criado_em, atualizado_em, criado_por, atualizado_por) "
                "VALUES ('00000000-0000-0000-0000-000000000001', 'Legado de teste', '0000001', "
                "'SP', 'pendente', now(), now(), 'teste', 'teste')"
            )
        executar_python(["-m", "alembic", "upgrade", "0002_qualificacoes"], ambiente, raiz)
        with psycopg.connect(url) as conexao:
            conexao.execute(
                "INSERT INTO profissoes (id, nome, codigo_cbo, hash_conteudo_semantico, "
                "criado_em, atualizado_em, criado_por, atualizado_por) "
                "VALUES ('00000000-0000-0000-0000-000000000002', 'Profissão legado', '782510', "
                "%(hash)s, now(), now(), 'teste', 'teste')",
                {"hash": "a" * 64},
            )
        executar_python(["-m", "alembic", "upgrade", "0003_capacidades"], ambiente, raiz)
        atividade_legada: Atividade = Atividade(
            id=UUID(int=5),
            codigo="atividade-legado",
            nome="Atividade legado",
            descricao="Apoio de teste",
            categoria_id=UUID(int=4),
            id_unidade_capacidade=UUID(int=3),
            hash_conteudo_semantico="",
            criado_por="teste",
            atualizado_por="teste",
        )
        hash_legado: str = hash_atividade(atividade_legada, ["apoio legado"])
        with psycopg.connect(url) as conexao:
            conexao.execute(
                "INSERT INTO unidades_medida (id, codigo, nome, simbolo, criado_em, atualizado_em, "
                "criado_por, atualizado_por) VALUES ('00000000-0000-0000-0000-000000000003', "
                "'unidade-legado', 'Unidade legado', 'u', now(), now(), 'teste', 'teste')"
            )
            conexao.execute(
                "INSERT INTO categorias_atividade (id, codigo, nome, criado_em, atualizado_em, "
                "criado_por, atualizado_por) VALUES ('00000000-0000-0000-0000-000000000004', "
                "'categoria-legado', 'Categoria legado', now(), now(), 'teste', 'teste')"
            )
            conexao.execute(
                "INSERT INTO atividades (id, codigo, nome, descricao, categoria_id, "
                "id_unidade_capacidade, hash_conteudo_semantico, criado_em, atualizado_em, "
                "criado_por, atualizado_por) VALUES ('00000000-0000-0000-0000-000000000005', "
                "'atividade-legado', 'Atividade legado', 'Apoio de teste', "
                "'00000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000003', "
                "%(hash)s, now(), now(), 'teste', 'teste')",
                {"hash": hash_legado},
            )
            conexao.execute(
                "INSERT INTO atividade_termos (id, atividade_id, termo, criado_em, atualizado_em, "
                "criado_por, atualizado_por) VALUES ('00000000-0000-0000-0000-000000000006', "
                "'00000000-0000-0000-0000-000000000005', 'apoio legado', "
                "now(), now(), 'teste', 'teste')"
            )
        executar_python(["-m", "alembic", "upgrade", "head"], ambiente, raiz)
        with psycopg.connect(url) as conexao:
            linha: tuple[str] | None = conexao.execute(
                "SELECT nome FROM pessoas WHERE id = '00000000-0000-0000-0000-000000000001'"
            ).fetchone()
            if linha != ("Legado de teste",):
                raise RuntimeError("A atualização não preservou o cadastro anterior.")
            qualificacao: tuple[str, str] | None = conexao.execute(
                "SELECT nome, codigo_cbo FROM profissoes "
                "WHERE id = '00000000-0000-0000-0000-000000000002'"
            ).fetchone()
            if qualificacao != ("Profissão legado", "782510"):
                raise RuntimeError("A atualização não preservou o catálogo do incremento 2.")
            capacidade: tuple[str, str] | None = conexao.execute(
                "SELECT a.hash_conteudo_semantico, t.termo FROM atividades a "
                "JOIN atividade_termos t ON t.atividade_id = a.id "
                "WHERE a.id = '00000000-0000-0000-0000-000000000005'"
            ).fetchone()
            if capacidade != (hash_legado, "apoio legado"):
                raise RuntimeError("A atualização não preservou a atividade/termo do incremento 3.")
        print("Cadastro anterior preservado; verificando schema e testes.", flush=True)
        executar_python(["-m", "alembic", "check"], ambiente, raiz)
        executar_python(["-m", "pytest", "-q"], ambiente, raiz)
        if verificar_frontend:
            testar_frontend(ambiente, raiz)
        executar_python(["-m", "alembic", "downgrade", "base"], ambiente, raiz)
        executar_python(["-m", "alembic", "upgrade", "head"], ambiente, raiz)
        print("Testes e ciclo de migração concluídos.", flush=True)
        return 0
    finally:
        if identificador is not None and re.fullmatch(r"[a-f0-9]{64}", identificador):
            docker(["rm", "--force", "--volumes", identificador], ambiente)
            print("Container de teste e seu volume temporário removidos.", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
