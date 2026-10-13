import { Component, DestroyRef, inject, input, OnInit, output, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, ReactiveFormsModule } from '@angular/forms';
import { finalize, Observable } from 'rxjs';
import { mensagemErro } from '../core/api';
import { QualificacoesApi } from '../core/qualificacoes-api';
import { ApiResponse, CadastroVM, SituacaoCadastral } from '../shared/contratos';
import { QualificacaoVM, TipoReferencia, TipoVinculo } from '../shared/qualificacoes';
import { ReferenciaComponent } from './referencia';

const NOMES_CAMPOS: Record<string, string> = {
  inicio_em: 'Início',
  fim_em: 'Encerramento',
  tipo_vinculo: 'Tipo de vínculo',
  registro_profissional: 'Registro profissional',
  orgao_registro: 'Órgão de registro',
  uf_registro: 'UF do registro',
  validade_em: 'Validade',
  instituicao_emissora: 'Instituição emissora',
  conclusao_em: 'Conclusão',
  carga_horaria: 'Carga horária',
  comprovante_referencia: 'Referência do comprovante',
  situacao_validacao: 'Situação da validação',
};

const CAMPOS_POR_TIPO: Record<TipoReferencia, string[]> = {
  instituicoes: ['tipo_vinculo', 'inicio_em', 'fim_em', 'situacao_validacao'],
  profissoes: ['registro_profissional', 'orgao_registro', 'uf_registro', 'validade_em', 'situacao_validacao'],
  cursos: ['instituicao_emissora', 'conclusao_em', 'validade_em', 'carga_horaria', 'comprovante_referencia', 'situacao_validacao'],
};

@Component({ selector: 'app-vinculos', imports: [ReactiveFormsModule, DatePipe, ReferenciaComponent], templateUrl: './vinculos.html' })
export class VinculosComponent implements OnInit {
  private readonly api = inject(QualificacoesApi);
  private readonly fb = inject(NonNullableFormBuilder);
  private readonly destroyRef = inject(DestroyRef);
  readonly pessoa = input.required<CadastroVM>();
  readonly voltar = output<void>();
  readonly tipo = signal<TipoReferencia>('instituicoes');
  readonly registros = signal<QualificacaoVM[]>([]);
  readonly historico = signal(false);
  readonly carregando = signal(false);
  readonly erro = signal('');
  readonly aviso = signal('');
  readonly editando = signal<string | null>(null);
  readonly tentouSalvar = signal(false);
  readonly referencia = signal('');
  readonly referenciaNome = signal('');
  readonly deslocamento = signal(0);
  private avisoTimeout: ReturnType<typeof setTimeout> | null = null;
  readonly form = this.fb.group({
    situacao_validacao: this.fb.control<SituacaoCadastral>('pendente'),
    tipo_vinculo: this.fb.control<TipoVinculo>('voluntario'), inicio_em: [''], fim_em: [''],
    registro_profissional: [''], orgao_registro: [''], uf_registro: [''], validade_em: [''],
    instituicao_emissora: [''], conclusao_em: [''], carga_horaria: [''], comprovante_referencia: [''],
  });
  ngOnInit(): void { this.recarregar(); }
  selecionar(tipo: TipoReferencia): void {
    this.tipo.set(tipo); this.deslocamento.set(0); this.novo(); this.recarregar();
  }
  alternarHistorico(): void {
    this.historico.update((v) => !v); this.deslocamento.set(0); this.recarregar();
  }
  paginar(delta: number): void {
    this.deslocamento.update((n) => Math.max(0, n + delta * 50)); this.recarregar();
  }
  mostrarAviso(msg: string): void {
    this.aviso.set(msg);
    if (this.avisoTimeout) clearTimeout(this.avisoTimeout);
    this.avisoTimeout = setTimeout(() => {
      this.aviso.set('');
    }, 4500);
  }
  fecharAviso(): void {
    if (this.avisoTimeout) clearTimeout(this.avisoTimeout);
    this.aviso.set('');
  }
  recarregar(): void {
    this.carregando.set(true); this.erro.set('');
    this.api.vinculos(this.pessoa().id, this.tipo(), this.deslocamento(), this.historico())
      .pipe(takeUntilDestroyed(this.destroyRef), finalize(() => this.carregando.set(false))).subscribe({
        next: (r) => this.registros.set(r.data), error: (e: unknown) => { this.registros.set([]); this.erro.set(mensagemErro(e)); },
      });
  }
  novo(): void {
    this.tentouSalvar.set(false);
    this.editando.set(null); this.referencia.set(''); this.referenciaNome.set('');
    this.form.reset({ situacao_validacao: 'pendente', tipo_vinculo: 'voluntario' });
    this.form.markAsPristine();
    this.form.markAsUntouched();
  }
  editar(registro: QualificacaoVM): void {
    this.novo(); this.editando.set(registro.id); this.referenciaNome.set(registro.referencia_nome);
    this.form.patchValue({ situacao_validacao: registro.situacao_validacao });
    if ('instituicao_id' in registro) {
      this.referencia.set(registro.instituicao_id);
      this.form.patchValue({ tipo_vinculo: registro.tipo_vinculo, inicio_em: registro.inicio_em, fim_em: registro.fim_em ?? '' });
    } else if ('profissao_id' in registro) {
      this.referencia.set(registro.profissao_id);
      this.form.patchValue({ registro_profissional: registro.registro_profissional ?? '', orgao_registro: registro.orgao_registro ?? '', uf_registro: registro.uf_registro ?? '', validade_em: registro.validade_em ?? '' });
    } else {
      this.referencia.set(registro.curso_id);
      this.form.patchValue({ instituicao_emissora: registro.instituicao_emissora, conclusao_em: registro.conclusao_em, validade_em: registro.validade_em ?? '', carga_horaria: registro.carga_horaria ?? '', comprovante_referencia: registro.comprovante_referencia ?? '' });
    }
  }
  pendencias(): string[] {
    const lista: string[] = [];
    if (!this.referencia()) {
      const rotulo = this.tipo() === 'instituicoes' ? 'uma instituição no catálogo' : this.tipo() === 'profissoes' ? 'uma profissão no catálogo' : 'um curso no catálogo';
      lista.push(`selecionar ${rotulo}`);
    }
    const f = this.form.controls;
    if (this.tipo() === 'instituicoes') {
      if (!f.inicio_em.value?.trim()) {
        lista.push('preencher o campo "Início"');
      }
    } else if (this.tipo() === 'cursos') {
      if (!f.instituicao_emissora.value?.trim()) {
        lista.push('preencher o campo "Instituição emissora"');
      }
      if (!f.conclusao_em.value?.trim()) {
        lista.push('preencher o campo "Conclusão"');
      }
    }

    const camposAtivos = CAMPOS_POR_TIPO[this.tipo()];
    for (const nome of camposAtivos) {
      const control = this.form.get(nome);
      if (control?.invalid) {
        const rotuloCampo = NOMES_CAMPOS[nome] || nome;
        const msg = `corrigir o campo "${rotuloCampo}"`;
        if (!lista.some(item => item.includes(`"${rotuloCampo}"`))) {
          lista.push(msg);
        }
      }
    }
    return lista;
  }
  motivoBloqueio(): string {
    if (this.carregando()) return 'Aguarde o processamento em andamento.';
    const f = this.form.controls;
    const temDados = !!this.referencia() || !!f.inicio_em.value || !!f.instituicao_emissora.value || !!f.conclusao_em.value || !!f.registro_profissional.value || this.form.dirty || this.tentouSalvar();
    if (!this.editando() && !temDados) {
      return '';
    }
    const p = this.pendencias();
    return p.length > 0 ? `Para salvar: ${p.join(', ')}.` : '';
  }
  salvar(): void {
    this.tentouSalvar.set(true);
    if (this.pendencias().length > 0 || this.carregando()) return;
    const f = this.form.getRawValue();
    const base = { situacao_validacao: f.situacao_validacao };
    let operacao: Observable<ApiResponse<QualificacaoVM>>;
    if (this.tipo() === 'instituicoes') {
      operacao = this.api.salvarVinculo(this.pessoa().id, 'instituicoes', this.editando(), {
        ...base, instituicao_id: this.referencia(), tipo_vinculo: f.tipo_vinculo,
        inicio_em: f.inicio_em, fim_em: f.fim_em || null,
      });
    } else if (this.tipo() === 'profissoes') {
      operacao = this.api.salvarVinculo(this.pessoa().id, 'profissoes', this.editando(), {
        ...base, profissao_id: this.referencia(), registro_profissional: f.registro_profissional.trim() || null,
        orgao_registro: f.orgao_registro.trim() || null, uf_registro: f.uf_registro.trim() || null, validade_em: f.validade_em || null,
      });
    } else {
      operacao = this.api.salvarVinculo(this.pessoa().id, 'cursos', this.editando(), {
        ...base, curso_id: this.referencia(), instituicao_emissora: f.instituicao_emissora,
        conclusao_em: f.conclusao_em, validade_em: f.validade_em || null,
        carga_horaria: f.carga_horaria.trim() || null, comprovante_referencia: f.comprovante_referencia.trim() || null,
      });
    }
    this.carregando.set(true); this.erro.set('');
    operacao.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => { this.mostrarAviso('Vínculo salvo com sucesso.'); this.novo(); this.recarregar(); },
      error: (e: unknown) => { this.carregando.set(false); this.erro.set(mensagemErro(e)); },
    });
  }
  inativar(registro: QualificacaoVM): void {
    if (!confirm('Inativar este vínculo? O registro será preservado no histórico.')) return;
    this.carregando.set(true); this.erro.set('');
    this.api.inativarVinculo(this.pessoa().id, this.tipo(), registro.id).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => { this.mostrarAviso('Vínculo inativado.'); this.novo(); this.recarregar(); },
      error: (e: unknown) => { this.carregando.set(false); this.erro.set(mensagemErro(e)); },
    });
  }
}
