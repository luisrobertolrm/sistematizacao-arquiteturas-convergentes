from core.ia_operacao import ClienteEmbedding
from core.vetores import validar_vetor


def gerar_embeddings(
    cliente: ClienteEmbedding, textos: list[str], dimensao: int
) -> list[list[float]]:
    vetores = cliente.gerar(textos)
    if len(vetores) != len(textos):
        from core.http.contratos import ErroNegocio

        raise ErroNegocio(
            502, "Embedding inválido", "Provedor retornou quantidade incorreta de vetores."
        )
    for vetor in vetores:
        validar_vetor(vetor, dimensao)
    return vetores
