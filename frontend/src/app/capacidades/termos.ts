import { Component, DestroyRef, effect, inject, input, output, signal, untracked } from '@angular/core';
import { DatePipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize, forkJoin, Observable } from 'rxjs';
import { mensagemErro } from '../core/api';
import { CapacidadesApi } from '../core/capacidades-api';
import { ApiResponse } from '../shared/contratos';
import { AtividadeTermoVM, AtividadeVM } from '../shared/capacidades';

@Component({ selector: 'app-termos', imports: [ReactiveFormsModule, DatePipe], templateUrl: './termos.html' })
export class TermosComponent {
  private readonly api = inject(CapacidadesApi);
  private readonly destroyRef = inject(DestroyRef);
  readonly atividade = input.required<AtividadeVM>();
  readonly voltar = output<void>();
  readonly atual = signal<AtividadeVM | null>(null);
  readonly registros = signal<AtividadeTermoVM[]>([]);
  readonly carregando = signal(false);
  readonly historico = signal(false);
  readonly deslocamento = signal(0);
  readonly erro = signal('');
  readonly aviso = signal('');
  readonly editando = signal<string | null>(null);
  readonly termo = new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.minLength(2), Validators.maxLength(200)] });
  constructor() {
    effect(() => { const atividade = this.atividade(); untracked(() => { this.atual.set(atividade); this.historico.set(!!atividade.inativado_em); this.deslocamento.set(0); this.novo(); this.recarregar(); }); });
  }
  recarregar(): void {
    const id = this.atividade().id; this.carregando.set(true); this.erro.set('');
    forkJoin({ atividade: this.api.atividade(id, true), termos: this.api.termos(id, this.deslocamento(), this.historico() || !!this.atividade().inativado_em) })
      .pipe(takeUntilDestroyed(this.destroyRef), finalize(() => this.carregando.set(false)))
      .subscribe({ next: (r) => { this.atual.set(r.atividade.data); this.registros.set(r.termos.data); },
        error: (e: unknown) => { this.registros.set([]); this.erro.set(mensagemErro(e)); } });
  }
  novo(): void { this.editando.set(null); this.termo.reset(); }
  editar(registro: AtividadeTermoVM): void { this.editando.set(registro.id); this.termo.setValue(registro.termo); }
  alternarHistorico(evento: Event): void {
    if (!(evento.target instanceof HTMLInputElement)) return;
    this.historico.set(evento.target.checked); this.deslocamento.set(0); this.recarregar();
  }
  paginar(delta: number): void { this.deslocamento.update((n) => Math.max(0, n + delta * 50)); this.recarregar(); }
  salvar(): void {
    this.termo.markAsTouched(); if (this.termo.invalid || this.atual()?.inativado_em || this.carregando()) return;
    this.executar(this.api.salvarTermo(this.atividade().id, this.editando(), { termo: this.termo.value }), 'Termo salvo.');
  }
  inativar(registro: AtividadeTermoVM): void {
    if (!confirm(`Inativar o termo “${registro.termo}”? O registro será preservado.`)) return;
    this.executar(this.api.inativarTermo(this.atividade().id, registro.id), 'Termo inativado.');
  }
  private executar(operacao: Observable<ApiResponse<AtividadeTermoVM>>, aviso: string): void {
    this.carregando.set(true); this.erro.set(''); this.aviso.set('');
    operacao.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => { this.aviso.set(aviso); this.novo(); this.recarregar(); },
      error: (e: unknown) => { this.carregando.set(false); this.erro.set(mensagemErro(e)); },
    });
  }
}
