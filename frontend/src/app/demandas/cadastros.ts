import { Component, DestroyRef, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup, NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { mensagemErro } from '../core/api';
import { OperacaoApi } from '../core/operacao-api';
import { DemandaInput, DemandaItemVM, DemandaVM, Prioridade, SituacaoDemanda } from '../shared/operacao';
import { SeletorComponent } from '../shared/seletor';
import { RecomendacoesComponent } from './recomendacoes';

type ItemForm = FormGroup<{ id: FormControl<string>; tipo: FormControl<'atividade' | 'recurso'>; necessidade: FormControl<string>; unidade: FormControl<string>; quantidade: FormControl<string>; observacoes: FormControl<string>; }>;

@Component({ selector: 'app-demandas', imports: [ReactiveFormsModule, DatePipe, SeletorComponent, RecomendacoesComponent], templateUrl: './cadastros.html' })
export class DemandasComponent {
  private readonly api = inject(OperacaoApi); private readonly fb = inject(NonNullableFormBuilder); private readonly destroy = inject(DestroyRef);
  readonly registros = signal<DemandaVM[]>([]); readonly ocupado = signal(false); readonly erro = signal(''); readonly aviso = signal(''); readonly editando = signal<DemandaVM | null>(null); readonly analisar = signal<DemandaVM | null>(null);
  readonly busca = this.fb.control(''); readonly historico = this.fb.control(false); readonly deslocamento = signal(0);
  readonly form = this.fb.group({ id_area_afetada: ['', Validators.required], id_pessoa_solicitante: ['', Validators.required], titulo: ['', [Validators.required, Validators.minLength(2)]], descricao: ['', [Validators.required, Validators.minLength(2)]], prioridade: this.fb.control<Prioridade>('normal'), situacao: this.fb.control<SituacaoDemanda>('aberta'), inicio_previsto_em: ['', Validators.required], prazo_em: ['', Validators.required], itens: this.fb.array<ItemForm>([]) });
  constructor() { this.novo(); this.recarregar(); }
  get itens(): typeof this.form.controls.itens { return this.form.controls.itens; }
  private item(d?: DemandaItemVM): ItemForm { return this.fb.group({ id: [d?.id ?? ''], tipo: this.fb.control<'atividade' | 'recurso'>(d?.id_tipo_recurso ? 'recurso' : 'atividade'), necessidade: [d?.id_atividade ?? d?.id_tipo_recurso ?? '', Validators.required], unidade: [d?.id_unidade_medida ?? '', Validators.required], quantidade: [d?.quantidade_solicitada ?? '1', Validators.required], observacoes: [d?.observacoes ?? ''] }); }
  adicionar(): void { if (this.itens.length < 100) this.itens.push(this.item()); }
  remover(i: number): void { if (this.itens.length > 1) this.itens.removeAt(i); }
  mudarTipo(i: number): void { const f = this.itens.at(i); f.controls.necessidade.reset(); f.controls.unidade.reset(); }
  novo(): void { this.editando.set(null); this.form.reset({ prioridade: 'normal', situacao: 'aberta' }); this.itens.clear(); this.adicionar(); }
  recarregar(): void {
    this.ocupado.set(true); this.erro.set('');
    this.api.listar<DemandaVM>('demandas', this.deslocamento(), this.busca.value.trim(), this.historico.value).pipe(takeUntilDestroyed(this.destroy)).subscribe({ next: r => { this.registros.set(r.data); this.ocupado.set(false); }, error: (e: unknown) => this.falhar(e) });
  }
  pesquisar(): void { this.deslocamento.set(0); this.recarregar(); }
  paginar(delta: number): void { this.deslocamento.update(p => Math.max(0, p + 50 * delta)); this.recarregar(); }
  editar(d: DemandaVM): void {
    this.editando.set(d); this.form.patchValue({ id_area_afetada: d.id_area_afetada, id_pessoa_solicitante: d.id_pessoa_solicitante, titulo: d.titulo, descricao: d.descricao, prioridade: d.prioridade, situacao: d.situacao, inicio_previsto_em: this.local(d.inicio_previsto_em), prazo_em: this.local(d.prazo_em) });
    this.itens.clear(); d.itens.filter(i => !i.inativado_em).forEach(i => this.itens.push(this.item(i)));
  }
  private local(v: string): string { const d = new Date(v); return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0,16); }
  nomeItem(id: string): string { return this.editando()?.itens.find(i => i.id === id)?.necessidade_nome ?? ''; }
  salvar(): void {
    this.form.markAllAsTouched(); if (this.form.invalid || !this.itens.length) return;
    const f = this.form.getRawValue(); const inicio = new Date(f.inicio_previsto_em); const prazo = new Date(f.prazo_em);
    if (!Number.isFinite(inicio.getTime()) || !Number.isFinite(prazo.getTime()) || prazo < inicio) { this.erro.set('Informe uma janela de atendimento válida.'); return; }
    const dados: DemandaInput = { ...f, inicio_previsto_em: inicio.toISOString(), prazo_em: prazo.toISOString(), itens: f.itens.map(i => ({ id: i.id || null, id_atividade: i.tipo === 'atividade' ? i.necessidade : null, id_tipo_recurso: i.tipo === 'recurso' ? i.necessidade : null, id_unidade_medida: i.unidade, quantidade_solicitada: i.quantidade, observacoes: i.observacoes.trim() || null })) };
    this.ocupado.set(true); this.erro.set(''); this.aviso.set('');
    this.api.salvar<DemandaInput, DemandaVM>('demandas', this.editando()?.id ?? null, dados).pipe(takeUntilDestroyed(this.destroy)).subscribe({ next: () => { this.aviso.set('Demanda salva.'); this.novo(); this.recarregar(); }, error: (e: unknown) => this.falhar(e) });
  }
  inativar(d: DemandaVM): void { if (!confirm('Inativar demanda preservando histórico?')) return; this.ocupado.set(true); this.api.inativar<DemandaVM>('demandas', d.id).pipe(takeUntilDestroyed(this.destroy)).subscribe({ next: () => { this.aviso.set('Demanda inativada.'); this.novo(); this.recarregar(); }, error: (e: unknown) => this.falhar(e) }); }
  private falhar(e: unknown): void { this.ocupado.set(false); this.erro.set(mensagemErro(e)); }
}
