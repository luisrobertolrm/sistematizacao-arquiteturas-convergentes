"""Script de teste e diagnóstico de conexão com o banco de dados configurado no .env."""

from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path

# Garante saída UTF-8 no terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DIR_BACKEND = Path(__file__).resolve().parent.parent
if str(DIR_BACKEND) not in sys.path:
    sys.path.insert(0, str(DIR_BACKEND))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ENV_PATH = DIR_BACKEND / ".env"


def main() -> int:
    print("=" * 65)
    print(" TESTE DE CONEXÃO — REDESOLIDÁRIA BACKEND (.ENV)")
    print("=" * 65)
    caminho_env = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else (DIR_BACKEND / ".env")
    print(f"Arquivo .env: {caminho_env}")

    if not caminho_env.exists():
        print(f"✗ Arquivo {caminho_env} não encontrado!")
        return 1

    load_dotenv(caminho_env, override=True)
    db_url = os.getenv("REDE_DATABASE_URL")
    env_name = os.getenv("REDE_ENVIRONMENT", "não definido")

    print(f"Ambiente: {env_name}")
    masked_url = re.sub(r":([^@]+)@", r":*****@", db_url) if db_url else "Não definida"
    print(f"Database URL: {masked_url}")
    print("-" * 65)

    if not db_url:
        print("✗ Variável REDE_DATABASE_URL não configurada no .env!")
        return 1

    try:
        t0 = time.perf_counter()
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            latencia_ms = (time.perf_counter() - t0) * 1000
            db_version = conn.execute(text("SELECT version();")).scalar()
            current_db = conn.execute(text("SELECT current_database();")).scalar()
            current_user = conn.execute(text("SELECT current_user;")).scalar()
            current_schema = conn.execute(text("SELECT current_schema();")).scalar()

            print("✓ Conexão estabelecida com sucesso!")
            print(f"Tempo de resposta: {latencia_ms:.2f} ms")
            print(f"Banco de dados: {current_db}")
            print(f"Usuário conectado: {current_user}")
            print(f"Schema: {current_schema}")
            print(f"Versão PostgreSQL: {db_version}")
            print("-" * 65)

            query = text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
            )
            tables = [r[0] for r in conn.execute(query).fetchall()]
            print(f"Total de tabelas no schema public: {len(tables)}")

            tabelas_principais = [
                "unidades_medida",
                "categorias_atividade",
                "atividades",
                "atividade_termos",
                "cursos",
                "profissoes",
                "tipos_desastre",
                "tipos_recurso",
                "recursos",
                "ofertas_atividade",
                "desastres",
                "instituicoes",
                "pessoas",
                "demandas",
            ]
            print("\nContagem de registros nas tabelas:")
            for t in tabelas_principais:
                if t in tables:
                    qtd = conn.execute(text(f"SELECT count(*) FROM {t};")).scalar()
                    print(f"  • {t}: {qtd} registro(s)")

        # Validação das configurações FastAPI / Pydantic
        try:
            from web.settings import Settings
            cfg = Settings()
            print("-" * 65)
            print("✓ Configurações da aplicação (Settings) validadas com sucesso!")
            print(f"  • Ambiente: {cfg.environment}")
            print(f"  • JWT Issuer: {cfg.jwt_issuer}")
            print(f"  • JWT Secret configurado: {'Sim' if cfg.jwt_secret else 'Não'}")
            print(f"  • Encryption Key configurada: {'Sim' if cfg.encryption_key else 'Não'}")
        except Exception as e_cfg:
            print(f"✗ Aviso na validação das configurações da aplicação: {e_cfg}")

        print("=" * 65)
        print("✓ Diagnóstico de conexão concluído com êxito!")
        print("=" * 65)
        return 0

    except Exception as e:
        print(f"\n✗ Falha ao conectar ao banco de dados: {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
