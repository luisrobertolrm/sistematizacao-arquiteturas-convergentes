import { AuditoriaVM } from './qualificacoes';

export type TipoCapacidade = 'unidades-medida' | 'categorias-atividade' | 'atividades';
export type TipoReferenciaCapacidade = 'unidades-medida' | 'categorias-atividade';
export interface CatalogoCodigoInput { codigo: string; nome: string; }
export interface UnidadeMedidaInput extends CatalogoCodigoInput { simbolo: string; }
export interface CategoriaAtividadeInput extends CatalogoCodigoInput { descricao: string | null; }
export interface AtividadeInput extends CatalogoCodigoInput {
  descricao: string; categoria_id: string; id_unidade_capacidade: string | null;
  orientacoes: string | null; restricoes: string | null;
}
export interface UnidadeMedidaVM extends UnidadeMedidaInput, AuditoriaVM {}
export interface CategoriaAtividadeVM extends CategoriaAtividadeInput, AuditoriaVM {}
export interface AtividadeVM extends AtividadeInput, AuditoriaVM {
  hash_conteudo_semantico: string; categoria_nome: string; categoria_inativa: boolean;
  unidade_nome: string | null; unidade_inativa: boolean;
}
export interface AtividadeTermoInput { termo: string; }
export interface AtividadeTermoVM extends AtividadeTermoInput, AuditoriaVM { atividade_id: string; }
export interface CapacidadesPorTipo {
  'unidades-medida': UnidadeMedidaVM; 'categorias-atividade': CategoriaAtividadeVM; atividades: AtividadeVM;
}
export interface CapacidadesEntradaPorTipo {
  'unidades-medida': UnidadeMedidaInput; 'categorias-atividade': CategoriaAtividadeInput; atividades: AtividadeInput;
}
export type CapacidadeVM = UnidadeMedidaVM | CategoriaAtividadeVM | AtividadeVM;
