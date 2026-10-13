import { DatePipe } from '@angular/common';
import { Component, DestroyRef, effect, inject, input, output, signal, untracked } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { mensagemErro } from '../core/api';
import { RecursosApi } from '../core/recursos-api';
import { ApiResponse } from '../shared/contratos';
import { OfertaAtividadeVM, OfertaRecursoInput, OfertaRecursoVM } from '../shared/recursos';
import { ReferenciaRecursoComponent } from './referencia';

@Component({ selector: 'app-oferta-recursos', imports: [ReactiveFormsModule, DatePipe, ReferenciaRecursoComponent], templateUrl: './vinculos.html' })
export class OfertaRecursosComponent {
  private readonly api = inject(RecursosApi);
  private readonly fb = inject(NonNullableFormBuilder);
  private readonly destroyRef = inject(DestroyRef);
  readonly oferta = input.required<OfertaAtividadeVM>();
  readonly voltar = output<void>();
  readonly registros = signal<OfertaRecursoVM[]>([]);
  readonly carregando = signal(false); readonly erro = signal(''); readonly aviso = signal('');
  readonly historico = signal(false); readonly deslocamento = signal(0);
  readonly editando = signal<string | null>(null); readonly recurso = signal(''); readonly recursoNome = signal('');
  readonly form = this.fb.group({ quantidade: ['1', [Validators.required, Validators.pattern(/^\d{1,14}(\.\d{1,4})?$/)]] });
  private versao = 0;
  constructor() {
    effect(() => { const oferta = this.oferta(); untracked(() => {
      this.historico.set(!!oferta.inativado_em); this.deslocamento.set(0); this.novo(); this.recarregar();
    }); });
  }
  novo(): void { this.editando.set(null); this.recurso.set(''); this.recursoNome.set(''); this.form.reset({ quantidade: '1' }); }
  editar(r: OfertaRecursoVM): void { this.editando.set(r.id); this.recurso.set(r.recurso_id); this.recursoNome.set(r.recurso_nome); this.form.setValue({ quantidade: r.quantidade_prevista }); }
  recarregar(): void {
    const versao = ++this.versao; this.carregando.set(true); this.erro.set('');
    this.api.vinculos(this.oferta().id, this.deslocamento(), this.historico()).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: r => { if (versao === this.versao) { this.registros.set(r.data); this.carregando.set(false); } },
      error: (e: unknown) => { if (versao === this.versao) { this.registros.set([]); this.carregando.set(false); this.erro.set(mensagemErro(e)); } },
    });
  }
  alternarHistorico(evento: Event): void { if (evento.target instanceof HTMLInputElement) { this.historico.set(evento.target.checked); this.deslocamento.set(0); this.recarregar(); } }
  paginar(delta: number): void { this.deslocamento.update(n => Math.max(0, n + delta * 50)); this.recarregar(); }
  pendencias(): string[] {
    if (this.oferta().inativado_em) {
      return ['a oferta está inativada (não permite novos vínculos)'];
    }
    const lista: string[] = [];
    if (!this.recurso()) {
      lista.push('selecionar um recurso no catálogo');
    }
    const qtdControl = this.form.controls.quantidade;
    const qtd = qtdControl.value?.trim();
    if (!qtd) {
      lista.push('preencher o campo "Quantidade prevista"');
    } else if (qtdControl.invalid || !/^\d{1,14}(\.\d{1,4})?$/.test(qtd) || Number(qtd) <= 0) {
      lista.push('o campo "Quantidade prevista" deve ser maior que zero (até 4 casas decimais)');
    }
    return lista;
  }
  motivoBloqueio(): string {
    if (this.carregando()) return 'Aguarde o processamento em andamento.';
    const p = this.pendencias();
    return p.length > 0 ? `Para salvar: ${p.join(', ')}.` : '';
  }
  salvar(): void {
    if (this.pendencias().length > 0 || this.carregando()) return;
    const dados: OfertaRecursoInput = { recurso_id: this.recurso(), quantidade_prevista: this.form.getRawValue().quantidade };
    this.executar(this.api.salvarVinculo(this.oferta().id, this.editando(), dados), 'Vínculo salvo.');
  }
  inativar(r: OfertaRecursoVM): void {
    if (this.carregando() || !confirm(`Inativar o vínculo com ${r.recurso_nome}?`)) return;
    this.executar(this.api.inativarVinculo(this.oferta().id, r.id), 'Vínculo inativado.');
  }
  private executar(operacao: Observable<ApiResponse<OfertaRecursoVM>>, aviso: string): void {
    this.carregando.set(true); this.erro.set(''); this.aviso.set('');
    operacao.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => { this.aviso.set(aviso); this.novo(); this.recarregar(); },
      error: (e: unknown) => { this.carregando.set(false); this.erro.set(mensagemErro(e)); },
    });
  }
}
