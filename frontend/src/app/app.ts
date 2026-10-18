import { Component, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize, Observable } from 'rxjs';
import { CadastrosApi, mensagemErro, Sessao } from './core/api';
import {
  ApiResponse,
  CadastroPublicoPessoaInput,
  CadastroVM,
  ContatoInput,
  InstituicaoInput,
  InstituicaoVM,
  PessoaVM,
  SituacaoCadastral,
  TipoInstituicao,
} from './shared/contratos';
import { CatalogosComponent } from './qualificacoes/catalogos';
import { VinculosComponent } from './qualificacoes/vinculos';
import { CapacidadesComponent } from './capacidades/catalogos';
import { RecursosComponent } from './recursos/cadastros';
import { DesastresComponent } from './desastres/cadastros';
import { ConfiguracaoIAComponent } from './ia/configuracao';
import { DemandasComponent } from './demandas/cadastros';

type Secao = 'cadastros' | 'catalogos' | 'capacidades' | 'recursos' | 'desastres' | 'ia' | 'demandas';
const PAGINAS: Record<Exclude<Secao, 'cadastros'>, { titulo: string; descricao: string }> = {
  catalogos: { titulo: 'Profissões e cursos', descricao: 'Organize os catálogos de formação e qualificação da rede.' },
  capacidades: { titulo: 'Atividades e unidades', descricao: 'Mantenha o catálogo de serviços, categorias e unidades de capacidade.' },
  recursos: { titulo: 'Recursos e ofertas', descricao: 'Conheça os bens, insumos e serviços oferecidos por pessoas e instituições.' },
  desastres: { titulo: 'Desastres e áreas', descricao: 'Registre ocorrências, delimite as áreas afetadas e acompanhe suas avaliações.' },
  ia: { titulo: 'Configuração de IA', descricao: 'Gerencie conexões e modelos, prepare os índices e consulte atividades por significado.' },
  demandas: { titulo: 'Demandas e recomendações', descricao: 'Registre necessidades das áreas e analise sugestões para apoiar a decisão administrativa.' },
};

@Component({ selector: 'app-root', imports: [ReactiveFormsModule, DatePipe, CatalogosComponent, VinculosComponent, CapacidadesComponent, RecursosComponent, DesastresComponent, ConfiguracaoIAComponent, DemandasComponent], templateUrl: './app.html' })
export class App {
  readonly sessao = inject(Sessao);
  private readonly api = inject(CadastrosApi);
  private readonly fb = inject(NonNullableFormBuilder);
  readonly aba = signal<'instituicoes' | 'pessoas'>('instituicoes');
  readonly secao = signal<Secao>('cadastros');
  readonly menuAberto = signal(false);
  readonly telaPublica = signal<'inicio' | 'cadastro'>('inicio');
  readonly pessoaSelecionada = signal<CadastroVM | null>(null);
  readonly registros = signal<readonly CadastroVM[]>([]);
  readonly carregando = signal(false);
  readonly gerandoToken = signal(false);
  readonly cadastrandoPublico = signal(false);
  readonly verificandoEmail = signal(false);
  readonly cadastroPublicoRecente = signal<PessoaVM | null>(null);
  readonly erro = signal('');
  readonly aviso = signal('');
  readonly editando = signal<string | null>(null);
  readonly deslocamento = signal(0);
  readonly titulo = computed(() => this.aba() === 'instituicoes' ? 'Instituições' : 'Pessoas');
  readonly tituloPagina = computed(() => {
    if (!this.sessao.token()) return 'Uma rede de capacidades para apoiar a resposta.';
    const secao = this.secao();
    return secao === 'cadastros' ? this.titulo() : PAGINAS[secao].titulo;
  });
  readonly descricaoPagina = computed(() => {
    if (!this.sessao.token()) return 'Conecte instituições, pessoas e recursos às necessidades das localidades afetadas.';
    const secao = this.secao();
    return secao === 'cadastros'
      ? 'Mantenha os cadastros e suas informações para conhecer quem participa da rede.'
      : PAGINAS[secao].descricao;
  });
  readonly acesso = this.fb.control('', [Validators.required]);
  readonly formPublico = this.fb.group({
    nome: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(200)]],
    email_contato: ['', [Validators.required, Validators.email, Validators.maxLength(320)]],
    telefone_contato: [''],
    municipio_codigo_ibge: ['3550308', [Validators.required, Validators.pattern(/^[0-9]{7}$/)]],
    uf: ['SP', [Validators.required]],
  });
  readonly emailVerificacao = this.fb.control('', [Validators.required, Validators.email, Validators.maxLength(320)]);
  readonly form = this.fb.group({
    nome: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(200)]],
    municipio_codigo_ibge: ['', [Validators.required, Validators.pattern(/^[0-9]{7}$/)]],
    uf: ['SP', [Validators.required]], email_contato: [''], telefone_contato: [''],
    latitude: [''], longitude: [''], situacao_cadastral: this.fb.control<SituacaoCadastral>('pendente'),
    tipo: this.fb.control<TipoInstituicao>('associacao'), cnpj: [''], razao_social: [''], descricao: [''],
  });

  gerarTokenAdmin(): void {
    this.erro.set(''); this.aviso.set(''); this.gerandoToken.set(true);
    this.api.gerarTokenAdmin().pipe(finalize(() => this.gerandoToken.set(false))).subscribe({
      next: (r) => {
        this.acesso.setValue(r.data.token);
        this.aviso.set('Token administrativo gerado e preenchido no campo.');
      },
      error: (e: unknown) => this.erro.set(mensagemErro(e)),
    });
  }
  autocadastrar(): void {
    this.formPublico.markAllAsTouched();
    if (this.formPublico.invalid) return;
    const f = this.formPublico.getRawValue();
    const dados: CadastroPublicoPessoaInput = {
      nome: f.nome.trim(),
      municipio_codigo_ibge: f.municipio_codigo_ibge.trim(),
      uf: f.uf.trim().toUpperCase(),
      email_contato: f.email_contato.trim(),
      telefone_contato: f.telefone_contato.trim() || null,
      latitude: null,
      longitude: null,
    };
    this.erro.set(''); this.aviso.set(''); this.cadastrandoPublico.set(true);
    this.api.autocadastrarPessoa(dados).pipe(finalize(() => this.cadastrandoPublico.set(false))).subscribe({
      next: (r) => {
        this.cadastroPublicoRecente.set(r.data);
        this.emailVerificacao.setValue(r.data.email_contato ?? dados.email_contato);
        this.formPublico.reset({ municipio_codigo_ibge: '3550308', uf: 'SP' });
        this.aviso.set('Cadastro realizado com situação pendente. Confirme seu e-mail para validar.');
      },
      error: (e: unknown) => this.erro.set(mensagemErro(e)),
    });
  }
  verificarEmail(): void {
    this.emailVerificacao.markAllAsTouched();
    if (this.emailVerificacao.invalid) return;
    const email = this.emailVerificacao.value.trim();
    this.erro.set(''); this.aviso.set(''); this.verificandoEmail.set(true);
    this.api.verificarEmailPessoa({ email_contato: email }).pipe(finalize(() => this.verificandoEmail.set(false))).subscribe({
      next: (r) => {
        this.cadastroPublicoRecente.set(r.data);
        this.aviso.set('E-mail verificado com sucesso! Situação cadastral validada.');
      },
      error: (e: unknown) => this.erro.set(mensagemErro(e)),
    });
  }
  abrirCadastroPublico(): void {
    this.telaPublica.set('cadastro'); this.erro.set(''); this.aviso.set('');
  }
  voltarInicio(): void {
    this.telaPublica.set('inicio'); this.erro.set(''); this.aviso.set('');
    this.cadastroPublicoRecente.set(null);
  }
  conectar(): void {
    if (this.acesso.invalid) return;
    this.sessao.token.set(this.acesso.value.trim());
    this.acesso.reset();
    this.recarregar();
  }
  desconectar(): void {
    this.menuAberto.set(false);
    this.secao.set('cadastros'); this.pessoaSelecionada.set(null); this.telaPublica.set('inicio');
    this.sessao.desconectar(); this.registros.set([]); this.erro.set(''); this.aviso.set(''); this.novo();
  }

  selecionar(aba: 'instituicoes' | 'pessoas'): void {
    this.menuAberto.set(false);
    this.secao.set('cadastros'); this.pessoaSelecionada.set(null);
    this.aba.set(aba); this.deslocamento.set(0); this.registros.set([]); this.novo();
    if (this.sessao.token()) this.recarregar();
  }
  abrirCatalogos(): void { this.menuAberto.set(false); this.secao.set('catalogos'); this.pessoaSelecionada.set(null); this.erro.set(''); this.aviso.set(''); }
  abrirCapacidades(): void { this.menuAberto.set(false); this.secao.set('capacidades'); this.pessoaSelecionada.set(null); this.erro.set(''); this.aviso.set(''); }
  abrirRecursos(): void { this.menuAberto.set(false); this.secao.set('recursos'); this.pessoaSelecionada.set(null); this.erro.set(''); this.aviso.set(''); }
  abrirDesastres(): void { this.menuAberto.set(false); this.secao.set('desastres'); this.pessoaSelecionada.set(null); this.erro.set(''); this.aviso.set(''); }
  abrirIA(): void { this.menuAberto.set(false); this.secao.set('ia'); this.erro.set(''); this.aviso.set(''); }
  abrirDemandas(): void { this.menuAberto.set(false); this.secao.set('demandas'); this.erro.set(''); this.aviso.set(''); }
  abrirVinculos(pessoa: CadastroVM): void { this.pessoaSelecionada.set(pessoa); this.erro.set(''); this.aviso.set(''); }
  recarregar(): void {
    this.erro.set(''); this.carregando.set(true);
    const consulta: Observable<ApiResponse<CadastroVM[]>> = this.aba() === 'instituicoes'
      ? this.api.listarInstituicoes(this.deslocamento()) : this.api.listarPessoas(this.deslocamento());
    consulta.pipe(finalize(() => this.carregando.set(false))).subscribe({
      next: (r) => this.registros.set(r.data), error: (e: unknown) => { this.registros.set([]); this.erro.set(mensagemErro(e)); },
    });
  }
  paginar(delta: number): void {
    this.deslocamento.update((n) => Math.max(0, n + delta * 50)); this.recarregar();
  }
  novo(): void {
    this.editando.set(null);
    this.form.reset({ uf: 'SP', situacao_cadastral: 'pendente', tipo: 'associacao' });
  }
  editar(registro: CadastroVM): void {
    this.editando.set(registro.id);
    const instituicao: InstituicaoVM | null = 'tipo' in registro ? registro as InstituicaoVM : null;
    this.form.setValue({
      nome: registro.nome, municipio_codigo_ibge: registro.municipio_codigo_ibge, uf: registro.uf,
      email_contato: registro.email_contato ?? '', telefone_contato: registro.telefone_contato ?? '',
      latitude: registro.latitude ?? '', longitude: registro.longitude ?? '', situacao_cadastral: registro.situacao_cadastral,
      tipo: instituicao?.tipo ?? 'associacao', cnpj: instituicao?.cnpj ?? '',
      razao_social: instituicao?.razao_social ?? '', descricao: instituicao?.descricao ?? '',
    });
    document.getElementById('cadastro-nome')?.focus();
  }
  salvar(): void {
    this.form.markAllAsTouched();
    if (this.form.invalid || !this.sessao.token()) return;
    const f = this.form.getRawValue();
    const contato: ContatoInput = {
      nome: f.nome, municipio_codigo_ibge: f.municipio_codigo_ibge, uf: f.uf,
      email_contato: f.email_contato.trim() || null, telefone_contato: f.telefone_contato.trim() || null,
      latitude: f.latitude.trim() || null, longitude: f.longitude.trim() || null, situacao_cadastral: f.situacao_cadastral,
    };
    const instituicao: InstituicaoInput = { ...contato, tipo: f.tipo, cnpj: f.cnpj.trim() || null,
      razao_social: f.razao_social.trim() || null, descricao: f.descricao.trim() || null };
    const operacao: Observable<ApiResponse<CadastroVM>> = this.aba() === 'instituicoes'
      ? this.api.salvarInstituicao(this.editando(), instituicao) : this.api.salvarPessoa(this.editando(), contato);
    this.carregando.set(true); this.erro.set(''); this.aviso.set('');
    operacao.subscribe({
      next: () => { this.aviso.set('Cadastro salvo.'); this.novo(); this.recarregar(); },
      error: (e: unknown) => { this.carregando.set(false); this.erro.set(mensagemErro(e)); },
    });
  }
  inativar(registro: CadastroVM): void {
    if (!confirm(`Inativar o cadastro de ${registro.nome}? O histórico será preservado.`)) return;
    this.carregando.set(true); this.erro.set('');
    this.api.inativar(this.aba(), registro.id).subscribe({
      next: () => { this.aviso.set('Cadastro inativado.'); this.novo(); this.recarregar(); },
      error: (e: unknown) => { this.carregando.set(false); this.erro.set(mensagemErro(e)); },
    });
  }
}
