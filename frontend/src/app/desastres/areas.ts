import { DatePipe } from '@angular/common';
import { Component, DestroyRef, effect, inject, input, output, signal, untracked, viewChild } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { mensagemErro } from '../core/api';
import { DesastresApi } from '../core/desastres-api';
import { ApiResponse } from '../shared/contratos';
import { AreaAfetadaInput, AreaAfetadaVM, DesastreVM, GeometriaArea, GravidadeArea, SituacaoArea } from '../shared/desastres';
import { MapaAreasComponent } from './mapa';

@Component({ selector: 'app-areas', imports: [ReactiveFormsModule, DatePipe, MapaAreasComponent], templateUrl: './areas.html' })
export class AreasComponent {
  private readonly api = inject(DesastresApi); private readonly fb = inject(NonNullableFormBuilder); private readonly destroyRef = inject(DestroyRef);
  readonly desastre = input.required<DesastreVM>(); readonly voltar = output<void>();
  private readonly mapa = viewChild(MapaAreasComponent);
  readonly registros = signal<AreaAfetadaVM[]>([]); readonly carregando = signal(false); readonly erro = signal(''); readonly aviso = signal('');
  readonly editando = signal<string | null>(null); readonly geometria = signal<GeometriaArea | null>(null);
  readonly historico = signal(false); readonly deslocamento = signal(0); readonly busca = this.fb.control('');
  readonly form = this.fb.group({ nome: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(200)]], descricao: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(4000)]], municipio: ['', [Validators.required, Validators.pattern(/^[0-9]{7}$/)]], gravidade: this.fb.control<GravidadeArea>('moderada'), situacao: this.fb.control<SituacaoArea>('em_avaliacao') });
  private versao = 0;
  constructor() { effect(() => { const d = this.desastre(); untracked(() => { this.historico.set(!!d.inativado_em); this.deslocamento.set(0); this.busca.reset(); this.novo(); this.recarregar(); }); }); }
  novo(): void { this.mapa()?.cancelarDesenho(); this.editando.set(null); this.geometria.set(null); this.form.reset({ gravidade: 'moderada', situacao: 'em_avaliacao' }); }
  editar(a: AreaAfetadaVM): void { this.mapa()?.cancelarDesenho(); this.editando.set(a.id); this.geometria.set(a.geometria); this.form.setValue({ nome: a.nome, descricao: a.descricao, municipio: a.municipio_codigo_ibge, gravidade: a.gravidade, situacao: a.situacao }); }
  visualizar(a: AreaAfetadaVM): void { this.mapa()?.cancelarDesenho(); this.geometria.set(a.geometria); }
  recarregar(): void {
    const versao = ++this.versao; this.carregando.set(true); this.erro.set('');
    this.api.areas(this.desastre().id, this.deslocamento(), this.busca.value, this.historico()).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: r => { if (versao === this.versao) { this.registros.set(r.data); this.carregando.set(false); } },
      error: (e: unknown) => { if (versao === this.versao) { this.registros.set([]); this.carregando.set(false); this.erro.set(mensagemErro(e)); } },
    });
  }
  pesquisar(): void { this.deslocamento.set(0); this.recarregar(); }
  paginar(delta: number): void { this.deslocamento.update(n => Math.max(0, n + delta * 50)); this.recarregar(); }
  alternarHistorico(evento: Event): void { if (evento.target instanceof HTMLInputElement) { this.historico.set(evento.target.checked); this.pesquisar(); } }
  salvar(): void {
    this.form.markAllAsTouched(); if (this.form.invalid || this.carregando() || this.desastre().inativado_em) return;
    const geometria = this.geometria(); if (!geometria) { this.erro.set('Desenhe e conclua a delimitação da área no mapa.'); return; }
    const f = this.form.getRawValue(); const dados: AreaAfetadaInput = { nome: f.nome, descricao: f.descricao, municipio_codigo_ibge: f.municipio, gravidade: f.gravidade, situacao: f.situacao, geometria };
    this.executar(this.api.salvarArea(this.desastre().id, this.editando(), dados), 'Área salva.');
  }
  avaliar(a: AreaAfetadaVM): void {
    if (!confirm(`Confirmar avaliação atual de ${a.nome}: ${a.gravidade}, ${a.situacao}?`)) return;
    this.executar(this.api.avaliar(this.desastre().id, a.id, { gravidade: a.gravidade, situacao: a.situacao }), 'Avaliação confirmada.');
  }
  inativar(a: AreaAfetadaVM): void { if (confirm(`Inativar a área ${a.nome}?`)) this.executar(this.api.inativarArea(this.desastre().id, a.id), 'Área inativada.'); }
  private executar(operacao: Observable<ApiResponse<AreaAfetadaVM>>, aviso: string): void {
    this.carregando.set(true); this.erro.set(''); this.aviso.set('');
    operacao.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({ next: () => { this.aviso.set(aviso); this.novo(); this.recarregar(); }, error: (e: unknown) => { this.carregando.set(false); this.erro.set(mensagemErro(e)); } });
  }
}
