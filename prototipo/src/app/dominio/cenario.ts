import { CamposRegistro, EstadoPrototipo, Registro } from './contratos';
import { TELAS } from './telas';

interface Semente { tabela: string; id: string; campos: CamposRegistro; }
const SEMENTES: readonly Semente[] = [
  {
    "tabela": "instituicoes",
    "id": "inst-dc",
    "campos": {
      "nome": "Defesa Civil de Vale Azul — fictícia",
      "municipio_codigo_ibge": "0000001",
      "uf": "SP",
      "situacao_cadastral": "validada",
      "email_contato": "contato@exemplo.invalid",
      "telefone_contato": "",
      "latitude": "",
      "longitude": "",
      "tipo": "orgao_publico",
      "descricao": "Coordenação da demonstração"
    }
  },
  {
    "tabela": "instituicoes",
    "id": "inst-cozinha",
    "campos": {
      "nome": "Cozinha Solidária — fictícia",
      "municipio_codigo_ibge": "0000001",
      "uf": "SP",
      "situacao_cadastral": "validada",
      "email_contato": "contato@exemplo.invalid",
      "telefone_contato": "",
      "latitude": "",
      "longitude": "",
      "tipo": "associacao",
      "descricao": "Oferta de alimentação"
    }
  },
  {
    "tabela": "instituicoes",
    "id": "inst-logistica",
    "campos": {
      "nome": "Associação de Logística — fictícia",
      "municipio_codigo_ibge": "0000001",
      "uf": "SP",
      "situacao_cadastral": "validada",
      "email_contato": "contato@exemplo.invalid",
      "telefone_contato": "",
      "latitude": "",
      "longitude": "",
      "tipo": "associacao",
      "descricao": "Transporte de suprimentos"
    }
  },
  {
    "tabela": "pessoas",
    "id": "p-joao",
    "campos": {
      "nome": "João — fictício",
      "municipio_codigo_ibge": "0000001",
      "uf": "SP",
      "situacao_cadastral": "validada",
      "email_contato": "contato@exemplo.invalid",
      "telefone_contato": "",
      "latitude": "",
      "longitude": ""
    }
  },
  {
    "tabela": "pessoas",
    "id": "p-carlos",
    "campos": {
      "nome": "Carlos — fictício",
      "municipio_codigo_ibge": "0000001",
      "uf": "SP",
      "situacao_cadastral": "validada",
      "email_contato": "contato@exemplo.invalid",
      "telefone_contato": "",
      "latitude": "",
      "longitude": ""
    }
  },
  {
    "tabela": "pessoas",
    "id": "p-marta",
    "campos": {
      "nome": "Marta — fictícia",
      "municipio_codigo_ibge": "0000001",
      "uf": "SP",
      "situacao_cadastral": "validada",
      "email_contato": "contato@exemplo.invalid",
      "telefone_contato": "",
      "latitude": "",
      "longitude": ""
    }
  },
  {
    "tabela": "pessoas",
    "id": "p-paula",
    "campos": {
      "nome": "Paula — fictícia",
      "municipio_codigo_ibge": "0000001",
      "uf": "SP",
      "situacao_cadastral": "validada",
      "email_contato": "contato@exemplo.invalid",
      "telefone_contato": "",
      "latitude": "",
      "longitude": ""
    }
  },
  {
    "tabela": "profissoes",
    "id": "prof-condutor",
    "campos": {
      "nome": "Condutor — catálogo ilustrativo",
      "codigo_cbo": "123456",
      "descricao": "Descrição fictícia; não comprova habilitação"
    }
  },
  {
    "tabela": "profissoes",
    "id": "prof-cozinha",
    "campos": {
      "nome": "Cozinheiro — catálogo ilustrativo",
      "codigo_cbo": "",
      "descricao": "Preparação de alimentação"
    }
  },
  {
    "tabela": "cursos",
    "id": "curso-transporte",
    "campos": {
      "nome": "Transporte seguro — treinamento ilustrativo",
      "tipo": "treinamento",
      "descricao": "Exemplo de formação, sem equivalência profissional afirmada"
    }
  },
  {
    "tabela": "cursos",
    "id": "curso-cozinha",
    "campos": {
      "nome": "Preparo de refeições — curso ilustrativo",
      "tipo": "capacitacao",
      "descricao": "Curso fictício"
    }
  },
  {
    "tabela": "pessoa_instituicao",
    "id": "vi-p-joao",
    "campos": {
      "pessoa_id": "p-joao",
      "instituicao_id": "inst-logistica",
      "tipo_vinculo": "voluntario",
      "inicio_em": "2026-01-01",
      "fim_em": "",
      "situacao_validacao": "validada"
    }
  },
  {
    "tabela": "pessoa_instituicao",
    "id": "vi-p-carlos",
    "campos": {
      "pessoa_id": "p-carlos",
      "instituicao_id": "inst-logistica",
      "tipo_vinculo": "voluntario",
      "inicio_em": "2026-01-01",
      "fim_em": "",
      "situacao_validacao": "validada"
    }
  },
  {
    "tabela": "pessoa_instituicao",
    "id": "vi-p-marta",
    "campos": {
      "pessoa_id": "p-marta",
      "instituicao_id": "inst-dc",
      "tipo_vinculo": "voluntario",
      "inicio_em": "2026-01-01",
      "fim_em": "",
      "situacao_validacao": "validada"
    }
  },
  {
    "tabela": "pessoa_instituicao",
    "id": "vi-p-paula",
    "campos": {
      "pessoa_id": "p-paula",
      "instituicao_id": "inst-cozinha",
      "tipo_vinculo": "voluntario",
      "inicio_em": "2026-01-01",
      "fim_em": "",
      "situacao_validacao": "validada"
    }
  },
  {
    "tabela": "pessoa_profissao",
    "id": "vp-p-joao",
    "campos": {
      "pessoa_id": "p-joao",
      "profissao_id": "prof-condutor",
      "registro_profissional": "DEMO-p-joao",
      "orgao_registro": "Órgão fictício",
      "uf_registro": "SP",
      "validade_em": "2027-12-31",
      "situacao_validacao": "validada"
    }
  },
  {
    "tabela": "pessoa_profissao",
    "id": "vp-p-carlos",
    "campos": {
      "pessoa_id": "p-carlos",
      "profissao_id": "prof-condutor",
      "registro_profissional": "DEMO-p-carlos",
      "orgao_registro": "Órgão fictício",
      "uf_registro": "SP",
      "validade_em": "2027-12-31",
      "situacao_validacao": "validada"
    }
  },
  {
    "tabela": "pessoa_profissao",
    "id": "vp-p-marta",
    "campos": {
      "pessoa_id": "p-marta",
      "profissao_id": "prof-condutor",
      "registro_profissional": "DEMO-p-marta",
      "orgao_registro": "Órgão fictício",
      "uf_registro": "SP",
      "validade_em": "2027-12-31",
      "situacao_validacao": "pendente"
    }
  },
  {
    "tabela": "pessoa_profissao",
    "id": "vp-paula",
    "campos": {
      "pessoa_id": "p-paula",
      "profissao_id": "prof-cozinha",
      "situacao_validacao": "validada"
    }
  },
  {
    "tabela": "pessoa_curso",
    "id": "vc-p-joao",
    "campos": {
      "pessoa_id": "p-joao",
      "curso_id": "curso-transporte",
      "instituicao_emissora": "Centro de formação fictício",
      "conclusao_em": "2025-01-01",
      "validade_em": "2027-12-31",
      "carga_horaria": "40",
      "comprovante_referencia": "documento:demo-p-joao",
      "situacao_validacao": "validada"
    }
  },
  {
    "tabela": "pessoa_curso",
    "id": "vc-p-carlos",
    "campos": {
      "pessoa_id": "p-carlos",
      "curso_id": "curso-transporte",
      "instituicao_emissora": "Centro de formação fictício",
      "conclusao_em": "2025-01-01",
      "validade_em": "2025-12-31",
      "carga_horaria": "40",
      "comprovante_referencia": "documento:demo-p-carlos",
      "situacao_validacao": "validada"
    }
  },
  {
    "tabela": "pessoa_curso",
    "id": "vc-p-marta",
    "campos": {
      "pessoa_id": "p-marta",
      "curso_id": "curso-transporte",
      "instituicao_emissora": "Centro de formação fictício",
      "conclusao_em": "2025-01-01",
      "validade_em": "2027-12-31",
      "carga_horaria": "40",
      "comprovante_referencia": "documento:demo-p-marta",
      "situacao_validacao": "pendente"
    }
  },
  {
    "tabela": "pessoa_curso",
    "id": "vc-p-paula",
    "campos": {
      "pessoa_id": "p-paula",
      "curso_id": "curso-cozinha",
      "instituicao_emissora": "Centro de formação fictício",
      "conclusao_em": "2025-01-01",
      "validade_em": "2027-12-31",
      "carga_horaria": "40",
      "comprovante_referencia": "documento:demo-p-paula",
      "situacao_validacao": "validada"
    }
  },
  {
    "tabela": "unidades_medida",
    "id": "u-viagem",
    "campos": {
      "codigo": "u-viagem",
      "nome": "Viagem",
      "simbolo": "viagem"
    }
  },
  {
    "tabela": "unidades_medida",
    "id": "u-litro",
    "campos": {
      "codigo": "u-litro",
      "nome": "Litro",
      "simbolo": "L"
    }
  },
  {
    "tabela": "unidades_medida",
    "id": "u-refeicao",
    "campos": {
      "codigo": "u-refeicao",
      "nome": "Refeição",
      "simbolo": "refeição"
    }
  },
  {
    "tabela": "unidades_medida",
    "id": "u-unidade",
    "campos": {
      "codigo": "u-unidade",
      "nome": "Unidade",
      "simbolo": "un"
    }
  },
  {
    "tabela": "categorias_atividade",
    "id": "cat-logistica",
    "campos": {
      "codigo": "cat-logistica",
      "nome": "Logística",
      "descricao": "Categoria ilustrativa"
    }
  },
  {
    "tabela": "categorias_atividade",
    "id": "cat-alimentacao",
    "campos": {
      "codigo": "cat-alimentacao",
      "nome": "Alimentação",
      "descricao": "Categoria ilustrativa"
    }
  },
  {
    "tabela": "atividades",
    "id": "a-transporte",
    "campos": {
      "codigo": "ACT-01",
      "nome": "Transporte de suprimentos",
      "descricao": "Levar alimentos e água para as áreas",
      "categoria_id": "cat-logistica",
      "id_unidade_capacidade": "u-viagem",
      "orientacoes": "Confirmar acesso e condições operacionais",
      "restricoes": "Habilitação e agenda exigem conferência"
    }
  },
  {
    "tabela": "atividades",
    "id": "a-refeicoes",
    "campos": {
      "codigo": "ACT-02",
      "nome": "Preparo de refeições",
      "descricao": "Preparar alimentação para famílias",
      "categoria_id": "cat-alimentacao",
      "id_unidade_capacidade": "u-refeicao",
      "orientacoes": "Confirmar período-base da capacidade"
    }
  },
  {
    "tabela": "atividade_termos",
    "id": "termo-1",
    "campos": {
      "atividade_id": "a-transporte",
      "termo": "logística de doações"
    }
  },
  {
    "tabela": "atividade_termos",
    "id": "termo-2",
    "campos": {
      "atividade_id": "a-refeicoes",
      "termo": "alimentação"
    }
  },
  {
    "tabela": "ofertas_atividade",
    "id": "of-transporte",
    "campos": {
      "atividade_id": "a-transporte",
      "instituicao_id": "inst-logistica",
      "pessoa_id": "",
      "capacidade_declarada": "1",
      "municipio_atendimento_codigo_ibge": "0000001",
      "situacao_validacao": "validada",
      "descricao_complementar": "Caminhão previsto; confirmar acesso e condutor"
    }
  },
  {
    "tabela": "ofertas_atividade",
    "id": "of-cozinha",
    "campos": {
      "atividade_id": "a-refeicoes",
      "instituicao_id": "inst-cozinha",
      "pessoa_id": "",
      "capacidade_declarada": "80",
      "municipio_atendimento_codigo_ibge": "0000001",
      "situacao_validacao": "validada",
      "descricao_complementar": "Período-base não definido neste protótipo"
    }
  },
  {
    "tabela": "ofertas_atividade",
    "id": "of-paula",
    "campos": {
      "atividade_id": "a-refeicoes",
      "pessoa_id": "p-paula",
      "instituicao_id": "",
      "capacidade_declarada": "40",
      "municipio_atendimento_codigo_ibge": "0000001",
      "situacao_validacao": "validada",
      "descricao_complementar": "Paula integra a cozinha; não somar capacidades"
    }
  },
  {
    "tabela": "tipos_recurso",
    "id": "tipo-caminhao",
    "campos": {
      "nome": "Caminhão",
      "descricao": "Tipo ilustrativo",
      "categoria": "veiculo",
      "id_unidade_medida": "u-unidade",
      "modo_controle": "individual"
    }
  },
  {
    "tabela": "tipos_recurso",
    "id": "tipo-agua",
    "campos": {
      "nome": "Água potável",
      "descricao": "Tipo ilustrativo",
      "categoria": "insumo",
      "id_unidade_medida": "u-litro",
      "modo_controle": "estoque"
    }
  },
  {
    "tabela": "tipos_recurso",
    "id": "tipo-gerador",
    "campos": {
      "nome": "Gerador",
      "descricao": "Tipo ilustrativo",
      "categoria": "equipamento",
      "id_unidade_medida": "u-unidade",
      "modo_controle": "individual"
    }
  },
  {
    "tabela": "recursos",
    "id": "r-caminhao",
    "campos": {
      "nome": "Caminhão da associação — fictício",
      "tipo_recurso_id": "tipo-caminhao",
      "instituicao_id": "inst-logistica",
      "pessoa_id": "",
      "quantidade_total": "1",
      "estado_operacional": "operacional",
      "municipio_codigo_ibge": "0000001",
      "descricao": "Um veículo compartilhado entre demandas"
    }
  },
  {
    "tabela": "recursos",
    "id": "r-agua",
    "campos": {
      "nome": "Lote de água — fictício",
      "tipo_recurso_id": "tipo-agua",
      "instituicao_id": "inst-dc",
      "pessoa_id": "",
      "quantidade_total": "300",
      "estado_operacional": "operacional",
      "municipio_codigo_ibge": "0000001",
      "descricao": "300 litros; recomendações não reservam esse lote"
    }
  },
  {
    "tabela": "recursos",
    "id": "r-gerador",
    "campos": {
      "nome": "Gerador 2 kVA — fictício",
      "tipo_recurso_id": "tipo-gerador",
      "instituicao_id": "inst-logistica",
      "pessoa_id": "",
      "quantidade_total": "1",
      "estado_operacional": "operacional",
      "municipio_codigo_ibge": "0000001",
      "descricao": "Potência declarada: 2 kVA. Compatibilidade não validada."
    }
  },
  {
    "tabela": "oferta_atividade_recurso",
    "id": "ofr-1",
    "campos": {
      "oferta_atividade_id": "of-transporte",
      "recurso_id": "r-caminhao",
      "quantidade_prevista": "1"
    }
  },
  {
    "tabela": "tipos_desastre",
    "id": "td-inundacao",
    "campos": {
      "codigo": "DEMO-INUNDACAO",
      "nome": "Inundação",
      "descricao": "Classificação ilustrativa"
    }
  },
  {
    "tabela": "tipos_desastre",
    "id": "td-deslizamento",
    "campos": {
      "codigo": "DEMO-DESLIZAMENTO",
      "nome": "Deslizamento",
      "descricao": "Classificação ilustrativa"
    }
  },
  {
    "tabela": "desastres",
    "id": "d-vale",
    "campos": {
      "titulo": "Inundação e deslizamento — Vale Azul",
      "descricao": "Ocorrência fictícia para navegar por todo o fluxo",
      "inicio_em": "2026-10-08T09:00",
      "encerramento_em": "",
      "situacao": "em_resposta",
      "id_instituicao_coordenadora": "inst-dc"
    }
  },
  {
    "tabela": "desastre_tipo",
    "id": "dt-1",
    "campos": {
      "id_desastre": "d-vale",
      "id_tipo_desastre": "td-inundacao",
      "principal": true
    }
  },
  {
    "tabela": "desastre_tipo",
    "id": "dt-2",
    "campos": {
      "id_desastre": "d-vale",
      "id_tipo_desastre": "td-deslizamento",
      "principal": false
    }
  },
  {
    "tabela": "areas_afetadas",
    "id": "area-varzea",
    "campos": {
      "nome": "Várzea",
      "id_desastre": "d-vale",
      "descricao": "Área fictícia",
      "municipio_codigo_ibge": "0000001",
      "gravidade": "alta",
      "situacao": "avaliada",
      "geometria": [
        {
          "x": 100,
          "y": 100
        },
        {
          "x": 380,
          "y": 90
        },
        {
          "x": 400,
          "y": 310
        },
        {
          "x": 120,
          "y": 330
        }
      ],
      "ultima_avaliacao_em": "2026-10-08T12:00:00Z"
    }
  },
  {
    "tabela": "areas_afetadas",
    "id": "area-encosta",
    "campos": {
      "nome": "Encosta",
      "id_desastre": "d-vale",
      "descricao": "Área fictícia",
      "municipio_codigo_ibge": "0000001",
      "gravidade": "alta",
      "situacao": "avaliada",
      "geometria": [
        {
          "x": 570,
          "y": 70
        },
        {
          "x": 860,
          "y": 110
        },
        {
          "x": 830,
          "y": 330
        },
        {
          "x": 580,
          "y": 290
        }
      ],
      "ultima_avaliacao_em": "2026-10-08T12:00:00Z"
    }
  },
  {
    "tabela": "areas_afetadas",
    "id": "area-centro",
    "campos": {
      "nome": "Centro",
      "id_desastre": "d-vale",
      "descricao": "Área fictícia",
      "municipio_codigo_ibge": "0000001",
      "gravidade": "moderada",
      "situacao": "avaliada",
      "geometria": [
        {
          "x": 330,
          "y": 390
        },
        {
          "x": 680,
          "y": 350
        },
        {
          "x": 720,
          "y": 520
        },
        {
          "x": 340,
          "y": 540
        }
      ],
      "ultima_avaliacao_em": "2026-10-08T12:00:00Z"
    }
  },
  {
    "tabela": "demandas",
    "id": "dem-varzea",
    "campos": {
      "titulo": "Atender famílias da Várzea",
      "id_area_afetada": "area-varzea",
      "descricao": "Pedido fictício para simulação",
      "prioridade": "urgente",
      "inicio_previsto_em": "2026-10-08T09:00",
      "prazo_em": "2026-10-08T14:00",
      "id_pessoa_solicitante": "p-marta",
      "situacao": "aberta"
    }
  },
  {
    "tabela": "demandas",
    "id": "dem-encosta",
    "campos": {
      "titulo": "Atender famílias da Encosta",
      "id_area_afetada": "area-encosta",
      "descricao": "Pedido fictício para simulação",
      "prioridade": "urgente",
      "inicio_previsto_em": "2026-10-08T09:00",
      "prazo_em": "2026-10-08T14:00",
      "id_pessoa_solicitante": "p-marta",
      "situacao": "aberta"
    }
  },
  {
    "tabela": "demandas",
    "id": "dem-centro",
    "campos": {
      "titulo": "Alimentação no Centro",
      "id_area_afetada": "area-centro",
      "descricao": "Pedido fictício para simulação",
      "prioridade": "urgente",
      "inicio_previsto_em": "2026-10-08T09:00",
      "prazo_em": "2026-10-08T17:00",
      "id_pessoa_solicitante": "p-marta",
      "situacao": "aberta"
    }
  },
  {
    "tabela": "demanda_itens",
    "id": "item-v-transp",
    "campos": {
      "id_demanda": "dem-varzea",
      "id_atividade": "a-transporte",
      "id_tipo_recurso": "",
      "quantidade_solicitada": "1",
      "id_unidade_medida": "u-viagem",
      "observacoes": "Confirmar condutor e acesso"
    }
  },
  {
    "tabela": "demanda_itens",
    "id": "item-v-agua",
    "campos": {
      "id_demanda": "dem-varzea",
      "id_atividade": "",
      "id_tipo_recurso": "tipo-agua",
      "quantidade_solicitada": "200",
      "id_unidade_medida": "u-litro",
      "observacoes": "Água potável"
    }
  },
  {
    "tabela": "demanda_itens",
    "id": "item-e-transp",
    "campos": {
      "id_demanda": "dem-encosta",
      "id_atividade": "a-transporte",
      "id_tipo_recurso": "",
      "quantidade_solicitada": "1",
      "id_unidade_medida": "u-viagem",
      "observacoes": "Mesmo período da Várzea"
    }
  },
  {
    "tabela": "demanda_itens",
    "id": "item-e-agua",
    "campos": {
      "id_demanda": "dem-encosta",
      "id_atividade": "",
      "id_tipo_recurso": "tipo-agua",
      "quantidade_solicitada": "200",
      "id_unidade_medida": "u-litro",
      "observacoes": "Pedidos totais superam o lote"
    }
  },
  {
    "tabela": "demanda_itens",
    "id": "item-e-gerador",
    "campos": {
      "id_demanda": "dem-encosta",
      "id_atividade": "",
      "id_tipo_recurso": "tipo-gerador",
      "quantidade_solicitada": "1",
      "id_unidade_medida": "u-unidade",
      "observacoes": "Necessidade declarada: mínimo 5 kVA; conferir tecnicamente"
    }
  },
  {
    "tabela": "demanda_itens",
    "id": "item-c-refeicao",
    "campos": {
      "id_demanda": "dem-centro",
      "id_atividade": "a-refeicoes",
      "id_tipo_recurso": "",
      "quantidade_solicitada": "100",
      "id_unidade_medida": "u-refeicao",
      "observacoes": "Não somar capacidade da cozinha à de Paula"
    }
  },
  {
    "tabela": "conexao_ia",
    "id": "con-demo",
    "campos": {
      "nome": "Provedor de demonstração",
      "provedor": "adaptador-deterministico",
      "url_base": "https://provedor.invalid",
      "tipo_autenticacao": "token",
      "token_configurado": true,
      "identificador_chave": "chave-ficticia"
    }
  },
  {
    "tabela": "modelo_ia",
    "id": "mod-emb",
    "campos": {
      "id_conexao": "con-demo",
      "identificador_modelo": "embedding-demo-v1",
      "revisao": "demo",
      "finalidade": "embedding",
      "dimensao": "3",
      "ativo": true
    }
  },
  {
    "tabela": "modelo_ia",
    "id": "mod-emb-alt",
    "campos": {
      "id_conexao": "con-demo",
      "identificador_modelo": "embedding-demo-v2",
      "revisao": "demo",
      "finalidade": "embedding",
      "dimensao": "4",
      "ativo": false
    }
  },
  {
    "tabela": "modelo_ia",
    "id": "mod-text",
    "campos": {
      "id_conexao": "con-demo",
      "identificador_modelo": "texto-demo-v1",
      "revisao": "demo",
      "finalidade": "inferencia_texto",
      "dimensao": "",
      "ativo": true
    }
  },
  {
    "tabela": "modelo_ia",
    "id": "mod-text-alt",
    "campos": {
      "id_conexao": "con-demo",
      "identificador_modelo": "texto-demo-v2",
      "revisao": "demo",
      "finalidade": "inferencia_texto",
      "dimensao": "",
      "ativo": false
    }
  },
  {
    "tabela": "caracteristicas_recurso",
    "id": "car-potencia",
    "campos": {
      "codigo": "potencia",
      "nome": "Potência declarada",
      "tipo_valor": "numero",
      "id_unidade_medida": ""
    }
  },
  {
    "tabela": "tipo_recurso_caracteristica",
    "id": "trc-1",
    "campos": {
      "id_tipo_recurso": "tipo-gerador",
      "id_caracteristica": "car-potencia",
      "obrigatoria": true
    }
  },
  {
    "tabela": "recurso_caracteristica",
    "id": "rc-1",
    "campos": {
      "id_recurso": "r-gerador",
      "id_caracteristica": "car-potencia",
      "valor_numerico": "2",
      "valor_texto": "",
      "valor_booleano": false
    }
  },
  {
    "tabela": "demanda_item_requisito_recurso",
    "id": "dir-1",
    "campos": {
      "id_demanda_item": "item-e-gerador",
      "id_caracteristica": "car-potencia",
      "operador": "maior_igual",
      "valor_numerico": "5"
    }
  },
  {
    "tabela": "atividade_requisito_profissao",
    "id": "arp-1",
    "campos": {
      "id_atividade": "a-transporte",
      "id_profissao": "prof-condutor",
      "quantidade_minima_pessoas": "1"
    }
  },
  {
    "tabela": "atividade_requisito_curso",
    "id": "arc-1",
    "campos": {
      "id_atividade": "a-transporte",
      "id_curso": "curso-transporte",
      "quantidade_minima_pessoas": "1"
    }
  },
  {
    "tabela": "oferta_atividade_pessoa",
    "id": "oap-1",
    "campos": {
      "id_oferta_atividade": "of-cozinha",
      "id_pessoa": "p-paula",
      "papel": "Preparo de alimentos"
    }
  },
  {
    "tabela": "disponibilidades_pessoa",
    "id": "disp-1",
    "campos": {
      "id_pessoa": "p-joao",
      "inicio_em": "2026-10-08T09:00",
      "fim_em": "2026-10-08T17:00",
      "situacao": "declarada"
    }
  },
  {
    "tabela": "disponibilidades_oferta",
    "id": "dispo-1",
    "campos": {
      "id_oferta_atividade": "of-cozinha",
      "inicio_em": "2026-10-08T09:00",
      "fim_em": "2026-10-08T17:00",
      "situacao": "declarada",
      "capacidade_declarada": "80"
    }
  },
  {
    "tabela": "missoes",
    "id": "missao-rascunho",
    "campos": {
      "titulo": "Exemplo futuro — entrega planejada",
      "id_recomendacao": "",
      "id_instituicao_responsavel": "inst-dc",
      "inicio_previsto_em": "2026-10-08T10:00",
      "fim_previsto_em": "2026-10-08T14:00",
      "situacao": "planejada"
    }
  },
  {
    "tabela": "missao_itens",
    "id": "mi-1",
    "campos": {
      "id_missao": "missao-rascunho",
      "id_demanda_item": "item-v-agua",
      "quantidade_planejada": "100"
    }
  },
  {
    "tabela": "alocacoes_pessoa",
    "id": "al-1",
    "campos": {
      "id_missao": "missao-rascunho",
      "id_pessoa": "p-joao",
      "papel": "Condutor a confirmar",
      "situacao": "proposta"
    }
  },
  {
    "tabela": "reservas_recurso",
    "id": "reserva-1",
    "campos": {
      "id_missao": "missao-rascunho",
      "id_recurso": "r-agua",
      "quantidade_reservada": "100",
      "inicio_em": "2026-10-08T10:00",
      "fim_em": "2026-10-08T14:00",
      "situacao": "proposta"
    }
  }
];

export function criarEstado(): EstadoPrototipo {
  const estado: EstadoPrototipo = { versao: 1, tabelas: {}, eventos: [], ator: 'Administrador de demonstração' };
  for (const tela of TELAS) estado.tabelas[tela.chave] = [];
  for (const semente of SEMENTES) {
    const registro: Registro = { id: semente.id, inativo: false, criado_em: '2026-10-08T12:00:00Z',
      atualizado_em: '2026-10-08T12:00:00Z', campos: structuredClone(semente.campos) };
    estado.tabelas[semente.tabela].push(registro);
  }
  return estado;
}

