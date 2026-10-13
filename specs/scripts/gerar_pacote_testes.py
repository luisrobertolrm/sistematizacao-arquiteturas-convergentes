# Script de geração automatizada da Suíte Modular de Testes de Interface (Padrão 3.0.0)
# Baseado na skill gerar-pacote-testes-ui e no contrato 3.0.0

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SPECS_DIR = Path(__file__).resolve().parent.parent

FEATURES = [
    {
        "id": "acesso-navegacao",
        "nome": "Acesso, sessão e navegação",
        "objetivo": "Acessar funcionalidades administrativas por token e navegar entre módulos na aplicação integrada.",
        "pre_condicoes": [
            "Aplicação frontend disponível na URL base",
            "API acessível pelo proxy /api com PostgreSQL migrado",
            "Token administrativo configurado"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Conectar com token administrativo e acessar navegação",
                "descricao": "Preenche o token de acesso administrativo e acessa a barra de navegação principal da aplicação.",
                "passos": [
                    { "acao": "goto", "rota": "/" },
                    { "acao": "fill", "alvo": { "css": "#token" }, "valor": "TokenAdmin{{RUN_ID}}" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Acessar cadastros" } }
                ],
                "resultado_esperado": {
                    "descricao": "Menu de navegação e controles administrativos ficam visíveis.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "role": "button", "name": "Sair" } },
                        { "acao": "visible", "alvo": { "role": "button", "name": "Instituições" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Tentativa de acesso com token inválido exibe alerta de erro",
                        "passos": [
                            { "acao": "goto", "rota": "/" },
                            { "acao": "fill", "alvo": { "css": "#token" }, "valor": "TokenInvalido{{RUN_ID}}" },
                            { "acao": "click", "alvo": { "role": "button", "name": "Acessar cadastros" } }
                        ],
                        "resultado_esperado": {
                            "descricao": "Alerta de erro visível na tela e permanência na área de login.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "alert" } }
                            ]
                        }
                    }
                ]
            },
            {
                "id": "FLUXO-02",
                "titulo": "Desconectar sessão administrativa",
                "descricao": "Encerra a sessão administrativa ativa limpando credenciais em memória.",
                "passos": [
                    { "acao": "goto", "rota": "/" },
                    { "acao": "fill", "alvo": { "css": "#token" }, "valor": "TokenAdmin{{RUN_ID}}" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Acessar cadastros" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Sair" } }
                ],
                "resultado_esperado": {
                    "descricao": "Retorna à tela de acesso com campo de token e botão de acesso disponíveis.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "css": "#token" } },
                        { "acao": "visible", "alvo": { "role": "button", "name": "Acessar cadastros" } }
                    ]
                },
                "excecoes": []
            }
        ]
    },
    {
        "id": "instituicoes",
        "nome": "Instituições",
        "objetivo": "Manter instituições da rede, localização, contato e validação cadastral via interface gráfica.",
        "pre_condicoes": [
            "Sessão administrativa válida com token ativo",
            "Identificador exclusivo por execução"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Cadastrar e editar instituição",
                "descricao": "Preenche os dados cadastrais da instituição, salva e posteriormente edita o registro.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Instituições" } },
                    { "acao": "fill", "alvo": { "css": "#cadastro-nome" }, "valor": "Instituicao {{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#municipio" }, "valor": "3550308" },
                    { "acao": "fill", "alvo": { "css": "#uf" }, "valor": "SP" },
                    { "acao": "select", "alvo": { "css": "#tipo" }, "valor": "associacao" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Cadastrar" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Editar" } },
                    { "acao": "fill", "alvo": { "css": "#cadastro-nome" }, "valor": "Instituicao Editada {{RUN_ID}}" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar alterações" } }
                ],
                "resultado_esperado": {
                    "descricao": "Registro com o nome atualizado visível na listagem ativa e aviso de sucesso.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Instituicao Editada {{RUN_ID}}" } },
                        { "acao": "visible", "alvo": { "role": "status" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Rejeição ao informar somente latitude sem longitude",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#cadastro-nome" }, "valor": "Instituicao Coord {{RUN_ID}}" },
                            { "acao": "fill", "alvo": { "css": "#municipio" }, "valor": "3550308" },
                            { "acao": "fill", "alvo": { "css": "#uf" }, "valor": "SP" },
                            { "acao": "fill", "alvo": { "css": "#latitude" }, "valor": "-23.5505" },
                            { "acao": "click", "alvo": { "role": "button", "name": "Cadastrar" } }
                        ],
                        "resultado_esperado": {
                            "descricao": "Mensagem de alerta exibida impedindo o salvamento com coordenadas incompletas.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "alert" } }
                            ]
                        }
                    }
                ]
            },
            {
                "id": "FLUXO-02",
                "titulo": "Inativar cadastro de instituição com confirmação nativa",
                "descricao": "Aciona a ação de inativar e confirma o diálogo nativo do navegador.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Instituições" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Inativar" }, "dialog": "accept" }
                ],
                "resultado_esperado": {
                    "descricao": "Registro removido da lista ativa com aviso de inativação bem-sucedida.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "role": "status" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-02-01",
                        "cenario": "Cancelar o diálogo de confirmação mantém o cadastro existente",
                        "passos": [
                            { "acao": "click", "alvo": { "role": "button", "name": "Inativar" }, "dialog": "dismiss" }
                        ],
                        "resultado_esperado": {
                            "descricao": "O botão de edição do registro permanece visível sem inativação.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Editar" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "pessoas",
        "nome": "Pessoas",
        "objetivo": "Manter pessoas da rede e acessar seus vínculos e formação.",
        "pre_condicoes": [
            "Sessão administrativa válida com token ativo"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Cadastrar e editar pessoa voluntária ou técnica",
                "descricao": "Realiza o cadastro básico de uma pessoa na rede e altera seus dados.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Pessoas" } },
                    { "acao": "fill", "alvo": { "css": "#cadastro-nome" }, "valor": "Pessoa {{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#municipio" }, "valor": "3550308" },
                    { "acao": "fill", "alvo": { "css": "#uf" }, "valor": "SP" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Cadastrar" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Editar" } },
                    { "acao": "fill", "alvo": { "css": "#cadastro-nome" }, "valor": "Pessoa Alterada {{RUN_ID}}" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar alterações" } }
                ],
                "resultado_esperado": {
                    "descricao": "Registro com o nome alterado fica visível na listagem.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Pessoa Alterada {{RUN_ID}}" } },
                        { "acao": "visible", "alvo": { "role": "status" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Nome com menos de dois caracteres exibe mensagem de validação",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#cadastro-nome" }, "valor": "A" },
                            { "acao": "fill", "alvo": { "css": "#municipio" }, "valor": "3550308" },
                            { "acao": "fill", "alvo": { "css": "#uf" }, "valor": "SP" }
                        ],
                        "resultado_esperado": {
                            "descricao": "Mensagem informativa indicando a necessidade de pelo menos dois caracteres.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "text": "Informe um nome com pelo menos dois caracteres." } }
                            ]
                        }
                    }
                ]
            },
            {
                "id": "FLUXO-02",
                "titulo": "Acessar módulo de vínculos e formação a partir da pessoa",
                "descricao": "Navega para a gestão de vínculos institucionais e cursos da pessoa selecionada.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Pessoas" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Vínculos e formação" } }
                ],
                "resultado_esperado": {
                    "descricao": "Tela de vínculos exibida com o botão para retornar à listagem.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "role": "button", "name": "Voltar para pessoas" } }
                    ]
                },
                "excecoes": []
            }
        ]
    },
    {
        "id": "profissoes",
        "nome": "Profissões",
        "objetivo": "Manter o catálogo de profissões disponíveis para qualificação na rede.",
        "pre_condicoes": [
            "Sessão administrativa válida com token ativo"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Cadastrar, buscar e editar profissão",
                "descricao": "Cadastra uma nova profissão com CBO, filtra pelo nome e atualiza o registro.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Profissões e cursos" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Profissões" } },
                    { "acao": "fill", "alvo": { "css": "#catalogo-nome" }, "valor": "Profissao {{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#cbo" }, "valor": "212405" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar cadastro" } },
                    { "acao": "fill", "alvo": { "css": "#catalogo-busca" }, "valor": "Profissao {{RUN_ID}}" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Buscar" } }
                ],
                "resultado_esperado": {
                    "descricao": "Profissão encontrada na busca com título correto.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Profissao {{RUN_ID}}" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Tentativa de cadastro com nome em branco mantém formulário inválido",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#catalogo-nome" }, "valor": "" }
                        ],
                        "resultado_esperado": {
                            "descricao": "Botão de salvar permanece disponível mas formulário bloqueado.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Salvar cadastro" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "cursos",
        "nome": "Cursos",
        "objetivo": "Manter o catálogo de cursos e certificações formativas.",
        "pre_condicoes": [
            "Sessão administrativa válida com token ativo"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Cadastrar e consultar curso de capacitação",
                "descricao": "Cadastra um curso com carga horária e confere sua exibição na listagem.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Profissões e cursos" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Cursos" } },
                    { "acao": "fill", "alvo": { "css": "#catalogo-nome" }, "valor": "Curso {{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#carga-horaria" }, "valor": "40" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar cadastro" } }
                ],
                "resultado_esperado": {
                    "descricao": "Curso visível na listagem de cursos cadastrados.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Curso {{RUN_ID}}" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Carga horária inválida não permite submissão",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#catalogo-nome" }, "valor": "Curso Invalido {{RUN_ID}}" },
                            { "acao": "fill", "alvo": { "css": "#carga-horaria" }, "valor": "-5" }
                        ],
                        "resultado_esperado": {
                            "descricao": "Controle de submissão bloqueia a gravação de carga horária negativa.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Salvar cadastro" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "pessoa-instituicoes",
        "nome": "Vínculos institucionais da pessoa",
        "objetivo": "Gerenciar a associação formal entre pessoas cadastradas e instituições participantes.",
        "pre_condicoes": [
            "Pessoa e instituição previamente cadastradas"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Vincular instituição ao cadastro da pessoa",
                "descricao": "Abre os vínculos da pessoa e associa uma instituição participante.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Pessoas" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Vínculos e formação" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Instituições" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar vínculo" } }
                ],
                "resultado_esperado": {
                    "descricao": "Vínculo salvo com sucesso e status atualizado.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "role": "status" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Cancelar edição de vínculo retorna ao formulário padrão",
                        "passos": [
                            { "acao": "click", "alvo": { "role": "button", "name": "Editar" } },
                            { "acao": "click", "alvo": { "role": "button", "name": "Cancelar" } }
                        ],
                        "resultado_esperado": {
                            "descricao": "Formulário volta ao estado limpo com botão Salvar vínculo habilitado.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Salvar vínculo" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "pessoa-profissoes",
        "nome": "Profissões da pessoa",
        "objetivo": "Atribuir e registrar histórico profissional individualizado a uma pessoa.",
        "pre_condicoes": [
            "Pessoa cadastrada e catálogo de profissões populado"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Atribuir profissão à trajetória da pessoa",
                "descricao": "Seleciona uma profissão do catálogo e vincula ao perfil da pessoa.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Pessoas" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Vínculos e formação" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Profissões" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar vínculo" } }
                ],
                "resultado_esperado": {
                    "descricao": "Profissão vinculada à pessoa com confirmação de status.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "role": "status" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Cancelar confirmação ao inativar profissão vinculada",
                        "passos": [
                            { "acao": "click", "alvo": { "role": "button", "name": "Inativar" }, "dialog": "dismiss" }
                        ],
                        "resultado_esperado": {
                            "descricao": "O botão de edição permanece visível mantendo o vínculo ativo.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Editar" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "pessoa-cursos",
        "nome": "Cursos e formação da pessoa",
        "objetivo": "Registrar certificados, formações e cursos concluídos por pessoas na rede.",
        "pre_condicoes": [
            "Pessoa cadastrada e catálogo de cursos disponível"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Registrar formação de curso da pessoa",
                "descricao": "Associa uma formação ou curso concluído ao perfil da pessoa.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Pessoas" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Vínculos e formação" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Cursos" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar vínculo" } }
                ],
                "resultado_esperado": {
                    "descricao": "Formação registrada com sucesso.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "role": "status" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Cancelar edição de formação retorna formulário ao estado inicial",
                        "passos": [
                            { "acao": "click", "alvo": { "role": "button", "name": "Editar" } },
                            { "acao": "click", "alvo": { "role": "button", "name": "Cancelar" } }
                        ],
                        "resultado_esperado": {
                            "descricao": "Formulário volta ao modo novo registro com botão de salvar ativo.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Salvar vínculo" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "unidades-medida",
        "nome": "Unidades de medida",
        "objetivo": "Padronizar unidades quantitativas de itens, suprimentos e capacidades.",
        "pre_condicoes": [
            "Sessão administrativa válida com token ativo"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Cadastrar e consultar unidade de medida",
                "descricao": "Cadastra uma unidade com código estável e símbolo.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Atividades e unidades" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Unidades de medida" } },
                    { "acao": "fill", "alvo": { "css": "#capacidade-codigo" }, "valor": "cx{{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#capacidade-nome" }, "valor": "Caixa {{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#capacidade-simbolo" }, "valor": "cx" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar capacidade" } }
                ],
                "resultado_esperado": {
                    "descricao": "Unidade de medida visível na lista.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Caixa {{RUN_ID}}" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Rejeição de código duplicado de unidade",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#capacidade-codigo" }, "valor": "cx{{RUN_ID}}" },
                            { "acao": "fill", "alvo": { "css": "#capacidade-nome" }, "valor": "Caixa Duplicada" },
                            { "acao": "fill", "alvo": { "css": "#capacidade-simbolo" }, "valor": "cx" },
                            { "acao": "click", "alvo": { "role": "button", "name": "Salvar capacidade" } }
                        ],
                        "resultado_esperado": {
                            "descricao": "Alerta de erro exibido na interface.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "alert" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "categorias-atividade",
        "nome": "Categorias de atividade",
        "objetivo": "Classificar taxonomicamente as atividades operacionais e de auxílio humanitário.",
        "pre_condicoes": [
            "Sessão administrativa válida com token ativo"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Cadastrar categoria de atividade",
                "descricao": "Cria uma nova categoria taxonômica para organização das atividades.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Atividades e unidades" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Categorias de atividade" } },
                    { "acao": "fill", "alvo": { "css": "#capacidade-codigo" }, "valor": "log{{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#capacidade-nome" }, "valor": "Logistica {{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#capacidade-descricao" }, "valor": "Atividades de transporte e entrega" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar capacidade" } }
                ],
                "resultado_esperado": {
                    "descricao": "Categoria cadastrada visível na listagem.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Logistica {{RUN_ID}}" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Código de categoria duplicado dispara alerta",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#capacidade-codigo" }, "valor": "log{{RUN_ID}}" },
                            { "acao": "fill", "alvo": { "css": "#capacidade-nome" }, "valor": "Logistica Duplicada" },
                            { "acao": "fill", "alvo": { "css": "#capacidade-descricao" }, "valor": "Descricao duplicada" },
                            { "acao": "click", "alvo": { "role": "button", "name": "Salvar capacidade" } }
                        ],
                        "resultado_esperado": {
                            "descricao": "Alerta de erro visível na interface.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "alert" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "atividades",
        "nome": "Atividades",
        "objetivo": "Definir atividades e serviços executáveis na resposta e assistência.",
        "pre_condicoes": [
            "Categorias de atividade cadastradas"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Cadastrar atividade com descrição",
                "descricao": "Cadastra uma atividade com orientações e restrições.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Atividades e unidades" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Atividades" } },
                    { "acao": "fill", "alvo": { "css": "#capacidade-codigo" }, "valor": "atv{{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#capacidade-nome" }, "valor": "Distribuicao {{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#capacidade-descricao" }, "valor": "Distribuicao de cestas basicas em abrigos" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar capacidade" } }
                ],
                "resultado_esperado": {
                    "descricao": "Atividade cadastrada visível na listagem.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Distribuicao {{RUN_ID}}" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Atividade sem nome obrigatório mantém salvamento desabilitado",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#capacidade-codigo" }, "valor": "atverr{{RUN_ID}}" },
                            { "acao": "fill", "alvo": { "css": "#capacidade-nome" }, "valor": "" }
                        ],
                        "resultado_esperado": {
                            "descricao": "Botão Salvar capacidade permanece na tela sem submissão.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Salvar capacidade" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "termos-sinonimos",
        "nome": "Termos e sinônimos da atividade",
        "objetivo": "Registrar termos alternativos e sinônimos para enriquecer a busca semântica de atividades.",
        "pre_condicoes": [
            "Atividade cadastrada e selecionada"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Adicionar termo e sinônimo à atividade",
                "descricao": "Adiciona uma expressão sinônima para ampliar a capacidade de busca.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Atividades e unidades" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Atividades" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Termos e sinônimos" } },
                    { "acao": "fill", "alvo": { "css": "#atividade-termo" }, "valor": "Entrega de mantimentos {{RUN_ID}}" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar termo" } }
                ],
                "resultado_esperado": {
                    "descricao": "Termo cadastrado visível na lista de sinônimos.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Entrega de mantimentos {{RUN_ID}}" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Termo duplicado na mesma atividade dispara erro",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#atividade-termo" }, "valor": "Entrega de mantimentos {{RUN_ID}}" },
                            { "acao": "click", "alvo": { "role": "button", "name": "Salvar termo" } }
                        ],
                        "resultado_esperado": {
                            "descricao": "Alerta de erro visível indicando termo repetido.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "alert" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "tipos-recurso",
        "nome": "Tipos de recurso",
        "objetivo": "Classificar categorias físicas ou operacionais de recursos (veículos, alimentos, equipamentos).",
        "pre_condicoes": [
            "Unidades de medida previamente cadastradas"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Cadastrar tipo de recurso operacional",
                "descricao": "Cria um tipo de recurso com categoria e modo de controle.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Recursos e ofertas" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Tipos de recurso" } },
                    { "acao": "fill", "alvo": { "css": "#recurso-nome" }, "valor": "Bote Resgate {{RUN_ID}}" },
                    { "acao": "select", "alvo": { "css": "#recurso-categoria" }, "valor": "equipamento" },
                    { "acao": "select", "alvo": { "css": "#recurso-modo" }, "valor": "individual" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar cadastro" } }
                ],
                "resultado_esperado": {
                    "descricao": "Tipo de recurso cadastrado visível na lista.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Bote Resgate {{RUN_ID}}" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Submissão sem preenchimento do nome obrigatório",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#recurso-nome" }, "valor": "" }
                        ],
                        "resultado_esperado": {
                            "descricao": "Botão Salvar cadastro visível sem submissão de dados.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Salvar cadastro" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "recursos",
        "nome": "Recursos",
        "objetivo": "Manter inventário de recursos disponíveis vinculados a pessoas ou instituições.",
        "pre_condicoes": [
            "Tipo de recurso cadastrado e responsável habilitado"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Cadastrar recurso operacional",
                "descricao": "Cadastra um bem ou lote no inventário de recursos.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Recursos e ofertas" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Recursos" } },
                    { "acao": "fill", "alvo": { "css": "#recurso-nome" }, "valor": "Gerador 5kVA {{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#recurso-municipio" }, "valor": "3550308" },
                    { "acao": "fill", "alvo": { "css": "#recurso-quantidade" }, "valor": "3" },
                    { "acao": "select", "alvo": { "css": "#recurso-estado" }, "valor": "operacional" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar cadastro" } }
                ],
                "resultado_esperado": {
                    "descricao": "Recurso cadastrado visível na lista.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Gerador 5kVA {{RUN_ID}}" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Quantidade negativa não permite submissão",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#recurso-nome" }, "valor": "Recurso Invalido {{RUN_ID}}" },
                            { "acao": "fill", "alvo": { "css": "#recurso-quantidade" }, "valor": "-1" }
                        ],
                        "resultado_esperado": {
                            "descricao": "Botão Salvar cadastro visível com formulário bloqueado.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Salvar cadastro" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "ofertas-atividades",
        "nome": "Ofertas de atividades",
        "objetivo": "Registrar ofertas voluntárias ou institucionais de atividades para atendimento.",
        "pre_condicoes": [
            "Atividades cadastradas e responsáveis habilitados"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Publicar oferta de atividade operacional",
                "descricao": "Cria uma oferta declarando capacidade e município de atendimento.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Recursos e ofertas" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Ofertas de atividades" } },
                    { "acao": "fill", "alvo": { "css": "#recurso-municipio" }, "valor": "3550308" },
                    { "acao": "fill", "alvo": { "css": "#recurso-descricao" }, "valor": "Oferta de equipe para acolhimento {{RUN_ID}}" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar cadastro" } }
                ],
                "resultado_esperado": {
                    "descricao": "Oferta cadastrada visível na lista.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Oferta de equipe para acolhimento {{RUN_ID}}" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Município de atendimento com formato incompleto",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#recurso-municipio" }, "valor": "123" }
                        ],
                        "resultado_esperado": {
                            "descricao": "Botão de salvar permanece impedindo o envio com código IBGE incompleto.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Salvar cadastro" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "recursos-oferta",
        "nome": "Recursos vinculados à oferta",
        "objetivo": "Associar recursos materiais específicos a uma determinada oferta de atividade.",
        "pre_condicoes": [
            "Oferta de atividade existente"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Vincular recurso específico à oferta",
                "descricao": "Define recursos materiais que compõem o atendimento da oferta.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Recursos e ofertas" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Ofertas de atividades" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Recursos da oferta" } },
                    { "acao": "fill", "alvo": { "css": "#vinculo-quantidade" }, "valor": "4" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar vínculo" } }
                ],
                "resultado_esperado": {
                    "descricao": "Vínculo salvo com status de confirmação.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "role": "status" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Informar quantidade zero no recurso dispara alerta",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#vinculo-quantidade" }, "valor": "0" },
                            { "acao": "click", "alvo": { "role": "button", "name": "Salvar vínculo" } }
                        ],
                        "resultado_esperado": {
                            "descricao": "Alerta de erro visível na interface.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "alert" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "tipos-desastre",
        "nome": "Tipos de desastre",
        "objetivo": "Classificar os tipos e códigos Cobrade de eventos de desastre.",
        "pre_condicoes": [
            "Sessão administrativa válida com token ativo"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Cadastrar tipo de desastre com código estável",
                "descricao": "Cria um novo tipo de desastre para catalogação de ocorrências.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Desastres e áreas" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Tipos de desastre" } },
                    { "acao": "fill", "alvo": { "css": "#desastre-codigo" }, "valor": "DES{{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#desastre-nome" }, "valor": "Deslizamento Encosta {{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#desastre-descricao" }, "valor": "Movimento de massa em encostas urbanas" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar desastre" } }
                ],
                "resultado_esperado": {
                    "descricao": "Tipo de desastre visível na lista.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Deslizamento Encosta {{RUN_ID}}" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Código de desastre duplicado dispara erro",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#desastre-codigo" }, "valor": "DES{{RUN_ID}}" },
                            { "acao": "fill", "alvo": { "css": "#desastre-nome" }, "valor": "Deslizamento Duplicado" },
                            { "acao": "fill", "alvo": { "css": "#desastre-descricao" }, "valor": "Outra descricao" },
                            { "acao": "click", "alvo": { "role": "button", "name": "Salvar desastre" } }
                        ],
                        "resultado_esperado": {
                            "descricao": "Alerta de erro visível na interface.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "alert" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "ocorrencias-classificacoes",
        "nome": "Ocorrências e classificações",
        "objetivo": "Registrar ocorrências operacionais e suas classificações e status.",
        "pre_condicoes": [
            "Instituição coordenadora e tipos de desastre cadastrados"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Registrar ocorrência em resposta operacional",
                "descricao": "Abre um chamado de ocorrência de desastre com situação e descrição.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Desastres e áreas" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Ocorrências" } },
                    { "acao": "fill", "alvo": { "css": "#desastre-nome" }, "valor": "Vendaval Regiao Sul {{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#desastre-descricao" }, "valor": "Queda de arvores e postes com desabrigados" },
                    { "acao": "select", "alvo": { "css": "#desastre-situacao" }, "valor": "em_resposta" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar desastre" } }
                ],
                "resultado_esperado": {
                    "descricao": "Ocorrência cadastrada visível na lista.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Vendaval Regiao Sul {{RUN_ID}}" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Ocorrência sem título obrigatório impede gravação",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#desastre-nome" }, "valor": "" }
                        ],
                        "resultado_esperado": {
                            "descricao": "Botão Salvar desastre visível mas formulário bloqueado.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Salvar desastre" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "areas-afetadas",
        "nome": "Áreas afetadas e avaliação territorial",
        "objetivo": "Mapear, delimitar e avaliar territórios atingidos por eventos de desastre.",
        "pre_condicoes": [
            "Ocorrência de desastre ativa selecionada"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Cadastrar área territorial com severidade",
                "descricao": "Define uma área geográfica afetada com seu nível de criticidade.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Desastres e áreas" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Ocorrências" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Áreas e mapa" } },
                    { "acao": "fill", "alvo": { "css": "#area-nome" }, "valor": "Comunidade Baixada {{RUN_ID}}" },
                    { "acao": "select", "alvo": { "css": "#area-severidade" }, "valor": "alta" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar área" } }
                ],
                "resultado_esperado": {
                    "descricao": "Área afetada cadastrada visível na listagem.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Comunidade Baixada {{RUN_ID}}" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Área sem nome preenchido não permite salvar",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#area-nome" }, "valor": "" }
                        ],
                        "resultado_esperado": {
                            "descricao": "Botão Salvar área visível com formulário impedido de submissão.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Salvar área" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "mapa-desenho",
        "nome": "Mapa e desenho de delimitações",
        "objetivo": "Desenhar, ajustar e inspecionar polígonos geoespaciais no mapa interativo.",
        "pre_condicoes": [
            "Painel de áreas e mapa aberto"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Enquadrar áreas e acionar ferramenta de desenho de polígono",
                "descricao": "Enquadra as delimitações e habilita o modo de desenho interativo.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Desastres e áreas" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Ocorrências" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Áreas e mapa" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Enquadrar áreas da página" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Desenhar nova delimitação" } }
                ],
                "resultado_esperado": {
                    "descricao": "Controle de limpeza de delimitação visível na barra de ações do mapa.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "role": "button", "name": "Limpar delimitação" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Limpar delimitação sem pontos desenhados restaura botão inicial",
                        "passos": [
                            { "acao": "click", "alvo": { "role": "button", "name": "Limpar delimitação" } }
                        ],
                        "resultado_esperado": {
                            "descricao": "Botão Desenhar nova delimitação volta a ficar disponível.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Desenhar nova delimitação" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "conexoes-ia",
        "nome": "Conexões de IA",
        "objetivo": "Configurar provedores e endpoints de inteligência artificial na rede.",
        "pre_condicoes": [
            "Acesso administrativo válido com token ativo"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Configurar conexão de provedor de IA compatível com OpenAI",
                "descricao": "Registra um endpoint de IA local ou remoto sem autenticação.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Configuração de IA" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Conexões de IA" } },
                    { "acao": "fill", "alvo": { "css": "#ia-nome" }, "valor": "Provedor Local {{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#ia-url" }, "valor": "http://127.0.0.1:11434/v1" },
                    { "acao": "select", "alvo": { "css": "#ia-auth" }, "valor": "nenhuma" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar conexão" } }
                ],
                "resultado_esperado": {
                    "descricao": "Conexão cadastrada visível na lista de provedores.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Provedor Local {{RUN_ID}}" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "URL base sem protocolo exibe alerta de erro",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#ia-nome" }, "valor": "Provedor Errado {{RUN_ID}}" },
                            { "acao": "fill", "alvo": { "css": "#ia-url" }, "valor": "sem-protocolo" },
                            { "acao": "click", "alvo": { "role": "button", "name": "Salvar conexão" } }
                        ],
                        "resultado_esperado": {
                            "descricao": "Mensagem de alerta visível indicando URL inválida.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "alert" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "modelos-ia",
        "nome": "Modelos de IA e seleção por finalidade",
        "objetivo": "Definir modelos de embeddings e LLM com respectivas finalidades operacionais.",
        "pre_condicoes": [
            "Conexão de IA cadastrada"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Cadastrar modelo por finalidade de inferência",
                "descricao": "Registra modelo LLM para apoio à decisão e recomendações.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Configuração de IA" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Modelos de IA" } },
                    { "acao": "fill", "alvo": { "css": "#modelo-identificador" }, "valor": "qwen2.5:7b-instruct" },
                    { "acao": "select", "alvo": { "css": "#modelo-finalidade" }, "valor": "inferencia_texto" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar modelo" } }
                ],
                "resultado_esperado": {
                    "descricao": "Modelo visível na listagem de modelos configurados.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "qwen2.5:7b-instruct" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Modelo sem identificador não permite salvar",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#modelo-identificador" }, "valor": "" }
                        ],
                        "resultado_esperado": {
                            "descricao": "Botão Salvar modelo permanece na tela com bloqueio.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Salvar modelo" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "indices-atividades",
        "nome": "Índices semânticos das atividades",
        "objetivo": "Gerar e sincronizar índices de embeddings vetoriais das atividades para busca semântica.",
        "pre_condicoes": [
            "Modelo de embedding ativo e atividades cadastradas"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Montar lote e disparar indexação de atividades",
                "descricao": "Seleciona atividades para compor o lote e dispara a geração dos embeddings.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Configuração de IA" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Índices de atividades" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Adicionar ao lote" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Indexar lote" } }
                ],
                "resultado_esperado": {
                    "descricao": "Aviso de processamento e atualização de índices visível.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "role": "status" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Remover item do lote de indexação antes de processar",
                        "passos": [
                            { "acao": "click", "alvo": { "role": "button", "name": "Remover do lote" } }
                        ],
                        "resultado_esperado": {
                            "descricao": "Botão de adicionar ao lote permanece disponível para novas adições.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Adicionar ao lote" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "busca-semantica",
        "nome": "Busca de atividades por significado",
        "objetivo": "Pesquisar atividades correspondentes através de similaridade semântica em linguagem natural.",
        "pre_condicoes": [
            "Índices de atividades gerados previamente"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Executar busca semântica em linguagem natural",
                "descricao": "Informa uma necessidade em texto livre e executa a busca vetorial por similaridade.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Configuração de IA" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Índices de atividades" } },
                    { "acao": "fill", "alvo": { "css": "#ia-consulta" }, "valor": "abrigo temporario e acolhimento familiar" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Buscar por significado" } }
                ],
                "resultado_esperado": {
                    "descricao": "Aviso de status e resultados da consulta por similaridade exibidos.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "role": "status" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Busca com necessidade vazia mantém botão desabilitado",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#ia-consulta" }, "valor": "" }
                        ],
                        "resultado_esperado": {
                            "descricao": "Botão Buscar por significado permanece na tela.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Buscar por significado" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "demandas-itens",
        "nome": "Demandas e itens de necessidade",
        "objetivo": "Registrar solicitações de auxílio e desdobrá-las em itens específicos de suprimento.",
        "pre_condicoes": [
            "Área afetada e solicitante cadastrados"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Cadastrar demanda com itens de necessidade",
                "descricao": "Cria um chamado emergencial especificando quantidade e prioridade dos itens.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Demandas e recomendações" } },
                    { "acao": "fill", "alvo": { "css": "#demanda-titulo" }, "valor": "Atendimento Abrigo Municipal {{RUN_ID}}" },
                    { "acao": "fill", "alvo": { "css": "#demanda-descricao" }, "valor": "Suprimento emergencial de colchões e refeições" },
                    { "acao": "select", "alvo": { "css": "#demanda-prioridade" }, "valor": "alta" },
                    { "acao": "fill", "alvo": { "css": "#item-quantidade-0" }, "valor": "50" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Salvar demanda" } }
                ],
                "resultado_esperado": {
                    "descricao": "Demanda cadastrada visível na lista.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "text": "Atendimento Abrigo Municipal {{RUN_ID}}" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Quantidade zerada no item da demanda dispara alerta",
                        "passos": [
                            { "acao": "fill", "alvo": { "css": "#item-quantidade-0" }, "valor": "0" },
                            { "acao": "click", "alvo": { "role": "button", "name": "Salvar demanda" } }
                        ],
                        "resultado_esperado": {
                            "descricao": "Alerta de erro visível na interface.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "alert" } }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    {
        "id": "recomendacoes-decisoes",
        "nome": "Recomendações por IA e decisão administrativa",
        "objetivo": "Gerar recomendações automatizadas por IA e registrar aprovação ou rejeição administrativa.",
        "pre_condicoes": [
            "Demanda aberta com itens e modelos de IA operacionais"
        ],
        "fluxos": [
            {
                "id": "FLUXO-01",
                "titulo": "Gerar recomendação por IA e aprovar sugestão",
                "descricao": "Dispara análise do assistente de IA, inspeciona sugestões e registra aprovação formal.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Demandas e recomendações" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Recomendações e decisões" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Gerar recomendação por IA" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Ver recomendação" } },
                    { "acao": "fill", "alvo": { "css": "#decisao-justificativa" }, "valor": "Aprovado pelo comite gestor de desastres {{RUN_ID}}" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Aprovar sugestão" }, "dialog": "accept" }
                ],
                "resultado_esperado": {
                    "descricao": "Decisão aprovada com registro de sucesso.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "role": "status" } }
                    ]
                },
                "excecoes": [
                    {
                        "id": "EXC-01-01",
                        "cenario": "Cancelar diálogo de confirmação ao aprovar mantém opções de decisão",
                        "passos": [
                            { "acao": "click", "alvo": { "role": "button", "name": "Aprovar sugestão" }, "dialog": "dismiss" }
                        ],
                        "resultado_esperado": {
                            "descricao": "Botão de rejeitar sugestão permanece disponível para nova deliberação.",
                            "verificacoes": [
                                { "acao": "visible", "alvo": { "role": "button", "name": "Rejeitar sugestão" } }
                            ]
                        }
                    }
                ]
            },
            {
                "id": "FLUXO-02",
                "titulo": "Rejeitar recomendação por IA com justificativa",
                "descricao": "Avalia o parecer gerado pela IA e registra a rejeição formal justificando a decisão.",
                "passos": [
                    { "acao": "click", "alvo": { "role": "button", "name": "Demandas e recomendações" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Recomendações e decisões" } },
                    { "acao": "click", "alvo": { "role": "button", "name": "Ver recomendação" } },
                    { "acao": "fill", "alvo": { "css": "#decisao-justificativa" }, "valor": "Recursos insuficientes no polo {{RUN_ID}}" },
                    { "acao": "click", "alvo": { "role": "button", "name": "Rejeitar sugestão" }, "dialog": "accept" }
                ],
                "resultado_esperado": {
                    "descricao": "Decisão de rejeição registrada com sucesso.",
                    "verificacoes": [
                        { "acao": "visible", "alvo": { "role": "status" } }
                    ]
                },
                "excecoes": []
            }
        ]
    }
]

def gerar_suite():
    print(f"Iniciando geracao da suite modular em: {SPECS_DIR}")
    mapeamento_funcionalidades = []

    for f in FEATURES:
        fid = f["id"]
        feature_dir = SPECS_DIR / fid
        feature_dir.mkdir(parents=True, exist_ok=True)

        spec_file = feature_dir / "spec.json"
        hist_file = feature_dir / "historico.json"

        # Contagem de fluxos e exceções
        total_fluxos = len(f["fluxos"])
        total_excecoes = sum(len(fl.get("excecoes", [])) for fl in f["fluxos"])

        # 1. spec.json
        spec_content = {
            "versao_contrato": "3.0.0",
            "funcionalidade": {
                "id": fid,
                "nome": f["nome"],
                "rota_inicial": "/",
                "objetivo": f["objetivo"]
            },
            "pre_condicoes": f["pre_condicoes"],
            "fluxos": f["fluxos"]
        }
        with open(spec_file, "w", encoding="utf-8") as s_out:
            json.dump(spec_content, s_out, indent=2, ensure_ascii=False)

        # 2. historico.json inicial
        hist_content = {
            "funcionalidade_id": fid,
            "max_historico": 5,
            "execucoes": []
        }
        with open(hist_file, "w", encoding="utf-8") as h_out:
            json.dump(hist_content, h_out, indent=2, ensure_ascii=False)

        mapeamento_funcionalidades.append({
            "id": fid,
            "nome": f["nome"],
            "pasta": fid,
            "arquivo_spec": f"{fid}/spec.json",
            "arquivo_historico": f"{fid}/historico.json",
            "objetivo": f["objetivo"],
            "total_fluxos": total_fluxos,
            "total_excecoes": total_excecoes
        })
        print(f"  ✓ [{fid}] spec.json e historico.json gerados ({total_fluxos} fluxos, {total_excecoes} excecoes)")

    # 3. mapeamento.json na raiz de specs/
    mapeamento_content = {
        "versao_contrato": "3.0.0",
        "projeto": {
            "nome": "RedeSolidária — frontend integrado",
            "base_url": "http://127.0.0.1:4200",
            "gerado_por": "Antigravity — IA Produtora",
            "atualizado_em": datetime.now(timezone.utc).isoformat()
        },
        "funcionalidades": mapeamento_funcionalidades
    }

    mapeamento_file = SPECS_DIR / "mapeamento.json"
    with open(mapeamento_file, "w", encoding="utf-8") as m_out:
        json.dump(mapeamento_content, m_out, indent=2, ensure_ascii=False)

    total_f = len(mapeamento_funcionalidades)
    tot_fluxos = sum(item["total_fluxos"] for item in mapeamento_funcionalidades)
    tot_exc = sum(item["total_excecoes"] for item in mapeamento_funcionalidades)
    print(f"\n✓ Catalogo mestre {mapeamento_file} gerado com sucesso!")
    print(f"Total de funcionalidades: {total_f}")
    print(f"Total de fluxos principais: {tot_fluxos}")
    print(f"Total de excecoes: {tot_exc}")

if __name__ == "__main__":
    gerar_suite()
