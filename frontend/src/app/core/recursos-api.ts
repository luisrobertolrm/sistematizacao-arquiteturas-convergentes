import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiResponse } from '../shared/contratos';
import { ReferenciaVM } from '../shared/qualificacoes';
import { OfertaRecursoInput, OfertaRecursoVM, RecursoInputMap, RecursoVMMap, ReferenciaRecurso, TipoCadastroRecurso } from '../shared/recursos';

@Injectable({ providedIn: 'root' })
export class RecursosApi {
  private readonly http = inject(HttpClient);
  private params(deslocamento: number, busca: string, historico = false): Record<string, string | number | boolean> {
    return { limite: 50, deslocamento, incluir_inativos: historico, ...(busca.trim().length >= 2 ? { busca: busca.trim() } : {}) };
  }
  referencias(tipo: ReferenciaRecurso, deslocamento: number, busca: string): Observable<ApiResponse<ReferenciaVM[]>> {
    return this.http.get<ApiResponse<ReferenciaVM[]>>(`/api/v1/${tipo}`, { params: this.params(deslocamento, busca) });
  }
  listar<T extends TipoCadastroRecurso>(tipo: T, deslocamento: number, busca: string, historico: boolean): Observable<ApiResponse<RecursoVMMap[T][]>> {
    return this.http.get<ApiResponse<RecursoVMMap[T][]>>(`/api/v1/${tipo}`, { params: this.params(deslocamento, busca, historico) });
  }
  salvar<T extends TipoCadastroRecurso>(tipo: T, id: string | null, dados: RecursoInputMap[T]): Observable<ApiResponse<RecursoVMMap[T]>> {
    return id ? this.http.put<ApiResponse<RecursoVMMap[T]>>(`/api/v1/${tipo}/${id}`, dados)
      : this.http.post<ApiResponse<RecursoVMMap[T]>>(`/api/v1/${tipo}`, dados);
  }
  inativar<T extends TipoCadastroRecurso>(tipo: T, id: string): Observable<ApiResponse<RecursoVMMap[T]>> {
    return this.http.delete<ApiResponse<RecursoVMMap[T]>>(`/api/v1/${tipo}/${id}`);
  }
  vinculos(oferta: string, deslocamento: number, historico: boolean): Observable<ApiResponse<OfertaRecursoVM[]>> {
    return this.http.get<ApiResponse<OfertaRecursoVM[]>>(`/api/v1/ofertas-atividade/${oferta}/recursos`, { params: this.params(deslocamento, '', historico) });
  }
  salvarVinculo(oferta: string, id: string | null, dados: OfertaRecursoInput): Observable<ApiResponse<OfertaRecursoVM>> {
    const url = `/api/v1/ofertas-atividade/${oferta}/recursos`;
    return id ? this.http.put<ApiResponse<OfertaRecursoVM>>(`${url}/${id}`, dados) : this.http.post<ApiResponse<OfertaRecursoVM>>(url, dados);
  }
  inativarVinculo(oferta: string, id: string): Observable<ApiResponse<OfertaRecursoVM>> {
    return this.http.delete<ApiResponse<OfertaRecursoVM>>(`/api/v1/ofertas-atividade/${oferta}/recursos/${id}`);
  }
}
