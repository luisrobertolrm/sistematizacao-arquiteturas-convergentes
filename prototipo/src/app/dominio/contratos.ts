/** Contratos exclusivos do protótipo. Não representam DTOs finais da API. */
export type Etapa = 'inicial' | 'futuro';
export type TipoCampo = 'texto' | 'area' | 'numero' | 'data' | 'datahora' | 'opcao' | 'referencia' | 'booleano';
export interface Ponto { x: number; y: number; }
export type ValorCampo = string | boolean | Ponto[];
export interface CamposRegistro { [campo: string]: ValorCampo; }
export interface Registro {
  id: string; inativo: boolean; criado_em: string; atualizado_em: string; campos: CamposRegistro;
}
export interface Opcao { valor: string; nome: string; }
export interface Campo {
  chave: string; nome: string; tipo: TipoCampo; obrigatorio?: boolean;
  tabela?: string; opcoes?: Opcao[]; minimo?: number; dica?: string; padrao?: string | boolean;
}
export interface Relacionamento { tabela: string; campo: string; nome: string; }
export interface Tela {
  chave: string; nome: string; singular: string; grupo: string; etapa: Etapa;
  campos: Campo[]; colunas: string[]; relacoes?: Relacionamento[]; menu?: boolean;
  descricao?: string; somenteLeitura?: boolean;
}
export interface Tabelas { [tabela: string]: Registro[]; }
export interface Evento {
  id: string; instante: string; ator: string; tipo: string; tabela: string; registro: string; texto: string;
}
export interface EstadoPrototipo { versao: 1; tabelas: Tabelas; eventos: Evento[]; ator: string; }
export interface Rota { tela: string; id: string; consulta: URLSearchParams; }
export interface ErroCampo { campo: string; mensagem: string; }
export interface ResultadoSalvamento { registro?: Registro; erros: ErroCampo[]; }
export interface ItemRecomendado {
  item: Registro; pessoas: Registro[]; instituicoes: Registro[]; recursos: Registro[];
}

export function texto(registro: Registro | undefined, campo: string): string {
  const valor = registro?.campos[campo]; return typeof valor === 'string' ? valor : '';
}
export function marcado(registro: Registro | undefined, campo: string): boolean {
  return registro?.campos[campo] === true;
}
export function pontos(registro: Registro | undefined): Ponto[] {
  const valor = registro?.campos['geometria']; return Array.isArray(valor) ? valor : [];
}
export function novaRota(hash: string): Rota {
  const [caminho, consulta = ''] = hash.replace(/^#\/?/, '').split('?');
  const [tela = 'inicio', id = ''] = caminho.split('/').map(decodeURIComponent);
  return { tela: tela || 'inicio', id, consulta: new URLSearchParams(consulta) };
}
