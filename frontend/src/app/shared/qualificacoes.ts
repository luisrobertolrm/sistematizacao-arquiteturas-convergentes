import { SituacaoCadastral } from './contratos';

export type TipoCurso = 'tecnico' | 'capacitacao' | 'treinamento';
export type TipoVinculo = 'voluntario' | 'funcionario' | 'associado' | 'representante';
export type TipoReferencia = 'instituicoes' | 'profissoes' | 'cursos';
export type TipoCatalogo = 'profissoes' | 'cursos';
export interface ReferenciaVM { id: string; nome: string; }
export interface AuditoriaVM {
  id: string; criado_em: string; atualizado_em: string; inativado_em: string | null;
}
export interface CatalogoInput { nome: string; descricao: string | null; }
export interface ProfissaoInput extends CatalogoInput { codigo_cbo: string | null; }
export interface CursoInput extends CatalogoInput { tipo: TipoCurso; }
export interface ProfissaoVM extends ProfissaoInput, AuditoriaVM { hash_conteudo_semantico: string; }
export interface CursoVM extends CursoInput, AuditoriaVM { hash_conteudo_semantico: string; }
export interface VinculoInput { situacao_validacao: SituacaoCadastral; }
export interface PessoaInstituicaoInput extends VinculoInput {
  instituicao_id: string; tipo_vinculo: TipoVinculo; inicio_em: string; fim_em: string | null;
}
export interface PessoaProfissaoInput extends VinculoInput {
  profissao_id: string; registro_profissional: string | null; orgao_registro: string | null;
  uf_registro: string | null; validade_em: string | null;
}
export interface PessoaCursoInput extends VinculoInput {
  curso_id: string; instituicao_emissora: string; conclusao_em: string;
  validade_em: string | null; carga_horaria: string | null; comprovante_referencia: string | null;
}
export interface VinculoVM extends AuditoriaVM { pessoa_id: string; referencia_nome: string; }
export interface PessoaInstituicaoVM extends PessoaInstituicaoInput, VinculoVM {}
export interface PessoaProfissaoVM extends PessoaProfissaoInput, VinculoVM {}
export interface PessoaCursoVM extends PessoaCursoInput, VinculoVM {}
export interface CatalogosPorTipo { profissoes: ProfissaoVM; cursos: CursoVM; }
export interface CatalogosEntradaPorTipo { profissoes: ProfissaoInput; cursos: CursoInput; }
export interface VinculosPorTipo {
  instituicoes: PessoaInstituicaoVM; profissoes: PessoaProfissaoVM; cursos: PessoaCursoVM;
}
export interface VinculosEntradaPorTipo {
  instituicoes: PessoaInstituicaoInput; profissoes: PessoaProfissaoInput; cursos: PessoaCursoInput;
}
export type QualificacaoVM = PessoaInstituicaoVM | PessoaProfissaoVM | PessoaCursoVM;
