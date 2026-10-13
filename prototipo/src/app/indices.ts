import { Component, computed, inject, signal } from '@angular/core';
import { Registro, texto } from './dominio/contratos';
import { EstadoTela } from './estado';

@Component({
  selector: 'app-indices',
  template: `
    <div class="cabecalho-pagina">
      <h1>Índices semânticos</h1>
      <p class="subtitulo-pagina">Simulação de preparo e invalidação por hash. Nenhum vetor, chamada externa ou busca semântica é executado.</p>
    </div>

    <div class="bloco">
      <div class="campo-grupo">
        <label for="catalogo-indice">Catálogo</label>
        <select id="catalogo-indice" [value]="tabela()" (change)="escolherTabela($event)">
          <option value="atividade_indice_semantico">Atividades — etapa inicial</option>
          <option value="profissao_indice_semantico">Profissões — futuro</option>
          <option value="curso_indice_semantico">Cursos — futuro</option>
          <option value="tipo_recurso_indice_semantico">Tipos de recurso — futuro</option>
        </select>
      </div>

      <div class="campo-grupo">
        <label for="modelo-indice">Modelo de embeddings</label>
        <select id="modelo-indice" [value]="modelo()" (change)="escolherModelo($event)">
          @for (m of modelos(); track m.id) {
            <option [value]="m.id">{{ texto(m, 'identificador_modelo') }} · {{ texto(m, 'dimensao') }} dimensões</option>
          }
        </select>
      </div>

      <div class="acoes">
        <button (click)="indexar()" [disabled]="estado.ocupado() || !modelo()" class="btn-primario">Simular preparo dos índices</button>
        <a href="#/modelo_ia" class="btn-secundario">Configurar modelos</a>
      </div>
    </div>

    @if (erro()) { <p role="alert" class="erro">{{ erro() }}</p> }
    @if (aviso()) { <p role="status">{{ aviso() }}</p> }

    <div class="bloco" style="padding: 12px 18px; margin: 16px 0;">
      <p style="margin: 0;">Atividades cobertas para o modelo selecionado: <strong [style.color]="estado.motor.cobertura(modelo()) ? 'var(--cor-sucesso)' : 'var(--cor-alerta)'">{{ estado.motor.cobertura(modelo()) ? 'sim' : 'não' }}</strong>. Trocar somente inferência preserva os índices.</p>
    </div>

    <div class="tabela-rolagem">
      <table>
        <thead>
          <tr>
            <th>Origem</th>
            <th>Modelo</th>
            <th>Estado</th>
            <th>Hash capturado</th>
            <th>Hash atual</th>
            <th>Representação</th>
          </tr>
        </thead>
        <tbody>
          @for (i of registros(); track i.id) {
            <tr>
              <td><a [href]="'#/' + origem() + '/' + texto(i, fk())"><strong>{{ estado.motor.nome(origem(), texto(i, fk())) }}</strong></a></td>
              <td>{{ estado.motor.nome('modelo_ia', texto(i, 'id_modelo')) }}</td>
              <td><span class="badge" [class.badge-sucesso]="texto(i, 'situacao_indexacao') === 'atualizado'" [class.badge-aviso]="texto(i, 'situacao_indexacao') === 'pendente'">{{ texto(i, 'situacao_indexacao') }}</span></td>
              <td class="hash">{{ texto(i, 'hash_origem') }}</td>
              <td class="hash">{{ texto(estado.motor.obter(origem(), texto(i, fk())), 'hash_conteudo_semantico') }}</td>
              <td>{{ texto(i, 'representacao') }}</td>
            </tr>
          } @empty {
            <tr><td colspan="6" class="tabela-vazia">Sem índices para esse modelo/catálogo. Use o preparo simulado.</td></tr>
          }
        </tbody>
      </table>
    </div>
  `
})
export class IndicesComponent {
  readonly estado = inject(EstadoTela);
  readonly tabela = signal('atividade_indice_semantico');
  readonly modelo = signal('mod-emb');
  readonly erro = signal(''); readonly aviso = signal(''); readonly texto = texto;
  readonly modelos = computed(() => this.estado.motor.registros('modelo_ia').filter((m) => texto(m, 'finalidade') === 'embedding'));
  readonly registros = computed(() => this.estado.motor.filhos(this.tabela(), 'id_modelo', this.modelo()));
  readonly origem = computed(() => ({ atividade_indice_semantico: 'atividades', profissao_indice_semantico: 'profissoes', curso_indice_semantico: 'cursos', tipo_recurso_indice_semantico: 'tipos_recurso' } as Readonly<Record<string, string>>)[this.tabela()] ?? 'atividades');
  readonly fk = computed(() => ({ atividades: 'id_atividade', profissoes: 'id_profissao', cursos: 'id_curso', tipos_recurso: 'id_tipo_recurso' } as Readonly<Record<string, string>>)[this.origem()] ?? 'id_atividade');
  escolherTabela(evento: Event): void { if (evento.target instanceof HTMLSelectElement) this.tabela.set(evento.target.value); this.aviso.set(''); }
  escolherModelo(evento: Event): void { if (evento.target instanceof HTMLSelectElement) this.modelo.set(evento.target.value); this.aviso.set(''); }
  async indexar(): Promise<void> {
    this.erro.set(''); try { await this.estado.executar((motor) => motor.indexar(this.modelo(), this.tabela())); this.aviso.set('Índices preparados em modo simulado.'); }
    catch (erro: unknown) { this.erro.set(erro instanceof Error ? erro.message : 'Não foi possível preparar.'); }
  }
}
