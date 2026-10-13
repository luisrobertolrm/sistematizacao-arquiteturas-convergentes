import { Component, DestroyRef, effect, inject, input, model, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { finalize } from 'rxjs';
import { mensagemErro } from '../core/api';
import { CapacidadesApi } from '../core/capacidades-api';
import { TipoReferenciaCapacidade } from '../shared/capacidades';
import { ReferenciaVM } from '../shared/qualificacoes';

@Component({
  selector: 'app-referencia-capacidade', imports: [ReactiveFormsModule],
  template: `
    <label [for]="prefixo() + '-busca'">{{ rotulo() }} — buscar por nome ou código</label>
    <div class="search-row"><input [id]="prefixo() + '-busca'" [formControl]="busca" maxlength="200">
      <button type="button" class="secondary" (click)="pesquisar()" [disabled]="carregando()">Buscar referência</button></div>
    <label [for]="prefixo() + '-id'">{{ rotulo() }}</label>
    <select [id]="prefixo() + '-id'" [value]="selecionado()" (change)="escolher($event)" [disabled]="carregando()">
      <option value="">{{ obrigatorio() ? 'Selecione' : 'Não informada' }}</option>
      @if (selecionado() && !opcaoVisivel()) { <option [value]="selecionado()">{{ nomeAtual() || 'Referência selecionada' }}</option> }
      @for (opcao of opcoes(); track opcao.id) { <option [value]="opcao.id">{{ opcao.nome }}</option> }
    </select>
    @if (erro()) { <p class="field-error" role="alert">{{ erro() }}</p> }
    <div class="pagination"><button type="button" class="text-button" (click)="paginar(-1)" [disabled]="carregando() || deslocamento() === 0">Referências anteriores</button>
      <small>Página {{ deslocamento() / 50 + 1 }}</small><button type="button" class="text-button" (click)="paginar(1)" [disabled]="carregando() || opcoes().length < 50">Próximas referências</button></div>
  `,
})
export class ReferenciaCapacidadeComponent {
  private readonly api = inject(CapacidadesApi);
  private readonly destroyRef = inject(DestroyRef);
  readonly tipo = input.required<TipoReferenciaCapacidade>();
  readonly prefixo = input.required<string>();
  readonly rotulo = input.required<string>();
  readonly obrigatorio = input(false);
  readonly nomeAtual = input('');
  readonly selecionado = model('');
  readonly busca = new FormControl('', { nonNullable: true });
  readonly opcoes = signal<ReferenciaVM[]>([]);
  readonly carregando = signal(false);
  readonly erro = signal('');
  readonly deslocamento = signal(0);
  private versao = 0;
  constructor() {
    effect(() => { const tipo = this.tipo(); this.busca.reset(); this.deslocamento.set(0); this.carregar(tipo, 0); });
  }
  opcaoVisivel(): boolean { return this.opcoes().some((o) => o.id === this.selecionado()); }
  escolher(evento: Event): void { if (evento.target instanceof HTMLSelectElement) this.selecionado.set(evento.target.value); }
  pesquisar(): void { this.deslocamento.set(0); this.carregar(this.tipo(), 0); }
  paginar(delta: number): void { this.deslocamento.update((n) => Math.max(0, n + delta * 50)); this.carregar(this.tipo(), this.deslocamento()); }
  private carregar(tipo: TipoReferenciaCapacidade, deslocamento: number): void {
    const versao = ++this.versao; this.carregando.set(true); this.erro.set('');
    this.api.listar(tipo, deslocamento, this.busca.value.trim()).pipe(takeUntilDestroyed(this.destroyRef), finalize(() => {
      if (versao === this.versao) this.carregando.set(false);
    })).subscribe({
      next: (r) => { if (versao === this.versao) this.opcoes.set(r.data); },
      error: (e: unknown) => { if (versao === this.versao) { this.opcoes.set([]); this.erro.set(mensagemErro(e)); } },
    });
  }
}
