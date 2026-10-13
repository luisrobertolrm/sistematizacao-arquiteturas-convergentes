import { Component, computed, effect, inject, input, signal, untracked } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { CamposRegistro, Ponto, Registro, pontos, texto } from './dominio/contratos';
import { EstadoTela } from './estado';

@Component({ selector: 'app-mapa', imports: [ReactiveFormsModule], templateUrl: './mapa.html' })
export class MapaComponent {
  readonly estado = inject(EstadoTela);
  readonly idOcorrencia = input('');
  readonly idArea = input('');
  readonly ocorrencia = signal('d-vale');
  readonly selecionada = signal('');
  readonly desenhando = signal(false);
  readonly desenho = signal<Ponto[]>([]);
  readonly nome = new FormControl('', { nonNullable: true });
  readonly descricao = new FormControl('', { nonNullable: true });
  readonly municipio = new FormControl('0000001', { nonNullable: true });
  readonly gravidade = new FormControl('alta', { nonNullable: true });
  readonly situacao = new FormControl('avaliada', { nonNullable: true });
  readonly erro = signal('');
  readonly aviso = signal('');
  readonly areas = computed(() => this.estado.motor.filhos('areas_afetadas', 'id_desastre', this.ocorrencia()));
  readonly registro = computed(() => this.estado.motor.obter('areas_afetadas', this.selecionada()));
  readonly demandas = computed(() => this.estado.motor.filhos('demandas', 'id_area_afetada', this.selecionada()));
  readonly texto = texto;
  constructor() {
    effect(() => {
      const id = this.idOcorrencia(), areaId = this.idArea();
      untracked(() => {
        const ocorrencias = this.estado.motor.registros('desastres');
        this.ocorrencia.set(ocorrencias.find((r) => r.id === id)?.id ?? ocorrencias[0]?.id ?? '');
        this.selecionada.set(''); this.cancelar();
        const area = this.estado.motor.obter('areas_afetadas', areaId);
        if (area && !area.inativo && texto(area, 'id_desastre') === this.ocorrencia()) this.selecionar(area);
      });
    });
  }
  coordenadas(area: Registro): string { return pontos(area).map((p) => `${p.x},${p.y}`).join(' '); }
  coordenadasDesenho(): string { return this.desenho().map((p) => `${p.x},${p.y}`).join(' '); }
  centro(area: Registro): Ponto {
    const ps = pontos(area); return { x: ps.reduce((s, p) => s + p.x, 0) / (ps.length || 1), y: ps.reduce((s, p) => s + p.y, 0) / (ps.length || 1) };
  }
  trocar(evento: Event): void {
    if (!(evento.target instanceof HTMLSelectElement)) return;
    this.ocorrencia.set(evento.target.value); this.selecionada.set(''); this.cancelar();
  }
  selecionar(area: Registro, evento?: Event): void {
    if (this.desenhando()) return;
    evento?.stopPropagation();
    this.selecionada.set(area.id); this.nome.setValue(texto(area, 'nome')); this.descricao.setValue(texto(area, 'descricao'));
    this.municipio.setValue(texto(area, 'municipio_codigo_ibge')); this.gravidade.setValue(texto(area, 'gravidade')); this.situacao.setValue(texto(area, 'situacao'));
    this.erro.set(''); this.aviso.set('');
  }
  iniciar(): void {
    this.selecionada.set(''); this.desenho.set([]); this.nome.reset(); this.descricao.reset();
    this.gravidade.setValue('alta'); this.situacao.setValue('em_avaliacao'); this.desenhando.set(true); this.erro.set('');
  }
  redesenhar(): void { this.desenho.set([]); this.desenhando.set(true); }
  cancelar(): void { this.desenhando.set(false); this.desenho.set([]); this.erro.set(''); }
  desfazer(): void { this.desenho.update((ps) => ps.slice(0, -1)); }
  clicar(evento: MouseEvent): void {
    if (!this.desenhando() || !(evento.currentTarget instanceof SVGSVGElement)) return;
    const ponto = evento.currentTarget.createSVGPoint(); ponto.x = evento.clientX; ponto.y = evento.clientY;
    const matriz = evento.currentTarget.getScreenCTM(); if (!matriz) return;
    const local = ponto.matrixTransform(matriz.inverse());
    this.desenho.update((ps) => [...ps, { x: Math.round(Math.max(0, Math.min(1000, local.x))), y: Math.round(Math.max(0, Math.min(600, local.y))) }]);
  }
  async salvar(): Promise<void> {
    const geometria = this.desenhando() ? this.desenho() : pontos(this.registro());
    if (geometria.length < 3) { this.erro.set('Marque pelo menos três vértices no mapa.'); return; }
    const area = Math.abs(geometria.reduce((s, p, i) => {
      const proximo = geometria[(i + 1) % geometria.length]; return s + p.x * proximo.y - proximo.x * p.y;
    }, 0)) / 2;
    if (area < 1) { this.erro.set('O polígono precisa delimitar uma área.'); return; }
    const campos: CamposRegistro = { id_desastre: this.ocorrencia(), nome: this.nome.value,
      descricao: this.descricao.value, municipio_codigo_ibge: this.municipio.value,
      gravidade: this.gravidade.value, situacao: this.situacao.value, geometria };
    try {
      const resultado = await this.estado.executar((motor) => motor.salvar('areas_afetadas', campos, this.selecionada()));
      if (resultado.erros.length) { this.erro.set(resultado.erros.map((e) => e.mensagem).join(' ')); return; }
      this.selecionada.set(resultado.registro?.id ?? ''); this.cancelar(); this.aviso.set('Área e avaliação salvas nesta sessão.');
    } catch (erro: unknown) { this.erro.set(erro instanceof Error ? erro.message : 'Não foi possível salvar.'); }
  }
}
