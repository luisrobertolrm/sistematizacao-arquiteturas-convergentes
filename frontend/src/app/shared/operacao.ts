export interface Auditoria { id: string; criado_em: string; atualizado_em: string; inativado_em: string | null; }
export interface ConexaoInput { nome: string; provedor: 'openai_compativel'; url_base: string; tipo_autenticacao: 'bearer' | 'nenhuma'; token: string | null; }
export interface ConexaoVM extends Auditoria { nome: string; provedor: string; url_base: string; tipo_autenticacao: 'bearer' | 'nenhuma'; tem_token: boolean; identificador_chave: string | null; }
export type Finalidade = 'embedding' | 'inferencia_texto';
export interface ModeloInput { id_conexao: string; identificador_modelo: string; revisao: string | null; finalidade: Finalidade; dimensao: number | null; ativo: boolean; }
export interface ModeloVM extends ModeloInput, Auditoria { conexao_nome: string; conexao_inativa: boolean; }
export interface IndiceVM extends Auditoria { id_atividade: string; id_modelo: string; hash_atividade_origem: string; situacao_indexacao: 'pendente' | 'pronta'; indexado_em: string | null; atualizado: boolean; atividade_nome: string; }
export interface BuscaVM { id_modelo: string; resultados: { id_atividade: string; nome: string; similaridade: number; }[]; }
export type Prioridade = 'baixa' | 'normal' | 'alta' | 'urgente';
export type SituacaoDemanda = 'aberta' | 'em_atendimento' | 'concluida' | 'cancelada';
export interface DemandaItemInput { id: string | null; id_atividade: string | null; id_tipo_recurso: string | null; id_unidade_medida: string; quantidade_solicitada: string; observacoes: string | null; }
export interface DemandaInput { id_area_afetada: string; id_pessoa_solicitante: string; titulo: string; descricao: string; prioridade: Prioridade; inicio_previsto_em: string; prazo_em: string; situacao: SituacaoDemanda; itens: DemandaItemInput[]; }
export interface DemandaItemVM extends Auditoria { id_demanda: string; id_atividade: string | null; id_tipo_recurso: string | null; id_unidade_medida: string; quantidade_solicitada: string; observacoes: string | null; necessidade_nome: string; unidade_simbolo: string; }
export interface DemandaVM extends Omit<DemandaInput, 'itens'>, Auditoria { area_nome: string; solicitante_nome: string; itens: DemandaItemVM[]; }
export interface PessoaSugerida { id_pessoa: string; id_oferta_atividade: string; papel_sugerido: string; }
export interface InstituicaoSugerida { id_instituicao: string; id_oferta_atividade: string; }
export interface RecursoSugerido { id_recurso: string; quantidade_sugerida: string; }
export interface RecomendacaoItemVM { id: string; id_demanda_item: string; quantidade_sugerida: string; justificativa: string; pessoas: PessoaSugerida[]; instituicoes: InstituicaoSugerida[]; recursos: RecursoSugerido[]; }
export interface RecomendacaoVM extends Auditoria { id_demanda: string; id_modelo_embedding: string; id_modelo_inferencia: string; hash_contexto: string; gerada_em: string; justificativa: string; pendencias: string[]; situacao: 'gerada' | 'aprovada' | 'rejeitada'; decidida_em: string | null; decidida_por: string | null; justificativa_decisao: string | null; itens: RecomendacaoItemVM[]; nomes_candidatos: Record<string, string>; }
export interface OpcaoOperacao { id: string; nome?: string; titulo?: string; identificador_modelo?: string; }
