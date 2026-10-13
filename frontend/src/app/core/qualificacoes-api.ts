import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiResponse } from '../shared/contratos';
import {
  CatalogosEntradaPorTipo, CatalogosPorTipo, ReferenciaVM, TipoCatalogo, TipoReferencia,
  VinculosEntradaPorTipo, VinculosPorTipo,
} from '../shared/qualificacoes';

@Injectable({ providedIn: 'root' })
export class QualificacoesApi {
  private readonly http = inject(HttpClient);
  referencias(tipo: TipoReferencia, deslocamento: number, busca = ''): Observable<ApiResponse<ReferenciaVM[]>> {
    return this.http.get<ApiResponse<ReferenciaVM[]>>(`/api/v1/${tipo}`, {
      params: busca.length >= 2 ? { limite: 50, deslocamento, busca } : { limite: 50, deslocamento },
    });
  }
  catalogos<T extends TipoCatalogo>(tipo: T, deslocamento: number, busca: string): Observable<ApiResponse<CatalogosPorTipo[T][]>> {
    return this.http.get<ApiResponse<CatalogosPorTipo[T][]>>(`/api/v1/${tipo}`, {
      params: busca.length >= 2 ? { limite: 50, deslocamento, busca } : { limite: 50, deslocamento },
    });
  }
  salvarCatalogo<T extends TipoCatalogo>(tipo: T, id: string | null, dados: CatalogosEntradaPorTipo[T]): Observable<ApiResponse<CatalogosPorTipo[T]>> {
    return id ? this.http.put<ApiResponse<CatalogosPorTipo[T]>>(`/api/v1/${tipo}/${id}`, dados)
      : this.http.post<ApiResponse<CatalogosPorTipo[T]>>(`/api/v1/${tipo}`, dados);
  }
  inativarCatalogo<T extends TipoCatalogo>(tipo: T, id: string): Observable<ApiResponse<CatalogosPorTipo[T]>> {
    return this.http.delete<ApiResponse<CatalogosPorTipo[T]>>(`/api/v1/${tipo}/${id}`);
  }
  vinculos<T extends TipoReferencia>(pessoa: string, tipo: T, deslocamento: number, historico: boolean): Observable<ApiResponse<VinculosPorTipo[T][]>> {
    return this.http.get<ApiResponse<VinculosPorTipo[T][]>>(`/api/v1/pessoas/${pessoa}/${tipo}`, {
      params: { limite: 50, deslocamento, incluir_inativos: historico },
    });
  }
  salvarVinculo<T extends TipoReferencia>(pessoa: string, tipo: T, id: string | null, dados: VinculosEntradaPorTipo[T]): Observable<ApiResponse<VinculosPorTipo[T]>> {
    const url = `/api/v1/pessoas/${pessoa}/${tipo}`;
    return id ? this.http.put<ApiResponse<VinculosPorTipo[T]>>(`${url}/${id}`, dados)
      : this.http.post<ApiResponse<VinculosPorTipo[T]>>(url, dados);
  }
  inativarVinculo<T extends TipoReferencia>(pessoa: string, tipo: T, id: string): Observable<ApiResponse<VinculosPorTipo[T]>> {
    return this.http.delete<ApiResponse<VinculosPorTipo[T]>>(`/api/v1/pessoas/${pessoa}/${tipo}/${id}`);
  }
}
