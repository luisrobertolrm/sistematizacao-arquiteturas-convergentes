"""Dados fictícios determinísticos. Não há configuração ou credencial real."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from modelos import (
    AreaAfetada, Atividade, AtividadeTermo, CategoriaAtividade, Cenario,
    ConexaoIA, Coordenada, Curso, Demanda, DemandaItem, Desastre, DesastreTipo,
    Finalidade, IndiceAtividade, Instituicao, ModeloIA, OfertaAtividade,
    OfertaAtividadeRecurso, Pessoa, PessoaCurso, PessoaInstituicao,
    PessoaProfissao, Profissao, Recurso, TipoDesastre, TipoRecurso,
    UnidadeMedida, Validacao,
)


def uid(numero: int) -> UUID:
    return UUID(int=numero)


def poligono(longitude: str, latitude: str) -> tuple[Coordenada, ...]:
    x: Decimal = Decimal(longitude)
    y: Decimal = Decimal(latitude)
    delta: Decimal = Decimal("0.001")
    return (
        Coordenada(x, y), Coordenada(x + delta, y),
        Coordenada(x + delta, y + delta), Coordenada(x, y + delta),
        Coordenada(x, y),
    )


def criar_cenario() -> Cenario:
    instante: datetime = datetime(2026, 10, 8, 9, tzinfo=timezone(timedelta(hours=-3)))
    municipio: str = "0000001"  # Código fictício, sem correspondência territorial.
    instituicoes: dict[UUID, Instituicao] = {
        uid(n): Instituicao(uid(n), nome, municipio, Validacao.VALIDADA)
        for n, nome in (
            (1, "Defesa Civil fictícia"), (2, "Cozinha comunitária fictícia"),
            (3, "Associação logística fictícia"),
        )
    }
    pessoas: dict[UUID, Pessoa] = {
        uid(n): Pessoa(uid(n), nome, municipio, Validacao.VALIDADA)
        for n, nome in ((30, "João"), (31, "Carlos"), (32, "Marta"), (33, "Paula"))
    }
    vinculos: tuple[PessoaInstituicao, ...] = tuple(
        PessoaInstituicao(uid(p), uid(i), date(2025, 1, 1), None, Validacao.VALIDADA)
        for p, i in ((30, 3), (31, 3), (32, 3), (33, 2))
    )
    profissoes: dict[UUID, Profissao] = {
        uid(35): Profissao(uid(35), "Condutor — exemplo"),
        uid(36): Profissao(uid(36), "Cozinheiro — exemplo"),
    }
    qualificacoes: tuple[PessoaProfissao, ...] = tuple(
        PessoaProfissao(uid(p), uid(prof), Validacao.VALIDADA)
        for p, prof in ((30, 35), (31, 35), (32, 35), (33, 36))
    )
    cursos: dict[UUID, Curso] = {
        uid(40): Curso(uid(40), "Treinamento fictício de transporte"),
        uid(41): Curso(uid(41), "Treinamento fictício de alimentação"),
    }
    formacoes: tuple[PessoaCurso, ...] = (
        PessoaCurso(uid(30), uid(40), date(2025, 1, 1), date(2027, 1, 1), Validacao.VALIDADA),
        PessoaCurso(uid(31), uid(40), date(2025, 1, 1), date(2026, 9, 1), Validacao.VALIDADA),
        PessoaCurso(uid(32), uid(40), date(2025, 1, 1), date(2027, 1, 1), Validacao.PENDENTE),
        PessoaCurso(uid(33), uid(41), date(2025, 1, 1), None, Validacao.VALIDADA),
    )
    unidades: dict[UUID, UnidadeMedida] = {
        uid(n): UnidadeMedida(uid(n), codigo, nome)
        for n, codigo, nome in (
            (100, "un", "Unidade"), (101, "l", "Litro"),
            (102, "ref", "Refeição"), (103, "viagem", "Viagem"),
        )
    }
    categorias: dict[UUID, CategoriaAtividade] = {
        uid(110): CategoriaAtividade(uid(110), "Logística"),
        uid(111): CategoriaAtividade(uid(111), "Alimentação"),
    }
    atividades: dict[UUID, Atividade] = {
        uid(70): Atividade(uid(70), "TRANSP", "Transporte de suprimentos",
                           "Levar alimentos e água; condições a confirmar", uid(110), uid(103)),
        uid(71): Atividade(uid(71), "REFEICAO", "Preparo de refeições",
                           "Preparar refeições; período-base ainda a detalhar", uid(111), uid(102)),
    }
    ofertas: dict[UUID, OfertaAtividade] = {
        uid(n): OfertaAtividade(uid(n), uid(a), uid(i) if i else None,
                                uid(p) if p else None, Decimal(q), municipio, Validacao.VALIDADA)
        for n, a, i, p, q in (
            (80, 70, 3, 0, "1"), (81, 71, 2, 0, "80"), (82, 71, 0, 33, "40"),
        )
    }
    tipos_recurso: dict[UUID, TipoRecurso] = {
        uid(50): TipoRecurso(uid(50), "Caminhão", uid(100), "individual"),
        uid(51): TipoRecurso(uid(51), "Água potável", uid(101), "estoque"),
        uid(52): TipoRecurso(uid(52), "Gerador", uid(100), "individual"),
    }
    recursos: dict[UUID, Recurso] = {
        uid(n): Recurso(uid(n), uid(t), nome, descricao, uid(i), None,
                        Decimal(q), "operacional", municipio)
        for n, t, nome, descricao, i, q in (
            (60, 50, "Caminhão 01", "Carga até 1000 kg; verificar acesso", 3, "1"),
            (61, 51, "Lote de água", "Água para distribuição", 2, "300"),
            (62, 52, "Gerador 01", "Potência nominal de 2 kVA, somente em texto", 1, "1"),
        )
    }
    desastre: Desastre = Desastre(uid(10), "Chuvas em Vale Azul — fictício", instante, "em_resposta", uid(1))
    tipos_desastre: dict[UUID, TipoDesastre] = {
        uid(11): TipoDesastre(uid(11), "Inundação"),
        uid(12): TipoDesastre(uid(12), "Deslizamento"),
    }
    classificacoes: tuple[DesastreTipo, ...] = (
        DesastreTipo(desastre.id, uid(11), True), DesastreTipo(desastre.id, uid(12), False),
    )
    areas: dict[UUID, AreaAfetada] = {
        uid(n): AreaAfetada(uid(n), desastre.id, nome, municipio, poligono(x, y), gravidade, instante)
        for n, nome, x, y, gravidade in (
            (20, "Várzea", "-46.600", "-23.500", "alta"),
            (21, "Centro", "-46.595", "-23.495", "moderada"),
            (22, "Encosta", "-46.590", "-23.490", "alta"),
        )
    }
    demandas: dict[UUID, Demanda] = {
        uid(n): Demanda(uid(n), uid(a), titulo, prioridade, instante,
                        instante + timedelta(hours=horas), uid(33), "aberta")
        for n, a, titulo, prioridade, horas in (
            (200, 20, "Suprimentos para Várzea", "urgente", 2),
            (201, 22, "Suprimentos e energia para Encosta", "urgente", 2),
            (202, 21, "Refeições para Centro", "urgente", 8),
        )
    }
    itens: dict[UUID, DemandaItem] = {
        uid(n): DemandaItem(uid(n), uid(d), uid(a) if a else None, uid(t) if t else None,
                            Decimal(q), uid(u), obs)
        for n, d, a, t, q, u, obs in (
            (210, 200, 70, 0, "1", 103, "Condições da viagem a confirmar"),
            (211, 200, 0, 51, "200", 101, None),
            (212, 201, 70, 0, "1", 103, "Mesmo horário do transporte para Várzea"),
            (213, 201, 0, 51, "200", 101, None),
            (214, 202, 71, 0, "100", 102, "Capacidade por período não validada"),
            (215, 201, 0, 52, "1", 100, "Necessário mínimo de 5 kVA; requisito ainda não estruturado"),
        )
    }
    conexao: ConexaoIA = ConexaoIA(uid(89), "Adaptador simulado", "fixture",
                                  "https://provedor.invalid", "nenhuma", None, None)
    modelos: dict[UUID, ModeloIA] = {
        uid(90): ModeloIA(uid(90), conexao.id, "embedding-artificial-v1", Finalidade.EMBEDDING, True, 3),
        uid(91): ModeloIA(uid(91), conexao.id, "texto-simulado-v1", Finalidade.TEXTO, True, None),
        uid(92): ModeloIA(uid(92), conexao.id, "embedding-artificial-v2", Finalidade.EMBEDDING, False, 4),
        uid(93): ModeloIA(uid(93), conexao.id, "texto-simulado-v2", Finalidade.TEXTO, False, None),
    }
    indices: tuple[IndiceAtividade, ...] = tuple(
        IndiceAtividade(uid(a), uid(m), vetor, atividades[uid(a)].hash_conteudo_semantico, "pronta")
        for a, m, vetor in (
            (70, 90, (1.0, 0.0, 0.0)), (71, 90, (0.0, 1.0, 0.0)),
            (70, 92, (1.0, 0.0, 0.0, 0.0)),
        )
    )
    return Cenario(
        instante, instituicoes, pessoas, vinculos, profissoes, qualificacoes,
        cursos, formacoes, unidades, categorias, atividades,
        (AtividadeTermo(uid(70), "levar suprimentos"), AtividadeTermo(uid(71), "cozinhar")),
        ofertas, (OfertaAtividadeRecurso(uid(80), uid(60), Decimal(1)),),
        tipos_recurso, recursos, tipos_desastre, desastre, classificacoes, areas,
        demandas, itens, {conexao.id: conexao}, modelos, indices, uid(40),
    )
