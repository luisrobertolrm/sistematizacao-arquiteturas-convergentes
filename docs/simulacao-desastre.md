# Simulação em memória — avaliação do modelo lógico

**Relatório histórico anterior a D008/D009.** A execução atual, com demandas, recomendações e decisão administrativa, está em [Simulação do escopo inicial](../simulacoes/escopo_inicial/README.md), com [resultado executado](../simulacoes/escopo_inicial/resultados/relatorio.md). As lacunas abaixo preservam o entendimento na data do primeiro exercício.

Conclusão: o cadastro representa o desastre e as capacidades, mas o modelo ainda não fecha o ciclo de atendimento e alocação.

Cenário fictício: inundação e deslizamento; três áreas em dois municípios; três instituições; quatro pessoas; seis demandas; um caminhão, um gerador e 300 litros de água. Janela inicial: 08/10/2026, 09h–11h, UTC−03:00.

Os municípios, pessoas, instituições e códigos territoriais são fictícios. O mesmo polígono ilustrativo foi reutilizado: a simulação não valida geografia ou exibe mapa. As qualificações são exemplos de modelagem, não requisitos reais de atuação.

Foram exercitados 23 cenários: 6 representáveis, 7 verificações de regras e 10 lacunas demonstradas.

| Cenário | Resultado | Evidência |
|---|---|---|
| Ocorrência multifenômeno | ATENDE | Uma operação, dois tipos e exatamente um principal; coordenação institucional vinculada. |
| Sem classificação principal | REGRA EXERCITADA | Entrada inválida rejeitada pelo validador em memória. |
| Duas classificações principais | REGRA EXERCITADA | Entrada inválida rejeitada pelo validador em memória. |
| Tipo repetido | REGRA EXERCITADA | Entrada inválida rejeitada pelo validador em memória. |
| Tipo inexistente | REGRA EXERCITADA | Entrada inválida rejeitada pelo validador em memória. |
| Território | ATENDE | Três áreas em dois municípios fictícios, vinculadas à mesma ocorrência. |
| Geometria e avaliação | LACUNA | É possível guardar uma geometria no contrato simulado; formato físico, validação espacial, limites e histórico de avaliações não estão definidos. Nenhum mapa foi renderizado. |
| Instituições, pessoas e formação | ATENDE | Quatro pessoas vinculadas; formação validada e vigente distingue João de Carlos (vencida) e Marta (pendente). |
| Requisitos da atividade | LACUNA | O filtro de curso foi escolhido manualmente para o cenário. Falta mapear exigências, habilitações e alternativas da atividade; João ainda não pode ser declarado apto para uma missão real. |
| Bens e estoques | ATENDE | Um caminhão, um gerador e estoque de 300 litros, cada recurso com exatamente um responsável. |
| Responsável exclusivo | REGRA EXERCITADA | Recurso com dois responsáveis ou sem responsável é rejeitado pela regra proposta. |
| Atividades e ofertas | ATENDE | Catálogo separado de três ofertas; oferta logística associa o caminhão sem reservá-lo. |
| Registro de necessidades | LACUNA | Seis necessidades são entradas auxiliares do exercício: ainda não há modelo de demanda, itens, prioridade, unidade, período ou atendimento parcial. |
| Conflito de veículo | LACUNA | Duas missões requerem o único caminhão das 09h às 11h. Cadastro atual não registra nem impede dupla reserva. |
| Disponibilidade de pessoas | LACUNA | João é candidato nas duas demandas; faltam agenda, aceite, equipe e alocação por período. |
| Estoque compartilhado | LACUNA | Há 400 litros solicitados e 300 em estoque: déficit de 100. Faltam reservas, movimentações e entrega/atendimento parcial. |
| Sobreposição de capacidades | LACUNA | Somar cozinha (80) e Paula (40) sugere 120 refeições, mas Paula integra a mesma cozinha. Falta composição da oferta/equipe para comprovar capacidade adicional. |
| Compatibilidade técnica | LACUNA | A demanda exige 5 kVA e o gerador descreve 2 kVA. Falta potência estruturada, unidade e requisito; classificar como gerador não comprova atendimento. |
| Cobertura e acesso | LACUNA | A oferta inicial atende a um município; uma demanda é de outro. Faltam cobertura ampliada e condições de acesso/rota, sem inferir segurança pela proximidade. |
| Aprovação e rastreabilidade | LACUNA | Não há modelo de missão, membros, itens alocados, aprovação administrativa, aceite, entrega ou execução para fechar o ciclo. |
| Alteração de conteúdo | REGRA EXERCITADA | Alterar a descrição muda o hash e exclui o embedding antigo; publicação condicionada ao mesmo hash rejeita o resultado antigo. |
| Modelo e dimensão | REGRA EXERCITADA | Vetor de outro modelo, dimensão incorreta e modelo de inferência são rejeitados. Vetores são fixtures artificiais; não foi avaliada relevância semântica. |
| Encerramento e histórico | ATENDE | Encerramento mantém ocorrência, classificações e áreas; regras para pendências e reabertura ainda precisam de definição. |

## Alcance da verificação

Execução Python 3.13 com biblioteca padrão, dataclasses tipadas e dados somente em memória. As classes são recortes para o exercício, não implementação do backend. Demandas e seus períodos são entradas auxiliares, sem promover campos novos a decisões aprovadas. Não há PostgreSQL, Alembic, restrições SQL, transações concorrentes, criptografia, frontend, LLM ou embeddings reais sendo testados.

Os validadores em memória exercitam regras documentadas. Seu sucesso não comprova que um banco ainda não implementado rejeitaria os mesmos casos. O exercício de hash verifica consistência lógica, sem simular corrida entre processos nem fixar a serialização final. Não houve medição de redução de tempo ou validação de qualidade de RAG.

As verificações de embedding usam apenas o catálogo de atividades com vetores artificiais. Não foram exercitadas cobertura dos quatro catálogos, troca transacional do modelo ativo, classificação por profissão, aprovação de missões ou reserva concorrente. As lacunas são achados do modelo, não falhas de testes de uma aplicação implementada.

## Próxima discussão sugerida

Definir demanda e itens solicitados, depois requisitos e qualificações, disponibilidade/equipes, composição das ofertas, missões/alocações, reservas/movimentos e entrega/atendimento parcial. Esses pontos são achados da simulação, não novas decisões aprovadas.

Reprodução: `python simulacoes/simular_desastre.py`, usando Python 3.13. Nenhum dado é persistido pelo script.
