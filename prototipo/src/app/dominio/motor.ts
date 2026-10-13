import {
  CamposRegistro, ErroCampo, EstadoPrototipo, Evento, Registro, ResultadoSalvamento,
  marcado, texto,
} from './contratos';
import { criarEstado } from './cenario';
import { TELAS, telaPorChave } from './telas';

const INDICES: Readonly<Record<string, { origem: string; fk: string }>> = {
  atividade_indice_semantico: { origem: 'atividades', fk: 'id_atividade' },
  profissao_indice_semantico: { origem: 'profissoes', fk: 'id_profissao' },
  curso_indice_semantico: { origem: 'cursos', fk: 'id_curso' },
  tipo_recurso_indice_semantico: { origem: 'tipos_recurso', fk: 'id_tipo_recurso' },
};

function valor(campos: CamposRegistro, chave: string): string {
  const dado = campos[chave]; return typeof dado === 'string' ? dado.trim() : '';
}
function chave(): string { return crypto.randomUUID(); }
function instante(): string { return new Date().toISOString(); }
function canonico(campos: CamposRegistro): string {
  const ordenado: CamposRegistro = {};
  for (const nome of Object.keys(campos).sort()) ordenado[nome] = campos[nome];
  return JSON.stringify(ordenado);
}
async function sha256(conteudo: string): Promise<string> {
  const resumo = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(conteudo));
  return [...new Uint8Array(resumo)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

/** Motor local de navegação e simulação. Não chama API, provedor ou banco. */
export class MotorPrototipo {
  readonly estado: EstadoPrototipo;
  constructor(estado: EstadoPrototipo = criarEstado()) { this.estado = estado; }

  async preparar(): Promise<void> {
    await this.atualizarHashes();
    await this.indexar('mod-emb', 'atividade_indice_semantico', false);
    const primeira = await this.recomendar('dem-varzea');
    this.decidir(primeira.id, 'aprovada', 'Exemplo de decisão: confirmar agenda e condições antes de executar.');
    const segunda = await this.recomendar('dem-encosta');
    this.decidir(segunda.id, 'rejeitada', 'Exemplo: água compartilhada e compatibilidade técnica pendentes.');
    await this.recomendar('dem-centro');
  }
  registros(tabela: string, incluirInativos = false): Registro[] {
    return (this.estado.tabelas[tabela] ?? []).filter((r) => incluirInativos || !r.inativo);
  }
  obter(tabela: string, id: string): Registro | undefined {
    return this.estado.tabelas[tabela]?.find((r) => r.id === id);
  }
  filhos(tabela: string, campo: string, id: string, incluirInativos = false): Registro[] {
    return this.registros(tabela, incluirInativos).filter((r) => texto(r, campo) === id);
  }
  nome(tabela: string, id: string, profundidade = 0): string {
    const registro = this.obter(tabela, id);
    if (!registro) return id || '—';
    for (const campo of ['nome', 'titulo', 'identificador_modelo', 'termo', 'codigo']) {
      if (texto(registro, campo)) return texto(registro, campo) + (registro.inativo ? ' (inativo)' : '');
    }
    if (profundidade > 2) return id;
    const campos = telaPorChave(tabela)?.campos.filter((c) => c.tipo === 'referencia' && texto(registro, c.chave)).slice(0, 2) ?? [];
    return campos.map((c) => this.nome(c.tabela ?? '', texto(registro, c.chave), profundidade + 1)).join(' · ') || id;
  }
  exibir(tabela: string, registro: Registro, campo: string): string {
    const definicao = telaPorChave(tabela)?.campos.find((c) => c.chave === campo);
    if (definicao?.tipo === 'referencia') return this.nome(definicao.tabela ?? '', texto(registro, campo));
    if (definicao?.opcoes) return definicao.opcoes.find((o) => o.valor === texto(registro, campo))?.nome ?? '—';
    const dado = registro.campos[campo];
    return typeof dado === 'boolean' ? (dado ? 'Sim' : 'Não') : Array.isArray(dado) ? `${dado.length} vértices` : dado || '—';
  }
  evento(tipo: string, tabela: string, registro: string, mensagem: string): void {
    const evento: Evento = { id: chave(), instante: instante(), ator: this.estado.ator,
      tipo, tabela, registro, texto: mensagem };
    this.estado.eventos.unshift(evento);
  }

  validar(tabela: string, campos: CamposRegistro, id = ''): ErroCampo[] {
    const tela = telaPorChave(tabela);
    const erros: ErroCampo[] = [];
    const erro = (campo: string, mensagem: string): void => { erros.push({ campo, mensagem }); };
    if (!tela) return [{ campo: '', mensagem: 'Tela desconhecida.' }];
    for (const campo of tela.campos) {
      const v = valor(campos, campo.chave);
      if (campo.obrigatorio && campo.tipo !== 'booleano' && !v) erro(campo.chave, `${campo.nome}: obrigatório.`);
      if (v && campo.tipo === 'referencia') {
        const referencia = this.obter(campo.tabela ?? '', v);
        if (!referencia || referencia.inativo) erro(campo.chave, `${campo.nome}: escolha um cadastro ativo.`);
      }
      if (v && campo.tipo === 'opcao' && !campo.opcoes?.some((o) => o.valor === v)) erro(campo.chave, `${campo.nome}: opção inválida.`);
      if (v && campo.tipo === 'numero' && (!Number.isFinite(Number(v)) || Number(v) < (campo.minimo ?? -Infinity))) erro(campo.chave, `${campo.nome}: quantidade inválida.`);
      if (v && (campo.tipo === 'data' || campo.tipo === 'datahora') && Number.isNaN(Date.parse(v))) erro(campo.chave, `${campo.nome}: data inválida.`);
    }
    for (const [inicio, fim] of [['inicio_em', 'fim_em'], ['inicio_em', 'encerramento_em'],
      ['inicio_previsto_em', 'prazo_em'], ['inicio_previsto_em', 'fim_previsto_em'], ['conclusao_em', 'validade_em']]) {
      if (valor(campos, inicio) && valor(campos, fim) && Date.parse(valor(campos, fim)) < Date.parse(valor(campos, inicio))) erro(fim, 'A data final não pode anteceder a inicial.');
    }
    const duplicado = (chaves: string[], normalizar = false): boolean => this.registros(tabela).some((r) => r.id !== id && chaves.every((c) => {
      const atual = valor(campos, c), anterior = texto(r, c).trim();
      return normalizar ? atual.toLocaleLowerCase() === anterior.toLocaleLowerCase() : atual === anterior;
    }));
    if (['instituicoes', 'pessoas', 'recursos'].includes(tabela)) {
      if (valor(campos, 'municipio_codigo_ibge') && !/^\d{7}$/.test(valor(campos, 'municipio_codigo_ibge'))) erro('municipio_codigo_ibge', 'Município: use sete dígitos.');
      if (!!valor(campos, 'latitude') !== !!valor(campos, 'longitude')) erro('latitude', 'Informe latitude e longitude juntas.');
      if (Math.abs(Number(valor(campos, 'latitude'))) > 90 || Math.abs(Number(valor(campos, 'longitude'))) > 180) erro('latitude', 'Coordenadas fora dos limites.');
    }
    if (tabela === 'instituicoes' && valor(campos, 'cnpj')) {
      const cnpj = valor(campos, 'cnpj');
      if (!/^[A-Z0-9]{12}[0-9]{2}$/.test(cnpj)) erro('cnpj', 'CNPJ: formato de 14 posições.');
      if (this.registros(tabela, true).some((r) => r.id !== id && texto(r, 'cnpj') === cnpj)) erro('cnpj', 'CNPJ já cadastrado.');
    }
    if (valor(campos, 'codigo') && duplicado(['codigo'])) erro('codigo', 'Código já cadastrado.');
    if (tabela === 'profissoes' && valor(campos, 'codigo_cbo') && !/^\d{6}$/.test(valor(campos, 'codigo_cbo'))) erro('codigo_cbo', 'CBO: use seis dígitos.');
    if (tabela === 'pessoa_instituicao') {
      const sobrepoe = this.registros(tabela).some((r) => r.id !== id && ['pessoa_id', 'instituicao_id', 'tipo_vinculo'].every((c) => texto(r, c) === valor(campos, c))
        && (!texto(r, 'fim_em') || texto(r, 'fim_em') >= valor(campos, 'inicio_em'))
        && (!valor(campos, 'fim_em') || texto(r, 'inicio_em') <= valor(campos, 'fim_em')));
      if (sobrepoe) erro('inicio_em', 'Já existe vínculo desse tipo no período informado.');
    }
    if (tabela.startsWith('pessoa_') && id && texto(this.obter(tabela, id), 'pessoa_id') !== valor(campos, 'pessoa_id')) erro('pessoa_id', 'A pessoa do vínculo não pode ser trocada.');
    if (tabela === 'areas_afetadas' && (!Array.isArray(campos['geometria']) || campos['geometria'].length < 3)) erro('geometria', 'Desenhe ao menos três vértices na tela Mapa.');
    if (tabela === 'pessoa_profissao' && duplicado(['pessoa_id', 'profissao_id', 'registro_profissional', 'orgao_registro', 'uf_registro', 'validade_em'], true)) erro('profissao_id', 'Qualificação duplicada; edite ou registre outra renovação.');
    if (tabela === 'pessoa_curso' && duplicado(['pessoa_id', 'curso_id', 'instituicao_emissora', 'conclusao_em'], true)) erro('conclusao_em', 'Essa conclusão já foi registrada.');
    if (tabela === 'atividade_termos' && duplicado(['atividade_id', 'termo'], true)) erro('termo', 'Termo já associado.');
    if (tabela === 'oferta_atividade_recurso' && duplicado(['oferta_atividade_id', 'recurso_id'])) erro('recurso_id', 'Recurso já associado à oferta.');
    if (['ofertas_atividade', 'recursos'].includes(tabela) && !!valor(campos, 'pessoa_id') === !!valor(campos, 'instituicao_id')) erro('pessoa_id', 'Informe uma pessoa OU uma instituição.');
    if (tabela === 'ofertas_atividade' && duplicado(['atividade_id', 'pessoa_id', 'instituicao_id', 'municipio_atendimento_codigo_ibge'])) erro('atividade_id', 'Já existe oferta para esse ofertante/atividade/município.');
    if (tabela === 'recursos') {
      const tipo = this.obter('tipos_recurso', valor(campos, 'tipo_recurso_id'));
      if (texto(tipo, 'modo_controle') === 'individual' && Number(valor(campos, 'quantidade_total')) !== 1) erro('quantidade_total', 'Recurso individual deve ter quantidade 1.');
    }
    if (tabela === 'demanda_itens') {
      const atividade = valor(campos, 'id_atividade'), tipo = valor(campos, 'id_tipo_recurso');
      if (!!atividade === !!tipo) erro('id_atividade', 'Escolha uma atividade OU um tipo de recurso.');
      const unidade = atividade ? texto(this.obter('atividades', atividade), 'id_unidade_capacidade') : texto(this.obter('tipos_recurso', tipo), 'id_unidade_medida');
      if (unidade && unidade !== valor(campos, 'id_unidade_medida')) erro('id_unidade_medida', 'Unidade diferente da definida no catálogo.');
    }
    if (tabela === 'desastres' && ((valor(campos, 'situacao') === 'encerrado') !== !!valor(campos, 'encerramento_em'))) erro('encerramento_em', 'Ocorrência encerrada exige data de encerramento; outras situações não a usam.');
    if (tabela === 'modelo_ia') {
      const embedding = valor(campos, 'finalidade') === 'embedding';
      if (embedding && (!Number.isInteger(Number(valor(campos, 'dimensao'))) || Number(valor(campos, 'dimensao')) <= 0)) erro('dimensao', 'Embedding exige dimensão inteira positiva.');
      if (!embedding && valor(campos, 'dimensao')) erro('dimensao', 'Inferência de texto não possui dimensão de embedding.');
      const indices = Object.keys(INDICES).some((t) => this.filhos(t, 'id_modelo', id).length > 0);
      const anterior = this.obter(tabela, id);
      if (indices && ['identificador_modelo', 'revisao', 'finalidade', 'dimensao', 'id_conexao'].some((c) => texto(anterior, c) !== valor(campos, c))) erro('identificador_modelo', 'Modelo com índices: cadastre outro modelo para mudar sua identidade.');
      if (embedding && campos['ativo'] === true && !this.cobertura(id)) erro('ativo', 'Salve desmarcado, prepare os índices de atividades e depois selecione o modelo.');
    }
    return erros;
  }

  async salvar(tabela: string, entrada: CamposRegistro, id = ''): Promise<ResultadoSalvamento> {
    const tela = telaPorChave(tabela);
    if (!tela || tela.somenteLeitura || tabela === 'desastre_tipo') return { erros: [{ campo: '', mensagem: 'Use a ação específica dessa tela.' }] };
    const anterior = this.obter(tabela, id);
    if (id && (!anterior || anterior.inativo)) return { erros: [{ campo: '', mensagem: 'Registro inexistente ou inativo.' }] };
    const campos: CamposRegistro = structuredClone(entrada);
    for (const c of Object.keys(campos)) if (typeof campos[c] === 'string') campos[c] = valor(campos, c);
    if (campos['cnpj']) campos['cnpj'] = valor(campos, 'cnpj').replace(/[./\s-]/g, '').toUpperCase();
    if (campos['codigo_cbo']) campos['codigo_cbo'] = valor(campos, 'codigo_cbo').replace(/[\s-]/g, '');
    for (const c of ['registro_profissional', 'orgao_registro', 'uf_registro', 'uf']) if (campos[c]) campos[c] = valor(campos, c).toUpperCase();
    const erros = this.validar(tabela, campos, id); if (erros.length) return { erros };
    if (tabela === 'modelo_ia' && campos['ativo'] === true) {
      for (const modelo of this.registros(tabela)) if (texto(modelo, 'finalidade') === valor(campos, 'finalidade')) modelo.campos['ativo'] = false;
    }
    const registro: Registro = anterior ?? { id: chave(), inativo: false, criado_em: instante(), atualizado_em: instante(), campos: {} };
    registro.campos = { ...anterior?.campos, ...campos };
    registro.atualizado_em = instante();
    if (tabela === 'areas_afetadas') registro.campos['ultima_avaliacao_em'] = instante();
    if (!anterior) this.estado.tabelas[tabela].push(registro);
    this.evento(anterior ? 'edição' : 'cadastro', tabela, registro.id, this.nome(tabela, registro.id));
    await this.atualizarHashes();
    return { registro, erros: [] };
  }

  async salvarDesastre(campos: CamposRegistro, id: string, principal: string, associados: string[]): Promise<ResultadoSalvamento> {
    const tipos = [...new Set([principal, ...associados].filter(Boolean))];
    if (!principal || tipos.some((t) => !this.obter('tipos_desastre', t) || this.obter('tipos_desastre', t)?.inativo)) return { erros: [{ campo: 'principal', mensagem: 'Selecione uma classificação principal ativa.' }] };
    const resultado = await this.salvar('desastres', campos, id);
    if (!resultado.registro) return resultado;
    const desastre = resultado.registro;
    for (const relacao of this.filhos('desastre_tipo', 'id_desastre', desastre.id)) relacao.inativo = true;
    for (const tipo of tipos) this.inserir('desastre_tipo', { id_desastre: desastre.id, id_tipo_desastre: tipo, principal: tipo === principal });
    return resultado;
  }
  async inativar(tabela: string, id: string): Promise<void> {
    const registro = this.obter(tabela, id);
    if (!registro || registro.inativo) throw new Error('Registro inexistente ou inativo.');
    if (telaPorChave(tabela)?.somenteLeitura || tabela === 'desastre_tipo') throw new Error('Use a ação específica da tela.');
    if (tabela === 'modelo_ia' && marcado(registro, 'ativo')) throw new Error('Desmarque o modelo antes de inativar.');
    if (tabela === 'conexao_ia' && this.filhos('modelo_ia', 'id_conexao', id).some((m) => marcado(m, 'ativo'))) throw new Error('A conexão possui modelos selecionados.');
    registro.inativo = true; registro.atualizado_em = instante();
    this.evento('inativação', tabela, id, this.nome(tabela, id));
    await this.atualizarHashes();
  }

  private inserir(tabela: string, campos: CamposRegistro): Registro {
    const registro: Registro = { id: chave(), inativo: false, criado_em: instante(), atualizado_em: instante(), campos };
    this.estado.tabelas[tabela].push(registro); return registro;
  }
  private async atualizarHashes(): Promise<void> {
    for (const tabela of ['atividades', 'profissoes', 'cursos', 'tipos_recurso']) {
      for (const registro of this.registros(tabela)) {
        const campos: CamposRegistro = {};
        for (const c of telaPorChave(tabela)?.campos ?? []) campos[c.chave] = registro.campos[c.chave] ?? '';
        if (tabela === 'atividades') {
          campos['termos'] = this.filhos('atividade_termos', 'atividade_id', registro.id).map((t) => texto(t, 'termo')).sort().join('\n');
          const categoria = this.obter('categorias_atividade', texto(registro, 'categoria_id'));
          campos['categoria_nome'] = texto(categoria, 'nome'); campos['categoria_descricao'] = texto(categoria, 'descricao');
        }
        registro.campos['hash_conteudo_semantico'] = await sha256(canonico(campos));
      }
    }
    for (const [indice, definicao] of Object.entries(INDICES)) for (const registro of this.registros(indice)) {
      const origem = this.obter(definicao.origem, texto(registro, definicao.fk));
      if (!origem || origem.inativo || texto(registro, 'hash_origem') !== texto(origem, 'hash_conteudo_semantico')) registro.campos['situacao_indexacao'] = 'pendente';
    }
    for (const demanda of this.registros('demandas')) {
      const campos: CamposRegistro = {};
      for (const campo of telaPorChave('demandas')?.campos ?? []) campos[campo.chave] = demanda.campos[campo.chave] ?? '';
      const itens = this.filhos('demanda_itens', 'id_demanda', demanda.id).map((i) => canonico(i.campos)).sort();
      campos['itens'] = itens.join('\n');
      demanda.campos['hash_demanda'] = await sha256(canonico(campos));
    }
  }
  cobertura(modelo: string): boolean {
    const atividades = this.registros('atividades');
    return !!modelo && atividades.length > 0 && atividades.every((a) => this.registros('atividade_indice_semantico').some((i) => texto(i, 'id_modelo') === modelo && texto(i, 'id_atividade') === a.id && texto(i, 'situacao_indexacao') === 'pronta' && texto(i, 'hash_origem') === texto(a, 'hash_conteudo_semantico')));
  }
  async indexar(modeloId: string, indice: string, registrarEvento = true): Promise<void> {
    const modelo = this.obter('modelo_ia', modeloId), definicao = INDICES[indice];
    if (!modelo || modelo.inativo || texto(modelo, 'finalidade') !== 'embedding' || !definicao) throw new Error('Selecione um modelo cadastrado de embedding.');
    await this.atualizarHashes();
    for (const origem of this.registros(definicao.origem)) {
      const atual = this.registros(indice).find((i) => texto(i, definicao.fk) === origem.id && texto(i, 'id_modelo') === modeloId);
      const campos: CamposRegistro = { [definicao.fk]: origem.id, id_modelo: modeloId, hash_origem: texto(origem, 'hash_conteudo_semantico'), situacao_indexacao: 'pronta', indexado_em: instante(), representacao: 'Simulada: nenhum vetor foi gerado' };
      if (atual) { atual.campos = campos; atual.atualizado_em = instante(); } else this.inserir(indice, campos);
    }
    if (registrarEvento) this.evento('indexação simulada', indice, modeloId, 'Estado dos índices atualizado sem gerar embeddings.');
  }
  recomendacaoDesatualizada(recomendacao: Registro): boolean {
    return texto(recomendacao, 'hash_demanda_origem') !== texto(this.obter('demandas', texto(recomendacao, 'id_demanda')), 'hash_demanda');
  }
  async recomendar(demandaId: string): Promise<Registro> {
    const demanda = this.obter('demandas', demandaId);
    if (!demanda || demanda.inativo || ['cancelada', 'concluida'].includes(texto(demanda, 'situacao'))) throw new Error('Escolha uma demanda ativa e aberta para análise.');
    const itens = this.filhos('demanda_itens', 'id_demanda', demandaId);
    if (!itens.length) throw new Error('Inclua ao menos um item antes de gerar a recomendação.');
    const embedding = this.registros('modelo_ia').find((m) => marcado(m, 'ativo') && texto(m, 'finalidade') === 'embedding');
    const inferencia = this.registros('modelo_ia').find((m) => marcado(m, 'ativo') && texto(m, 'finalidade') === 'inferencia_texto');
    if (!embedding || !inferencia || !this.cobertura(embedding.id)) throw new Error('Configure os dois modelos e prepare os índices de atividades.');
    for (const item of itens) if (this.validar('demanda_itens', item.campos, item.id).length) throw new Error('Há item com referência inativa ou unidade inválida. Revise a demanda.');
    const area = this.obter('areas_afetadas', texto(demanda, 'id_area_afetada'));
    if (!area || area.inativo) throw new Error('A área da demanda está inativa.');
    const rec = this.inserir('recomendacoes', {
      id_demanda: demanda.id, id_modelo_embedding: embedding.id, id_modelo_inferencia: inferencia.id,
      gerada_em: instante(), situacao: 'gerada', hash_demanda_origem: texto(demanda, 'hash_demanda'),
      justificativa: 'Simulação determinística por IDs e filtros locais. Não foi executado LLM ou busca vetorial. Confirmar formação, compatibilidade, agenda e acesso antes de qualquer operação.',
    });
    for (const item of itens) {
      const atividade = texto(item, 'id_atividade');
      const sugestao = this.inserir('recomendacao_itens', {
        id_recomendacao: rec.id, id_demanda_item: item.id, quantidade_sugerida: '0',
        justificativa: atividade ? 'Ofertas relacionadas; capacidade por período e composição não validadas. Quantidades das ofertas não são somadas.' : 'Candidatos por tipo e município. Quantidade potencial não é reserva nem comprovação técnica.',
      });
      if (atividade) {
        const ofertas = this.registros('ofertas_atividade').filter((o) => texto(o, 'atividade_id') === atividade && texto(o, 'situacao_validacao') === 'validada' && texto(o, 'municipio_atendimento_codigo_ibge') === texto(area, 'municipio_codigo_ibge'));
        for (const oferta of ofertas) {
          const pessoaId = texto(oferta, 'pessoa_id'), instituicaoId = texto(oferta, 'instituicao_id');
          const dono = this.obter(pessoaId ? 'pessoas' : 'instituicoes', pessoaId || instituicaoId);
          if (!dono || dono.inativo || texto(dono, 'situacao_cadastral') !== 'validada') continue;
          if (pessoaId) this.inserir('recomendacao_pessoas', { id_recomendacao_item: sugestao.id, id_pessoa: pessoaId, id_oferta_atividade: oferta.id, papel_sugerido: 'Ofertante pessoal; conferir formação, composição e agenda' });
          else this.inserir('recomendacao_instituicoes', { id_recomendacao_item: sugestao.id, id_instituicao: instituicaoId, id_oferta_atividade: oferta.id });
          for (const uso of this.filhos('oferta_atividade_recurso', 'oferta_atividade_id', oferta.id)) {
            const recurso = this.obter('recursos', texto(uso, 'recurso_id'));
            if (recurso && !recurso.inativo && texto(recurso, 'estado_operacional') === 'operacional') this.inserir('recomendacao_recursos', { id_recomendacao_item: sugestao.id, id_recurso: recurso.id, quantidade_sugerida: texto(uso, 'quantidade_prevista'), uso: 'Dependência prevista da oferta; acesso/agenda pendentes' });
          }
        }
      } else {
        const candidatos = this.registros('recursos').filter((r) => texto(r, 'tipo_recurso_id') === texto(item, 'id_tipo_recurso') && texto(r, 'estado_operacional') === 'operacional' && texto(r, 'municipio_codigo_ibge') === texto(area, 'municipio_codigo_ibge') && Number(texto(r, 'quantidade_total')) > 0);
        let restante = Number(texto(item, 'quantidade_solicitada'));
        const exigeConferencia = /kva|pot[eê]ncia|compatibilidade/i.test(texto(item, 'observacoes'));
        for (const recurso of candidatos) {
          const dono = this.obter(texto(recurso, 'pessoa_id') ? 'pessoas' : 'instituicoes', texto(recurso, 'pessoa_id') || texto(recurso, 'instituicao_id'));
          if (!dono || dono.inativo) continue;
          const quantidade = exigeConferencia ? 0 : Math.min(restante, Number(texto(recurso, 'quantidade_total')));
          if (!exigeConferencia && quantidade <= 0) break;
          this.inserir('recomendacao_recursos', { id_recomendacao_item: sugestao.id, id_recurso: recurso.id, quantidade_sugerida: String(quantidade), uso: exigeConferencia ? 'Compatibilidade técnica não validada; análise manual necessária' : 'Quantidade potencial, sem reserva' });
          restante -= quantidade;
        }
        sugestao.campos['quantidade_sugerida'] = String(Number(texto(item, 'quantidade_solicitada')) - restante);
        if (exigeConferencia) sugestao.campos['justificativa'] = 'Conferência técnica pendente. A regra ilustrativa reconhece termos do cenário; não interpreta requisitos técnicos genericamente.';
      }
    }
    this.evento('sugestão simulada', 'recomendacoes', rec.id, this.nome('demandas', demandaId));
    return rec;
  }
  decidir(id: string, decisao: 'aprovada' | 'rejeitada', justificativa: string): void {
    const rec = this.obter('recomendacoes', id);
    if (!rec || texto(rec, 'situacao') !== 'gerada') throw new Error('A recomendação já foi decidida ou não existe.');
    if (!justificativa.trim()) throw new Error('Informe a justificativa da decisão.');
    if (decisao === 'aprovada' && this.recomendacaoDesatualizada(rec)) throw new Error('A demanda foi alterada. Gere outra análise antes de aprovar.');
    rec.campos['situacao'] = decisao; rec.campos['decidida_em'] = instante();
    rec.campos['decidida_por'] = this.estado.ator; rec.campos['justificativa_decisao'] = justificativa.trim();
    rec.atualizado_em = instante(); this.evento(decisao, 'recomendacoes', id, justificativa.trim());
  }
  alertasCompartilhamento(id: string): string[] {
    const itemIds = this.filhos('recomendacao_itens', 'id_recomendacao', id).map((i) => i.id);
    const recursos = this.registros('recomendacao_recursos').filter((r) => itemIds.includes(texto(r, 'id_recomendacao_item')));
    const alertas: string[] = [];
    for (const r of recursos) {
      const outras = this.registros('recomendacao_recursos').filter((o) => texto(o, 'id_recurso') === texto(r, 'id_recurso') && !itemIds.includes(texto(o, 'id_recomendacao_item'))).filter((o) => {
        const item = this.obter('recomendacao_itens', texto(o, 'id_recomendacao_item'));
        return texto(this.obter('recomendacoes', texto(item, 'id_recomendacao')), 'situacao') !== 'rejeitada';
      });
      if (outras.length) alertas.push(`${this.nome('recursos', texto(r, 'id_recurso'))}: aparece em outra análise não rejeitada. Conferir sobreposição, quantidade e horário; não há reserva.`);
    }
    return [...new Set(alertas)];
  }
}
