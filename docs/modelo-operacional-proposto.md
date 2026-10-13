# Modelo operacional proposto

**Estado: inventário do modelo operacional.** O grupo de recomendações integra a primeira entrega (D009). Requisitos avançados, disponibilidade, missões, reservas, atendimentos e estoque ficam registrados como sugestões para evolução futura, com contratos ainda em discussão.

Demandas, itens e unidades de medida estão aprovados em D008 e implementados em D016. Recomendações estão implementadas em D017. O [escopo inicial](escopo-inicial.md) define a primeira entrega; este documento preserva as tabelas restantes para execução e resolução dos conflitos da [simulação](simulacao-desastre.md). Requisitos avançados, disponibilidade, missões, reservas, atendimentos e movimentações ainda não têm implementação/migração.

Os campos listados são um recorte para discussão, com tipos explícitos. Identificadores e auditoria seguem o padrão comum do projeto. Enums, índices, estados finais e regras de integridade serão detalhados após concordância sobre as responsabilidades.

## 1. Requisitos e características técnicas

### Qualificações exigidas

Proposta de tabelas específicas:

- `atividade_requisito_profissao`: `id_atividade: UUID`, `id_profissao: UUID`, `quantidade_minima_pessoas: int`.
- `atividade_requisito_curso`: `id_atividade: UUID`, `id_curso: UUID`, `quantidade_minima_pessoas: int`.
- `demanda_item_requisito_profissao`: `id_demanda_item: UUID`, `id_profissao: UUID`, `quantidade_minima_pessoas: int`.
- `demanda_item_requisito_curso`: `id_demanda_item: UUID`, `id_curso: UUID`, `quantidade_minima_pessoas: int`.

Os requisitos da atividade estabelecem condições gerais; os do item acrescentam exigências do atendimento concreto. Exigências locais não devem enfraquecer requisitos obrigatórios da atividade. Exemplo: um profissional habilitado e duas pessoas com treinamento específico.

Pendências: grupos alternativos de requisitos (“A ou B”), combinação “A e B na mesma pessoa” versus pessoas distintas, habilitações/registros profissionais e validade na data da missão. A estrutura acima não resolve essas combinações sozinha. Recuperação semântica de profissão/curso não concede equivalência para satisfazer requisitos.

### Recursos compatíveis

Proposta:

- `caracteristicas_recurso`: catálogo com `codigo: str`, `nome: str`, `tipo_valor: TipoValorCaracteristica`, `id_unidade_medida: UUID | None`.
- `tipo_recurso_caracteristica`: associação `id_tipo_recurso: UUID`, `id_caracteristica: UUID`, `obrigatoria: bool`.
- `recurso_caracteristica`: `id_recurso: UUID`, `id_caracteristica: UUID`, `valor_numerico: Decimal | None`, `valor_texto: str | None`, `valor_booleano: bool | None`.
- `demanda_item_requisito_recurso`: `id_demanda_item: UUID`, `id_caracteristica: UUID`, `operador: OperadorComparacao`, valores tipados compatíveis com a característica.

Exatamente um valor compatível com o tipo declarado; associação recurso/característica única. Operadores permitidos dependem do tipo de valor. Não guardar as exigências em `dict` genérico nem depender apenas de texto livre. A unidade pertence à definição da característica, com conversões explícitas quando necessárias.

Exemplo: potência de 2 kVA não atende a requisito mínimo de 5 kVA. O tipo “gerador” identifica candidatos, mas não prova compatibilidade. A aplicabilidade de cada característica ao tipo solicitado precisa ser validada.

## 2. Composição das ofertas e disponibilidade

- `oferta_atividade_pessoa`: `id_oferta_atividade: UUID`, `id_pessoa: UUID`, `papel: str`. Identifica quem compõe a capacidade institucional. Não basta inferir que todo membro da instituição participa de toda oferta.
- `disponibilidades_pessoa`: `id_pessoa: UUID`, `inicio_em: datetime`, `fim_em: datetime`, `situacao: SituacaoDisponibilidade`.
- `disponibilidades_oferta`: `id_oferta_atividade: UUID`, `inicio_em: datetime`, `fim_em: datetime`, `capacidade_declarada: Decimal`.

Disponibilidade declarada não é reserva nem aceite de missão. Uma oferta institucional e uma oferta pessoal podem depender da mesma pessoa, veículo ou infraestrutura; não somar capacidades sem verificar composição e dependências compartilhadas.

O período-base da capacidade precisa ser explícito. A capacidade de 80 refeições/dia não equivale automaticamente a 80 refeições em duas horas. Definir a relação entre capacidade geral da oferta, capacidade por janela e possíveis gargalos compartilhados, sem manter saldos independentes contraditórios.

## 3. Recomendações rastreáveis

**Primeira entrega implementada:** registrar sugestões por IA e decisão administrativa, conforme [D017 e contratos](ia-demandas-recomendacoes.md). Campos abaixo atualizados para o incremento 6:

- `recomendacoes`: `id_demanda: UUID`, `id_modelo_embedding: UUID`, `id_modelo_inferencia: UUID`, `hash_contexto: str`, `gerada_em: datetime`, `justificativa: str`, `pendencias: list[str]`, `situacao: SituacaoRecomendacao` e campos da decisão abaixo.
- `recomendacao_itens`: `id_recomendacao: UUID`, `id_demanda_item: UUID`, `quantidade_sugerida: Decimal`, `justificativa: str`.
- `recomendacao_pessoas`: `id_recomendacao_item: UUID`, `id_pessoa: UUID`, `id_oferta_atividade: UUID`, `papel_sugerido: str`.
- `recomendacao_instituicoes`: `id_recomendacao_item: UUID`, `id_instituicao: UUID`, `id_oferta_atividade: UUID`. Associar a instituição à oferta que fundamenta a sugestão e validar esse vínculo.
- `recomendacao_recursos`: `id_recomendacao_item: UUID`, `id_recurso: UUID`, `quantidade_sugerida: Decimal`.

Registrar IDs reais dos candidatos e justificativa, modelos, hash do contexto, data e pendências (`list[str]` em JSONB). A justificativa é resultado da análise. Guardar hash/referências, sem cópia integral imutável das entradas; nomes exibidos vêm dos cadastros relacionados. Contexto é revalidado antes de publicação/aprovação.

Recomendação não reserva nem movimenta recursos. Aprovação/rejeição exige justificativa e registra `decidida_em`, `decidida_por` (sujeito JWT) e `justificativa_decisao`, sem criar missão ou alterar pedido/estoque. Estados implementados: `gerada`, `aprovada`, `rejeitada`. A decisão é única/final; nova análise não marca automaticamente a anterior como substituída. Cadastro de usuários de produção permanece pendente.

Nova análise gera nova recomendação, preservando as anteriores. Uma recomendação pode apontar quantidade sugerida inferior ao pedido ou ausência de candidatos; isso não é atendimento parcial executado. O sistema não deve inventar capacidade para preencher a demanda nem garantir disponibilidade por horário sem agenda/reservas. Na evolução operacional, aprovação para criar missão precisará revalidar elegibilidade, quantidade e disponibilidade atuais.

## 4. Missões e alocações

- `missoes`: `id_desastre: UUID`, `id_instituicao_responsavel: UUID`, `id_pessoa_responsavel: UUID`, `inicio_previsto_em: datetime`, `fim_previsto_em: datetime`, `situacao: SituacaoMissao`.
- `missao_itens`: `id_missao: UUID`, `id_demanda_item: UUID`, `quantidade_planejada: Decimal`.
- `alocacoes_pessoa`: `id_missao: UUID`, `id_pessoa: UUID`, `inicio_em: datetime`, `fim_em: datetime`, `papel: str`, `situacao: SituacaoAlocacao`.
- `reservas_recurso`: `id_missao: UUID`, `id_recurso: UUID`, `quantidade_reservada: Decimal`, `inicio_em: datetime`, `fim_em: datetime`, `situacao: SituacaoReserva`.

Uma missão pode atender vários itens, inclusive de demandas diferentes, desde que pertençam ao mesmo desastre. Um item pode ser atendido por várias missões. Pessoas e recursos podem participar de operações distintas em horários diferentes, mas conflitos devem ser verificados globalmente, inclusive entre desastres.

Alocações de pessoas impedem sobreposição incompatível entre missões. Bens individuais impedem dupla reserva no mesmo intervalo. Estoques precisam de reserva quantitativa: sua disponibilidade depende do saldo e dos compromissos ainda não consumidos, não apenas do horário de uma missão.

Revalidar e reservar dentro de operação transacional. Uma consulta prévia de disponibilidade, isolada, não impede duas aprovações simultâneas. Aceite da pessoa, aprovação administrativa, início real, cancelamento e liberação devem ter estados e auditoria próprios a detalhar. Não criar inicialmente um cadastro permanente de equipes; os participantes da missão podem ser obtidos pelas alocações. Equipes reutilizáveis ficam para uma necessidade posterior.

## 5. Atendimento efetivo e estoque

- `atendimentos`: `id_missao: UUID`, `registrado_em: datetime`, `id_pessoa_responsavel: UUID`, `situacao: SituacaoAtendimento`.
- `atendimento_itens`: `id_atendimento: UUID`, `id_missao_item: UUID`, `quantidade_realizada: Decimal`, `realizado_em: datetime`, `chave_idempotencia: str`.
- `movimentacoes_recurso`: `id_recurso: UUID`, `tipo: TipoMovimentacao`, `quantidade: Decimal`, `ocorrido_em: datetime`, `id_atendimento_item: UUID | None`, `id_reserva_recurso: UUID | None`.

Atendimentos registram o que foi efetivamente entregue/executado. O item precisa pertencer à missão e a quantidade usar a unidade do item de demanda; prazo, duplicidades e limites do saldo serão validados. A chave de idempotência precisa de escopo/unicidade definidos para impedir que um reenvio conte a mesma entrega duas vezes.

Somente atendimento confirmado reduz saldo da demanda. Correções/estornos preservam o histórico e devem ser representados explicitamente; não basta editar ou excluir uma entrega já contabilizada. A forma de vincular correções ao lançamento original ainda será escolhida.

Para consumíveis, confirmar entrega deve registrar a saída do estoque e consumir/liberar a reserva correspondente na mesma transação, evitando descontar a mesma quantidade duas vezes. Devoluções e reposições também precisam de movimentos. Para bens reutilizáveis, uso e devolução não significam consumo físico de uma unidade do patrimônio.

O modelo atual tem `recursos.quantidade_total`. Antes de implementar movimentos, decidir se ele será um saldo materializado mantido transacionalmente ou um valor calculado do histórico. Não manter contador e histórico como fontes independentes nem somar saldo inicial duas vezes. As reservas também não podem reduzir estoque físico antes da entrega e voltar a reduzi-lo na confirmação.

## Inventário das tabelas restantes para evolução futura

O registro abaixo preserva o planejamento; não obriga implementação na primeira entrega nem aprova automaticamente os contratos propostos.

| Grupo futuro | Tabelas |
|---|---|
| Requisitos de qualificação | `atividade_requisito_profissao`, `atividade_requisito_curso`, `demanda_item_requisito_profissao`, `demanda_item_requisito_curso` |
| Compatibilidade técnica | `caracteristicas_recurso`, `tipo_recurso_caracteristica`, `recurso_caracteristica`, `demanda_item_requisito_recurso` |
| Composição de ofertas | `oferta_atividade_pessoa` |
| Disponibilidade | `disponibilidades_pessoa`, `disponibilidades_oferta` |
| Execução | `missoes`, `missao_itens`, `alocacoes_pessoa`, `reservas_recurso` |
| Atendimento e estoque | `atendimentos`, `atendimento_itens`, `movimentacoes_recurso` |
| Recuperação semântica ampliada | `profissao_indice_semantico`, `curso_indice_semantico`, `tipo_recurso_indice_semantico` — previstas em D006, implementação adiada por D009 |

Usuários/perfis administrativos, histórico de avaliações de área, cobertura territorial de ofertas, rotas e equipes permanentes ainda não têm tabelas finais definidas. Não introduzir nomes ou contratos como se já estivessem aprovados.

## Exemplo de fluxo futuro completo

1. Área solicita 200 litros de água e uma atividade de transporte.
2. A recomendação sugere pessoas e recursos verificados, com atendimento parcial quando necessário.
3. O administrador aprova uma missão que planeja entregar 100 litros; sistema reserva estoque, veículo e participantes.
4. A entrega confirmada registra 100 litros no atendimento, movimenta o estoque e ajusta a reserva.
5. O item continua com 100 litros pendentes. Cancelar a missão depois da entrega não apaga o atendimento já realizado.

## Ordem sugerida de discussão da evolução futura

1. Requisitos de qualificação e características técnicas.
2. Composição das ofertas, capacidade por período e disponibilidade.
3. Missões, alocações e reservas com controle de concorrência.
4. Atendimentos, estoque, correções e conclusão parcial.
5. Recomendações e evidências da IA, usando as regras operacionais já definidas.

Após consolidar essas decisões futuras, atualizar a simulação em memória com os mesmos conflitos e verificar se o desenho passa a representar o atendimento completo. Para a primeira entrega, seguir D009 e o escopo de apoio à decisão, sem exigir missões/reservas/entregas.
