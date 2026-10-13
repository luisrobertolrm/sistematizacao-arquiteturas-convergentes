import { Component, DestroyRef, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize, Observable } from 'rxjs';
import { mensagemErro } from '../core/api';
import { QualificacoesApi } from '../core/qualificacoes-api';
import { ApiResponse } from '../shared/contratos';
import { CursoVM, ProfissaoVM, TipoCatalogo, TipoCurso } from '../shared/qualificacoes';

@Component({ selector: 'app-catalogos', imports: [ReactiveFormsModule, DatePipe], templateUrl: './catalogos.html' })
export class CatalogosComponent {
  private readonly api = inject(QualificacoesApi);
  private readonly fb = inject(NonNullableFormBuilder);
  private readonly destroyRef = inject(DestroyRef);
  readonly tipo = signal<TipoCatalogo>('profissoes');
  readonly registros = signal<(ProfissaoVM | CursoVM)[]>([]);
  readonly carregando = signal(false);
  readonly erro = signal('');
  readonly aviso = signal('');
  readonly editando = signal<string | null>(null);
  readonly deslocamento = signal(0);
  readonly busca = this.fb.control('');
  readonly form = this.fb.group({
    nome: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(200)]],
    descricao: ['', [Validators.maxLength(4000)]], codigo_cbo: [''], tipo: this.fb.control<TipoCurso>('tecnico'),
  });
  constructor() { this.recarregar(); }
  selecionar(tipo: TipoCatalogo): void {
    this.tipo.set(tipo); this.busca.reset(); this.deslocamento.set(0); this.novo(); this.recarregar();
  }
  pesquisar(): void { this.deslocamento.set(0); this.recarregar(); }
  paginar(delta: number): void {
    this.deslocamento.update((n) => Math.max(0, n + delta * 50)); this.recarregar();
  }
  recarregar(): void {
    this.carregando.set(true); this.erro.set('');
    this.api.catalogos(this.tipo(), this.deslocamento(), this.busca.value.trim())
      .pipe(takeUntilDestroyed(this.destroyRef), finalize(() => this.carregando.set(false)))
      .subscribe({ next: (r) => this.registros.set(r.data), error: (e: unknown) => {
        this.registros.set([]); this.erro.set(mensagemErro(e));
      } });
  }
  novo(): void { this.editando.set(null); this.form.reset({ tipo: 'tecnico' }); }
  editar(registro: ProfissaoVM | CursoVM): void {
    this.editando.set(registro.id);
    this.form.setValue({ nome: registro.nome, descricao: registro.descricao ?? '',
      codigo_cbo: 'codigo_cbo' in registro ? registro.codigo_cbo ?? '' : '',
      tipo: 'tipo' in registro ? registro.tipo : 'tecnico' });
  }
  salvar(): void {
    this.form.markAllAsTouched(); if (this.form.invalid) return;
    const f = this.form.getRawValue();
    const base = { nome: f.nome, descricao: f.descricao.trim() || null };
    const operacao: Observable<ApiResponse<ProfissaoVM | CursoVM>> = this.tipo() === 'profissoes'
      ? this.api.salvarCatalogo('profissoes', this.editando(), { ...base, codigo_cbo: f.codigo_cbo.trim() || null })
      : this.api.salvarCatalogo('cursos', this.editando(), { ...base, tipo: f.tipo });
    this.carregando.set(true); this.erro.set(''); this.aviso.set('');
    operacao.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => { this.aviso.set('Catálogo salvo.'); this.novo(); this.recarregar(); },
      error: (e: unknown) => { this.carregando.set(false); this.erro.set(mensagemErro(e)); },
    });
  }
  inativar(registro: ProfissaoVM | CursoVM): void {
    if (!confirm(`Inativar ${registro.nome}? Os vínculos anteriores serão preservados no histórico.`)) return;
    this.carregando.set(true); this.erro.set('');
    this.api.inativarCatalogo(this.tipo(), registro.id).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => { this.aviso.set('Catálogo inativado.'); this.novo(); this.recarregar(); },
      error: (e: unknown) => { this.carregando.set(false); this.erro.set(mensagemErro(e)); },
    });
  }
}
