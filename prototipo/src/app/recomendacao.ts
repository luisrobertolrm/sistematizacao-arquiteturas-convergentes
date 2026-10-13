import { Component, computed, effect, inject, input, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { Registro, texto } from './dominio/contratos';
import { EstadoTela } from './estado';

@Component({ selector: 'app-recomendacao', imports: [ReactiveFormsModule], templateUrl: './recomendacao.html' })
export class RecomendacaoComponent {
  readonly id = input.required<string>();
  readonly estado = inject(EstadoTela);
  readonly registro = computed(() => this.estado.motor.obter('recomendacoes', this.id()));
  readonly demanda = computed(() => this.estado.motor.obter('demandas', texto(this.registro(), 'id_demanda')));
  readonly itens = computed(() => this.estado.motor.filhos('recomendacao_itens', 'id_recomendacao', this.id()));
  readonly alertas = computed(() => this.estado.motor.alertasCompartilhamento(this.id()));
  readonly justificativa = new FormControl('', { nonNullable: true });
  readonly erro = signal('');
  readonly aviso = signal('');
  readonly texto = texto;
  constructor() { effect(() => { this.id(); this.justificativa.reset(); this.erro.set(''); this.aviso.set(''); }); }
  pedido(item: Registro): Registro | undefined { return this.estado.motor.obter('demanda_itens', texto(item, 'id_demanda_item')); }
  pessoas(item: Registro): Registro[] { return this.estado.motor.filhos('recomendacao_pessoas', 'id_recomendacao_item', item.id); }
  instituicoes(item: Registro): Registro[] { return this.estado.motor.filhos('recomendacao_instituicoes', 'id_recomendacao_item', item.id); }
  recursos(item: Registro): Registro[] { return this.estado.motor.filhos('recomendacao_recursos', 'id_recomendacao_item', item.id); }
  async decidir(decisao: 'aprovada' | 'rejeitada'): Promise<void> {
    this.erro.set('');
    try { await this.estado.executar((motor) => motor.decidir(this.id(), decisao, this.justificativa.value)); this.aviso.set('Decisão registrada. Nenhum recurso foi reservado ou consumido.'); }
    catch (erro: unknown) { this.erro.set(erro instanceof Error ? erro.message : 'Não foi possível decidir.'); }
  }
  async novaAnalise(): Promise<void> {
    this.erro.set('');
    try {
      const rec = await this.estado.executar((motor) => motor.recomendar(texto(this.registro(), 'id_demanda')));
      window.location.hash = `/recomendacoes/${rec.id}`;
    } catch (erro: unknown) { this.erro.set(erro instanceof Error ? erro.message : 'Não foi possível analisar.'); }
  }
}
