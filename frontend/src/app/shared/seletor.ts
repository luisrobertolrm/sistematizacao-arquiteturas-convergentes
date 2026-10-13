import { Component, DestroyRef, effect, inject, input, model, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { OperacaoApi } from '../core/operacao-api';
import { mensagemErro } from '../core/api';
import { OpcaoOperacao } from './operacao';

@Component({ selector: 'app-seletor', imports: [ReactiveFormsModule], template: `
  <label [for]="prefixo() + '-busca'">{{ rotulo() }} — buscar</label>
  <div class="search-row"><input [id]="prefixo() + '-busca'" [formControl]="busca" maxlength="200"><button type="button" (click)="pesquisar()" [disabled]="bloqueado() || carregando()">Buscar opções</button></div>
  <label [for]="prefixo() + '-id'">{{ rotulo() }}</label>
  <select [id]="prefixo() + '-id'" [value]="selecionado()" (change)="escolher($event)" [disabled]="bloqueado() || carregando()"><option value="">Selecione</option>
  @if (selecionado() && !visivel()) { <option [value]="selecionado()">{{ nomeAtual() || 'Referência selecionada' }}</option> }
  @for (o of opcoes(); track o.id) { <option [value]="o.id">{{ nome(o) }}</option> }</select>
  @if (erro()) { <p role="alert" class="field-error">{{ erro() }}</p> }
  <div class="pagination"><button type="button" (click)="paginar(-1)" [disabled]="bloqueado() || carregando() || pagina() === 0">Opções anteriores</button><small>Página {{ pagina() / 50 + 1 }}</small><button type="button" (click)="paginar(1)" [disabled]="bloqueado() || carregando() || opcoes().length < 50">Próximas opções</button></div>
` })
export class SeletorComponent {
  private readonly api = inject(OperacaoApi);
  private readonly destroy = inject(DestroyRef);
  readonly rota = input.required<string>(); readonly prefixo = input.required<string>(); readonly rotulo = input.required<string>();
  readonly bloqueado = input(false); readonly nomeAtual = input(''); readonly selecionado = model('');
  readonly opcoes = signal<OpcaoOperacao[]>([]); readonly pagina = signal(0); readonly carregando = signal(false); readonly erro = signal('');
  readonly busca = new FormControl('', { nonNullable: true }); private versao = 0;
  constructor() { effect(() => { const rota = this.rota(); this.pagina.set(0); this.busca.reset(); this.carregar(rota); }); }
  nome(o: OpcaoOperacao): string { return o.nome ?? o.titulo ?? o.identificador_modelo ?? o.id; }
  visivel(): boolean { return this.opcoes().some(o => o.id === this.selecionado()); }
  escolher(e: Event): void { if (e.target instanceof HTMLSelectElement) this.selecionado.set(e.target.value); }
  pesquisar(): void { this.pagina.set(0); this.carregar(this.rota()); }
  paginar(delta: number): void { this.pagina.update(p => Math.max(0, p + delta * 50)); this.carregar(this.rota()); }
  private carregar(rota: string): void {
    const versao = ++this.versao; this.erro.set(''); this.opcoes.set([]);
    if (!rota) { this.carregando.set(false); return; }
    this.carregando.set(true);
    this.api.listar<OpcaoOperacao>(rota, this.pagina(), this.busca.value.trim()).pipe(takeUntilDestroyed(this.destroy)).subscribe({
      next: r => { if (versao === this.versao) { this.opcoes.set(r.data); this.carregando.set(false); } },
      error: (e: unknown) => { if (versao === this.versao) { this.erro.set(mensagemErro(e)); this.carregando.set(false); } },
    });
  }
}
