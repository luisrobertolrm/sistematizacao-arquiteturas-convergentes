export type SituacaoCadastral = 'pendente' | 'validada' | 'rejeitada';
export type TipoInstituicao = 'orgao_publico' | 'empresa' | 'ong' | 'associacao';
export interface Mensagem { severity: 'success' | 'info' | 'warning' | 'error'; code: string; text: string; }
export interface ApiResponse<T> { data: T; messages?: Mensagem[]; }
export interface Problema { type: string; title: string; status: number; detail: string; instance: string; }
export interface ContatoInput {
  nome: string; municipio_codigo_ibge: string; uf: string;
  email_contato: string | null; telefone_contato: string | null;
  latitude: string | null; longitude: string | null; situacao_cadastral: SituacaoCadastral;
}
export interface InstituicaoInput extends ContatoInput {
  tipo: TipoInstituicao; razao_social: string | null; cnpj: string | null; descricao: string | null;
}
export interface CadastroVM extends ContatoInput {
  id: string; criado_em: string; atualizado_em: string; inativado_em: string | null;
}
export interface InstituicaoVM extends CadastroVM, InstituicaoInput {}
export interface PessoaVM extends CadastroVM {}
export interface TokenAdminVM { token: string; expira_em_minutos: number; }
export interface CadastroPublicoPessoaInput {
  nome: string; municipio_codigo_ibge: string; uf: string;
  email_contato: string; telefone_contato: string | null;
  latitude: string | null; longitude: string | null;
}
export interface VerificacaoEmailInput { email_contato: string; }

