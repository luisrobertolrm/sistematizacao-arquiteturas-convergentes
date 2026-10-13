import { Component, ElementRef, afterNextRender, effect, input, model, signal, untracked, viewChild, DestroyRef, inject } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import * as L from 'leaflet/dist/leaflet-src.esm.js';
import { AreaAfetadaVM, GeometriaArea, GravidadeArea, Posicao } from '../shared/desastres';

const CORES: Record<GravidadeArea, string> = { baixa: '#287844', moderada: '#a66b00', alta: '#d45000', critica: '#a11b36' };

@Component({
  selector: 'app-mapa-areas', imports: [ReactiveFormsModule],
  styles: ['.mapa-area { height: 420px; width: 100%; z-index: 0; }'],
  template: `
    <h3>Delimitação das áreas desta página</h3>
    <p>Baixa: verde · Moderada: ocre · Alta: laranja · Crítica: vinho. A avaliação é administrativa.</p>
    <div #superficie class="mapa-area" role="region" aria-label="Mapa para delimitar áreas afetadas"></div>
    @if (erroBase()) { <p class="field-error" role="status">O mapa de fundo não carregou. As delimitações continuam disponíveis; confira a conexão.</p> }
    <div class="record-actions">
      <button type="button" (click)="enquadrar()" [disabled]="!pronto() || areas().length === 0">Enquadrar áreas da página</button>
      <button type="button" (click)="iniciar()" [disabled]="bloqueado() || !pronto()">Desenhar nova delimitação</button>
      <button type="button" (click)="desfazer()" [disabled]="bloqueado() || !desenhando() || pontos().length === 0">Desfazer ponto</button>
      <button type="button" (click)="concluir()" [disabled]="bloqueado() || !desenhando() || pontos().length < 3">Concluir delimitação</button>
      <button type="button" (click)="limpar()" [disabled]="bloqueado()">Limpar delimitação</button>
    </div>
    <p role="status">{{ desenhando() ? 'Clique no mapa para adicionar de 3 a 200 vértices. Depois conclua a delimitação.' : geometria() ? 'Delimitação pronta para salvar no formulário da área.' : 'Selecione uma área para revisar ou desenhe uma delimitação.' }} Vértices do desenho: {{ pontos().length }}.</p>
    <div [formGroup]="centro" class="two-columns">
      <div><label for="mapa-centro-latitude">Latitude para centralizar</label><input id="mapa-centro-latitude" formControlName="latitude" inputmode="decimal"></div>
      <div><label for="mapa-centro-longitude">Longitude para centralizar</label><input id="mapa-centro-longitude" formControlName="longitude" inputmode="decimal"></div>
    </div><button type="button" (click)="centralizar()" [disabled]="centro.invalid || !pronto()">Centralizar coordenadas</button>
    <small>Vista inicial de referência em São Paulo. Coordenadas usam ponto decimal. Município não é geocodificado automaticamente.</small>
  `,
})
export class MapaAreasComponent {
  private readonly superficie = viewChild.required<ElementRef<HTMLDivElement>>('superficie');
  private readonly destroyRef = inject(DestroyRef);
  private readonly fb = inject(NonNullableFormBuilder);
  readonly areas = input<AreaAfetadaVM[]>([]);
  readonly bloqueado = input(false);
  readonly geometria = model<GeometriaArea | null>(null);
  readonly pronto = signal(false); readonly erroBase = signal(false);
  readonly desenhando = signal(false); readonly pontos = signal<Posicao[]>([]);
  readonly centro = this.fb.group({ latitude: ['-23.5505', [Validators.required, Validators.min(-85), Validators.max(85), Validators.pattern(/^-?\d+(\.\d+)?$/)]], longitude: ['-46.6333', [Validators.required, Validators.min(-180), Validators.max(180), Validators.pattern(/^-?\d+(\.\d+)?$/)]] });
  private mapa: L.Map | null = null;
  private readonly camadas = L.featureGroup();
  private readonly desenho = L.featureGroup();
  constructor() {
    afterNextRender(() => {
      this.mapa = L.map(this.superficie().nativeElement, { doubleClickZoom: false, minZoom: 2, maxZoom: 19 }).setView([-23.5505, -46.6333], 12);
      const base = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors', maxZoom: 19, noWrap: true,
      }).addTo(this.mapa);
      base.on('tileerror', () => this.erroBase.set(true));
      this.camadas.addTo(this.mapa); this.desenho.addTo(this.mapa);
      this.mapa.on('click', (evento: L.LeafletMouseEvent) => {
        if (!this.desenhando() || this.bloqueado() || this.pontos().length >= 200) return;
        this.pontos.update(p => [...p, [Number(evento.latlng.lng.toFixed(7)), Number(evento.latlng.lat.toFixed(7))]]);
        this.mostrarDesenho();
      });
      this.pronto.set(true);
    });
    effect(() => {
      const pronto = this.pronto(), areas = this.areas(), geometria = this.geometria();
      untracked(() => {
        if (!pronto || !this.mapa) return;
        this.camadas.clearLayers();
        for (const area of areas) {
          const poligono = L.polygon(this.latlngs(area.geometria), { color: CORES[area.gravidade], dashArray: area.inativado_em ? '4 6' : undefined, fillOpacity: 0.18 });
          const legenda = document.createElement('span'); legenda.textContent = `${area.nome} · ${area.gravidade}${area.inativado_em ? ' · inativada' : ''}`;
          poligono.bindTooltip(legenda).addTo(this.camadas);
        }
        if (!this.desenhando()) {
          this.desenho.clearLayers(); this.pontos.set([]);
          if (geometria) {
            const selecionado = L.polygon(this.latlngs(geometria), { color: '#135d9a', weight: 4 }).addTo(this.desenho);
            this.mapa.fitBounds(selecionado.getBounds(), { padding: [20, 20], maxZoom: 16, animate: false });
          }
        }
      });
    });
    this.destroyRef.onDestroy(() => this.mapa?.remove());
  }
  private latlngs(geometria: GeometriaArea): L.LatLngTuple[] { return geometria.coordinates[0].map(([x, y]) => [y, x]); }
  iniciar(): void { if (this.bloqueado()) return; this.desenhando.set(true); this.pontos.set([]); this.geometria.set(null); this.desenho.clearLayers(); }
  cancelarDesenho(): void { if (this.desenhando()) this.desenho.clearLayers(); this.desenhando.set(false); this.pontos.set([]); }
  limpar(): void { if (this.bloqueado()) return; this.desenhando.set(false); this.pontos.set([]); this.geometria.set(null); this.desenho.clearLayers(); }
  desfazer(): void { this.pontos.update(p => p.slice(0, -1)); this.mostrarDesenho(); }
  private mostrarDesenho(): void {
    this.desenho.clearLayers();
    const pontos: L.LatLngTuple[] = this.pontos().map(([x, y]) => [y, x]);
    L.polyline(pontos, { color: '#135d9a' }).addTo(this.desenho);
    for (const ponto of pontos) L.circleMarker(ponto, { radius: 4, color: '#135d9a' }).addTo(this.desenho);
  }
  concluir(): void {
    if (this.bloqueado() || this.pontos().length < 3) return;
    const pontos = this.pontos(); this.desenhando.set(false);
    this.geometria.set({ type: 'Polygon', coordinates: [[...pontos, [...pontos[0]]]] });
  }
  enquadrar(): void { if (this.camadas.getLayers().length) this.mapa?.fitBounds(this.camadas.getBounds(), { padding: [20, 20], maxZoom: 16, animate: false }); }
  centralizar(): void { if (this.centro.valid) this.mapa?.setView([Number(this.centro.controls.latitude.value), Number(this.centro.controls.longitude.value)], 13, { animate: false }); }
}
