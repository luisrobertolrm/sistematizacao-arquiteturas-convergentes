import { Tela } from './contratos';

export const TELAS: readonly Tela[] = [
  {
    "chave": "instituicoes",
    "nome": "Instituições",
    "singular": "instituição",
    "grupo": "Rede",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "nome",
        "nome": "Nome",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "municipio_codigo_ibge",
        "nome": "Município (código ilustrativo)",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "uf",
        "nome": "UF",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "email_contato",
        "nome": "Email",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "telefone_contato",
        "nome": "Telefone",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "latitude",
        "nome": "Latitude",
        "tipo": "numero",
        "obrigatorio": false,
        "minimo": -90
      },
      {
        "chave": "longitude",
        "nome": "Longitude",
        "tipo": "numero",
        "obrigatorio": false,
        "minimo": -180
      },
      {
        "chave": "situacao_cadastral",
        "nome": "Situação cadastral",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "pendente",
            "nome": "Pendente"
          },
          {
            "valor": "validada",
            "nome": "Validada"
          },
          {
            "valor": "rejeitada",
            "nome": "Rejeitada"
          }
        ],
        "padrao": "pendente"
      },
      {
        "chave": "tipo",
        "nome": "Tipo",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "associacao",
            "nome": "Associação"
          },
          {
            "valor": "ong",
            "nome": "ONG"
          },
          {
            "valor": "orgao_publico",
            "nome": "Órgão público"
          },
          {
            "valor": "empresa",
            "nome": "Empresa"
          }
        ],
        "padrao": "associacao"
      },
      {
        "chave": "razao_social",
        "nome": "Razão social",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "cnpj",
        "nome": "CNPJ",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "descricao",
        "nome": "Descrição",
        "tipo": "area",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "nome",
      "tipo",
      "situacao_cadastral"
    ],
    "menu": true,
    "relacoes": [
      {
        "tabela": "pessoa_instituicao",
        "campo": "instituicao_id",
        "nome": "Pessoas vinculadas"
      },
      {
        "tabela": "ofertas_atividade",
        "campo": "instituicao_id",
        "nome": "Ofertas institucionais"
      },
      {
        "tabela": "recursos",
        "campo": "instituicao_id",
        "nome": "Recursos sob responsabilidade"
      }
    ]
  },
  {
    "chave": "pessoas",
    "nome": "Pessoas",
    "singular": "pessoa",
    "grupo": "Rede",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "nome",
        "nome": "Nome",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "municipio_codigo_ibge",
        "nome": "Município (código ilustrativo)",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "uf",
        "nome": "UF",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "email_contato",
        "nome": "Email",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "telefone_contato",
        "nome": "Telefone",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "latitude",
        "nome": "Latitude",
        "tipo": "numero",
        "obrigatorio": false,
        "minimo": -90
      },
      {
        "chave": "longitude",
        "nome": "Longitude",
        "tipo": "numero",
        "obrigatorio": false,
        "minimo": -180
      },
      {
        "chave": "situacao_cadastral",
        "nome": "Situação cadastral",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "pendente",
            "nome": "Pendente"
          },
          {
            "valor": "validada",
            "nome": "Validada"
          },
          {
            "valor": "rejeitada",
            "nome": "Rejeitada"
          }
        ],
        "padrao": "pendente"
      }
    ],
    "colunas": [
      "nome",
      "municipio_codigo_ibge",
      "situacao_cadastral"
    ],
    "menu": true,
    "relacoes": [
      {
        "tabela": "pessoa_instituicao",
        "campo": "pessoa_id",
        "nome": "Instituições"
      },
      {
        "tabela": "pessoa_profissao",
        "campo": "pessoa_id",
        "nome": "Profissões"
      },
      {
        "tabela": "pessoa_curso",
        "campo": "pessoa_id",
        "nome": "Cursos e renovações"
      },
      {
        "tabela": "ofertas_atividade",
        "campo": "pessoa_id",
        "nome": "Ofertas pessoais"
      },
      {
        "tabela": "recursos",
        "campo": "pessoa_id",
        "nome": "Recursos sob responsabilidade"
      }
    ]
  },
  {
    "chave": "pessoa_instituicao",
    "nome": "Vínculos institucionais",
    "singular": "vínculo",
    "grupo": "Rede",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "pessoa_id",
        "nome": "Pessoa",
        "tipo": "referencia",
        "tabela": "pessoas",
        "obrigatorio": true
      },
      {
        "chave": "instituicao_id",
        "nome": "Instituição",
        "tipo": "referencia",
        "tabela": "instituicoes",
        "obrigatorio": true
      },
      {
        "chave": "tipo_vinculo",
        "nome": "Tipo",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "voluntario",
            "nome": "Voluntário"
          },
          {
            "valor": "funcionario",
            "nome": "Funcionário"
          },
          {
            "valor": "associado",
            "nome": "Associado"
          },
          {
            "valor": "representante",
            "nome": "Representante"
          }
        ],
        "padrao": "voluntario"
      },
      {
        "chave": "inicio_em",
        "nome": "Início",
        "tipo": "data",
        "obrigatorio": true
      },
      {
        "chave": "fim_em",
        "nome": "Encerramento",
        "tipo": "data",
        "obrigatorio": false
      },
      {
        "chave": "situacao_validacao",
        "nome": "Validação",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "pendente",
            "nome": "Pendente"
          },
          {
            "valor": "validada",
            "nome": "Validada"
          },
          {
            "valor": "rejeitada",
            "nome": "Rejeitada"
          }
        ],
        "padrao": "pendente"
      }
    ],
    "colunas": [
      "pessoa_id",
      "instituicao_id",
      "tipo_vinculo",
      "fim_em"
    ],
    "menu": false
  },
  {
    "chave": "profissoes",
    "nome": "Profissões",
    "singular": "profissão",
    "grupo": "Catálogos",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "nome",
        "nome": "Nome",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "descricao",
        "nome": "Descrição",
        "tipo": "area",
        "obrigatorio": false
      },
      {
        "chave": "codigo_cbo",
        "nome": "CBO",
        "tipo": "texto",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "nome",
      "codigo_cbo"
    ],
    "menu": true,
    "relacoes": [
      {
        "tabela": "pessoa_profissao",
        "campo": "profissao_id",
        "nome": "Qualificações individuais"
      }
    ]
  },
  {
    "chave": "pessoa_profissao",
    "nome": "Profissões das pessoas",
    "singular": "qualificação",
    "grupo": "Rede",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "pessoa_id",
        "nome": "Pessoa",
        "tipo": "referencia",
        "tabela": "pessoas",
        "obrigatorio": true
      },
      {
        "chave": "profissao_id",
        "nome": "Profissão",
        "tipo": "referencia",
        "tabela": "profissoes",
        "obrigatorio": true
      },
      {
        "chave": "registro_profissional",
        "nome": "Registro",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "orgao_registro",
        "nome": "Órgão",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "uf_registro",
        "nome": "UF do registro",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "validade_em",
        "nome": "Validade",
        "tipo": "data",
        "obrigatorio": false
      },
      {
        "chave": "situacao_validacao",
        "nome": "Validação",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "pendente",
            "nome": "Pendente"
          },
          {
            "valor": "validada",
            "nome": "Validada"
          },
          {
            "valor": "rejeitada",
            "nome": "Rejeitada"
          }
        ],
        "padrao": "pendente"
      }
    ],
    "colunas": [
      "pessoa_id",
      "profissao_id",
      "registro_profissional",
      "validade_em",
      "situacao_validacao"
    ],
    "menu": false
  },
  {
    "chave": "cursos",
    "nome": "Cursos",
    "singular": "curso",
    "grupo": "Catálogos",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "nome",
        "nome": "Nome",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "descricao",
        "nome": "Descrição",
        "tipo": "area",
        "obrigatorio": false
      },
      {
        "chave": "tipo",
        "nome": "Tipo",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "tecnico",
            "nome": "Técnico"
          },
          {
            "valor": "capacitacao",
            "nome": "Capacitação"
          },
          {
            "valor": "treinamento",
            "nome": "Treinamento"
          }
        ],
        "padrao": "tecnico"
      }
    ],
    "colunas": [
      "nome",
      "tipo"
    ],
    "menu": true,
    "relacoes": [
      {
        "tabela": "pessoa_curso",
        "campo": "curso_id",
        "nome": "Formações individuais"
      }
    ]
  },
  {
    "chave": "pessoa_curso",
    "nome": "Formações e renovações",
    "singular": "formação",
    "grupo": "Rede",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "pessoa_id",
        "nome": "Pessoa",
        "tipo": "referencia",
        "tabela": "pessoas",
        "obrigatorio": true
      },
      {
        "chave": "curso_id",
        "nome": "Curso",
        "tipo": "referencia",
        "tabela": "cursos",
        "obrigatorio": true
      },
      {
        "chave": "instituicao_emissora",
        "nome": "Instituição emissora",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "conclusao_em",
        "nome": "Conclusão",
        "tipo": "data",
        "obrigatorio": true
      },
      {
        "chave": "validade_em",
        "nome": "Validade",
        "tipo": "data",
        "obrigatorio": false
      },
      {
        "chave": "carga_horaria",
        "nome": "Carga horária",
        "tipo": "numero",
        "obrigatorio": false,
        "minimo": 0.01
      },
      {
        "chave": "comprovante_referencia",
        "nome": "Referência do comprovante",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "situacao_validacao",
        "nome": "Validação",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "pendente",
            "nome": "Pendente"
          },
          {
            "valor": "validada",
            "nome": "Validada"
          },
          {
            "valor": "rejeitada",
            "nome": "Rejeitada"
          }
        ],
        "padrao": "pendente"
      }
    ],
    "colunas": [
      "pessoa_id",
      "curso_id",
      "conclusao_em",
      "validade_em",
      "situacao_validacao"
    ],
    "menu": false,
    "descricao": "Comprovante é uma referência fictícia; não há upload/download."
  },
  {
    "chave": "unidades_medida",
    "nome": "Unidades de medida",
    "singular": "unidade",
    "grupo": "Catálogos",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "codigo",
        "nome": "Código",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "nome",
        "nome": "Nome",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "simbolo",
        "nome": "Símbolo",
        "tipo": "texto",
        "obrigatorio": true
      }
    ],
    "colunas": [
      "nome",
      "simbolo"
    ],
    "menu": true
  },
  {
    "chave": "categorias_atividade",
    "nome": "Categorias de atividade",
    "singular": "categoria",
    "grupo": "Catálogos",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "codigo",
        "nome": "Código",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "nome",
        "nome": "Nome",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "descricao",
        "nome": "Descrição",
        "tipo": "area",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "codigo",
      "nome"
    ],
    "menu": true
  },
  {
    "chave": "atividades",
    "nome": "Atividades",
    "singular": "atividade",
    "grupo": "Capacidades",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "codigo",
        "nome": "Código",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "nome",
        "nome": "Nome",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "descricao",
        "nome": "Descrição",
        "tipo": "area",
        "obrigatorio": false
      },
      {
        "chave": "categoria_id",
        "nome": "Categoria",
        "tipo": "referencia",
        "tabela": "categorias_atividade",
        "obrigatorio": true
      },
      {
        "chave": "orientacoes",
        "nome": "Orientações",
        "tipo": "area",
        "obrigatorio": false
      },
      {
        "chave": "restricoes",
        "nome": "Restrições",
        "tipo": "area",
        "obrigatorio": false
      },
      {
        "chave": "id_unidade_capacidade",
        "nome": "Unidade da capacidade",
        "tipo": "referencia",
        "tabela": "unidades_medida",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "codigo",
      "nome",
      "categoria_id"
    ],
    "menu": true,
    "relacoes": [
      {
        "tabela": "atividade_termos",
        "campo": "atividade_id",
        "nome": "Termos e sinônimos"
      },
      {
        "tabela": "ofertas_atividade",
        "campo": "atividade_id",
        "nome": "Quem oferece"
      },
      {
        "tabela": "atividade_indice_semantico",
        "campo": "id_atividade",
        "nome": "Índices por modelo"
      }
    ]
  },
  {
    "chave": "atividade_termos",
    "nome": "Termos de atividade",
    "singular": "termo",
    "grupo": "Capacidades",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "atividade_id",
        "nome": "Atividade",
        "tipo": "referencia",
        "tabela": "atividades",
        "obrigatorio": true
      },
      {
        "chave": "termo",
        "nome": "Termo",
        "tipo": "texto",
        "obrigatorio": true
      }
    ],
    "colunas": [
      "atividade_id",
      "termo"
    ],
    "menu": false
  },
  {
    "chave": "ofertas_atividade",
    "nome": "Ofertas de atividades",
    "singular": "oferta",
    "grupo": "Capacidades",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "atividade_id",
        "nome": "Atividade",
        "tipo": "referencia",
        "tabela": "atividades",
        "obrigatorio": true
      },
      {
        "chave": "instituicao_id",
        "nome": "Instituição ofertante",
        "tipo": "referencia",
        "tabela": "instituicoes",
        "obrigatorio": false
      },
      {
        "chave": "pessoa_id",
        "nome": "Pessoa ofertante",
        "tipo": "referencia",
        "tabela": "pessoas",
        "obrigatorio": false
      },
      {
        "chave": "descricao_complementar",
        "nome": "Condições da oferta",
        "tipo": "area",
        "obrigatorio": false
      },
      {
        "chave": "capacidade_declarada",
        "nome": "Capacidade declarada",
        "tipo": "numero",
        "obrigatorio": false,
        "minimo": 0.01
      },
      {
        "chave": "municipio_atendimento_codigo_ibge",
        "nome": "Município de atendimento",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "situacao_validacao",
        "nome": "Validação",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "pendente",
            "nome": "Pendente"
          },
          {
            "valor": "validada",
            "nome": "Validada"
          },
          {
            "valor": "rejeitada",
            "nome": "Rejeitada"
          }
        ],
        "padrao": "pendente"
      }
    ],
    "colunas": [
      "atividade_id",
      "instituicao_id",
      "pessoa_id",
      "capacidade_declarada",
      "situacao_validacao"
    ],
    "menu": true,
    "descricao": "Informe exatamente um ofertante. Capacidade declarada não é saldo reservado; período-base ainda depende de definição.",
    "relacoes": [
      {
        "tabela": "oferta_atividade_recurso",
        "campo": "oferta_atividade_id",
        "nome": "Recursos previstos"
      }
    ]
  },
  {
    "chave": "oferta_atividade_recurso",
    "nome": "Recursos de ofertas",
    "singular": "recurso previsto",
    "grupo": "Capacidades",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "oferta_atividade_id",
        "nome": "Oferta",
        "tipo": "referencia",
        "tabela": "ofertas_atividade",
        "obrigatorio": true
      },
      {
        "chave": "recurso_id",
        "nome": "Recurso",
        "tipo": "referencia",
        "tabela": "recursos",
        "obrigatorio": true
      },
      {
        "chave": "quantidade_prevista",
        "nome": "Quantidade prevista",
        "tipo": "numero",
        "obrigatorio": true,
        "minimo": 0.01
      }
    ],
    "colunas": [
      "oferta_atividade_id",
      "recurso_id",
      "quantidade_prevista"
    ],
    "menu": false
  },
  {
    "chave": "tipos_recurso",
    "nome": "Tipos de recurso",
    "singular": "tipo de recurso",
    "grupo": "Catálogos",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "nome",
        "nome": "Nome",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "descricao",
        "nome": "Descrição",
        "tipo": "area",
        "obrigatorio": false
      },
      {
        "chave": "categoria",
        "nome": "Categoria",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "veiculo",
            "nome": "Veículo"
          },
          {
            "valor": "equipamento",
            "nome": "Equipamento"
          },
          {
            "valor": "material",
            "nome": "Material"
          },
          {
            "valor": "insumo",
            "nome": "Insumo"
          }
        ],
        "padrao": "veiculo"
      },
      {
        "chave": "id_unidade_medida",
        "nome": "Unidade",
        "tipo": "referencia",
        "tabela": "unidades_medida",
        "obrigatorio": true
      },
      {
        "chave": "modo_controle",
        "nome": "Controle",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "individual",
            "nome": "Individual"
          },
          {
            "valor": "estoque",
            "nome": "Estoque"
          }
        ],
        "padrao": "individual"
      }
    ],
    "colunas": [
      "nome",
      "categoria",
      "modo_controle",
      "id_unidade_medida"
    ],
    "menu": true
  },
  {
    "chave": "recursos",
    "nome": "Recursos",
    "singular": "recurso",
    "grupo": "Capacidades",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "nome",
        "nome": "Nome",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "descricao",
        "nome": "Descrição",
        "tipo": "area",
        "obrigatorio": false
      },
      {
        "chave": "tipo_recurso_id",
        "nome": "Tipo de recurso",
        "tipo": "referencia",
        "tabela": "tipos_recurso",
        "obrigatorio": true
      },
      {
        "chave": "instituicao_id",
        "nome": "Instituição responsável",
        "tipo": "referencia",
        "tabela": "instituicoes",
        "obrigatorio": false
      },
      {
        "chave": "pessoa_id",
        "nome": "Pessoa responsável",
        "tipo": "referencia",
        "tabela": "pessoas",
        "obrigatorio": false
      },
      {
        "chave": "identificacao",
        "nome": "Identificação",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "quantidade_total",
        "nome": "Quantidade total",
        "tipo": "numero",
        "obrigatorio": true,
        "minimo": 0
      },
      {
        "chave": "estado_operacional",
        "nome": "Condição",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "operacional",
            "nome": "Operacional"
          },
          {
            "valor": "em_manutencao",
            "nome": "Em manutenção"
          },
          {
            "valor": "indisponivel",
            "nome": "Indisponível"
          }
        ],
        "padrao": "operacional"
      },
      {
        "chave": "municipio_codigo_ibge",
        "nome": "Município",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "latitude",
        "nome": "Latitude",
        "tipo": "numero",
        "obrigatorio": false,
        "minimo": -90
      },
      {
        "chave": "longitude",
        "nome": "Longitude",
        "tipo": "numero",
        "obrigatorio": false,
        "minimo": -180
      }
    ],
    "colunas": [
      "nome",
      "tipo_recurso_id",
      "quantidade_total",
      "estado_operacional"
    ],
    "menu": true,
    "descricao": "Exatamente um responsável. Nenhuma aprovação de recomendação reduz esta quantidade."
  },
  {
    "chave": "tipos_desastre",
    "nome": "Tipos de desastre",
    "singular": "tipo de desastre",
    "grupo": "Catálogos",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "codigo",
        "nome": "Código ilustrativo",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "nome",
        "nome": "Nome",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "descricao",
        "nome": "Descrição",
        "tipo": "area",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "codigo",
      "nome"
    ],
    "menu": true,
    "descricao": "Classificação fictícia para navegação, sem adoção de taxonomia oficial."
  },
  {
    "chave": "desastres",
    "nome": "Desastres",
    "singular": "ocorrência",
    "grupo": "Operação",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "titulo",
        "nome": "Título",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "descricao",
        "nome": "Descrição",
        "tipo": "area",
        "obrigatorio": true
      },
      {
        "chave": "inicio_em",
        "nome": "Início",
        "tipo": "datahora",
        "obrigatorio": true
      },
      {
        "chave": "encerramento_em",
        "nome": "Encerramento",
        "tipo": "datahora",
        "obrigatorio": false
      },
      {
        "chave": "situacao",
        "nome": "Situação",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "em_monitoramento",
            "nome": "Em monitoramento"
          },
          {
            "valor": "em_resposta",
            "nome": "Em resposta"
          },
          {
            "valor": "em_recuperacao",
            "nome": "Em recuperação"
          },
          {
            "valor": "encerrado",
            "nome": "Encerrado"
          }
        ],
        "padrao": "em_monitoramento"
      },
      {
        "chave": "id_instituicao_coordenadora",
        "nome": "Instituição coordenadora",
        "tipo": "referencia",
        "tabela": "instituicoes",
        "obrigatorio": true
      }
    ],
    "colunas": [
      "titulo",
      "situacao",
      "inicio_em"
    ],
    "menu": true,
    "relacoes": [
      {
        "tabela": "desastre_tipo",
        "campo": "id_desastre",
        "nome": "Classificações"
      },
      {
        "tabela": "areas_afetadas",
        "campo": "id_desastre",
        "nome": "Áreas afetadas"
      }
    ]
  },
  {
    "chave": "desastre_tipo",
    "nome": "Classificações da ocorrência",
    "singular": "classificação",
    "grupo": "Operação",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "id_desastre",
        "nome": "Ocorrência",
        "tipo": "referencia",
        "tabela": "desastres",
        "obrigatorio": true
      },
      {
        "chave": "id_tipo_desastre",
        "nome": "Tipo",
        "tipo": "referencia",
        "tabela": "tipos_desastre",
        "obrigatorio": true
      },
      {
        "chave": "principal",
        "nome": "Classificação principal",
        "tipo": "booleano",
        "padrao": false
      }
    ],
    "colunas": [
      "id_desastre",
      "id_tipo_desastre",
      "principal"
    ],
    "menu": false,
    "somenteLeitura": true
  },
  {
    "chave": "areas_afetadas",
    "nome": "Áreas afetadas",
    "singular": "área",
    "grupo": "Operação",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "id_desastre",
        "nome": "Ocorrência",
        "tipo": "referencia",
        "tabela": "desastres",
        "obrigatorio": true
      },
      {
        "chave": "nome",
        "nome": "Nome",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "descricao",
        "nome": "Descrição",
        "tipo": "area",
        "obrigatorio": false
      },
      {
        "chave": "municipio_codigo_ibge",
        "nome": "Município",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "gravidade",
        "nome": "Gravidade demonstrativa",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "alta",
            "nome": "Alta"
          },
          {
            "valor": "moderada",
            "nome": "Moderada"
          },
          {
            "valor": "baixa",
            "nome": "Baixa"
          }
        ],
        "padrao": "alta"
      },
      {
        "chave": "situacao",
        "nome": "Situação demonstrativa",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "em_avaliacao",
            "nome": "Em avaliação"
          },
          {
            "valor": "avaliada",
            "nome": "Avaliada"
          },
          {
            "valor": "monitorada",
            "nome": "Monitorada"
          }
        ],
        "padrao": "em_avaliacao"
      }
    ],
    "colunas": [
      "nome",
      "id_desastre",
      "gravidade",
      "situacao"
    ],
    "menu": true,
    "descricao": "A geometria é desenhada na tela Mapa. Escalas ilustrativas, ainda sujeitas a definição.",
    "relacoes": [
      {
        "tabela": "demandas",
        "campo": "id_area_afetada",
        "nome": "Demandas da área"
      }
    ]
  },
  {
    "chave": "demandas",
    "nome": "Demandas",
    "singular": "demanda",
    "grupo": "Operação",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "id_area_afetada",
        "nome": "Área",
        "tipo": "referencia",
        "tabela": "areas_afetadas",
        "obrigatorio": true
      },
      {
        "chave": "titulo",
        "nome": "Título",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "descricao",
        "nome": "Justificativa",
        "tipo": "area",
        "obrigatorio": true
      },
      {
        "chave": "prioridade",
        "nome": "Prioridade demonstrativa",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "urgente",
            "nome": "Urgente"
          },
          {
            "valor": "alta",
            "nome": "Alta"
          },
          {
            "valor": "normal",
            "nome": "Normal"
          }
        ],
        "padrao": "urgente"
      },
      {
        "chave": "inicio_previsto_em",
        "nome": "Início previsto",
        "tipo": "datahora",
        "obrigatorio": true
      },
      {
        "chave": "prazo_em",
        "nome": "Prazo",
        "tipo": "datahora",
        "obrigatorio": true
      },
      {
        "chave": "id_pessoa_solicitante",
        "nome": "Solicitante",
        "tipo": "referencia",
        "tabela": "pessoas",
        "obrigatorio": true
      },
      {
        "chave": "situacao",
        "nome": "Situação",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "aberta",
            "nome": "Aberta"
          },
          {
            "valor": "em_atendimento",
            "nome": "Em atendimento"
          },
          {
            "valor": "concluida",
            "nome": "Concluída"
          },
          {
            "valor": "cancelada",
            "nome": "Cancelada"
          }
        ],
        "padrao": "aberta"
      }
    ],
    "colunas": [
      "titulo",
      "id_area_afetada",
      "prioridade",
      "prazo_em",
      "situacao"
    ],
    "menu": true,
    "descricao": "Gravidade da área e prioridade são independentes. Cadastro permanece rascunho de demonstração até incluir itens.",
    "relacoes": [
      {
        "tabela": "demanda_itens",
        "campo": "id_demanda",
        "nome": "Itens solicitados"
      },
      {
        "tabela": "recomendacoes",
        "campo": "id_demanda",
        "nome": "Análises e decisões"
      }
    ]
  },
  {
    "chave": "demanda_itens",
    "nome": "Itens de demanda",
    "singular": "item",
    "grupo": "Operação",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "id_demanda",
        "nome": "Demanda",
        "tipo": "referencia",
        "tabela": "demandas",
        "obrigatorio": true
      },
      {
        "chave": "id_atividade",
        "nome": "Atividade solicitada",
        "tipo": "referencia",
        "tabela": "atividades",
        "obrigatorio": false
      },
      {
        "chave": "id_tipo_recurso",
        "nome": "Tipo de recurso solicitado",
        "tipo": "referencia",
        "tabela": "tipos_recurso",
        "obrigatorio": false
      },
      {
        "chave": "quantidade_solicitada",
        "nome": "Quantidade",
        "tipo": "numero",
        "obrigatorio": true,
        "minimo": 0.01
      },
      {
        "chave": "id_unidade_medida",
        "nome": "Unidade",
        "tipo": "referencia",
        "tabela": "unidades_medida",
        "obrigatorio": true
      },
      {
        "chave": "observacoes",
        "nome": "Observações",
        "tipo": "area",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "id_atividade",
      "id_tipo_recurso",
      "quantidade_solicitada",
      "id_unidade_medida"
    ],
    "menu": false,
    "descricao": "Escolha uma atividade OU um tipo de recurso. A unidade deve ser compatível."
  },
  {
    "chave": "conexao_ia",
    "nome": "Conexões de IA",
    "singular": "conexão",
    "grupo": "Administração",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "nome",
        "nome": "Nome",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "provedor",
        "nome": "Adaptador demonstrativo",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "url_base",
        "nome": "URL ilustrativa",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "tipo_autenticacao",
        "nome": "Autenticação",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "token",
            "nome": "Token"
          },
          {
            "valor": "nenhuma",
            "nome": "Nenhuma"
          }
        ],
        "padrao": "token"
      },
      {
        "chave": "token_configurado",
        "nome": "Credencial fictícia configurada",
        "tipo": "booleano",
        "padrao": false
      },
      {
        "chave": "identificador_chave",
        "nome": "Identificador da chave fictícia",
        "tipo": "texto",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "nome",
      "provedor",
      "url_base"
    ],
    "menu": true,
    "descricao": "Tela de configuração simulada. Não informe segredos reais: não há chamada a provedor ou criptografia neste protótipo.",
    "relacoes": [
      {
        "tabela": "modelo_ia",
        "campo": "id_conexao",
        "nome": "Modelos da conexão"
      }
    ]
  },
  {
    "chave": "modelo_ia",
    "nome": "Modelos de IA",
    "singular": "modelo",
    "grupo": "Administração",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "id_conexao",
        "nome": "Conexão",
        "tipo": "referencia",
        "tabela": "conexao_ia",
        "obrigatorio": true
      },
      {
        "chave": "identificador_modelo",
        "nome": "Identificador do modelo",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "revisao",
        "nome": "Revisão",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "finalidade",
        "nome": "Finalidade",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "embedding",
            "nome": "Embedding"
          },
          {
            "valor": "inferencia_texto",
            "nome": "Inferência de texto"
          }
        ],
        "padrao": "embedding"
      },
      {
        "chave": "dimensao",
        "nome": "Dimensão (somente embedding)",
        "tipo": "numero",
        "obrigatorio": false,
        "minimo": 1
      },
      {
        "chave": "ativo",
        "nome": "Selecionado para a finalidade",
        "tipo": "booleano",
        "padrao": false
      }
    ],
    "colunas": [
      "identificador_modelo",
      "finalidade",
      "dimensao",
      "ativo"
    ],
    "menu": true,
    "descricao": "Troca ilustrativa. Um selecionado por finalidade; preparar índices antes de selecionar outro embedding.",
    "relacoes": [
      {
        "tabela": "atividade_indice_semantico",
        "campo": "id_modelo",
        "nome": "Índices de atividades"
      }
    ]
  },
  {
    "chave": "atividade_indice_semantico",
    "nome": "Índices de atividades",
    "singular": "índice",
    "grupo": "Administração",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "id_atividade",
        "nome": "Origem",
        "tipo": "referencia",
        "tabela": "atividades",
        "obrigatorio": true
      },
      {
        "chave": "id_modelo",
        "nome": "Modelo",
        "tipo": "referencia",
        "tabela": "modelo_ia",
        "obrigatorio": true
      },
      {
        "chave": "situacao_indexacao",
        "nome": "Situação",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "hash_origem",
        "nome": "Hash capturado",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "indexado_em",
        "nome": "Indexado em",
        "tipo": "texto",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "id_atividade",
      "id_modelo",
      "situacao_indexacao"
    ],
    "menu": false,
    "somenteLeitura": true,
    "descricao": "Representação demonstrativa; nenhum vetor real é gerado. Descrições permanecem na origem."
  },
  {
    "chave": "profissao_indice_semantico",
    "nome": "Índices de profissões",
    "singular": "índice",
    "grupo": "Administração",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_profissao",
        "nome": "Origem",
        "tipo": "referencia",
        "tabela": "profissoes",
        "obrigatorio": true
      },
      {
        "chave": "id_modelo",
        "nome": "Modelo",
        "tipo": "referencia",
        "tabela": "modelo_ia",
        "obrigatorio": true
      },
      {
        "chave": "situacao_indexacao",
        "nome": "Situação",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "hash_origem",
        "nome": "Hash capturado",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "indexado_em",
        "nome": "Indexado em",
        "tipo": "texto",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "id_profissao",
      "id_modelo",
      "situacao_indexacao"
    ],
    "menu": false,
    "somenteLeitura": true,
    "descricao": "Representação demonstrativa; nenhum vetor real é gerado. Descrições permanecem na origem."
  },
  {
    "chave": "curso_indice_semantico",
    "nome": "Índices de cursos",
    "singular": "índice",
    "grupo": "Administração",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_curso",
        "nome": "Origem",
        "tipo": "referencia",
        "tabela": "cursos",
        "obrigatorio": true
      },
      {
        "chave": "id_modelo",
        "nome": "Modelo",
        "tipo": "referencia",
        "tabela": "modelo_ia",
        "obrigatorio": true
      },
      {
        "chave": "situacao_indexacao",
        "nome": "Situação",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "hash_origem",
        "nome": "Hash capturado",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "indexado_em",
        "nome": "Indexado em",
        "tipo": "texto",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "id_curso",
      "id_modelo",
      "situacao_indexacao"
    ],
    "menu": false,
    "somenteLeitura": true,
    "descricao": "Representação demonstrativa; nenhum vetor real é gerado. Descrições permanecem na origem."
  },
  {
    "chave": "tipo_recurso_indice_semantico",
    "nome": "Índices de tipos de recurso",
    "singular": "índice",
    "grupo": "Administração",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_tipo_recurso",
        "nome": "Origem",
        "tipo": "referencia",
        "tabela": "tipos_recurso",
        "obrigatorio": true
      },
      {
        "chave": "id_modelo",
        "nome": "Modelo",
        "tipo": "referencia",
        "tabela": "modelo_ia",
        "obrigatorio": true
      },
      {
        "chave": "situacao_indexacao",
        "nome": "Situação",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "hash_origem",
        "nome": "Hash capturado",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "indexado_em",
        "nome": "Indexado em",
        "tipo": "texto",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "id_tipo_recurso",
      "id_modelo",
      "situacao_indexacao"
    ],
    "menu": false,
    "somenteLeitura": true,
    "descricao": "Representação demonstrativa; nenhum vetor real é gerado. Descrições permanecem na origem."
  },
  {
    "chave": "recomendacoes",
    "nome": "Recomendações",
    "singular": "recomendação",
    "grupo": "Operação",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "id_demanda",
        "nome": "Demanda",
        "tipo": "referencia",
        "tabela": "demandas",
        "obrigatorio": true
      },
      {
        "chave": "id_modelo_embedding",
        "nome": "Embedding",
        "tipo": "referencia",
        "tabela": "modelo_ia",
        "obrigatorio": true
      },
      {
        "chave": "id_modelo_inferencia",
        "nome": "Inferência",
        "tipo": "referencia",
        "tabela": "modelo_ia",
        "obrigatorio": true
      },
      {
        "chave": "situacao",
        "nome": "Situação",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "justificativa",
        "nome": "Justificativa",
        "tipo": "texto",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "id_demanda",
      "situacao",
      "gerada_em"
    ],
    "menu": true,
    "somenteLeitura": true,
    "relacoes": [
      {
        "tabela": "recomendacao_itens",
        "campo": "id_recomendacao",
        "nome": "Itens sugeridos"
      }
    ]
  },
  {
    "chave": "recomendacao_itens",
    "nome": "Itens da recomendação",
    "singular": "sugestão",
    "grupo": "Operação",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "id_recomendacao",
        "nome": "Recomendação",
        "tipo": "referencia",
        "tabela": "recomendacoes",
        "obrigatorio": true
      },
      {
        "chave": "id_demanda_item",
        "nome": "Pedido",
        "tipo": "referencia",
        "tabela": "demanda_itens",
        "obrigatorio": true
      },
      {
        "chave": "quantidade_sugerida",
        "nome": "Quantidade potencial",
        "tipo": "numero",
        "obrigatorio": true,
        "minimo": 0
      },
      {
        "chave": "justificativa",
        "nome": "Justificativa",
        "tipo": "texto",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "id_demanda_item",
      "quantidade_sugerida",
      "justificativa"
    ],
    "menu": false,
    "somenteLeitura": true
  },
  {
    "chave": "recomendacao_pessoas",
    "nome": "Pessoas sugeridas",
    "singular": "candidato",
    "grupo": "Operação",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "id_recomendacao_item",
        "nome": "Item sugerido",
        "tipo": "referencia",
        "tabela": "recomendacao_itens",
        "obrigatorio": true
      },
      {
        "chave": "id_pessoa",
        "nome": "Candidato",
        "tipo": "referencia",
        "tabela": "pessoas",
        "obrigatorio": true
      },
      {
        "chave": "papel_sugerido",
        "nome": "Papel sugerido",
        "tipo": "texto",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "id_recomendacao_item",
      "id_pessoa"
    ],
    "menu": false,
    "somenteLeitura": true
  },
  {
    "chave": "recomendacao_instituicoes",
    "nome": "Instituições sugeridas",
    "singular": "candidato",
    "grupo": "Operação",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "id_recomendacao_item",
        "nome": "Item sugerido",
        "tipo": "referencia",
        "tabela": "recomendacao_itens",
        "obrigatorio": true
      },
      {
        "chave": "id_instituicao",
        "nome": "Candidato",
        "tipo": "referencia",
        "tabela": "instituicoes",
        "obrigatorio": true
      },
      {
        "chave": "id_oferta_atividade",
        "nome": "Oferta",
        "tipo": "referencia",
        "tabela": "ofertas_atividade",
        "obrigatorio": true
      }
    ],
    "colunas": [
      "id_recomendacao_item",
      "id_instituicao"
    ],
    "menu": false,
    "somenteLeitura": true
  },
  {
    "chave": "recomendacao_recursos",
    "nome": "Recursos sugeridos",
    "singular": "candidato",
    "grupo": "Operação",
    "etapa": "inicial",
    "campos": [
      {
        "chave": "id_recomendacao_item",
        "nome": "Item sugerido",
        "tipo": "referencia",
        "tabela": "recomendacao_itens",
        "obrigatorio": true
      },
      {
        "chave": "id_recurso",
        "nome": "Candidato",
        "tipo": "referencia",
        "tabela": "recursos",
        "obrigatorio": true
      },
      {
        "chave": "quantidade_sugerida",
        "nome": "Quantidade potencial",
        "tipo": "numero",
        "obrigatorio": true,
        "minimo": 0
      }
    ],
    "colunas": [
      "id_recomendacao_item",
      "id_recurso"
    ],
    "menu": false,
    "somenteLeitura": true
  },
  {
    "chave": "atividade_requisito_profissao",
    "nome": "Profissões exigidas por atividade",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_atividade",
        "nome": "Atividade ou item",
        "tipo": "referencia",
        "tabela": "atividades",
        "obrigatorio": true
      },
      {
        "chave": "id_profissao",
        "nome": "Qualificação",
        "tipo": "referencia",
        "tabela": "profissoes",
        "obrigatorio": true
      },
      {
        "chave": "quantidade_minima_pessoas",
        "nome": "Pessoas exigidas",
        "tipo": "numero",
        "obrigatorio": true,
        "minimo": 1
      }
    ],
    "colunas": [
      "id_atividade",
      "id_profissao",
      "quantidade_minima_pessoas"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "atividade_requisito_curso",
    "nome": "Cursos exigidos por atividade",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_atividade",
        "nome": "Atividade ou item",
        "tipo": "referencia",
        "tabela": "atividades",
        "obrigatorio": true
      },
      {
        "chave": "id_curso",
        "nome": "Qualificação",
        "tipo": "referencia",
        "tabela": "cursos",
        "obrigatorio": true
      },
      {
        "chave": "quantidade_minima_pessoas",
        "nome": "Pessoas exigidas",
        "tipo": "numero",
        "obrigatorio": true,
        "minimo": 1
      }
    ],
    "colunas": [
      "id_atividade",
      "id_curso",
      "quantidade_minima_pessoas"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "demanda_item_requisito_profissao",
    "nome": "Profissões exigidas no pedido",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_demanda_item",
        "nome": "Atividade ou item",
        "tipo": "referencia",
        "tabela": "demanda_itens",
        "obrigatorio": true
      },
      {
        "chave": "id_profissao",
        "nome": "Qualificação",
        "tipo": "referencia",
        "tabela": "profissoes",
        "obrigatorio": true
      },
      {
        "chave": "quantidade_minima_pessoas",
        "nome": "Pessoas exigidas",
        "tipo": "numero",
        "obrigatorio": true,
        "minimo": 1
      }
    ],
    "colunas": [
      "id_demanda_item",
      "id_profissao",
      "quantidade_minima_pessoas"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "demanda_item_requisito_curso",
    "nome": "Cursos exigidos no pedido",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_demanda_item",
        "nome": "Atividade ou item",
        "tipo": "referencia",
        "tabela": "demanda_itens",
        "obrigatorio": true
      },
      {
        "chave": "id_curso",
        "nome": "Qualificação",
        "tipo": "referencia",
        "tabela": "cursos",
        "obrigatorio": true
      },
      {
        "chave": "quantidade_minima_pessoas",
        "nome": "Pessoas exigidas",
        "tipo": "numero",
        "obrigatorio": true,
        "minimo": 1
      }
    ],
    "colunas": [
      "id_demanda_item",
      "id_curso",
      "quantidade_minima_pessoas"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "caracteristicas_recurso",
    "nome": "Características técnicas",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "codigo",
        "nome": "Código",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "nome",
        "nome": "Nome",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "tipo_valor",
        "nome": "Tipo",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "numero",
            "nome": "Número"
          },
          {
            "valor": "texto",
            "nome": "Texto"
          },
          {
            "valor": "booleano",
            "nome": "Sim/não"
          }
        ],
        "padrao": "numero"
      },
      {
        "chave": "id_unidade_medida",
        "nome": "Unidade",
        "tipo": "referencia",
        "tabela": "unidades_medida",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "codigo",
      "nome",
      "tipo_valor"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "tipo_recurso_caracteristica",
    "nome": "Características por tipo",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_tipo_recurso",
        "nome": "Tipo",
        "tipo": "referencia",
        "tabela": "tipos_recurso",
        "obrigatorio": true
      },
      {
        "chave": "id_caracteristica",
        "nome": "Característica",
        "tipo": "referencia",
        "tabela": "caracteristicas_recurso",
        "obrigatorio": true
      },
      {
        "chave": "obrigatoria",
        "nome": "Obrigatória",
        "tipo": "booleano",
        "padrao": false
      }
    ],
    "colunas": [
      "id_tipo_recurso",
      "id_caracteristica",
      "obrigatoria"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "recurso_caracteristica",
    "nome": "Valores técnicos dos recursos",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_recurso",
        "nome": "Recurso",
        "tipo": "referencia",
        "tabela": "recursos",
        "obrigatorio": true
      },
      {
        "chave": "id_caracteristica",
        "nome": "Característica",
        "tipo": "referencia",
        "tabela": "caracteristicas_recurso",
        "obrigatorio": true
      },
      {
        "chave": "valor_numerico",
        "nome": "Valor numérico",
        "tipo": "numero",
        "obrigatorio": false,
        "minimo": 0
      },
      {
        "chave": "valor_texto",
        "nome": "Valor textual",
        "tipo": "texto",
        "obrigatorio": false
      },
      {
        "chave": "valor_booleano",
        "nome": "Valor sim/não",
        "tipo": "booleano",
        "padrao": false
      }
    ],
    "colunas": [
      "id_recurso",
      "id_caracteristica",
      "valor_numerico"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "demanda_item_requisito_recurso",
    "nome": "Características exigidas no pedido",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_demanda_item",
        "nome": "Item",
        "tipo": "referencia",
        "tabela": "demanda_itens",
        "obrigatorio": true
      },
      {
        "chave": "id_caracteristica",
        "nome": "Característica",
        "tipo": "referencia",
        "tabela": "caracteristicas_recurso",
        "obrigatorio": true
      },
      {
        "chave": "operador",
        "nome": "Comparação",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "maior_igual",
            "nome": "Maior ou igual"
          },
          {
            "valor": "igual",
            "nome": "Igual"
          },
          {
            "valor": "menor_igual",
            "nome": "Menor ou igual"
          }
        ],
        "padrao": "maior_igual"
      },
      {
        "chave": "valor_numerico",
        "nome": "Valor numérico",
        "tipo": "numero",
        "obrigatorio": false,
        "minimo": 0
      },
      {
        "chave": "valor_texto",
        "nome": "Valor textual",
        "tipo": "texto",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "id_demanda_item",
      "id_caracteristica",
      "operador"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "oferta_atividade_pessoa",
    "nome": "Composição das ofertas",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_oferta_atividade",
        "nome": "Oferta",
        "tipo": "referencia",
        "tabela": "ofertas_atividade",
        "obrigatorio": true
      },
      {
        "chave": "id_pessoa",
        "nome": "Pessoa",
        "tipo": "referencia",
        "tabela": "pessoas",
        "obrigatorio": true
      },
      {
        "chave": "papel",
        "nome": "Papel",
        "tipo": "texto",
        "obrigatorio": true
      }
    ],
    "colunas": [
      "id_oferta_atividade",
      "id_pessoa",
      "papel"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "disponibilidades_pessoa",
    "nome": "Disponibilidade de pessoas",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_pessoa",
        "nome": "Pessoa ou oferta",
        "tipo": "referencia",
        "tabela": "pessoas",
        "obrigatorio": true
      },
      {
        "chave": "inicio_em",
        "nome": "Início",
        "tipo": "datahora",
        "obrigatorio": true
      },
      {
        "chave": "fim_em",
        "nome": "Fim",
        "tipo": "datahora",
        "obrigatorio": true
      },
      {
        "chave": "situacao",
        "nome": "Situação",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "declarada",
            "nome": "Declarada"
          },
          {
            "valor": "indisponivel",
            "nome": "Indisponível"
          }
        ],
        "padrao": "declarada"
      }
    ],
    "colunas": [
      "id_pessoa",
      "inicio_em",
      "fim_em"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "disponibilidades_oferta",
    "nome": "Disponibilidade de ofertas",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_oferta_atividade",
        "nome": "Pessoa ou oferta",
        "tipo": "referencia",
        "tabela": "ofertas_atividade",
        "obrigatorio": true
      },
      {
        "chave": "inicio_em",
        "nome": "Início",
        "tipo": "datahora",
        "obrigatorio": true
      },
      {
        "chave": "fim_em",
        "nome": "Fim",
        "tipo": "datahora",
        "obrigatorio": true
      },
      {
        "chave": "situacao",
        "nome": "Situação",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "declarada",
            "nome": "Declarada"
          },
          {
            "valor": "indisponivel",
            "nome": "Indisponível"
          }
        ],
        "padrao": "declarada"
      },
      {
        "chave": "capacidade_declarada",
        "nome": "Capacidade",
        "tipo": "numero",
        "obrigatorio": true,
        "minimo": 0.01
      }
    ],
    "colunas": [
      "id_oferta_atividade",
      "inicio_em",
      "fim_em"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "missoes",
    "nome": "Missões",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "titulo",
        "nome": "Título",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "id_recomendacao",
        "nome": "Recomendação",
        "tipo": "referencia",
        "tabela": "recomendacoes",
        "obrigatorio": false
      },
      {
        "chave": "id_instituicao_responsavel",
        "nome": "Responsável",
        "tipo": "referencia",
        "tabela": "instituicoes",
        "obrigatorio": true
      },
      {
        "chave": "inicio_previsto_em",
        "nome": "Início",
        "tipo": "datahora",
        "obrigatorio": true
      },
      {
        "chave": "fim_previsto_em",
        "nome": "Fim",
        "tipo": "datahora",
        "obrigatorio": true
      },
      {
        "chave": "situacao",
        "nome": "Situação demonstrativa",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "planejada",
            "nome": "Planejada"
          },
          {
            "valor": "em_execucao",
            "nome": "Em execução"
          },
          {
            "valor": "encerrada",
            "nome": "Encerrada"
          },
          {
            "valor": "cancelada",
            "nome": "Cancelada"
          }
        ],
        "padrao": "planejada"
      }
    ],
    "colunas": [
      "titulo",
      "situacao",
      "inicio_previsto_em"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão.",
    "relacoes": [
      {
        "tabela": "missao_itens",
        "campo": "id_missao",
        "nome": "Itens"
      },
      {
        "tabela": "alocacoes_pessoa",
        "campo": "id_missao",
        "nome": "Pessoas"
      },
      {
        "tabela": "reservas_recurso",
        "campo": "id_missao",
        "nome": "Recursos"
      }
    ]
  },
  {
    "chave": "missao_itens",
    "nome": "Itens de missão",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_missao",
        "nome": "Missão",
        "tipo": "referencia",
        "tabela": "missoes",
        "obrigatorio": true
      },
      {
        "chave": "id_demanda_item",
        "nome": "Item",
        "tipo": "referencia",
        "tabela": "demanda_itens",
        "obrigatorio": true
      },
      {
        "chave": "quantidade_planejada",
        "nome": "Quantidade",
        "tipo": "numero",
        "obrigatorio": true,
        "minimo": 0.01
      }
    ],
    "colunas": [
      "id_missao",
      "id_demanda_item",
      "quantidade_planejada"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "alocacoes_pessoa",
    "nome": "Alocações de pessoas",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_missao",
        "nome": "Missão",
        "tipo": "referencia",
        "tabela": "missoes",
        "obrigatorio": true
      },
      {
        "chave": "id_pessoa",
        "nome": "Pessoa",
        "tipo": "referencia",
        "tabela": "pessoas",
        "obrigatorio": true
      },
      {
        "chave": "papel",
        "nome": "Papel",
        "tipo": "texto",
        "obrigatorio": true
      },
      {
        "chave": "situacao",
        "nome": "Situação",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "proposta",
            "nome": "Proposta"
          },
          {
            "valor": "aceita",
            "nome": "Aceita"
          },
          {
            "valor": "cancelada",
            "nome": "Cancelada"
          }
        ],
        "padrao": "proposta"
      }
    ],
    "colunas": [
      "id_missao",
      "id_pessoa",
      "situacao"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "reservas_recurso",
    "nome": "Reservas de recursos",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_missao",
        "nome": "Missão",
        "tipo": "referencia",
        "tabela": "missoes",
        "obrigatorio": true
      },
      {
        "chave": "id_recurso",
        "nome": "Recurso",
        "tipo": "referencia",
        "tabela": "recursos",
        "obrigatorio": true
      },
      {
        "chave": "quantidade_reservada",
        "nome": "Quantidade",
        "tipo": "numero",
        "obrigatorio": true,
        "minimo": 0.01
      },
      {
        "chave": "inicio_em",
        "nome": "Início",
        "tipo": "datahora",
        "obrigatorio": true
      },
      {
        "chave": "fim_em",
        "nome": "Fim",
        "tipo": "datahora",
        "obrigatorio": true
      },
      {
        "chave": "situacao",
        "nome": "Situação",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "proposta",
            "nome": "Proposta"
          },
          {
            "valor": "confirmada",
            "nome": "Confirmada"
          },
          {
            "valor": "cancelada",
            "nome": "Cancelada"
          }
        ],
        "padrao": "proposta"
      }
    ],
    "colunas": [
      "id_missao",
      "id_recurso",
      "quantidade_reservada"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "atendimentos",
    "nome": "Atendimentos",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_missao",
        "nome": "Missão",
        "tipo": "referencia",
        "tabela": "missoes",
        "obrigatorio": true
      },
      {
        "chave": "realizado_em",
        "nome": "Data",
        "tipo": "datahora",
        "obrigatorio": true
      },
      {
        "chave": "observacoes",
        "nome": "Observações",
        "tipo": "area",
        "obrigatorio": false
      }
    ],
    "colunas": [
      "id_missao",
      "realizado_em"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão.",
    "relacoes": [
      {
        "tabela": "atendimento_itens",
        "campo": "id_atendimento",
        "nome": "Itens registrados"
      }
    ]
  },
  {
    "chave": "atendimento_itens",
    "nome": "Itens atendidos",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_atendimento",
        "nome": "Atendimento",
        "tipo": "referencia",
        "tabela": "atendimentos",
        "obrigatorio": true
      },
      {
        "chave": "id_demanda_item",
        "nome": "Item",
        "tipo": "referencia",
        "tabela": "demanda_itens",
        "obrigatorio": true
      },
      {
        "chave": "quantidade_confirmada",
        "nome": "Quantidade",
        "tipo": "numero",
        "obrigatorio": true,
        "minimo": 0.01
      }
    ],
    "colunas": [
      "id_atendimento",
      "id_demanda_item",
      "quantidade_confirmada"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  },
  {
    "chave": "movimentacoes_recurso",
    "nome": "Movimentações de estoque",
    "singular": "registro",
    "grupo": "Evolução futura",
    "etapa": "futuro",
    "campos": [
      {
        "chave": "id_recurso",
        "nome": "Recurso",
        "tipo": "referencia",
        "tabela": "recursos",
        "obrigatorio": true
      },
      {
        "chave": "tipo",
        "nome": "Tipo",
        "tipo": "opcao",
        "obrigatorio": true,
        "opcoes": [
          {
            "valor": "entrada",
            "nome": "Entrada"
          },
          {
            "valor": "saida",
            "nome": "Saída"
          },
          {
            "valor": "estorno",
            "nome": "Estorno"
          }
        ],
        "padrao": "entrada"
      },
      {
        "chave": "quantidade",
        "nome": "Quantidade",
        "tipo": "numero",
        "obrigatorio": true,
        "minimo": 0.01
      },
      {
        "chave": "realizada_em",
        "nome": "Data",
        "tipo": "datahora",
        "obrigatorio": true
      },
      {
        "chave": "justificativa",
        "nome": "Justificativa",
        "tipo": "texto",
        "obrigatorio": true
      }
    ],
    "colunas": [
      "id_recurso",
      "tipo",
      "quantidade",
      "realizada_em"
    ],
    "menu": true,
    "descricao": "Rascunho de navegação. Contratos e regras operacionais desta etapa continuam em discussão."
  }
];

export function telaPorChave(chave: string): Tela | undefined { return TELAS.find((t) => t.chave === chave); }

