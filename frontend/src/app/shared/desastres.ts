import { AuditoriaVM } from './qualificacoes';

export type SituacaoDesastre = 'em_monitoramento' | 'em_resposta' | 'em_recuperacao' | 'encerrado';
export type GravidadeArea = 'baixa' | 'moderada' | 'alta' | 'critica';
export type SituacaoArea = 'em_avaliacao' | 'em_resposta' | 'em_recuperacao' | 'encerrada';
export type Posicao = [number, number];
export interface GeometriaArea { type: 'Polygon'; coordinates: Posicao[][]; }
export interface TipoDesastreInput { codigo: string; nome: string; descricao: string; }
export interface TipoDesastreVM extends TipoDesastreInput, AuditoriaVM {}
export interface ClassificacaoInput { id_tipo_desastre: string; principal: boolean; }
export interface DesastreTipoVM extends ClassificacaoInput, AuditoriaVM { id_desastre: string; tipo_nome: string; tipo_inativo: boolean; }
export interface DesastreInput {
  titulo: string; descricao: string; inicio_em: string; encerramento_em: string | null;
  situacao: SituacaoDesastre; id_instituicao_coordenadora: string; classificacoes: ClassificacaoInput[];
}
export interface DesastreVM extends Omit<DesastreInput, 'classificacoes'>, AuditoriaVM {
  coordenadora_nome: string; coordenadora_inativa: boolean; classificacoes: DesastreTipoVM[];
}
export interface AvaliacaoAreaInput { gravidade: GravidadeArea; situacao: SituacaoArea; }
export interface AreaAfetadaInput extends AvaliacaoAreaInput { nome: string; descricao: string; municipio_codigo_ibge: string; geometria: GeometriaArea; }
export interface AreaAfetadaVM extends AreaAfetadaInput, AuditoriaVM { id_desastre: string; ultima_avaliacao_em: string; }
export interface ClassificacaoRascunho extends ClassificacaoInput { tipo_nome: string; tipo_inativo: boolean; }
