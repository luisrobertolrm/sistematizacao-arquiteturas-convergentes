import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize, Observable } from 'rxjs';
import { mensagemErro } from '../core/api';
import { CapacidadesApi } from '../core/capacidades-api';
import { ApiResponse } from '../shared/contratos';
import { AtividadeVM, CapacidadeVM, TipoCapacidade } from '../shared/capacidades';
import { ReferenciaCapacidadeComponent } from './referencia';
import { TermosComponent } from './termos';

@Component({ selector: 'app-capacidades', imports: [ReactiveFormsModule, DatePipe, ReferenciaCapacidadeComponent, TermosComponent], templateUrl: './catalogos.html' })
export class CapacidadesComponent {
  private readonly api = inject(CapacidadesApi);
  private readonly fb = inject(NonNullableFormBuilder);
  private readonly destroyRef = inject(DestroyRef);
  readonly tipo = signal<TipoCapacidade>('unidades-medida');
  readonly titulo = computed(() => this.tipo() === 'unidades-medida' ? 'Unidades de medida' : this.tipo() === 'categorias-atividade' ? 'Categorias de atividade' : 'Atividades');
  readonly registros = signal<CapacidadeVM[]>([]);
  readonly termosAtividade = signal<AtividadeVM | null>(null);
  readonly carregando = signal(false);
  readonly erro = signal('');
  readonly aviso = signal('');
  readonly editando = signal<string | null>(null);
  readonly deslocamento = signal(0);
  readonly historico = signal(false);
  readonly categoria = signal('');
  readonly unidade = signal('');
  readonly categoriaNome = signal('');
  readonly unidadeNome = signal('');
  readonly busca = this.fb.control('');
  readonly form = this.fb.group({
    codigo: ['', [Validators.required, Validators.maxLength(50), Validators.pattern(/^[a-zA-Z0-9][a-zA-Z0-9_-]*$/)]],
    nome: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(200)]],
    descricao: ['', [Validators.maxLength(4000)]], simbolo: ['', [Validators.maxLength(30)]],
    orientacoes: ['', [Validators.maxLength(4000)]], restricoes: ['', [Validators.maxLength(4000)]],
  });
  constructor() { this.configurarValidacao(); this.recarregar(); }
  private configurarValidacao(): void {
    this.form.controls.simbolo.setValidators(this.tipo() === 'unidades-medida' ? [Validators.required, Validators.maxLength(30)] : [Validators.maxLength(30)]);
    this.form.controls.descricao.setValidators(this.tipo() === 'atividades' ? [Validators.required, Validators.minLength(2), Validators.maxLength(4000)] : [Validators.maxLength(4000)]);
    this.form.controls.simbolo.updateValueAndValidity({ emitEvent: false });
    this.form.controls.descricao.updateValueAndValidity({ emitEvent: false });
  }
  selecionar(tipo: TipoCapacidade): void {
    this.tipo.set(tipo); this.termosAtividade.set(null); this.busca.reset(); this.historico.set(false);
    this.deslocamento.set(0); this.aviso.set(''); this.configurarValidacao(); this.novo(); this.recarregar();
  }
  pesquisar(): void { this.deslocamento.set(0); this.recarregar(); }
  alternarHistorico(evento: Event): void {
    if (!(evento.target instanceof HTMLInputElement)) return;
    this.historico.set(evento.target.checked); this.pesquisar();
  }
  paginar(delta: number): void { this.deslocamento.update((n) => Math.max(0, n + delta * 50)); this.recarregar(); }
  recarregar(): void {
    this.carregando.set(true); this.erro.set('');
    this.api.listar(this.tipo(), this.deslocamento(), this.busca.value.trim(), this.historico())
      .pipe(takeUntilDestroyed(this.destroyRef), finalize(() => this.carregando.set(false)))
      .subscribe({ next: (r) => this.registros.set(r.data), error: (e: unknown) => {
        this.registros.set([]); this.erro.set(mensagemErro(e));
      } });
  }
  novo(): void {
    this.editando.set(null); this.form.reset(); this.categoria.set(''); this.unidade.set('');
    this.categoriaNome.set(''); this.unidadeNome.set('');
  }
  editar(registro: CapacidadeVM): void {
    this.editando.set(registro.id);
    this.form.setValue({ codigo: registro.codigo, nome: registro.nome,
      descricao: 'descricao' in registro ? registro.descricao ?? '' : '',
      simbolo: 'simbolo' in registro ? registro.simbolo : '',
      orientacoes: 'orientacoes' in registro ? registro.orientacoes ?? '' : '',
      restricoes: 'restricoes' in registro ? registro.restricoes ?? '' : '' });
    this.categoria.set('categoria_id' in registro ? registro.categoria_id : '');
    this.unidade.set('id_unidade_capacidade' in registro ? registro.id_unidade_capacidade ?? '' : '');
    this.categoriaNome.set('categoria_nome' in registro ? registro.categoria_nome + (registro.categoria_inativa ? ' (inativa)' : '') : '');
    this.unidadeNome.set('unidade_nome' in registro ? (registro.unidade_nome ?? '') + (registro.unidade_inativa ? ' (inativa)' : '') : '');
    document.getElementById('capacidade-nome')?.focus();
  }
  atividade(registro: CapacidadeVM): AtividadeVM | null { return 'categoria_id' in registro ? registro : null; }
  abrirTermos(registro: CapacidadeVM): void { this.termosAtividade.set(this.atividade(registro)); }
  voltarTermos(): void { this.termosAtividade.set(null); this.recarregar(); }
  salvar(): void {
    this.form.markAllAsTouched(); if (this.form.invalid || this.carregando()) return;
    const f = this.form.getRawValue();
    const base = { codigo: f.codigo.trim(), nome: f.nome.trim() };
    let operacao: Observable<ApiResponse<CapacidadeVM>>;
    if (this.tipo() === 'unidades-medida') {
      if (!f.simbolo.trim()) { this.erro.set('Informe o símbolo da unidade.'); return; }
      operacao = this.api.salvar('unidades-medida', this.editando(), { ...base, simbolo: f.simbolo.trim() });
    } else if (this.tipo() === 'categorias-atividade') {
      operacao = this.api.salvar('categorias-atividade', this.editando(), { ...base, descricao: f.descricao.trim() || null });
    } else {
      if (!this.categoria() || f.descricao.trim().length < 2) { this.erro.set('Informe categoria e descrição da atividade.'); return; }
      operacao = this.api.salvar('atividades', this.editando(), { ...base, descricao: f.descricao.trim(),
        categoria_id: this.categoria(), id_unidade_capacidade: this.unidade() || null,
        orientacoes: f.orientacoes.trim() || null, restricoes: f.restricoes.trim() || null });
    }
    this.carregando.set(true); this.erro.set(''); this.aviso.set('');
    operacao.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => { this.aviso.set('Cadastro salvo.'); this.novo(); this.recarregar(); },
      error: (e: unknown) => { this.carregando.set(false); this.erro.set(mensagemErro(e)); },
    });
  }
  inativar(registro: CapacidadeVM): void {
    if (!confirm(`Inativar ${registro.nome}? As referências anteriores serão preservadas.`)) return;
    this.carregando.set(true); this.erro.set(''); this.aviso.set('');
    this.api.inativar(this.tipo(), registro.id).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => { this.aviso.set('Cadastro inativado.'); this.novo(); this.recarregar(); },
      error: (e: unknown) => { this.carregando.set(false); this.erro.set(mensagemErro(e)); },
    });
  }
}
