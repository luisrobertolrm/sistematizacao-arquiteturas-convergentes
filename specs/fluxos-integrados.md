# Fluxos integrados e destinos de tela

Os IDs abaixo apontam para as specs no [índice](indice.md). Navegação ocorre na mesma URL; títulos, componente e aba comprovam o destino. Mudanças de rascunho não persistem até a ação de gravação indicada.

## FLX-01 — Pessoa e formação

| Passo | Ação | Destino / resultado observável |
|---|---|---|
| 1 | NAV → Pessoas | PES, lista/editor de pessoas |
| 2 | Cadastrar pessoa com nome exclusivo | Cadastro salvo.; registro persistido |
| 3 | No cartão correto, Vínculos e formação | VIN-INS, h2 com nome da pessoa, aba Instituições |
| 4 | Selecionar instituição; preencher início/tipo; Salvar vínculo | Vínculo salvo.; cartão da instituição |
| 5 | Aba Profissões; escolher profissão; Salvar vínculo | VIN-PRO; cartão da profissão/registro |
| 6 | Aba Cursos; escolher curso; informar emissor/conclusão; Salvar vínculo | VIN-CUR; cartão com conclusão/validade |
| 7 | Voltar às pessoas | PES, lista anterior novamente visível |

Critério final: ao reabrir a mesma pessoa e cada aba, vínculos persistidos aparecem; validação é administrativa. Não há navegação automática da escolha de curso para um cadastro de arquivos/comprovantes.

## FLX-02 — Atividade, termo e busca textual

| Passo | Ação | Destino / resultado |
|---|---|---|
| 1 | NAV → Atividades e unidades | UNI, aba inicial Unidades de medida |
| 2 | Cadastrar unidade, depois categoria | UNI/CAT; cadastros persistidos |
| 3 | Aba Atividades; cadastrar serviço com categoria/unidade | ATV; Cadastro salvo. |
| 4 | No cartão: Termos e sinônimos | TRM, título da atividade correta |
| 5 | Salvar termo único | Termo salvo.; lista/hash atualizados |
| 6 | Voltar às atividades | ATV reconsultada |
| 7 | Buscar pelo termo ativo | Atividade encontrada |

Critério final: código readonly ao editar; texto/termos estão na origem, sem descrição duplicada no índice. Busca textual não exige modelo de IA. Indexação semântica posterior é FLX-05.

## FLX-03 — Recurso e oferta

| Passo | Ação | Destino / resultado |
|---|---|---|
| 1 | NAV → Recursos e ofertas | TIR, aba inicial Tipos de recurso |
| 2 | Criar tipo com unidade/modo | TIR, tipo persistido |
| 3 | Aba Recursos; criar bem/estoque com responsável | REC, Cadastro salvo. |
| 4 | Aba Ofertas de atividades; cadastrar oferta validada | OFE, cartão da atividade/responsável |
| 5 | Recursos da oferta no cartão correto | OFR, h2 com atividade e responsável |
| 6 | Escolher recurso e quantidade; Salvar vínculo | Vínculo salvo. |
| 7 | Voltar às ofertas | OFE reconsultada |

Critério final: referência principal bloqueada na edição; duplicidade de vínculo recusada; quantidade prevista não debita estoque. Testar individual com quantidade 2 deve produzir recusa, não um cadastro de dois bens.

## FLX-04 — Ocorrência e território

| Passo | Ação | Destino / resultado |
|---|---|---|
| 1 | NAV → Desastres e áreas | OCO, aba inicial Ocorrências |
| 2 | Tipos de desastre; criar tipos necessários | TDE |
| 3 | Ocorrências; preencher coordenadora e adicionar classificações | OCO; rascunho com exatamente uma principal |
| 4 | Salvar desastre | Ocorrência salva.; lista com tipos/principal |
| 5 | Áreas e mapa no cartão | ARE + MAP, título da ocorrência |
| 6 | Preencher área; desenhar/concluir triângulo | MAP fornece geometria; ainda sem gravação |
| 7 | Salvar área | Área salva.; polígono/lista carregados do banco |
| 8 | Editar somente nome/descrição e salvar | Data de avaliação preservada |
| 9 | Confirmar avaliação atual e aceitar diálogo | Avaliação confirmada.; nova data |
| 10 | Voltar às ocorrências | OCO reconsultada |

Critério final: a mesma área poderá ser selecionada na demanda. Ver delimitação apenas muda a geometria selecionada, sem carregar campos do editor; Editar área faz a edição completa. Conferir timestamp exato pela API quando o formato visível arredondar segundos.

## FLX-05 — Configurar IA, indexar e buscar

| Passo | Ação | Destino / resultado |
|---|---|---|
| 1 | NAV → Configuração de IA | CON, aba inicial Conexões de IA |
| 2 | Criar conexão com endpoint do cenário | Conexão salva.; credencial protegida ou sem autenticação |
| 3 | Modelos de IA; criar embedding não selecionado | MOD, dimensão correta |
| 4 | Criar modelo de inferência selecionado | MOD, finalidade inferencia_texto Selecionado |
| 5 | Preparar índices no cartão do embedding | IND, modelo preselecionado, nenhuma geração automática |
| 6 | Adicionar atividades ao lote e Indexar lote | Índices prontos/atuais; repetir para cobertura integral |
| 7 | Modelos de IA → Editar seleção → marcar selecionado → Salvar modelo | Embedding Selecionado após cobertura |
| 8 | Índices de atividades → Necessidade → Buscar por significado | BUS, modelo utilizado e resultados |

Critério final: busca usa o modelo selecionado por finalidade, independente do seletor de preparação do lote. Alterar a atividade/termo invalida seu índice e impede busca com cobertura desatualizada até regeneração. Trocar de aba não esvazia automaticamente o lote.

## FLX-06 — Demanda, análise e decisão

| Passo | Ação | Destino / resultado |
|---|---|---|
| 1 | NAV → Demandas e recomendações | DEM, lista/editor |
| 2 | Selecionar área/solicitante; preencher janela/prioridade | Cabeçalho local válido |
| 3 | Configurar primeiro item; Adicionar item e configurar outro | Rascunho com necessidade/unidade/quantidade de cada item |
| 4 | Salvar demanda | Demanda salva.; agregado persistido |
| 5 | Recomendações e decisões no cartão | RCO, título com a demanda e histórico |
| 6 | Gerar recomendação por IA | Nova recomendação selecionada; itens/candidatos/pendências |
| 7 | Preencher justificativa; Aprovar sugestão; aceitar confirm | Aprovada, autor/data/justificativa; histórico atualizado |
| 8 | Gerar outra análise; justificar/rejeitar | Nova rejeitada; aprovada anterior continua no histórico |
| 9 | Ver recomendação no cartão aprovado anterior | Detalhe da análise histórica, sem botões de nova decisão |
| 10 | Voltar às demandas | DEM reconsultada; quantidades/situação do pedido sem atendimento automático |

Critério final: duas análises e decisões distintas; estoque e pedido não são consumidos/reservados. Uma sugestão de serviço pode apresentar quantidade zero com candidatos; isso é limite declarado do negócio inicial, não necessariamente falha de geração.

## FLX-07 — Inativação e consulta histórica

Criar entidades próprias do cenário; testar cada diálogo primeiro com cancelamento e depois com aceitação. Aceitar deve produzir mensagem da operação e retirar o registro da lista ativa. Marcar histórico apenas nas telas que oferecem esse controle.

Atividade inativada → Termos e sinônimos: histórico forçado, sem criação/edição de termos. Oferta inativada → Recursos da oferta: histórico forçado, formulário bloqueado, vínculo ativo ainda pode ser inativado. Ocorrência inativada → Áreas e mapa: formulário/desenho bloqueados, consulta e inativação de áreas ativas continuam disponíveis. Demanda cancelada/inativada → Recomendações: histórico consultável, geração bloqueada.

Listas de Instituições, Pessoas, Profissões e Cursos não oferecem histórico próprio. Histórico de vínculos da pessoa é outra consulta; não criar expectativas de um botão de reativação.

## FLX-08 — Navegação móvel e sessão

Viewport 390 px → acessar → focar Menu → Espaço → conferir `aria-expanded=true` → escolher módulo → conferir contexto/aba e `aria-expanded=false` → repetir para os oito módulos → Sair → acesso administrativo. Recarregar navegador também exige novo token.

Critério final: ações alcançáveis com os controles reais, sem rolagem horizontal da página ou uso de `force` para controles invisíveis/bloqueados. Capturar menu aberto e contexto de destino; não usar screenshot sozinho como prova de persistência.
