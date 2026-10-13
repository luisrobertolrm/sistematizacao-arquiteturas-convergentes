import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiResponse } from '../shared/contratos';
import { BuscaVM, IndiceVM, RecomendacaoVM } from '../shared/operacao';

@Injectable({ providedIn: 'root' })
export class OperacaoApi {
  private readonly http = inject(HttpClient);
  listar<T>(rota: string, deslocamento = 0, busca = '', incluir_inativos = false): Observable<ApiResponse<T[]>> {
    return this.http.get<ApiResponse<T[]>>(`/api/v1/${rota}`, { params: { limite: 50, deslocamento, incluir_inativos, ...(busca.length >= 2 ? { busca } : {}) } });
  }
  salvar<I, V>(rota: string, id: string | null, dados: I): Observable<ApiResponse<V>> {
    return id ? this.http.put<ApiResponse<V>>(`/api/v1/${rota}/${id}`, dados) : this.http.post<ApiResponse<V>>(`/api/v1/${rota}`, dados);
  }
  inativar<V>(rota: string, id: string): Observable<ApiResponse<V>> { return this.http.delete<ApiResponse<V>>(`/api/v1/${rota}/${id}`); }
  indexar(id_modelo: string, ids_atividades: string[]): Observable<ApiResponse<IndiceVM[]>> { return this.http.post<ApiResponse<IndiceVM[]>>('/api/v1/indices-atividade/indexar', { id_modelo, ids_atividades }); }
  buscar(texto: string): Observable<ApiResponse<BuscaVM>> { return this.http.post<ApiResponse<BuscaVM>>('/api/v1/atividades/busca-semantica', { texto, limite: 10 }); }
  gerar(id: string): Observable<ApiResponse<RecomendacaoVM>> { return this.http.post<ApiResponse<RecomendacaoVM>>(`/api/v1/demandas/${id}/recomendacoes`, {}); }
  historico(id: string, deslocamento: number): Observable<ApiResponse<RecomendacaoVM[]>> { return this.http.get<ApiResponse<RecomendacaoVM[]>>('/api/v1/recomendacoes', { params: { id_demanda: id, limite: 50, deslocamento } }); }
  decidir(id: string, situacao: 'aprovada' | 'rejeitada', justificativa: string): Observable<ApiResponse<RecomendacaoVM>> { return this.http.post<ApiResponse<RecomendacaoVM>>(`/api/v1/recomendacoes/${id}/decisao`, { situacao, justificativa }); }
}
