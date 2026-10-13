import { DatePipe } from '@angular/common';
import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { mensagemErro } from '../core/api';
import { RecursosApi } from '../core/recursos-api';
import { ApiResponse, SituacaoCadastral } from '../shared/contratos';
import { CadastroRecursoVM, CategoriaRecurso, EstadoRecurso, ModoControle, OfertaAtividadeInput, OfertaAtividadeVM, RecursoInput, RecursoVM, TipoCadastroRecurso, TipoRecursoInput } from '../shared/recursos';
import { ReferenciaRecursoComponent } from './referencia';
import { OfertaRecursosComponent } from './vinculos';

@Component({ selector: 'app-recursos', imports: [ReactiveFormsModule, DatePipe, ReferenciaRecursoComponent, OfertaRecursosComponent], templateUrl: './cadastros.html' })
export class RecursosComponent {
  private readonly api = inject(RecursosApi);
  private readonly fb = inject(NonNullableFormBuilder);
  private readonly destroyRef = inject(DestroyRef);
  readonly tipo = signal<TipoCadastroRecurso>('tipos-recurso');
  readonly titulo = computed(() => ({ 'tipos-recurso': 'Tipos de recurso', recursos: 'Recursos', 'ofertas-atividade': 'Ofertas de atividades' })[this.tipo()]);
  readonly registros = signal<CadastroRecursoVM[]>([]);
  readonly carregando = signal(false);
  readonly erro = signal(''); readonly aviso = signal('');
  readonly historico = signal(false); readonly deslocamento = signal(0);
  readonly editando = signal<string | null>(null);
  readonly ofertaSelecionada = signal<OfertaAtividadeVM | null>(null);
  readonly referencia = signal(''); readonly referenciaNome = signal('');
  readonly responsavel = signal(''); readonly responsavelNome = signal('');
  readonly tipoResponsavel = signal<'instituicoes' | 'pessoas'>('instituicoes');
  readonly busca = this.fb.control('');
  readonly form = this.fb.group({
    nome: [''], descricao: ['', Validators.maxLength(4000)],
    categoria: this.fb.control<CategoriaRecurso>('equipamento'), modo_controle: this.fb.control<ModoControle>('individual'),
    identificacao: ['', Validators.maxLength(200)], quantidade_total: ['1'],
    estado_operacional: this.fb.control<EstadoRecurso>('operacional'), municipio: [''],
    latitude: [''], longitude: [''], capacidade_declarada: [''],
    situacao_validacao: this.fb.control<SituacaoCadastral>('pendente'),
  });
  private versao = 0;
  constructor() { this.configurarValidacao(); this.recarregar(); }
  private configurarValidacao(): void {
    const tipo = this.tipo();
    this.form.controls.nome.setValidators(tipo === 'ofertas-atividade' ? [] : [Validators.required, Validators.minLength(2), Validators.maxLength(200)]);
    this.form.controls.municipio.setValidators(tipo === 'tipos-recurso' ? [] : [Validators.required, Validators.pattern(/^[0-9]{7}$/)]);
    this.form.controls.quantidade_total.setValidators(tipo === 'recursos' ? [Validators.required, Validators.pattern(/^\d{1,14}(\.\d{1,4})?$/)] : []);
    this.form.controls.capacidade_declarada.setValidators([Validators.pattern(/^\d{1,14}(\.\d{1,4})?$/)]);
    for (const controle of Object.values(this.form.controls)) controle.updateValueAndValidity();
  }
  selecionar(tipo: TipoCadastroRecurso): void {
    this.tipo.set(tipo); this.ofertaSelecionada.set(null); this.historico.set(false);
    this.busca.reset(); this.deslocamento.set(0); this.registros.set([]);
    this.configurarValidacao(); this.novo(); this.recarregar();
  }
  novo(): void {
    this.editando.set(null); this.referencia.set(''); this.referenciaNome.set('');
    this.responsavel.set(''); this.responsavelNome.set(''); this.tipoResponsavel.set('instituicoes');
    this.form.reset({ categoria: 'equipamento', modo_controle: 'individual', quantidade_total: '1', estado_operacional: 'operacional', situacao_validacao: 'pendente' });
  }
  mudarResponsavel(evento: Event): void {
    if (evento.target instanceof HTMLSelectElement) {
      this.tipoResponsavel.set(evento.target.value === 'pessoas' ? 'pessoas' : 'instituicoes');
      this.responsavel.set(''); this.responsavelNome.set('');
    }
  }
  recurso(r: CadastroRecursoVM): RecursoVM | null { return 'tipo_recurso_id' in r ? r : null; }
  oferta(r: CadastroRecursoVM): OfertaAtividadeVM | null { return 'atividade_id' in r ? r : null; }
  nome(r: CadastroRecursoVM): string { return 'nome' in r ? r.nome : r.atividade_nome; }
  editar(r: CadastroRecursoVM): void {
    this.novo(); this.editando.set(r.id);
    if ('id_unidade_medida' in r) {
      this.referencia.set(r.id_unidade_medida); this.referenciaNome.set(r.unidade_nome);
      this.form.patchValue({ nome: r.nome, descricao: r.descricao ?? '', categoria: r.categoria, modo_controle: r.modo_controle });
    } else {
      this.tipoResponsavel.set(r.instituicao_id ? 'instituicoes' : 'pessoas');
      this.responsavel.set(r.instituicao_id ?? r.pessoa_id ?? ''); this.responsavelNome.set(r.responsavel_nome);
      if ('tipo_recurso_id' in r) {
        this.referencia.set(r.tipo_recurso_id); this.referenciaNome.set(r.tipo_recurso_nome);
        this.form.patchValue({ nome: r.nome, descricao: r.descricao ?? '', identificacao: r.identificacao ?? '', quantidade_total: r.quantidade_total, estado_operacional: r.estado_operacional, municipio: r.municipio_codigo_ibge, latitude: r.latitude ?? '', longitude: r.longitude ?? '' });
      } else {
        this.referencia.set(r.atividade_id); this.referenciaNome.set(r.atividade_nome);
        this.form.patchValue({ descricao: r.descricao_complementar ?? '', municipio: r.municipio_atendimento_codigo_ibge, capacidade_declarada: r.capacidade_declarada ?? '', situacao_validacao: r.situacao_validacao });
      }
    }
  }
  recarregar(): void {
    const versao = ++this.versao; this.carregando.set(true); this.erro.set('');
    this.api.listar(this.tipo(), this.deslocamento(), this.busca.value, this.historico()).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (r) => { if (versao === this.versao) { this.registros.set(r.data); this.carregando.set(false); } },
      error: (e: unknown) => { if (versao === this.versao) { this.registros.set([]); this.carregando.set(false); this.erro.set(mensagemErro(e)); } },
    });
  }
  pesquisar(): void { this.deslocamento.set(0); this.recarregar(); }
  paginar(delta: number): void { this.deslocamento.update(n => Math.max(0, n + delta * 50)); this.recarregar(); }
  alternarHistorico(evento: Event): void { if (evento.target instanceof HTMLInputElement) { this.historico.set(evento.target.checked); this.pesquisar(); } }
  salvar(): void {
    this.form.markAllAsTouched(); if (this.form.invalid || this.carregando()) return;
    if (!this.referencia() || (this.tipo() !== 'tipos-recurso' && !this.responsavel())) { this.erro.set('Selecione a referência e o responsável exigidos.'); return; }
    const f = this.form.getRawValue();
    const dono = { instituicao_id: this.tipoResponsavel() === 'instituicoes' ? this.responsavel() : null, pessoa_id: this.tipoResponsavel() === 'pessoas' ? this.responsavel() : null };
    let operacao: Observable<ApiResponse<CadastroRecursoVM>>;
    if (this.tipo() === 'tipos-recurso') {
      const dados: TipoRecursoInput = { nome: f.nome, descricao: f.descricao.trim() || null, categoria: f.categoria, modo_controle: f.modo_controle, id_unidade_medida: this.referencia() };
      operacao = this.api.salvar('tipos-recurso', this.editando(), dados);
    } else if (this.tipo() === 'recursos') {
      const dados: RecursoInput = { ...dono, nome: f.nome, descricao: f.descricao.trim() || null, tipo_recurso_id: this.referencia(), identificacao: f.identificacao.trim() || null, quantidade_total: f.quantidade_total, estado_operacional: f.estado_operacional, municipio_codigo_ibge: f.municipio, latitude: f.latitude.trim() || null, longitude: f.longitude.trim() || null };
      operacao = this.api.salvar('recursos', this.editando(), dados);
    } else {
      const dados: OfertaAtividadeInput = { ...dono, atividade_id: this.referencia(), municipio_atendimento_codigo_ibge: f.municipio, descricao_complementar: f.descricao.trim() || null, capacidade_declarada: f.capacidade_declarada.trim() || null, situacao_validacao: f.situacao_validacao };
      operacao = this.api.salvar('ofertas-atividade', this.editando(), dados);
    }
    this.executar(operacao, 'Cadastro salvo.');
  }
  inativar(r: CadastroRecursoVM): void {
    if (this.carregando() || !confirm(`Inativar ${this.nome(r)}? O histórico será preservado.`)) return;
    this.executar(this.api.inativar(this.tipo(), r.id), 'Cadastro inativado.');
  }
  private executar(operacao: Observable<ApiResponse<CadastroRecursoVM>>, aviso: string): void {
    this.carregando.set(true); this.erro.set(''); this.aviso.set('');
    operacao.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => { this.aviso.set(aviso); this.novo(); this.recarregar(); },
      error: (e: unknown) => { this.carregando.set(false); this.erro.set(mensagemErro(e)); },
    });
  }
  voltar(): void { this.ofertaSelecionada.set(null); this.recarregar(); }
}
