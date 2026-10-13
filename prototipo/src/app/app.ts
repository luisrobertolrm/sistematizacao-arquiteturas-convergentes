import { Component, computed, DestroyRef, effect, inject, signal, untracked } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Campo, CamposRegistro, ErroCampo, Evento, Registro, Tela, novaRota, texto } from './dominio/contratos';
import { TELAS, telaPorChave } from './dominio/telas';
import { EstadoTela } from './estado';
import { MapaComponent } from './mapa';
import { RecomendacaoComponent } from './recomendacao';
import { IndicesComponent } from './indices';

type Controles = Record<string, FormControl<string | boolean>>;

@Component({ selector: 'app-root', imports: [ReactiveFormsModule, MapaComponent, RecomendacaoComponent, IndicesComponent], templateUrl: './app.html' })
export class App {
  readonly estado = inject(EstadoTela);
  readonly rota = signal(novaRota(window.location.hash));
  readonly tela = computed(() => telaPorChave(this.rota().tela));
  readonly registro = computed(() => this.estado.motor.obter(this.rota().tela, this.rota().id));
  readonly grupos = ['Rede', 'Capacidades', 'Operação', 'Catálogos', 'Administração'];
  readonly todasTelas = TELAS;
  readonly futuras = TELAS.filter((t) => t.etapa === 'futuro');
  readonly texto = texto;
  readonly busca = signal('');
  readonly incluirInativos = signal(false);
  readonly erros = signal<ErroCampo[]>([]);
  readonly aviso = signal('');
  readonly erro = signal('');
  readonly nomeAcesso = new FormControl('Administrador de demonstração', { nonNullable: true });
  readonly principal = new FormControl('', { nonNullable: true, validators: [Validators.required] });
  readonly associados = signal<string[]>([]);
  form = new FormGroup<Controles>({});
  readonly formulario = computed(() => !!this.tela() && !this.tela()?.somenteLeitura && (this.rota().id === 'novo' || this.rota().consulta.get('editar') === '1'));
  readonly lista = computed(() => {
    const rota = this.rota();
    const filtro = this.busca().trim().toLocaleLowerCase();
    const campo = rota.consulta.get('campo'), valor = rota.consulta.get('valor');
    return this.estado.motor.registros(rota.tela, this.incluirInativos()).filter((r) => (!campo || texto(r, campo) === valor)
      && (!filtro || this.estado.motor.nome(rota.tela, r.id).toLocaleLowerCase().includes(filtro) || Object.values(r.campos).some((v) => typeof v === 'string' && v.toLocaleLowerCase().includes(filtro))))
      .slice().sort((a, b) => b.criado_em.localeCompare(a.criado_em));
  });
  constructor() {
    const aoNavegar = (): void => { this.rota.set(novaRota(window.location.hash)); this.busca.set(''); this.erros.set([]); this.erro.set(''); this.aviso.set(''); window.scrollTo(0, 0); };
    window.addEventListener('hashchange', aoNavegar);
    inject(DestroyRef).onDestroy(() => window.removeEventListener('hashchange', aoNavegar));
    effect(() => {
      const rota = this.rota(), pronto = this.estado.pronto();
      if (pronto) untracked(() => this.prepararFormulario(rota.tela, rota.id));
    });
  }
  menu(grupo: string): Tela[] { return TELAS.filter((t) => t.etapa === 'inicial' && t.grupo === grupo && t.menu); }
  referencia(campo: Campo): Registro[] { return this.estado.motor.registros(campo.tabela ?? ''); }
  nomeColuna(chave: string, tela = this.tela()): string { return tela?.campos.find((c) => c.chave === chave)?.nome ?? chave.replaceAll('_', ' '); }
  camposDetalhe(tela: Tela): Campo[] { return tela.campos; }
  possuiRegistro(): boolean { return !!this.registro() && this.rota().id !== 'novo'; }
  editarLink(tabela: string, registro: Registro): string {
    if (tabela === 'desastre_tipo') return `#/desastres/${texto(registro, 'id_desastre')}?editar=1`;
    const consulta = new URLSearchParams(this.rota().consulta); consulta.set('editar', '1');
    return `#/${tabela}/${registro.id}?${consulta}`;
  }
  detalheLink(tabela: string, registro: Registro, retorno = ''): string {
    if (tabela === 'desastre_tipo') return `#/desastres/${texto(registro, 'id_desastre')}`;
    return `#/${tabela}/${registro.id}` + (retorno ? `?retorno=${encodeURIComponent(retorno)}` : '');
  }
  novoLink(tabela: string, campo = '', valor = ''): string {
    if (tabela === 'areas_afetadas') return '#/mapa' + (campo === 'id_desastre' ? `?id_desastre=${encodeURIComponent(valor)}` : '');
    if (tabela === 'desastre_tipo') return `#/desastres/${valor}?editar=1`;
    const params = new URLSearchParams();
    if (campo) params.set(campo, valor);
    if (this.rota().id && this.rota().id !== 'novo') params.set('retorno', `${this.rota().tela}/${this.rota().id}`);
    return `#/${tabela}/novo` + (params.size ? `?${params}` : '');
  }
  voltarLink(): string { return '#/' + (this.rota().consulta.get('retorno') || this.rota().tela); }
  mapaLink(tabela: string, registro: Registro): string {
    const consulta = new URLSearchParams({ id_desastre: tabela === 'desastres' ? registro.id : texto(registro, 'id_desastre') });
    if (tabela === 'areas_afetadas') consulta.set('id_area', registro.id);
    return '#/mapa?' + consulta;
  }
  private prepararFormulario(tabela: string, id: string): void {
    const tela = telaPorChave(tabela), registro = this.estado.motor.obter(tabela, id);
    const controles: Controles = {};
    for (const campo of tela?.campos ?? []) {
      const valorInicial = registro?.campos[campo.chave] ?? this.rota().consulta.get(campo.chave) ?? campo.padrao ?? (campo.tipo === 'booleano' ? false : '');
      const valor: string | boolean = typeof valorInicial === 'string' || typeof valorInicial === 'boolean' ? valorInicial : '';
      const bloqueado = !!this.rota().consulta.get(campo.chave) || (!!registro && tabela.startsWith('pessoa_') && campo.chave === 'pessoa_id');
      controles[campo.chave] = new FormControl<string | boolean>({ value: valor, disabled: bloqueado }, { nonNullable: true, validators: campo.obrigatorio ? [Validators.required] : [] });
    }
    this.form = new FormGroup(controles);
    const classificacoes = this.estado.motor.filhos('desastre_tipo', 'id_desastre', id);
    this.principal.setValue(texto(classificacoes.find((r) => r.campos['principal'] === true), 'id_tipo_desastre'));
    this.associados.set(classificacoes.filter((r) => r.campos['principal'] !== true).map((r) => texto(r, 'id_tipo_desastre')));
  }
  alternarAssociado(id: string, evento: Event): void {
    if (!(evento.target instanceof HTMLInputElement)) return;
    this.associados.update((ids) => evento.target instanceof HTMLInputElement && evento.target.checked ? [...new Set([...ids, id])] : ids.filter((i) => i !== id));
  }
  buscar(evento: Event): void { if (evento.target instanceof HTMLInputElement) this.busca.set(evento.target.value); }
  alternarInativos(evento: Event): void { if (evento.target instanceof HTMLInputElement) this.incluirInativos.set(evento.target.checked); }
  async salvar(): Promise<void> {
    this.erros.set([]); this.erro.set('');
    const campos: CamposRegistro = this.form.getRawValue();
    const id = this.rota().id === 'novo' ? '' : this.rota().id;
    const tabela = this.rota().tela;
    try {
      const resultado = await this.estado.executar((motor) => tabela === 'desastres'
        ? motor.salvarDesastre(campos, id, this.principal.value, this.associados()) : motor.salvar(tabela, campos, id));
      if (resultado.erros.length) { this.erros.set(resultado.erros); return; }
      const destino = this.rota().consulta.get('retorno') || `${tabela}/${resultado.registro?.id ?? ''}`;
      window.location.hash = '/' + destino;
    } catch (erro: unknown) { this.erro.set(erro instanceof Error ? erro.message : 'Não foi possível salvar.'); }
  }
  async inativar(tabela: string, registro: Registro): Promise<void> {
    if (!confirm('Inativar este registro de demonstração? O histórico será preservado.')) return;
    try { await this.estado.executar((motor) => motor.inativar(tabela, registro.id)); this.aviso.set('Registro inativado nesta sessão.'); }
    catch (erro: unknown) { this.erro.set(erro instanceof Error ? erro.message : 'Não foi possível inativar.'); }
  }
  async recomendar(demanda: Registro): Promise<void> {
    try { const rec = await this.estado.executar((motor) => motor.recomendar(demanda.id)); window.location.hash = `/recomendacoes/${rec.id}`; }
    catch (erro: unknown) { this.erro.set(erro instanceof Error ? erro.message : 'Não foi possível gerar a análise.'); }
  }
  async reiniciar(): Promise<void> {
    if (!confirm('Reiniciar o cenário fictício? Alterações desta sessão serão descartadas.')) return;
    try { await this.estado.reiniciar(); window.location.hash = '/inicio'; this.aviso.set('Cenário reiniciado.'); }
    catch (erro: unknown) { this.erro.set(erro instanceof Error ? erro.message : 'Não foi possível reiniciar.'); }
  }
  acesso(): void {
    if (!this.nomeAcesso.value.trim()) return;
    this.estado.motor.estado.ator = this.nomeAcesso.value.trim(); this.estado.revisao.update((n) => n + 1);
    window.location.hash = '/inicio';
  }
  exportar(): void {
    const blob = new Blob([JSON.stringify(this.estado.motor.estado, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = 'redesolidaria-prototipo.json'; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  relacionados(tabela: string, campo: string, id: string): Registro[] { return this.estado.motor.filhos(tabela, campo, id, this.incluirInativos()); }
  meta(tabela: string): Tela | undefined { return telaPorChave(tabela); }
  eventoLink(evento: Evento): string {
    return evento.tipo === 'indexação simulada' ? '#/indices' : `#/${evento.tabela}/${evento.registro}`;
  }
  contar(tabela: string): number { return this.estado.motor.registros(tabela).length; }
}
