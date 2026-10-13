# Simulação do escopo inicial — resultado executado

Versão: `escopo-inicial-d009-v2`. Python 3.13.12. Execução UTC: 2026-10-09T14:46:07.304325+00:00.

Cenário fictício fixo em 08/10/2026 às 09h UTC−03:00: um município (código fictício 0000001), uma ocorrência de inundação/deslizamento, três áreas distintas, três instituições, quatro pessoas, três demandas e seis itens. Recursos: um caminhão, 300 L de água e um gerador descrito como 2 kVA.

Resultado: **54 verificações OK, 0 falhas e 8 limites documentados**. Limites não contam como testes aprovados.

O fluxo de sugestão e avaliação administrativa foi exercitado em memória. Esse resultado não comprova aplicação, banco, IA real ou viabilidade de alocação. Demandas e recomendações já são representadas segundo D008/D009; execução operacional continua fora do recorte.

| Cenário | Natureza | Resultado | Evidência |
|---|---|---|---|
| Cadastros e relações do cenário | Regra/fluxo | OK | Relações verificadas em memória, incluindo qualificações, ofertas, unidades e modelos; não é teste de FKs SQL. |
| Município e três áreas | Regra/fluxo | OK | Três polígonos ilustrativos distintos em um município fictício; sem mapa ou análise espacial. |
| Sem classificação | Rejeição de entrada | OK | Classificação ausente |
| Sem tipo principal | Rejeição de entrada | OK | Exatamente um tipo principal |
| Dois tipos principais | Rejeição de entrada | OK | Exatamente um tipo principal |
| Tipo duplicado | Rejeição de entrada | OK | Tipo duplicado |
| Tipo inexistente | Rejeição de entrada | OK | FK tipo de desastre inválida |
| Demanda com itens mistos | Regra/fluxo | OK | Pedido contém uma viagem e 200 litros, cada item com uma referência exclusiva e unidade por FK. |
| Prioridade independente da gravidade | Regra/fluxo | OK | Área moderada pode ter pedido urgente; escalas são convenções fictícias. |
| Item com atividade e recurso | Rejeição de entrada | OK | Item deve pedir atividade ou recurso |
| Item sem objeto | Rejeição de entrada | OK | Item deve pedir atividade ou recurso |
| Atividade inexistente | Rejeição de entrada | OK | FK atividade inválida |
| Quantidade zero | Rejeição de entrada | OK | Quantidade inválida |
| Quantidade negativa | Rejeição de entrada | OK | Quantidade inválida |
| Unidade incompatível | Rejeição de entrada | OK | Unidade incompatível |
| Item de outra demanda | Rejeição de entrada | OK | Item pertence a outra demanda |
| Demanda sem itens | Rejeição de entrada | OK | Demanda sem itens |
| Prazo inválido | Rejeição de entrada | OK | Prazo anterior ao início |
| Solicitante inexistente | Rejeição de entrada | OK | FK solicitante inválida |
| Responsável ambíguo | Rejeição de entrada | OK | Responsável deve ser exclusivo |
| Ofertante ambíguo | Rejeição de entrada | OK | Ofertante deve ser exclusivo |
| Filtro demonstrativo de formação | Regra/fluxo | OK | João passa; Carlos tem curso vencido e Marta tem curso pendente. Requisito foi fornecido manualmente e não comprova aptidão. |
| Recuperação artificial | Regra/fluxo | OK | Cosseno de vetores artificiais recupera transporte; qualidade semântica não avaliada. |
| Hash obsoleto | Regra/fluxo | OK | Alteração de conteúdo exclui a representação antiga; atomicidade no banco não foi exercitada. |
| Dimensão errada | Regra/fluxo | OK | Vetor incompatível rejeitado. |
| Modelo diferente com mesma dimensão | Regra/fluxo | OK | Dimensão igual não permite comparar modelos diferentes. |
| Modelo de texto no índice | Regra/fluxo | OK | Finalidade de inferência não serve ao índice de embeddings. |
| Consulta de dimensão errada | Rejeição de entrada | OK | Consulta de dimensão inválida |
| Mais de um modelo ativo | Rejeição de entrada | OK | Mais de um modelo ativo por finalidade |
| Ausência de modelo ativo | Rejeição de entrada | OK | Modelo ativo ausente |
| Dimensões distintas armazenadas | Regra/fluxo | OK | Fixtures de 3 e 4 dimensões coexistem, com comparação limitada ao modelo; pgvector não foi usado. |
| Cobertura incompleta do modelo futuro | Regra/fluxo | OK | Modelo de 4 dimensões cobre só transporte. Falta preparar refeições; critério formal de cobertura continua pendente. |
| Sugestão para Suprimentos para Várzea | Regra/fluxo | OK | Itens, pessoas, instituições/ofertas, recursos e modelos referenciam registros reais do cenário. |
| Sugestão para Suprimentos e energia para Encosta | Regra/fluxo | OK | Itens, pessoas, instituições/ofertas, recursos e modelos referenciam registros reais do cenário. |
| Sugestão para Refeições para Centro | Regra/fluxo | OK | Itens, pessoas, instituições/ofertas, recursos e modelos referenciam registros reais do cenário. |
| Pessoa inventada | Rejeição de entrada | OK | Pessoa sugerida inexistente |
| Instituição de outra oferta | Rejeição de entrada | OK | Instituição não é dona da oferta |
| Recurso inventado | Rejeição de entrada | OK | Recurso sugerido inexistente |
| Item de pedido diferente | Rejeição de entrada | OK | Item pertence a outra demanda |
| Quantidade sugerida excessiva | Rejeição de entrada | OK | Quantidade sugerida inválida |
| Modelos trocados na recomendação | Rejeição de entrada | OK | Finalidade dos modelos inválida |
| Registro repetido | Rejeição de entrada | OK | Recomendação já registrada |
| Aprovação administrativa | Regra/fluxo | OK | Decisão e motivo registrados no histórico auxiliar, sem alterar quantidades. |
| Rejeição administrativa | Regra/fluxo | OK | Rejeição preserva a sugestão e suas pendências. |
| Administrador não autorizado | Rejeição de entrada | OK | Administrador não autorizado |
| Decisão repetida | Rejeição de entrada | OK | Recomendação já decidida |
| Nova análise e histórico | Regra/fluxo | OK | Nova recomendação tem ID próprio; a anterior mantém sua decisão. |
| Preservação das decisões | Regra/fluxo | OK | Quatro recomendações, duas decisões e duas análises ainda geradas. |
| Aprovação não altera estoque ou pedido | Regra/fluxo | OK | Lote continua com 300 L; quantidades e situações dos pedidos permanecem iguais. Missões/reservas não são modeladas neste exercício. |
| Novo LLM preserva embeddings | Regra/fluxo | OK | Seleção de configuração de inferência pode mudar sem reindexar; é verificação lógica, sem interface de troca ou chamada a provedor. |
| Déficit global explícito | Regra/fluxo | OK | Cálculo confirma 400 L pedidos/sugeridos independentemente para 300 L cadastrados: déficit 100 L; não equivale a plano viável. |
| Bem compartilhado identificado | Regra/fluxo | OK | As duas sugestões referenciam o mesmo caminhão em janelas sobrepostas; a pendência não é uma reserva resolvida. |
| Não somar capacidade dependente | Regra/fluxo | OK | Embora a soma declarada seja 120, a sugestão não afirma cobertura quantitativa; membros da instituição não comprovam composição da oferta. |
| Item sem candidato mantém lacuna | Regra/fluxo | OK | Energia permanece sem recurso sugerido pelo adaptador; nenhum recurso foi inventado para completar o pedido. |
| Estoque compartilhado | Limite do exercício | LIMITE | Dois pedidos somam 400 L; lote possui 300 L. Sugestões independentes somam 400 L e explicitam déficit global de 100 L; não há reserva ou plano global executável. |
| Caminhão e agenda | Limite do exercício | LIMITE | O mesmo caminhão e João aparecem nas duas demandas sobrepostas. Conflito fica como pendência; concorrência, agenda, aceite e reserva são evolução futura. |
| Capacidade compartilhada | Limite do exercício | LIMITE | Cozinha declara 80 e Paula 40, mas ela integra a cozinha. A sugestão apresenta candidatos sem somar 120; cobertura quantitativa fica em zero, pendente de composição/período-base. |
| Compatibilidade técnica | Limite do exercício | LIMITE | Gerador de 2 kVA e necessidade de 5 kVA constam em texto. O adaptador do cenário deixa o item sem sugestão; não existe validador técnico genérico de potência. |
| Geografia | Limite do exercício | LIMITE | Somente fechamento de anel e intervalo de coordenadas foram checados. CRS, validade topológica, limites municipais, mapa e acesso seguro permanecem pendentes. |
| IA real | Limite do exercício | LIMITE | Vetores e respostas são artificiais. Não há LangChain, LangGraph, provedor, qualidade de RAG ou medição do indicador de redução de tempo. |
| Banco e segurança | Limite do exercício | LIMITE | FKs e regras foram exercitadas em Python; não há PostgreSQL, pgvector, Alembic, transações, JWT ou criptografia testados. Conexão fictícia não contém token. |
| Contratos posteriores | Limite do exercício | LIMITE | O exercício mantém convenções D009 e não verifica os contratos implementados de escalas, auditoria, índices, quantidades e decisão em D015–D017. Requisitos avançados continuam futuros. Convenções do exercício não são novas decisões de modelagem. |

## Recomendações e histórico

| ID (UUID abreviado) | Demanda | Situação | Itens |
|---|---|---|---|
| 0000012c | 000000c8 | aprovada | 2 |
| 0000012d | 000000c9 | rejeitada | 3 |
| 0000012e | 000000ca | gerada | 1 |
| 0000012f | 000000c8 | gerada | 2 |

Identificadores completos, candidatos, quantidades, justificativas, pendências e duas decisões estão em [resultado.json](resultado.json). Os dados de entrada estão em [cenario.py](../cenario.py), com tipos em [modelos.py](../modelos.py).

Quantidade zero em refeição/energia significa cobertura quantitativa não validada ou ausência de candidato sugerido, conforme convenção deste exercício; não é entrega. As sugestões de água são independentes e não podem ser somadas como plano reservado.

## Reprodução

Na raiz do projeto, com Python >=3.13,<3.14: `python simulacoes/escopo_inicial/simular_desastre.py --salvar`. Sem `--salvar`, apenas imprime. Nenhuma dependência externa ou credencial é necessária; somente os artefatos de resultado são escritos.

Os hashes das fontes usadas nesta execução constam no JSON. Alterar os arquivos não atualiza resultados antigos automaticamente; execute novamente. O relatório e o JSON são gerados pelo mesmo código e substituídos ao salvar.

Consulte [o contexto da simulação](../README.md) e [o controle de tarefas](../../../docs/controle-tarefas.md).
