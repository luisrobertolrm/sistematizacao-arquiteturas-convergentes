import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiResponse } from '../shared/contratos';
import { AreaAfetadaInput, AreaAfetadaVM, AvaliacaoAreaInput, DesastreInput, DesastreVM, TipoDesastreInput, TipoDesastreVM } from '../shared/desastres';

@Injectable({ providedIn: 'root' })
export class DesastresApi {
  private readonly http = inject(HttpClient);
  private params(deslocamento: number, busca: string, historico: boolean): Record<string, string | number | boolean> {
    return { limite: 50, deslocamento, incluir_inativos: historico, ...(busca.trim().length >= 2 ? { busca: busca.trim() } : {}) };
  }
  tipos(deslocamento: number, busca: string, historico: boolean): Observable<ApiResponse<TipoDesastreVM[]>> {
    return this.http.get<ApiResponse<TipoDesastreVM[]>>('/api/v1/tipos-desastre', { params: this.params(deslocamento, busca, historico) });
  }
  salvarTipo(id: string | null, dados: TipoDesastreInput): Observable<ApiResponse<TipoDesastreVM>> {
    return id ? this.http.put<ApiResponse<TipoDesastreVM>>(`/api/v1/tipos-desastre/${id}`, dados) : this.http.post<ApiResponse<TipoDesastreVM>>('/api/v1/tipos-desastre', dados);
  }
  inativarTipo(id: string): Observable<ApiResponse<TipoDesastreVM>> { return this.http.delete<ApiResponse<TipoDesastreVM>>(`/api/v1/tipos-desastre/${id}`); }
  ocorrencias(deslocamento: number, busca: string, historico: boolean): Observable<ApiResponse<DesastreVM[]>> {
    return this.http.get<ApiResponse<DesastreVM[]>>('/api/v1/desastres', { params: this.params(deslocamento, busca, historico) });
  }
  salvar(id: string | null, dados: DesastreInput): Observable<ApiResponse<DesastreVM>> {
    return id ? this.http.put<ApiResponse<DesastreVM>>(`/api/v1/desastres/${id}`, dados) : this.http.post<ApiResponse<DesastreVM>>('/api/v1/desastres', dados);
  }
  inativar(id: string): Observable<ApiResponse<DesastreVM>> { return this.http.delete<ApiResponse<DesastreVM>>(`/api/v1/desastres/${id}`); }
  areas(desastre: string, deslocamento: number, busca: string, historico: boolean): Observable<ApiResponse<AreaAfetadaVM[]>> {
    return this.http.get<ApiResponse<AreaAfetadaVM[]>>(`/api/v1/desastres/${desastre}/areas`, { params: this.params(deslocamento, busca, historico) });
  }
  salvarArea(desastre: string, id: string | null, dados: AreaAfetadaInput): Observable<ApiResponse<AreaAfetadaVM>> {
    const url = `/api/v1/desastres/${desastre}/areas`;
    return id ? this.http.put<ApiResponse<AreaAfetadaVM>>(`${url}/${id}`, dados) : this.http.post<ApiResponse<AreaAfetadaVM>>(url, dados);
  }
  avaliar(desastre: string, id: string, dados: AvaliacaoAreaInput): Observable<ApiResponse<AreaAfetadaVM>> {
    return this.http.post<ApiResponse<AreaAfetadaVM>>(`/api/v1/desastres/${desastre}/areas/${id}/avaliar`, dados);
  }
  inativarArea(desastre: string, id: string): Observable<ApiResponse<AreaAfetadaVM>> {
    return this.http.delete<ApiResponse<AreaAfetadaVM>>(`/api/v1/desastres/${desastre}/areas/${id}`);
  }
}
