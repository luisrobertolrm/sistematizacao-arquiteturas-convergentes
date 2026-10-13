"""project.toml é a origem; pyproject.toml é um artefato de compatibilidade."""

import sys
from pathlib import Path


def main() -> int:
    raiz: Path = Path(__file__).resolve().parents[1]
    origem: bytes = (raiz / "project.toml").read_bytes()
    destino: Path = raiz / "pyproject.toml"
    conteudo: bytes = b"# Gerado por scripts/sync_manifest.py; editar project.toml.\n" + origem
    if sys.argv[1:] == ["--check"]:
        return 0 if destino.exists() and destino.read_bytes() == conteudo else 1
    if sys.argv[1:]:
        raise SystemExit("Uso: python scripts/sync_manifest.py [--check]")
    destino.write_bytes(conteudo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
