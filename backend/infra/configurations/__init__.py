"""Mapeamentos SQLAlchemy separados das entidades de domínio."""

from infra.configurations.cadastros import metadata as metadata
from infra.configurations.capacidades import atividades as atividades
from infra.configurations.demandas import demandas as demandas
from infra.configurations.desastres import desastres as desastres
from infra.configurations.indices import atividade_indice_semantico as atividade_indice_semantico
from infra.configurations.modelos_ia import modelo_ia as modelo_ia
from infra.configurations.qualificacoes import cursos as cursos
from infra.configurations.recomendacoes import recomendacoes as recomendacoes
from infra.configurations.recursos import recursos as recursos
