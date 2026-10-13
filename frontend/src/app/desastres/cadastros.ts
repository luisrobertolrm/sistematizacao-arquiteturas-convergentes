import { DatePipe } from '@angular/common';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { mensagemErro } from '../core/api';
import { DesastresApi } from '../core/desastres-api';
import { ReferenciaRecursoComponent } from '../recursos/referencia';
import { ApiResponse } from '../shared/contratos';
import { ClassificacaoRascunho, DesastreInput, DesastreVM, SituacaoDesastre, TipoDesastreInput, TipoDesastreVM } from '../shared/desastres';
import { AreasComponent } from './areas';

function dataLocal(iso: string): string { const data = new Date(iso); return new Date(data.getTime() - data.getTimezoneOffset() * 60000).toISOString().slice(0, 16); }

@Component({ selector: 'app-desastres', imports: [ReactiveFormsModule, DatePipe, ReferenciaRecursoComponent, AreasComponent], templateUrl: './cadastros.html' })
export class DesastresComponent {
  private readonly api = inject(DesastresApi); private readonly fb = inject(NonNullableFormBuilder); private readonly destroyRef = inject(DestroyRef);
  readonly aba = signal<'tipos' | 'ocorrencias'>('ocorrencias');
  readonly tipos = signal<TipoDesastreVM[]>([]); readonly ocorrencias = signal<DesastreVM[]>([]);
  readonly carregando = signal(false); readonly erro = signal(''); readonly aviso = signal('');
  readonly editando = signal<string | null>(null); readonly historico = signal(false); readonly deslocamento = signal(0);
  readonly ocorrenciaSelecionada = signal<DesastreVM | null>(null);
  readonly coordenadora = signal(''); readonly coordenadoraNome = signal('');
  readonly tipoEscolhido = signal(''); readonly tipoNome = signal('');
  readonly classificacoes = signal<ClassificacaoRascunho[]>([]); readonly busca = this.fb.control('');
  readonly form = this.fb.group({ codigo: [''], nome: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(200)]], descricao: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(4000)]], inicio: [''], encerramento: [''], situacao: this.fb.control<SituacaoDesastre>('em_monitoramento') });
  private versao = 0;
  constructor() { this.configurar(); this.novo(); this.recarregar(); }
  private configurar(): void {
    this.form.controls.codigo.setValidators(this.aba() === 'tipos' ? [Validators.required, Validators.pattern(/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,49}$/)] : []);
    this.form.controls.inicio.setValidators(this.aba() === 'ocorrencias' ? [Validators.required] : []);
    this.form.controls.codigo.updateValueAndValidity(); this.form.controls.inicio.updateValueAndValidity();
  }
  selecionar(aba: 'tipos' | 'ocorrencias'): void { this.aba.set(aba); this.ocorrenciaSelecionada.set(null); this.historico.set(false); this.deslocamento.set(0); this.busca.reset(); this.configurar(); this.novo(); this.recarregar(); }
  novo(): void {
    this.editando.set(null); this.coordenadora.set(''); this.coordenadoraNome.set(''); this.tipoEscolhido.set(''); this.tipoNome.set(''); this.classificacoes.set([]);
    this.form.reset({ inicio: dataLocal(new Date().toISOString()), situacao: 'em_monitoramento' });
  }
  adicionarTipo(): void {
    const id = this.tipoEscolhido();
    if (!id || this.classificacoes().some(c => c.id_tipo_desastre === id) || this.classificacoes().length >= 20) { this.erro.set('Selecione um tipo distinto; limite de 20 por ocorrência.'); return; }
    this.classificacoes.update(c => [...c, { id_tipo_desastre: id, tipo_nome: this.tipoNome(), principal: c.length === 0, tipo_inativo: false }]);
    this.erro.set(''); this.tipoEscolhido.set(''); this.tipoNome.set('');
  }
  principal(id: string): void { this.classificacoes.update(c => c.map(t => ({ ...t, principal: t.id_tipo_desastre === id }))); }
  removerTipo(id: string): void {
    this.classificacoes.update(c => {
      const restantes = c.filter(t => t.id_tipo_desastre !== id);
      return restantes.some(t => t.principal) ? restantes : restantes.map((t, i) => ({ ...t, principal: i === 0 }));
    });
  }
  editarTipo(t: TipoDesastreVM): void { this.novo(); this.editando.set(t.id); this.form.patchValue({ codigo: t.codigo, nome: t.nome, descricao: t.descricao }); }
  editar(d: DesastreVM): void {
    this.novo(); this.editando.set(d.id); this.coordenadora.set(d.id_instituicao_coordenadora); this.coordenadoraNome.set(d.coordenadora_nome);
    this.form.patchValue({ nome: d.titulo, descricao: d.descricao, inicio: dataLocal(d.inicio_em), encerramento: d.encerramento_em ? dataLocal(d.encerramento_em) : '', situacao: d.situacao });
    this.classificacoes.set(d.classificacoes.filter(c => !c.inativado_em).map(c => ({ id_tipo_desastre: c.id_tipo_desastre, principal: c.principal, tipo_nome: c.tipo_nome, tipo_inativo: c.tipo_inativo })));
  }
  recarregar(): void {
    const versao = ++this.versao; this.carregando.set(true); this.erro.set('');
    if (this.aba() === 'tipos') {
      this.api.tipos(this.deslocamento(), this.busca.value, this.historico()).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({ next: r => { if (versao === this.versao) { this.tipos.set(r.data); this.carregando.set(false); } }, error: (e: unknown) => this.falha(versao, e) });
    } else {
      this.api.ocorrencias(this.deslocamento(), this.busca.value, this.historico()).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({ next: r => { if (versao === this.versao) { this.ocorrencias.set(r.data); this.carregando.set(false); } }, error: (e: unknown) => this.falha(versao, e) });
    }
  }
  private falha(versao: number, erro: unknown): void { if (versao === this.versao) { this.tipos.set([]); this.ocorrencias.set([]); this.carregando.set(false); this.erro.set(mensagemErro(erro)); } }
  pesquisar(): void { this.deslocamento.set(0); this.recarregar(); }
  paginar(delta: number): void { this.deslocamento.update(n => Math.max(0, n + delta * 50)); this.recarregar(); }
  alternarHistorico(evento: Event): void { if (evento.target instanceof HTMLInputElement) { this.historico.set(evento.target.checked); this.pesquisar(); } }
  salvar(): void {
    this.form.markAllAsTouched(); if (this.form.invalid || this.carregando()) return;
    const f = this.form.getRawValue();
    if (this.aba() === 'tipos') {
      const dados: TipoDesastreInput = { codigo: f.codigo, nome: f.nome, descricao: f.descricao };
      this.executar(this.api.salvarTipo(this.editando(), dados), 'Tipo de desastre salvo.'); return;
    }
    if (!this.coordenadora() || !this.classificacoes().length) { this.erro.set('Selecione a coordenadora e ao menos uma classificação.'); return; }
    if ((f.situacao === 'encerrado') !== !!f.encerramento || (f.encerramento && new Date(f.encerramento) < new Date(f.inicio))) { this.erro.set('Informe encerramento igual ou posterior ao início, somente para situação encerrada.'); return; }
    const dados: DesastreInput = { titulo: f.nome, descricao: f.descricao, inicio_em: new Date(f.inicio).toISOString(), encerramento_em: f.encerramento ? new Date(f.encerramento).toISOString() : null, situacao: f.situacao, id_instituicao_coordenadora: this.coordenadora(), classificacoes: this.classificacoes().map(c => ({ id_tipo_desastre: c.id_tipo_desastre, principal: c.principal })) };
    this.executar(this.api.salvar(this.editando(), dados), 'Ocorrência salva.');
  }
  inativarTipo(t: TipoDesastreVM): void { if (confirm(`Inativar o tipo ${t.nome}?`)) this.executar(this.api.inativarTipo(t.id), 'Tipo inativado.'); }
  inativar(d: DesastreVM): void { if (confirm(`Inativar ${d.titulo}? Áreas e classificações serão preservadas.`)) this.executar(this.api.inativar(d.id), 'Ocorrência inativada.'); }
  private executar(operacao: Observable<ApiResponse<TipoDesastreVM | DesastreVM>>, aviso: string): void {
    this.carregando.set(true); this.erro.set(''); this.aviso.set('');
    operacao.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({ next: () => { this.aviso.set(aviso); this.novo(); this.recarregar(); }, error: (e: unknown) => { this.carregando.set(false); this.erro.set(mensagemErro(e)); } });
  }
  voltar(): void { this.ocorrenciaSelecionada.set(null); this.recarregar(); }
}
