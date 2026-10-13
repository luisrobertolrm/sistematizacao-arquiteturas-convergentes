"""Exercício do modelo lógico com dados exclusivamente em memória.

Versão histórica anterior a D008/D009. Para o escopo atual, executar
simulacoes/escopo_inicial/simular_desastre.py. Este arquivo preserva o exercício
original e suas lacunas na data da discussão.

Python 3.13, somente biblioteca padrão. Classes abaixo são recortes dos campos
necessários aos cenários, não entidades de produção nem proposta de migração.
Demandas são entradas fictícias do exercício: sua persistência ainda não existe.
Embeddings são vetores artificiais, sem LLM, LangChain ou avaliação de RAG real.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from enum import StrEnum
from hashlib import sha256
from uuid import UUID


class Resultado(StrEnum):
    ATENDE = "ATENDE"
    REGRA = "REGRA EXERCITADA"
    LACUNA = "LACUNA"


@dataclass(frozen=True, slots=True)
class Verificacao:
    cenario: str
    resultado: Resultado
    evidencia: str


@dataclass(frozen=True, slots=True)
class Instituicao:
    id: UUID
    nome: str


@dataclass(frozen=True, slots=True)
class Desastre:
    id: UUID
    titulo: str
    inicio_em: datetime
    encerramento_em: datetime | None
    situacao: str
    id_instituicao_coordenadora: UUID


@dataclass(frozen=True, slots=True)
class TipoDesastre:
    id: UUID
    nome: str


@dataclass(frozen=True, slots=True)
class DesastreTipo:
    id_desastre: UUID
    id_tipo_desastre: UUID
    principal: bool


@dataclass(frozen=True, slots=True)
class Coordenada:
    longitude: Decimal
    latitude: Decimal


@dataclass(frozen=True, slots=True)
class AreaAfetada:
    id: UUID
    id_desastre: UUID
    nome: str
    municipio_codigo_ibge: str
    geometria: tuple[Coordenada, ...]
    gravidade: str
    ultima_avaliacao_em: datetime


@dataclass(frozen=True, slots=True)
class Pessoa:
    id: UUID
    nome: str


@dataclass(frozen=True, slots=True)
class PessoaInstituicao:
    pessoa_id: UUID
    instituicao_id: UUID


@dataclass(frozen=True, slots=True)
class Curso:
    id: UUID
    nome: str


@dataclass(frozen=True, slots=True)
class PessoaCurso:
    pessoa_id: UUID
    curso_id: UUID
    validade_em: date | None
    situacao_validacao: str


@dataclass(frozen=True, slots=True)
class TipoRecurso:
    id: UUID
    nome: str
    unidade_medida: str
    modo_controle: str


@dataclass(frozen=True, slots=True)
class Recurso:
    id: UUID
    tipo_recurso_id: UUID
    nome: str
    descricao: str
    instituicao_id: UUID | None
    pessoa_id: UUID | None
    quantidade_total: Decimal
    estado_operacional: str


@dataclass(frozen=True, slots=True)
class Atividade:
    id: UUID
    nome: str
    descricao: str
    unidade_capacidade: str

    @property
    def hash_conteudo_semantico(self) -> str:
        # Composição ilustrativa, não define a serialização final do domínio.
        conteudo: str = f"{self.nome}\x00{self.descricao}\x00{self.unidade_capacidade}"
        return sha256(conteudo.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class OfertaAtividade:
    id: UUID
    atividade_id: UUID
    instituicao_id: UUID | None
    pessoa_id: UUID | None
    capacidade_declarada: Decimal
    situacao_validacao: str


@dataclass(frozen=True, slots=True)
class OfertaRecurso:
    oferta_atividade_id: UUID
    recurso_id: UUID
    quantidade_prevista: Decimal


@dataclass(frozen=True, slots=True)
class DemandaCenario:
    """Entrada de simulação; entidade persistente de demanda ainda pendente."""

    nome: str
    id_area: UUID
    atividade_id: UUID | None
    tipo_recurso_id: UUID | None
    quantidade: Decimal
    unidade: str
    inicio: datetime
    fim: datetime


@dataclass(frozen=True, slots=True)
class ModeloIA:
    id: UUID
    finalidade: str
    ativo: bool
    dimensao: int | None


@dataclass(frozen=True, slots=True)
class IndiceAtividade:
    id_atividade: UUID
    id_modelo: UUID
    embedding: tuple[float, ...]
    hash_atividade_origem: str
    situacao_indexacao: str


def identificador(numero: int) -> UUID:
    return UUID(int=numero)


def verificar(condicao: bool, mensagem: str) -> None:
    if not condicao:
        raise AssertionError(mensagem)


def validar_classificacoes(
    desastre: Desastre,
    classificacoes: tuple[DesastreTipo, ...],
    tipos: dict[UUID, TipoDesastre],
) -> None:
    verificar(bool(classificacoes), "Ocorrência sem classificação")
    verificar(sum(item.principal for item in classificacoes) == 1, "Principal inválido")
    pares: set[tuple[UUID, UUID]] = set()
    for item in classificacoes:
        verificar(item.id_desastre == desastre.id, "FK de desastre inválida")
        verificar(item.id_tipo_desastre in tipos, "FK de tipo inválida")
        par: tuple[UUID, UUID] = (item.id_desastre, item.id_tipo_desastre)
        verificar(par not in pares, "Classificação duplicada")
        pares.add(par)


def rejeita_classificacoes(
    desastre: Desastre,
    classificacoes: tuple[DesastreTipo, ...],
    tipos: dict[UUID, TipoDesastre],
) -> bool:
    try:
        validar_classificacoes(desastre, classificacoes, tipos)
    except AssertionError:
        return True
    return False


def exclusivo(pessoa_id: UUID | None, instituicao_id: UUID | None) -> bool:
    return (pessoa_id is None) != (instituicao_id is None)


def indice_utilizavel(atividade: Atividade, indice: IndiceAtividade, modelo: ModeloIA) -> bool:
    return (
        modelo.finalidade == "embedding"
        and modelo.ativo
        and indice.id_atividade == atividade.id
        and indice.id_modelo == modelo.id
        and indice.situacao_indexacao == "pronta"
        and indice.hash_atividade_origem == atividade.hash_conteudo_semantico
        and len(indice.embedding) == modelo.dimensao
    )


def executar() -> list[Verificacao]:
    resultados: list[Verificacao] = []
    instante: datetime = datetime(2026, 10, 8, 9, tzinfo=timezone(timedelta(hours=-3)))
    defesa: Instituicao = Instituicao(identificador(1), "Defesa Civil — fictícia")
    cozinha: Instituicao = Instituicao(identificador(2), "Cozinha comunitária — fictícia")
    logistica: Instituicao = Instituicao(identificador(3), "Associação logística — fictícia")
    instituicoes: dict[UUID, Instituicao] = {item.id: item for item in (defesa, cozinha, logistica)}
    desastre: Desastre = Desastre(
        identificador(10), "Chuvas em Vale Azul e Serra Clara — simulação",
        instante, None, "em_resposta", defesa.id,
    )
    tipos: dict[UUID, TipoDesastre] = {
        identificador(11): TipoDesastre(identificador(11), "Inundação"),
        identificador(12): TipoDesastre(identificador(12), "Deslizamento"),
    }
    classificacoes: tuple[DesastreTipo, ...] = (
        DesastreTipo(desastre.id, identificador(11), True),
        DesastreTipo(desastre.id, identificador(12), False),
    )
    validar_classificacoes(desastre, classificacoes, tipos)
    verificar(desastre.id_instituicao_coordenadora in instituicoes, "Coordenadora ausente")
    resultados.append(Verificacao("Ocorrência multifenômeno", Resultado.ATENDE,
        "Uma operação, dois tipos e exatamente um principal; coordenação institucional vinculada."))
    for nome, invalido in (
        ("Sem classificação principal", tuple(replace(item, principal=False) for item in classificacoes)),
        ("Duas classificações principais", tuple(replace(item, principal=True) for item in classificacoes)),
        ("Tipo repetido", classificacoes + (classificacoes[1],)),
        ("Tipo inexistente", (DesastreTipo(desastre.id, identificador(999), True),)),
    ):
        verificar(rejeita_classificacoes(desastre, invalido, tipos), nome)
        resultados.append(Verificacao(nome, Resultado.REGRA, "Entrada inválida rejeitada pelo validador em memória."))

    poligono: tuple[Coordenada, ...] = (
        Coordenada(Decimal("-46.60"), Decimal("-23.50")),
        Coordenada(Decimal("-46.59"), Decimal("-23.50")),
        Coordenada(Decimal("-46.59"), Decimal("-23.49")),
        Coordenada(Decimal("-46.60"), Decimal("-23.50")),
    )
    areas: dict[UUID, AreaAfetada] = {
        identificador(20): AreaAfetada(identificador(20), desastre.id, "Várzea", "0000001", poligono, "alta", instante),
        identificador(21): AreaAfetada(identificador(21), desastre.id, "Centro", "0000001", poligono, "moderada", instante),
        identificador(22): AreaAfetada(identificador(22), desastre.id, "Encosta", "0000002", poligono, "alta", instante),
    }
    verificar(all(area.id_desastre == desastre.id for area in areas.values()), "Área sem ocorrência")
    verificar(len({area.municipio_codigo_ibge for area in areas.values()}) == 2, "Cobertura incorreta")
    resultados.append(Verificacao("Território", Resultado.ATENDE,
        "Três áreas em dois municípios fictícios, vinculadas à mesma ocorrência."))
    resultados.append(Verificacao("Geometria e avaliação", Resultado.LACUNA,
        "É possível guardar uma geometria no contrato simulado; formato físico, validação espacial, limites e histórico de avaliações não estão definidos. Nenhum mapa foi renderizado."))

    joao: Pessoa = Pessoa(identificador(30), "João — condutor")
    carlos: Pessoa = Pessoa(identificador(31), "Carlos — condutor")
    marta: Pessoa = Pessoa(identificador(32), "Marta — condutora")
    paula: Pessoa = Pessoa(identificador(33), "Paula — cozinheira")
    pessoas: dict[UUID, Pessoa] = {item.id: item for item in (joao, carlos, marta, paula)}
    vinculos: tuple[PessoaInstituicao, ...] = (
        PessoaInstituicao(joao.id, logistica.id), PessoaInstituicao(carlos.id, logistica.id),
        PessoaInstituicao(marta.id, logistica.id), PessoaInstituicao(paula.id, cozinha.id),
    )
    verificar(all(v.pessoa_id in pessoas and v.instituicao_id in instituicoes for v in vinculos), "Vínculo inválido")
    curso: Curso = Curso(identificador(40), "Treinamento operacional fictício de transporte")
    formacoes: tuple[PessoaCurso, ...] = (
        PessoaCurso(joao.id, curso.id, date(2027, 1, 1), "validada"),
        PessoaCurso(carlos.id, curso.id, date(2026, 9, 1), "validada"),
        PessoaCurso(marta.id, curso.id, date(2027, 1, 1), "pendente"),
    )
    candidatos: list[UUID] = [f.pessoa_id for f in formacoes
        if f.curso_id == curso.id and f.situacao_validacao == "validada"
        and (f.validade_em is None or f.validade_em >= instante.date())]
    verificar(candidatos == [joao.id], "Filtro de formação incorreto")
    resultados.append(Verificacao("Instituições, pessoas e formação", Resultado.ATENDE,
        "Quatro pessoas vinculadas; formação validada e vigente distingue João de Carlos (vencida) e Marta (pendente)."))
    resultados.append(Verificacao("Requisitos da atividade", Resultado.LACUNA,
        "O filtro de curso foi escolhido manualmente para o cenário. Falta mapear exigências, habilitações e alternativas da atividade; João ainda não pode ser declarado apto para uma missão real."))

    caminhao: TipoRecurso = TipoRecurso(identificador(50), "Caminhão", "unidade", "individual")
    agua: TipoRecurso = TipoRecurso(identificador(51), "Água potável", "litro", "estoque")
    gerador: TipoRecurso = TipoRecurso(identificador(52), "Gerador", "unidade", "individual")
    recursos: tuple[Recurso, ...] = (
        Recurso(identificador(60), caminhao.id, "Caminhão 01", "Carga até 1000 kg", logistica.id, None, Decimal(1), "operacional"),
        Recurso(identificador(61), agua.id, "Lote de água", "Água para distribuição", cozinha.id, None, Decimal(300), "operacional"),
        Recurso(identificador(62), gerador.id, "Gerador 01", "Potência nominal 2 kVA", defesa.id, None, Decimal(1), "operacional"),
    )
    verificar(all(exclusivo(r.pessoa_id, r.instituicao_id) for r in recursos), "Responsabilidade ambígua")
    verificar(not exclusivo(joao.id, logistica.id), "Dois responsáveis aceitos")
    verificar(not exclusivo(None, None), "Recurso sem responsável aceito")
    verificar(all(r.quantidade_total == 1 for r in recursos if r.tipo_recurso_id in (caminhao.id, gerador.id)), "Bem individual inválido")
    resultados.append(Verificacao("Bens e estoques", Resultado.ATENDE,
        "Um caminhão, um gerador e estoque de 300 litros, cada recurso com exatamente um responsável."))
    resultados.append(Verificacao("Responsável exclusivo", Resultado.REGRA,
        "Recurso com dois responsáveis ou sem responsável é rejeitado pela regra proposta."))

    transporte: Atividade = Atividade(identificador(70), "Transporte de suprimentos", "Levar alimentos e água", "kg/viagem")
    alimentacao: Atividade = Atividade(identificador(71), "Preparo de refeições", "Produzir refeições", "refeições/dia")
    ofertas: tuple[OfertaAtividade, ...] = (
        OfertaAtividade(identificador(80), transporte.id, logistica.id, None, Decimal(1000), "validada"),
        OfertaAtividade(identificador(81), alimentacao.id, cozinha.id, None, Decimal(80), "validada"),
        OfertaAtividade(identificador(82), alimentacao.id, None, paula.id, Decimal(40), "validada"),
    )
    bens_oferta: tuple[OfertaRecurso, ...] = (OfertaRecurso(ofertas[0].id, recursos[0].id, Decimal(1)),)
    verificar(all(exclusivo(o.pessoa_id, o.instituicao_id) for o in ofertas), "Ofertante ambíguo")
    verificar(bens_oferta[0].recurso_id == recursos[0].id, "Bem da oferta inválido")
    resultados.append(Verificacao("Atividades e ofertas", Resultado.ATENDE,
        "Catálogo separado de três ofertas; oferta logística associa o caminhão sem reservá-lo."))

    demandas: tuple[DemandaCenario, ...] = (
        DemandaCenario("Transporte para Várzea", identificador(20), transporte.id, caminhao.id, Decimal(1), "unidade", instante, instante + timedelta(hours=2)),
        DemandaCenario("Transporte para Encosta", identificador(22), transporte.id, caminhao.id, Decimal(1), "unidade", instante, instante + timedelta(hours=2)),
        DemandaCenario("Água para Várzea", identificador(20), None, agua.id, Decimal(200), "litro", instante, instante + timedelta(hours=2)),
        DemandaCenario("Água para Encosta", identificador(22), None, agua.id, Decimal(200), "litro", instante, instante + timedelta(hours=2)),
        DemandaCenario("Refeições para Centro", identificador(21), alimentacao.id, None, Decimal(100), "refeições/dia", instante, instante + timedelta(hours=8)),
        DemandaCenario("Energia mínima de 5 kVA", identificador(22), None, gerador.id, Decimal(1), "unidade", instante, instante + timedelta(hours=2)),
    )
    verificar(all(d.id_area in areas for d in demandas), "Demanda sem área")
    resultados.append(Verificacao("Registro de necessidades", Resultado.LACUNA,
        "Seis necessidades são entradas auxiliares do exercício: ainda não há modelo de demanda, itens, prioridade, unidade, período ou atendimento parcial."))
    verificar(demandas[0].inicio < demandas[1].fim and demandas[1].inicio < demandas[0].fim, "Sem sobreposição")
    resultados.append(Verificacao("Conflito de veículo", Resultado.LACUNA,
        "Duas missões requerem o único caminhão das 09h às 11h. Cadastro atual não registra nem impede dupla reserva."))
    resultados.append(Verificacao("Disponibilidade de pessoas", Resultado.LACUNA,
        "João é candidato nas duas demandas; faltam agenda, aceite, equipe e alocação por período."))
    solicitada: Decimal = sum((d.quantidade for d in demandas if d.tipo_recurso_id == agua.id), Decimal(0))
    verificar(solicitada == 400 and recursos[1].quantidade_total == 300, "Cenário de escassez incorreto")
    resultados.append(Verificacao("Estoque compartilhado", Resultado.LACUNA,
        "Há 400 litros solicitados e 300 em estoque: déficit de 100. Faltam reservas, movimentações e entrega/atendimento parcial."))
    capacidade_aparente: Decimal = sum((o.capacidade_declarada for o in ofertas if o.atividade_id == alimentacao.id), Decimal(0))
    verificar(capacidade_aparente == 120 and ofertas[1].capacidade_declarada == 80, "Cenário de sobreposição incorreto")
    resultados.append(Verificacao("Sobreposição de capacidades", Resultado.LACUNA,
        "Somar cozinha (80) e Paula (40) sugere 120 refeições, mas Paula integra a mesma cozinha. Falta composição da oferta/equipe para comprovar capacidade adicional."))
    resultados.append(Verificacao("Compatibilidade técnica", Resultado.LACUNA,
        "A demanda exige 5 kVA e o gerador descreve 2 kVA. Falta potência estruturada, unidade e requisito; classificar como gerador não comprova atendimento."))
    resultados.append(Verificacao("Cobertura e acesso", Resultado.LACUNA,
        "A oferta inicial atende a um município; uma demanda é de outro. Faltam cobertura ampliada e condições de acesso/rota, sem inferir segurança pela proximidade."))
    resultados.append(Verificacao("Aprovação e rastreabilidade", Resultado.LACUNA,
        "Não há modelo de missão, membros, itens alocados, aprovação administrativa, aceite, entrega ou execução para fechar o ciclo."))

    modelo: ModeloIA = ModeloIA(identificador(90), "embedding", True, 3)
    indice: IndiceAtividade = IndiceAtividade(transporte.id, modelo.id, (1.0, 0.0, 0.0), transporte.hash_conteudo_semantico, "pronta")
    verificar(indice_utilizavel(transporte, indice, modelo), "Índice atual rejeitado")
    alterada: Atividade = replace(transporte, descricao="Somente transporte terrestre leve")
    verificar(not indice_utilizavel(alterada, indice, modelo), "Embedding obsoleto aceito")
    resultados.append(Verificacao("Alteração de conteúdo", Resultado.REGRA,
        "Alterar a descrição muda o hash e exclui o embedding antigo; publicação condicionada ao mesmo hash rejeita o resultado antigo."))
    novo_modelo: ModeloIA = ModeloIA(identificador(91), "embedding", True, 4)
    verificar(not indice_utilizavel(transporte, indice, novo_modelo), "Mistura de modelos aceita")
    verificar(not indice_utilizavel(transporte, replace(indice, embedding=(1.0, 0.0)), modelo), "Dimensão errada aceita")
    verificar(not indice_utilizavel(transporte, indice, replace(modelo, finalidade="inferencia_texto", dimensao=None)), "Modelo de texto aceito no índice")
    resultados.append(Verificacao("Modelo e dimensão", Resultado.REGRA,
        "Vetor de outro modelo, dimensão incorreta e modelo de inferência são rejeitados. Vetores são fixtures artificiais; não foi avaliada relevância semântica."))
    fechado: Desastre = replace(desastre, situacao="encerrado", encerramento_em=instante + timedelta(days=2))
    verificar(fechado.encerramento_em is not None and fechado.encerramento_em >= fechado.inicio_em, "Encerramento inválido")
    verificar(all(area.id_desastre == fechado.id for area in areas.values()), "Histórico perdido")
    resultados.append(Verificacao("Encerramento e histórico", Resultado.ATENDE,
        "Encerramento mantém ocorrência, classificações e áreas; regras para pendências e reabertura ainda precisam de definição."))
    return resultados


def main() -> None:
    resultados: list[Verificacao] = executar()
    contagens: dict[Resultado, int] = {tipo: sum(item.resultado == tipo for item in resultados) for tipo in Resultado}
    print("# Simulação em memória — avaliação do modelo lógico\n")
    print("Conclusão: o cadastro representa o desastre e as capacidades, mas o modelo ainda não fecha o ciclo de atendimento e alocação.\n")
    print("Cenário fictício: inundação e deslizamento; três áreas em dois municípios; três instituições; quatro pessoas; seis demandas; um caminhão, um gerador e 300 litros de água. Janela inicial: 08/10/2026, 09h–11h, UTC−03:00.\n")
    print("Os municípios, pessoas, instituições e códigos territoriais são fictícios. O mesmo polígono ilustrativo foi reutilizado: a simulação não valida geografia ou exibe mapa. As qualificações são exemplos de modelagem, não requisitos reais de atuação.\n")
    print(f"Foram exercitados {len(resultados)} cenários: {contagens[Resultado.ATENDE]} representáveis, {contagens[Resultado.REGRA]} verificações de regras e {contagens[Resultado.LACUNA]} lacunas demonstradas.\n")
    print("| Cenário | Resultado | Evidência |\n|---|---|---|")
    for item in resultados:
        print(f"| {item.cenario} | {item.resultado.value} | {item.evidencia} |")
    print("\n## Alcance da verificação\n")
    print("Execução Python 3.13 com biblioteca padrão, dataclasses tipadas e dados somente em memória. As classes são recortes para o exercício, não implementação do backend. Demandas e seus períodos são entradas auxiliares, sem promover campos novos a decisões aprovadas. Não há PostgreSQL, Alembic, restrições SQL, transações concorrentes, criptografia, frontend, LLM ou embeddings reais sendo testados.\n")
    print("Os validadores em memória exercitam regras documentadas. Seu sucesso não comprova que um banco ainda não implementado rejeitaria os mesmos casos. O exercício de hash verifica consistência lógica, sem simular corrida entre processos nem fixar a serialização final. Não houve medição de redução de tempo ou validação de qualidade de RAG.\n")
    print("As verificações de embedding usam apenas o catálogo de atividades com vetores artificiais. Não foram exercitadas cobertura dos quatro catálogos, troca transacional do modelo ativo, classificação por profissão, aprovação de missões ou reserva concorrente. As lacunas são achados do modelo, não falhas de testes de uma aplicação implementada.\n")
    print("## Próxima discussão sugerida\n")
    print("Definir demanda e itens solicitados, depois requisitos e qualificações, disponibilidade/equipes, composição das ofertas, missões/alocações, reservas/movimentos e entrega/atendimento parcial. Esses pontos são achados da simulação, não novas decisões aprovadas.\n")
    print("Reprodução: `python simulacoes/simular_desastre.py`, usando Python 3.13. Nenhum dado é persistido pelo script.")


if __name__ == "__main__":
    main()
