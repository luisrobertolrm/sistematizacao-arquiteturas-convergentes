import { SituacaoCadastral } from './contratos';
import { AuditoriaVM } from './qualificacoes';

export type CategoriaRecurso = 'veiculo' | 'equipamento' | 'material' | 'insumo';
export type ModoControle = 'individual' | 'estoque';
export type EstadoRecurso = 'operacional' | 'em_manutencao' | 'indisponivel';
export type TipoCadastroRecurso = 'tipos-recurso' | 'recursos' | 'ofertas-atividade';
export type ReferenciaRecurso = 'unidades-medida' | 'tipos-recurso' | 'atividades' | 'instituicoes' | 'pessoas' | 'recursos' | 'tipos-desastre';
export interface TipoRecursoInput {
  nome: string; descricao: string | null; categoria: CategoriaRecurso;
  id_unidade_medida: string; modo_controle: ModoControle;
}
export interface UnidadeRecursoVM { unidade_nome: string; unidade_simbolo: string; unidade_inativa: boolean; }
export interface TipoRecursoVM extends TipoRecursoInput, AuditoriaVM, UnidadeRecursoVM { hash_conteudo_semantico: string; }
export interface ResponsavelInput { instituicao_id: string | null; pessoa_id: string | null; }
export interface ResponsavelVM { responsavel_nome: string; responsavel_inativo: boolean; }
export interface RecursoInput extends ResponsavelInput {
  tipo_recurso_id: string; nome: string; descricao: string | null; identificacao: string | null;
  quantidade_total: string; estado_operacional: EstadoRecurso; municipio_codigo_ibge: string;
  latitude: string | null; longitude: string | null;
}
export interface RecursoVM extends RecursoInput, AuditoriaVM, UnidadeRecursoVM, ResponsavelVM {
  tipo_recurso_nome: string; tipo_recurso_inativo: boolean; modo_controle: ModoControle;
}
export interface OfertaAtividadeInput extends ResponsavelInput {
  atividade_id: string; municipio_atendimento_codigo_ibge: string; descricao_complementar: string | null;
  capacidade_declarada: string | null; situacao_validacao: SituacaoCadastral;
}
export interface OfertaAtividadeVM extends OfertaAtividadeInput, AuditoriaVM, ResponsavelVM {
  atividade_nome: string; atividade_inativa: boolean; unidade_nome: string | null;
  unidade_inativa: boolean; validado_em: string | null;
}
export interface OfertaRecursoInput { recurso_id: string; quantidade_prevista: string; }
export interface OfertaRecursoVM extends OfertaRecursoInput, AuditoriaVM {
  oferta_atividade_id: string; recurso_nome: string; recurso_inativo: boolean; recurso_estado: EstadoRecurso;
  recurso_responsavel_nome: string; unidade_simbolo: string;
}
export interface RecursoVMMap { 'tipos-recurso': TipoRecursoVM; 'recursos': RecursoVM; 'ofertas-atividade': OfertaAtividadeVM; }
export interface RecursoInputMap { 'tipos-recurso': TipoRecursoInput; 'recursos': RecursoInput; 'ofertas-atividade': OfertaAtividadeInput; }
export type CadastroRecursoVM = TipoRecursoVM | RecursoVM | OfertaAtividadeVM;
