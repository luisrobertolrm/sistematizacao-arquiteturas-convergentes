import { Component, DestroyRef, effect, inject, input, output, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { OperacaoApi } from '../core/operacao-api';
import { mensagemErro } from '../core/api';
import { DemandaVM, RecomendacaoVM } from '../shared/operacao';

@Component({ selector: 'app-recomendacoes', imports: [DatePipe, ReactiveFormsModule], templateUrl: './recomendacoes.html' })
export class RecomendacoesComponent {
  private readonly api = inject(OperacaoApi); private readonly destroy = inject(DestroyRef);
  readonly demanda = input.required<DemandaVM>(); readonly voltar = output<void>(); readonly registros = signal<RecomendacaoVM[]>([]); readonly selecionada = signal<RecomendacaoVM | null>(null); readonly ocupado = signal(false); readonly erro = signal(''); readonly aviso = signal(''); readonly deslocamento = signal(0);
  readonly justificativa = new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.minLength(2), Validators.maxLength(4000)] });
  constructor() { effect(() => { const id = this.demanda().id; this.deslocamento.set(0); this.selecionada.set(null); this.carregar(id); }); }
  recarregar(): void { this.carregar(this.demanda().id); }
  private carregar(id: string): void { this.ocupado.set(true); this.api.historico(id, this.deslocamento()).pipe(takeUntilDestroyed(this.destroy)).subscribe({ next: r => { this.registros.set(r.data); this.ocupado.set(false); }, error: (e: unknown) => this.falhar(e) }); }
  paginar(delta: number): void { this.deslocamento.update(p => Math.max(0, p + 50 * delta)); this.recarregar(); }
  selecionar(r: RecomendacaoVM): void { this.selecionada.set(r); this.justificativa.reset(); this.erro.set(''); }
  nome(id: string): string { return this.selecionada()?.nomes_candidatos[id] ?? this.demanda().itens.find(i => i.id === id)?.necessidade_nome ?? id; }
  gerar(): void { this.ocupado.set(true); this.erro.set(''); this.aviso.set(''); this.api.gerar(this.demanda().id).pipe(takeUntilDestroyed(this.destroy)).subscribe({ next: r => { this.selecionar(r.data); this.aviso.set('Sugestão gerada para análise administrativa.'); this.deslocamento.set(0); this.recarregar(); }, error: (e: unknown) => this.falhar(e) }); }
  decidir(situacao: 'aprovada' | 'rejeitada'): void { const r = this.selecionada(); if (!r || this.justificativa.invalid || !confirm('Registrar esta decisão administrativa?')) return; this.ocupado.set(true); this.erro.set(''); this.api.decidir(r.id, situacao, this.justificativa.value).pipe(takeUntilDestroyed(this.destroy)).subscribe({ next: resposta => { this.selecionada.set(resposta.data); this.aviso.set('Decisão registrada.'); this.recarregar(); }, error: (e: unknown) => this.falhar(e) }); }
  private falhar(e: unknown): void { this.ocupado.set(false); this.erro.set(mensagemErro(e)); }
}
