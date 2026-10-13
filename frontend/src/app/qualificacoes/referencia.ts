import { Component, effect, inject, input, model, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { finalize } from 'rxjs';
import { mensagemErro } from '../core/api';
import { QualificacoesApi } from '../core/qualificacoes-api';
import { ReferenciaVM, TipoReferencia } from '../shared/qualificacoes';

@Component({
  selector: 'app-referencia', imports: [ReactiveFormsModule],
  template: `
    <label for="referencia-busca">{{ rotuloBusca() }}</label>
    <div class="search-row"><input id="referencia-busca" [formControl]="busca" maxlength="200" [placeholder]="placeholderBusca()">
      <button type="button" class="secondary" (click)="pesquisar()" [disabled]="carregando()">Buscar</button></div>
    <label for="referencia-id">{{ rotuloCadastro() }} *</label>
    <select id="referencia-id" [value]="selecionado()" (change)="escolher($event)" [disabled]="carregando()">
      <option value="">{{ placeholderCadastro() }}</option>
      @if (selecionado() && !opcaoVisivel()) { <option [value]="selecionado()">{{ nomeAtual() || 'Cadastro selecionado' }}</option> }
      @for (opcao of opcoes(); track opcao.id) { <option [value]="opcao.id">{{ opcao.nome }}</option> }
    </select>
    @if (erro()) { <p class="field-error" role="alert">{{ erro() }}</p> }
    <div class="pagination"><button type="button" class="text-button" (click)="paginar(-1)" [disabled]="deslocamento() === 0 || carregando()">Anterior</button>
      <small>Página {{ deslocamento() / 50 + 1 }}</small><button type="button" class="text-button" (click)="paginar(1)" [disabled]="opcoes().length < 50 || carregando()">Próxima</button></div>
  `,
})
export class ReferenciaComponent {
  private readonly api = inject(QualificacoesApi);
  readonly tipo = input.required<TipoReferencia>();
  readonly nomeAtual = input('');
  readonly selecionado = model('');
  readonly busca = new FormControl('', { nonNullable: true });
  readonly opcoes = signal<ReferenciaVM[]>([]);
  readonly carregando = signal(false);
  readonly erro = signal('');
  readonly deslocamento = signal(0);
  private versao = 0;
  constructor() {
    effect(() => {
      const tipo = this.tipo();
      this.busca.reset(); this.deslocamento.set(0);
      this.carregar(tipo, 0);
    });
  }
  rotuloCadastro(): string {
    switch (this.tipo()) {
      case 'instituicoes': return 'Instituição';
      case 'profissoes': return 'Profissão';
      case 'cursos': return 'Curso';
      default: return 'Instituição, profissão ou curso';
    }
  }
  placeholderCadastro(): string {
    switch (this.tipo()) {
      case 'instituicoes': return 'Selecione uma instituição';
      case 'profissoes': return 'Selecione uma profissão';
      case 'cursos': return 'Selecione um curso';
      default: return 'Selecione um cadastro';
    }
  }
  rotuloBusca(): string {
    switch (this.tipo()) {
      case 'instituicoes': return 'Buscar instituição no catálogo (mínimo dois caracteres)';
      case 'profissoes': return 'Buscar profissão no catálogo (mínimo dois caracteres)';
      case 'cursos': return 'Buscar curso no catálogo (mínimo dois caracteres)';
      default: return 'Buscar no catálogo (mínimo dois caracteres)';
    }
  }
  placeholderBusca(): string {
    switch (this.tipo()) {
      case 'instituicoes': return 'Filtrar instituições pelo nome...';
      case 'profissoes': return 'Filtrar profissões pelo nome...';
      case 'cursos': return 'Filtrar cursos pelo nome...';
      default: return 'Filtrar catálogo...';
    }
  }
  opcaoVisivel(): boolean { return this.opcoes().some((o) => o.id === this.selecionado()); }
  escolher(evento: Event): void {
    if (evento.target instanceof HTMLSelectElement) this.selecionado.set(evento.target.value);
  }
  pesquisar(): void { this.deslocamento.set(0); this.carregar(this.tipo(), 0); }
  paginar(delta: number): void {
    this.deslocamento.update((n) => Math.max(0, n + delta * 50)); this.carregar(this.tipo(), this.deslocamento());
  }
  private carregar(tipo: TipoReferencia, deslocamento: number): void {
    const versao = ++this.versao;
    this.carregando.set(true); this.erro.set('');
    this.api.referencias(tipo, deslocamento, this.busca.value.trim()).pipe(finalize(() => {
      if (versao === this.versao) this.carregando.set(false);
    })).subscribe({
      next: (r) => { if (versao === this.versao) this.opcoes.set(r.data); },
      error: (e: unknown) => { if (versao === this.versao) { this.opcoes.set([]); this.erro.set(mensagemErro(e)); } },
    });
  }
}
