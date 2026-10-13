import { Injectable, signal } from '@angular/core';
import { MotorPrototipo } from './dominio/motor';

@Injectable({ providedIn: 'root' })
export class EstadoTela {
  private atual = new MotorPrototipo();
  readonly revisao = signal(0);
  readonly pronto = signal(false);
  readonly ocupado = signal(false);
  readonly falhaInicial = signal('');
  get motor(): MotorPrototipo { this.revisao(); return this.atual; }
  constructor() { void this.iniciar(); }
  private async iniciar(): Promise<void> {
    try { await this.atual.preparar(); this.revisao.update((n) => n + 1); this.pronto.set(true); }
    catch (erro: unknown) { this.falhaInicial.set(erro instanceof Error ? erro.message : 'Falha ao preparar cenário.'); }
  }
  async executar<T>(acao: (motor: MotorPrototipo) => T | Promise<T>): Promise<T> {
    if (this.ocupado()) throw new Error('Aguarde a operação atual.');
    this.ocupado.set(true);
    try { const resultado = await acao(this.atual); this.revisao.update((n) => n + 1); return resultado; }
    finally { this.ocupado.set(false); }
  }
  async reiniciar(): Promise<void> {
    await this.executar(async () => { this.atual = new MotorPrototipo(); await this.atual.preparar(); });
  }
}
