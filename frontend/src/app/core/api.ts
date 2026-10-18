import { HttpClient, HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  ApiResponse,
  CadastroPublicoPessoaInput,
  CadastroVM,
  ContatoInput,
  InstituicaoInput,
  InstituicaoVM,
  PessoaVM,
  TokenAdminVM,
  VerificacaoEmailInput,
} from '../shared/contratos';

@Injectable({ providedIn: 'root' })
export class Sessao {
  readonly token = signal('');
  readonly apiPort = environment.apiPort;
  readonly apiUrl = environment.apiUrl;
  desconectar(): void { this.token.set(''); }
}


export const autenticacaoInterceptor: HttpInterceptorFn = (req, next) => {
  const token = inject(Sessao).token();
  return next(token && req.url.startsWith('/api/')
    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }) : req);
};

@Injectable({ providedIn: 'root' })
export class CadastrosApi {
  private readonly http = inject(HttpClient);
  gerarTokenAdmin(): Observable<ApiResponse<TokenAdminVM>> {
    return this.http.post<ApiResponse<TokenAdminVM>>('/api/v1/autenticacao/token-admin', {});
  }
  autocadastrarPessoa(dados: CadastroPublicoPessoaInput): Observable<ApiResponse<PessoaVM>> {
    return this.http.post<ApiResponse<PessoaVM>>('/api/v1/publico/pessoas', dados);
  }
  verificarEmailPessoa(dados: VerificacaoEmailInput): Observable<ApiResponse<PessoaVM>> {
    return this.http.post<ApiResponse<PessoaVM>>('/api/v1/publico/pessoas/verificar-email', dados);
  }
  listarInstituicoes(deslocamento: number): Observable<ApiResponse<InstituicaoVM[]>> {
    return this.http.get<ApiResponse<InstituicaoVM[]>>('/api/v1/instituicoes', { params: { limite: 50, deslocamento } });
  }
  listarPessoas(deslocamento: number): Observable<ApiResponse<PessoaVM[]>> {
    return this.http.get<ApiResponse<PessoaVM[]>>('/api/v1/pessoas', { params: { limite: 50, deslocamento } });
  }
  salvarInstituicao(id: string | null, dados: InstituicaoInput): Observable<ApiResponse<InstituicaoVM>> {
    return id ? this.http.put<ApiResponse<InstituicaoVM>>(`/api/v1/instituicoes/${id}`, dados)
      : this.http.post<ApiResponse<InstituicaoVM>>('/api/v1/instituicoes', dados);
  }
  salvarPessoa(id: string | null, dados: ContatoInput): Observable<ApiResponse<PessoaVM>> {
    return id ? this.http.put<ApiResponse<PessoaVM>>(`/api/v1/pessoas/${id}`, dados)
      : this.http.post<ApiResponse<PessoaVM>>('/api/v1/pessoas', dados);
  }
  inativar(tipo: 'instituicoes' | 'pessoas', id: string): Observable<ApiResponse<CadastroVM>> {
    return this.http.delete<ApiResponse<CadastroVM>>(`/api/v1/${tipo}/${id}`);
  }
}


export function mensagemErro(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    const body: unknown = error.error;
    if (typeof body === 'object' && body !== null && 'detail' in body && typeof body.detail === 'string') {
      return body.detail;
    }
    if (error.status === 0) return 'Não foi possível conectar à API. Verifique a conexão e tente novamente.';
  }
  return 'Não foi possível concluir a operação.';
}
