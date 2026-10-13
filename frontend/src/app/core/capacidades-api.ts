import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiResponse } from '../shared/contratos';
import {
  AtividadeTermoInput, AtividadeTermoVM, AtividadeVM, CapacidadesEntradaPorTipo,
  CapacidadesPorTipo, TipoCapacidade,
} from '../shared/capacidades';

@Injectable({ providedIn: 'root' })
export class CapacidadesApi {
  private readonly http = inject(HttpClient);
  listar<T extends TipoCapacidade>(tipo: T, deslocamento: number, busca = '', historico = false): Observable<ApiResponse<CapacidadesPorTipo[T][]>> {
    const params: Record<string, string | number | boolean> = { limite: 50, deslocamento, incluir_inativos: historico };
    if (busca.length >= 2) params['busca'] = busca;
    return this.http.get<ApiResponse<CapacidadesPorTipo[T][]>>(`/api/v1/${tipo}`, { params });
  }
  salvar<T extends TipoCapacidade>(tipo: T, id: string | null, dados: CapacidadesEntradaPorTipo[T]): Observable<ApiResponse<CapacidadesPorTipo[T]>> {
    return id ? this.http.put<ApiResponse<CapacidadesPorTipo[T]>>(`/api/v1/${tipo}/${id}`, dados)
      : this.http.post<ApiResponse<CapacidadesPorTipo[T]>>(`/api/v1/${tipo}`, dados);
  }
  inativar<T extends TipoCapacidade>(tipo: T, id: string): Observable<ApiResponse<CapacidadesPorTipo[T]>> {
    return this.http.delete<ApiResponse<CapacidadesPorTipo[T]>>(`/api/v1/${tipo}/${id}`);
  }
  atividade(id: string, historico = false): Observable<ApiResponse<AtividadeVM>> {
    return this.http.get<ApiResponse<AtividadeVM>>(`/api/v1/atividades/${id}`, { params: { incluir_inativos: historico } });
  }
  termos(idAtividade: string, deslocamento: number, historico: boolean): Observable<ApiResponse<AtividadeTermoVM[]>> {
    return this.http.get<ApiResponse<AtividadeTermoVM[]>>(`/api/v1/atividades/${idAtividade}/termos`, {
      params: { limite: 50, deslocamento, incluir_inativos: historico },
    });
  }
  salvarTermo(idAtividade: string, id: string | null, dados: AtividadeTermoInput): Observable<ApiResponse<AtividadeTermoVM>> {
    const url = `/api/v1/atividades/${idAtividade}/termos`;
    return id ? this.http.put<ApiResponse<AtividadeTermoVM>>(`${url}/${id}`, dados)
      : this.http.post<ApiResponse<AtividadeTermoVM>>(url, dados);
  }
  inativarTermo(idAtividade: string, id: string): Observable<ApiResponse<AtividadeTermoVM>> {
    return this.http.delete<ApiResponse<AtividadeTermoVM>>(`/api/v1/atividades/${idAtividade}/termos/${id}`);
  }
}
