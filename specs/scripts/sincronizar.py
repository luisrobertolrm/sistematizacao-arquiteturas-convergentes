"""Gera Markdown e confere a cobertura documental dos botões declarados em Angular.

Uso na raiz: backend/.venv/Scripts/python.exe specs/scripts/sincronizar.py [--gerar]
Sem --gerar, apenas verifica os artefatos existentes. Não acessa navegador ou banco.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import TypedDict, cast


class Localizador(TypedDict, total=False):
    css: str
    escopo: str
    papel: str | None
    nome: str
    exato: bool
    texto: str


class Dialogo(TypedDict):
    tipo: str
    texto: str
    cancelar: str


class Acao(TypedDict, total=False):
    id: str
    controle: str
    localizador: Localizador
    evento: str
    precondicao: str
    resultado: list[str]
    destino: str
    http: str
    campo: str
    dialogo: Dialogo


class Campo(TypedDict):
    seletor: str
    regra: str


class Cenario(TypedDict):
    id: str
    titulo: str
    dado: str
    quando: str
    entao: str


class Entrada(TypedDict):
    caminho: list[str]
    raiz: str
    prontidao: list[str]


class Funcionalidade(TypedDict):
    id: str
    arquivo: str
    titulo: str
    intencao: str
    entrada: Entrada
    precondicoes: list[str]
    fontes: list[str]
    campos: list[Campo]
    acoes: list[Acao]
    cenarios: list[Cenario]
    observacoes: list[str]


class Catalogo(TypedDict):
    versao: str
    data_referencia: str
    aplicacao: str
    url_padrao: str
    natureza: str
    convencoes: str
    funcionalidades: list[Funcionalidade]
    componentes_compartilhados: list[Funcionalidade]
    sem_dados_sensiveis: bool


class ControleJSON(TypedDict):
    fonte: str
    linha: int
    tag: str
    nomes_declarados: list[str]
    eventos: dict[str, str]
    bloqueio: str | None
    acoes_documentadas: list[str]


class InventarioJSON(TypedDict):
    descricao: str
    catalogo_sha256: str
    fontes_sha256: dict[str, str]
    quantidade_controles: int
    controles: list[ControleJSON]
    controles_gerados_por_biblioteca: list[str]


@dataclass
class Controle:
    linha: int
    tag: str
    atributos: dict[str, str]
    eventos: dict[str, str]
    texto: list[str] = field(default_factory=list)


class LeitorControles(HTMLParser):
    """Inventaria button, a e summary, incluindo submit herdado do formulário."""

    def __init__(self, linha_inicial: int = 1) -> None:
        super().__init__(convert_charrefs=True)
        self.linha_inicial = linha_inicial
        self.controles: list[Controle] = []
        self.abertos: list[Controle] = []
        self.formularios: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        atributos: dict[str, str] = {k: v or "" for k, v in attrs}
        eventos: dict[str, str] = {k: v for k, v in atributos.items() if k.startswith("(")}
        if tag == "form":
            self.formularios.append(eventos)
        if tag not in {"button", "a", "summary"}:
            return
        if tag == "button" and atributos.get("type", "submit") != "button" and self.formularios:
            eventos = {**self.formularios[-1], **eventos}
        controle = Controle(self.getpos()[0] + self.linha_inicial - 1, tag, atributos, eventos)
        self.controles.append(controle)
        self.abertos.append(controle)

    def handle_data(self, data: str) -> None:
        for controle in self.abertos:
            controle.texto.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "form" and self.formularios:
            self.formularios.pop()
        self.abertos = [c for c in self.abertos if c.tag != tag]


RAIZ: Path = Path(__file__).resolve().parents[2]
PASTA: Path = RAIZ / "specs"


def codigo_json(valor: object) -> str:
    return json.dumps(valor, ensure_ascii=False, indent=2) + "\n"


def celula(valor: str) -> str:
    return valor.replace("|", "\\|").replace("\n", " ")


def lista(valores: list[str]) -> list[str]:
    return [f"- {valor}" for valor in valores]


def markdown(f: Funcionalidade, destinos: dict[str, Funcionalidade], data: str) -> str:
    entrada = f["entrada"]
    linhas: list[str] = [
        f'# {f["id"]} — {f["titulo"]}', "",
        f'Referência: {data}. Gerado de [catalogo.json](../catalogo.json); editar o catálogo e sincronizar.', "",
        "## Intenção", "", f["intencao"], "",
        "## Entrada e identificação", "",
        " → ".join(entrada["caminho"]), "",
        f'Raiz do componente/área: `{entrada["raiz"]}`. Navegação interna sem troca de URL.', "",
        *lista(entrada["prontidao"]), "",
        "## Pré-condições", "", *lista(f["precondicoes"]), "",
        "## Campos e controles de entrada", "",
        "| Seletor relativo à raiz | Regra / intenção |", "|---|---|",
        *[f'| `{celula(c["seletor"])}` | {celula(c["regra"])} |' for c in f["campos"]], "",
        "## Ações e resultados esperados", "",
        "Os escopos são relativos à raiz. `$registro` e `$item` dependem do contexto do cenário; ver [contrato do harness](../contrato-harness.md).", "",
    ]
    for acao in f["acoes"]:
        destino = acao["destino"]
        alvo = destinos.get(destino)
        link = f'[{destino}](./{alvo["arquivo"]})' if alvo else destino
        linhas.extend([
            f'### {acao["id"]} — {acao["controle"]}', "",
            f'- Localizador: `{json.dumps(acao["localizador"], ensure_ascii=False)}`.',
            f'- Gesto: `{acao["evento"]}`.',
            f'- Condição: {acao["precondicao"]}',
            f'- Destino: {link}.',
        ])
        if acao.get("campo"):
            linhas.append(f'- Campo associado: `{acao["campo"]}`.')
        if acao.get("http"):
            linhas.append(f'- Persistência/rede: `{acao["http"]}`.')
        if "dialogo" in acao:
            dialogo = acao["dialogo"]
            linhas.extend([
                f'- Diálogo nativo `{dialogo["tipo"]}`: {dialogo["texto"]}',
                f'- Ao cancelar o diálogo: {dialogo["cancelar"]}',
            ])
        linhas.extend(["", "Resultado:", "", *lista(acao["resultado"]), ""])
    linhas.extend(["## Cenários de aceitação", ""])
    for cenario in f["cenarios"]:
        linhas.extend([
            f'### {cenario["id"]} — {cenario["titulo"]}', "",
            f'- **Dado:** {cenario["dado"]}',
            f'- **Quando:** {cenario["quando"]}',
            f'- **Então:** {cenario["entao"]}', "",
        ])
    linhas.extend(["## Limites e particularidades", "", *lista(f["observacoes"]), "", "## Fontes da implementação", ""])
    linhas.extend(f'- [{fonte}](../../{fonte})' for fonte in f["fontes"])
    return "\n".join(linhas) + "\n"


def validar(catalogo: Catalogo) -> list[Funcionalidade]:
    funcionalidades = catalogo["funcionalidades"] + catalogo["componentes_compartilhados"]
    ids: set[str] = set()
    arquivos: set[str] = set()
    for f in funcionalidades:
        assert f["id"] not in ids, f'ID repetido: {f["id"]}'
        assert f["arquivo"] not in arquivos, f'Arquivo repetido: {f["arquivo"]}'
        assert Path(f["arquivo"]).name == f["arquivo"], "Arquivo precisa ficar em funcionalidades."
        ids.add(f["id"])
        arquivos.add(f["arquivo"])
        assert all(f.get(chave) for chave in ("entrada", "intencao", "precondicoes", "campos", "acoes", "cenarios", "fontes"))
        for fonte in f["fontes"]:
            assert (RAIZ / fonte).is_file(), f'Fonte ausente: {fonte}'
    ids_acao: set[str] = set()
    ids_cenario: set[str] = set()
    for f in funcionalidades:
        for acao in f["acoes"]:
            assert acao["id"] not in ids_acao, f'Ação duplicada: {acao["id"]}'
            ids_acao.add(acao["id"])
            assert all(acao.get(chave) for chave in ("controle", "localizador", "evento", "precondicao", "resultado", "destino"))
            assert acao["destino"] in ids | {"externo", "contexto de origem"}, f'Destino inválido: {acao["destino"]}'
            assert all(isinstance(v, str) and v for v in acao["resultado"])
        for cenario in f["cenarios"]:
            assert cenario["id"] not in ids_cenario, f'Cenário duplicado: {cenario["id"]}'
            ids_cenario.add(cenario["id"])
            assert all(cenario.get(chave) for chave in ("titulo", "dado", "quando", "entao"))
    return funcionalidades


def inventariar(funcionalidades: list[Funcionalidade]) -> InventarioJSON:
    controles: list[ControleJSON] = []
    hashes: dict[str, str] = {}
    for caminho in sorted((RAIZ / "frontend/src/app").rglob("*")):
        if caminho.suffix not in {".html", ".ts"}:
            continue
        texto = caminho.read_text(encoding="utf-8")
        trecho = texto
        linha = 1
        if caminho.suffix == ".ts":
            template = re.search(r"\btemplate\s*:\s*`([\s\S]*?)`", texto)
            if not template:
                continue
            trecho = template.group(1)
            linha = texto[:template.start(1)].count("\n") + 1
        fonte = caminho.relative_to(RAIZ).as_posix()
        hashes[fonte] = hashlib.sha256(caminho.read_bytes()).hexdigest()
        leitor = LeitorControles(linha)
        leitor.feed(trecho)
        for controle in leitor.controles:
            nome = controle.atributos.get("aria-label") or " ".join("".join(controle.texto).split())
            nomes = re.findall(r"['\"]([^'\"]+)['\"]", nome) if "{{" in nome else [nome]
            candidatos: list[str] = []
            for funcionalidade in funcionalidades:
                if fonte not in funcionalidade["fontes"]:
                    continue
                for acao in funcionalidade["acoes"]:
                    if acao["controle"] in nomes or acao["localizador"].get("nome") in nomes:
                        candidatos.append(acao["id"])
            assert candidatos, f'Controle sem spec: {fonte}:{controle.linha} {nome}'
            controles.append({
                "fonte": fonte, "linha": controle.linha, "tag": controle.tag,
                "nomes_declarados": nomes, "eventos": controle.eventos,
                "bloqueio": controle.atributos.get("[disabled]"),
                "acoes_documentadas": sorted(set(candidatos)),
            })
    return {
        "descricao": "Cobertura estática de button, a e summary declarados nos templates HTML e inline Angular. Não prova execução/qualidade dos cenários nem inventaria DOM gerado em runtime pelo Leaflet.",
        "catalogo_sha256": hashlib.sha256((PASTA / "catalogo.json").read_bytes()).hexdigest(),
        "fontes_sha256": hashes,
        "quantidade_controles": len(controles), "controles": controles,
        "controles_gerados_por_biblioteca": ["MAP-ZOOM-MAIS", "MAP-ZOOM-MENOS", "MAP-ATRIBUICAO"],
    }


def verificar_links() -> None:
    for arquivo in PASTA.rglob("*.md"):
        texto = arquivo.read_text(encoding="utf-8")
        for referencia in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", texto):
            destino = referencia.split("#", 1)[0].strip("<>")
            if not destino or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", destino):
                continue
            assert (arquivo.parent / destino).is_file(), f'Link local ausente em {arquivo.relative_to(RAIZ)}: {referencia}'


def indice(catalogo: Catalogo) -> str:
    linhas = ["# Índice das especificações", "", "Gerado de [catalogo.json](catalogo.json).", "", "| ID | Funcionalidade | Spec |", "|---|---|---|"]
    for f in catalogo["funcionalidades"] + catalogo["componentes_compartilhados"]:
        linhas.append(f'| {f["id"]} | {f["titulo"]} | [{f["arquivo"]}](funcionalidades/{f["arquivo"]}) |')
    return "\n".join(linhas) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gerar", action="store_true")
    args = parser.parse_args()
    catalogo = cast(Catalogo, json.loads((PASTA / "catalogo.json").read_text(encoding="utf-8")))
    funcionalidades = validar(catalogo)
    destinos = {f["id"]: f for f in funcionalidades}
    inventario = inventariar(funcionalidades)
    for funcionalidade in funcionalidades:
        for fonte in funcionalidade["fontes"]:
            inventario["fontes_sha256"][fonte] = hashlib.sha256((RAIZ / fonte).read_bytes()).hexdigest()
    artefatos: dict[Path, str] = {
        PASTA / "inventario-controles.json": codigo_json(inventario),
        PASTA / "indice.md": indice(catalogo),
    }
    for f in funcionalidades:
        artefatos[PASTA / "funcionalidades" / f["arquivo"]] = markdown(f, destinos, catalogo["data_referencia"])
    for caminho, conteudo in artefatos.items():
        if args.gerar:
            caminho.parent.mkdir(parents=True, exist_ok=True)
            caminho.write_text(conteudo, encoding="utf-8", newline="\n")
        else:
            assert caminho.is_file() and caminho.read_text(encoding="utf-8") == conteudo, f'Artefato desatualizado: {caminho.relative_to(RAIZ)}'
    verificar_links()
    acoes = sum(len(f["acoes"]) for f in funcionalidades)
    cenarios = sum(len(f["cenarios"]) for f in funcionalidades)
    print(f'{len(catalogo["funcionalidades"])} funcionalidades + {len(catalogo["componentes_compartilhados"])} componentes; {acoes} ações; {cenarios} cenários.')
    print(f'{inventario["quantidade_controles"]} botões/links/summary declarados com referência documental. Artefatos consistentes.')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
