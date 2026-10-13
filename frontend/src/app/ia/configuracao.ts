import { Component, DestroyRef, inject, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { mensagemErro } from '../core/api';
import { OperacaoApi } from '../core/operacao-api';
import { ApiResponse } from '../shared/contratos';
import { BuscaVM, ConexaoInput, ConexaoVM, Finalidade, IndiceVM, ModeloInput, ModeloVM } from '../shared/operacao';
import { SeletorComponent } from '../shared/seletor';

@Component({ selector: 'app-ia-configuracao', imports: [ReactiveFormsModule, DatePipe, DecimalPipe, SeletorComponent], templateUrl: './configuracao.html' })
export class ConfiguracaoIAComponent {
  private readonly api = inject(OperacaoApi); private readonly fb = inject(NonNullableFormBuilder); private readonly destroy = inject(DestroyRef);
  readonly aba = signal<'conexoes' | 'modelos' | 'indices'>('conexoes'); readonly ocupado = signal(false); readonly erro = signal(''); readonly aviso = signal(''); readonly editando = signal<string | null>(null);
  readonly conexoes = signal<ConexaoVM[]>([]); readonly modelos = signal<ModeloVM[]>([]); readonly indices = signal<IndiceVM[]>([]);
  readonly deslocamento = signal(0); readonly busca = this.fb.control(''); readonly historico = this.fb.control(false);
  readonly conexao = this.fb.group({ nome: ['', [Validators.required, Validators.minLength(2)]], url_base: ['', Validators.required], tipo_autenticacao: this.fb.control<'bearer' | 'nenhuma'>('bearer'), token: [''] });
  readonly modelo = this.fb.group({ id_conexao: ['', Validators.required], identificador_modelo: ['', Validators.required], revisao: [''], finalidade: this.fb.control<Finalidade>('embedding'), dimensao: [3], ativo: [false] });
  readonly idModeloIndice = signal(''); readonly idAtividade = signal(''); readonly lote = signal<string[]>([]); readonly texto = this.fb.control('', [Validators.required, Validators.minLength(2)]); readonly resultado = signal<BuscaVM | null>(null);
  constructor() { this.recarregar(); }
  mudar(aba: 'conexoes' | 'modelos' | 'indices'): void { this.aba.set(aba); this.deslocamento.set(0); this.busca.reset(); this.historico.reset(); this.novo(); this.recarregar(); }
  novo(): void { this.editando.set(null); this.conexao.reset({ tipo_autenticacao: 'bearer' }); this.modelo.reset({ finalidade: 'embedding', dimensao: 3, ativo: false }); }
  recarregar(): void {
    this.ocupado.set(true); this.erro.set('');
    const rota = this.aba() === 'conexoes' ? 'conexoes-ia' : this.aba() === 'modelos' ? 'modelos-ia' : 'indices-atividade';
    if (this.aba() === 'conexoes') this.api.listar<ConexaoVM>(rota, this.deslocamento(), this.busca.value.trim(), this.historico.value).subscribe({ next: r => { this.conexoes.set(r.data); this.ocupado.set(false); }, error: (e: unknown) => this.falhar(e) });
    else if (this.aba() === 'modelos') this.api.listar<ModeloVM>(rota, this.deslocamento(), this.busca.value.trim(), this.historico.value).subscribe({ next: r => { this.modelos.set(r.data); this.ocupado.set(false); }, error: (e: unknown) => this.falhar(e) });
    else this.api.listar<IndiceVM>(rota, this.deslocamento()).subscribe({ next: r => { this.indices.set(r.data); this.ocupado.set(false); }, error: (e: unknown) => this.falhar(e) });
  }
  tamanho(): number { return this.aba() === 'conexoes' ? this.conexoes().length : this.aba() === 'modelos' ? this.modelos().length : this.indices().length; }
  pesquisar(): void { this.deslocamento.set(0); this.recarregar(); }
  paginar(delta: number): void { this.deslocamento.update(p => Math.max(0, p + 50 * delta)); this.recarregar(); }
  editarConexao(c: ConexaoVM): void { this.editando.set(c.id); this.conexao.setValue({ nome: c.nome, url_base: c.url_base, tipo_autenticacao: c.tipo_autenticacao, token: '' }); }
  editarModelo(m: ModeloVM): void { this.editando.set(m.id); this.modelo.setValue({ id_conexao: m.id_conexao, identificador_modelo: m.identificador_modelo, revisao: m.revisao ?? '', finalidade: m.finalidade, dimensao: m.dimensao ?? 3, ativo: m.ativo }); }
  salvarConexao(): void {
    if (this.conexao.invalid) return; const f = this.conexao.getRawValue();
    const dados: ConexaoInput = { nome: f.nome, provedor: 'openai_compativel', url_base: f.url_base, tipo_autenticacao: f.tipo_autenticacao, token: f.tipo_autenticacao === 'bearer' ? f.token || null : null };
    this.executar(this.api.salvar<ConexaoInput, ConexaoVM>('conexoes-ia', this.editando(), dados), 'Conexão salva.');
  }
  salvarModelo(): void {
    if (this.modelo.invalid) return; const f = this.modelo.getRawValue();
    const dados: ModeloInput = { ...f, revisao: f.revisao.trim() || null, dimensao: f.finalidade === 'embedding' ? f.dimensao : null };
    this.executar(this.api.salvar<ModeloInput, ModeloVM>('modelos-ia', this.editando(), dados), 'Modelo salvo.');
  }
  inativar(rota: 'conexoes-ia' | 'modelos-ia', id: string): void { if (confirm('Inativar este cadastro?')) this.executar(this.api.inativar(rota, id), 'Cadastro inativado.'); }
  usar(m: ModeloVM): void { this.idModeloIndice.set(m.id); this.mudar('indices'); }
  adicionar(): void { if (this.idAtividade() && !this.lote().includes(this.idAtividade()) && this.lote().length < 50) this.lote.update(v => [...v, this.idAtividade()]); }
  remover(id: string): void { this.lote.update(v => v.filter(x => x !== id)); }
  indexar(): void {
    if (!this.idModeloIndice() || !this.lote().length) return;
    this.executar(this.api.indexar(this.idModeloIndice(), this.lote()), 'Lote indexado. Selecione o modelo após completar a cobertura.');
  }
  buscarSemantica(): void {
    if (this.texto.invalid) return; this.ocupado.set(true); this.erro.set(''); this.resultado.set(null);
    this.api.buscar(this.texto.value).pipe(takeUntilDestroyed(this.destroy)).subscribe({ next: r => { this.resultado.set(r.data); this.ocupado.set(false); }, error: (e: unknown) => this.falhar(e) });
  }
  private executar<T>(op: Observable<ApiResponse<T>>, aviso: string): void {
    this.ocupado.set(true); this.erro.set(''); this.aviso.set('');
    op.pipe(takeUntilDestroyed(this.destroy)).subscribe({ next: () => { this.aviso.set(aviso); this.novo(); this.recarregar(); }, error: (e: unknown) => this.falhar(e) });
  }
  private falhar(e: unknown): void { this.ocupado.set(false); this.erro.set(mensagemErro(e)); }
}
