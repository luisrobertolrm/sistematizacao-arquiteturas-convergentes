"""Servidor compatível fictício, exclusivo dos testes de navegador/adaptadores."""

from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from time import time
from typing import TypedDict

from pydantic import BaseModel, Field

from tests.fakes_ia import FabricaFicticia, InferenciaFicticia


class MensagemEntrada(BaseModel):
    role: str
    content: str | None = None


class FuncaoEntrada(BaseModel):
    name: str


class FerramentaEntrada(BaseModel):
    function: FuncaoEntrada


class EntradaHTTP(BaseModel):
    model: str
    input: list[str] | str | None = None
    messages: list[MensagemEntrada] = Field(default_factory=list)
    tools: list[FerramentaEntrada] = Field(default_factory=list)


class EmbeddingSaida(BaseModel):
    object: str = "embedding"
    index: int
    embedding: list[float]


class RespostaEmbedding(BaseModel):
    object: str = "list"
    data: list[EmbeddingSaida]
    model: str


class ChamadaFuncao(TypedDict):
    name: str
    arguments: str


class ChamadaFerramenta(TypedDict):
    id: str
    type: str
    function: ChamadaFuncao


class MensagemSaida(TypedDict):
    role: str
    content: None
    tool_calls: list[ChamadaFerramenta]


class EscolhaSaida(BaseModel):
    index: int = 0
    message: MensagemSaida
    finish_reason: str = "tool_calls"


class RespostaChat(BaseModel):
    id: str = "chatcmpl-ficticio"
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[EscolhaSaida]


class HandlerIA(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_POST(self) -> None:
        tamanho = int(self.headers.get("Content-Length", "0"))
        if not 0 < tamanho <= 2_000_000:
            self.send_error(413)
            return
        req = EntradaHTTP.model_validate_json(self.rfile.read(tamanho))
        resposta: BaseModel
        if self.path == "/v1/embeddings":
            textos = req.input if isinstance(req.input, list) else [req.input or ""]
            resposta = RespostaEmbedding(
                model=req.model,
                data=[
                    EmbeddingSaida(index=i, embedding=[1.0, 0.0, 0.0]) for i, _ in enumerate(textos)
                ],
            )
        elif self.path == "/v1/chat/completions" and req.tools and req.messages:
            p = InferenciaFicticia(FabricaFicticia()).gerar(req.messages[-1].content or "")
            funcao: ChamadaFuncao = {
                "name": req.tools[0].function.name,
                "arguments": p.model_dump_json(),
            }
            chamada: ChamadaFerramenta = {
                "id": "call-ficticio",
                "type": "function",
                "function": funcao,
            }
            mensagem: MensagemSaida = {
                "role": "assistant",
                "content": None,
                "tool_calls": [chamada],
            }
            resposta = RespostaChat(
                created=int(time()), model=req.model, choices=[EscolhaSaida(message=mensagem)]
            )
        else:
            self.send_error(404)
            return
        corpo = resposta.model_dump_json().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)


@contextmanager
def provedor_ficticio() -> Iterator[str]:
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), HandlerIA)
    thread = Thread(target=lambda: servidor.serve_forever(poll_interval=0.05), daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{servidor.server_address[1]}/v1"
    finally:
        servidor.shutdown()
        servidor.server_close()
        thread.join(timeout=2)
