import assert from 'node:assert/strict';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import ts from 'typescript';

const raiz = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const saida = resolve(raiz, '.teste/dominio');
mkdirSync(saida, { recursive: true });
for (const nome of ['contratos', 'telas', 'cenario', 'motor']) {
  const fonte = readFileSync(resolve(raiz, `src/app/dominio/${nome}.ts`), 'utf8');
  const convertido = ts.transpileModule(fonte, { compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS } });
  writeFileSync(resolve(saida, `${nome}.js`), convertido.outputText);
}
const require = createRequire(import.meta.url);
const { MotorPrototipo } = require(resolve(saida, 'motor.js'));
const { TELAS } = require(resolve(saida, 'telas.js'));
const { texto, novaRota } = require(resolve(saida, 'contratos.js'));
let total = 0;
async function verificar(nome, acao) { await acao(); total++; process.stdout.write(`OK ${nome}\n`); }
const motor = new MotorPrototipo(); await motor.preparar();

await verificar('50 tabelas, 29 iniciais, 21 futuras e rotas únicas', () => {
  assert.equal(TELAS.length, 50); assert.equal(new Set(TELAS.map((t) => t.chave)).size, 50);
  assert.equal(TELAS.filter((t) => t.etapa === 'inicial').length, 29);
  assert.equal(TELAS.filter((t) => t.etapa === 'futuro').length, 21);
  for (const tela of TELAS) {
    assert.equal(novaRota(`#/${tela.chave}`).tela, tela.chave);
    for (const campo of tela.campos) if (campo.tabela) assert.ok(TELAS.some((t) => t.chave === campo.tabela));
  }
});
await verificar('relações dos dados fictícios existentes', () => {
  for (const tela of TELAS) for (const registro of motor.registros(tela.chave)) {
    for (const campo of tela.campos.filter((c) => c.tabela)) {
      const id = texto(registro, campo.chave); if (id) assert.ok(motor.obter(campo.tabela, id), `${tela.chave}.${campo.chave}`);
    }
  }
});
await verificar('incluir, editar, inativar e consultar histórico de pessoa', async () => {
  const criada = await motor.salvar('pessoas', { nome: 'Pessoa nova fictícia', municipio_codigo_ibge: '0000001', uf: 'SP', situacao_cadastral: 'pendente' });
  assert.equal(criada.erros.length, 0); const id = criada.registro.id;
  const editada = await motor.salvar('pessoas', { ...criada.registro.campos, nome: 'Pessoa corrigida fictícia' }, id);
  assert.equal(texto(editada.registro, 'nome'), 'Pessoa corrigida fictícia');
  await motor.inativar('pessoas', id); assert.ok(!motor.registros('pessoas').some((p) => p.id === id));
  assert.ok(motor.registros('pessoas', true).find((p) => p.id === id)?.inativo);
});
await verificar('vínculos sobrepostos rejeitados e período posterior aceito', async () => {
  const id = 'vi-p-joao'; const anterior = motor.obter('pessoa_instituicao', id);
  assert.equal((await motor.salvar('pessoa_instituicao', { ...anterior.campos, fim_em: '2026-05-31' }, id)).erros.length, 0);
  assert.ok((await motor.salvar('pessoa_instituicao', { ...anterior.campos, inicio_em: '2026-05-31', fim_em: '2026-06-30' })).erros.length);
  assert.equal((await motor.salvar('pessoa_instituicao', { ...anterior.campos, inicio_em: '2026-06-01', fim_em: '' })).erros.length, 0);
  assert.ok((await motor.salvar('pessoa_instituicao', { ...anterior.campos, pessoa_id: 'p-marta' }, id)).erros.length);
});
await verificar('conclusão duplicada rejeitada, renovação preservada', async () => {
  const campos = motor.obter('pessoa_curso', 'vc-p-joao').campos;
  assert.ok((await motor.salvar('pessoa_curso', { ...campos, instituicao_emissora: texto({campos}, 'instituicao_emissora').toLowerCase() })).erros.length);
  assert.equal((await motor.salvar('pessoa_curso', { ...campos, conclusao_em: '2026-01-01' })).erros.length, 0);
});
await verificar('responsável exclusivo e unidade compatível', async () => {
  assert.ok((await motor.salvar('recursos', { ...motor.obter('recursos', 'r-agua').campos, pessoa_id: 'p-joao' }, 'r-agua')).erros.length);
  assert.ok((await motor.salvar('demanda_itens', { ...motor.obter('demanda_itens', 'item-v-agua').campos, id_unidade_medida: 'u-unidade' }, 'item-v-agua')).erros.length);
  assert.ok((await motor.salvar('demanda_itens', { ...motor.obter('demanda_itens', 'item-v-agua').campos, id_atividade: 'a-transporte' }, 'item-v-agua')).erros.length);
});
await verificar('nova ocorrência exige principal e preserva múltiplos tipos', async () => {
  const campos = { ...motor.obter('desastres', 'd-vale').campos, titulo: 'Outra ocorrência fictícia' };
  assert.ok((await motor.salvarDesastre(campos, '', '', [])).erros.length);
  const resultado = await motor.salvarDesastre(campos, '', 'td-inundacao', ['td-deslizamento', 'td-inundacao']);
  assert.equal(resultado.erros.length, 0);
  const tipos = motor.filhos('desastre_tipo', 'id_desastre', resultado.registro.id);
  assert.equal(tipos.length, 2); assert.equal(tipos.filter((t) => t.campos.principal).length, 1);
});
await verificar('nova área exige desenho e prioridade não copia gravidade', async () => {
  assert.ok((await motor.salvar('areas_afetadas', { ...motor.obter('areas_afetadas', 'area-centro').campos, geometria: [] })).erros.length);
  assert.equal(texto(motor.obter('areas_afetadas', 'area-centro'), 'gravidade'), 'moderada');
  assert.equal(texto(motor.obter('demandas', 'dem-centro'), 'prioridade'), 'urgente');
});
await verificar('alteração de termo invalida índices sem duplicar descrição', async () => {
  const atividade = motor.obter('atividades', 'a-transporte'), hash = texto(atividade, 'hash_conteudo_semantico');
  assert.match(hash, /^[0-9a-f]{64}$/);
  assert.equal((await motor.salvar('atividade_termos', { atividade_id: atividade.id, termo: 'Entrega ilustrativa' })).erros.length, 0);
  assert.notEqual(texto(atividade, 'hash_conteudo_semantico'), hash); assert.equal(motor.cobertura('mod-emb'), false);
  const indice = motor.filhos('atividade_indice_semantico', 'id_atividade', atividade.id)[0];
  assert.equal(texto(indice, 'situacao_indexacao'), 'pendente'); assert.ok(!('descricao' in indice.campos));
  await motor.indexar('mod-emb', 'atividade_indice_semantico'); assert.equal(motor.cobertura('mod-emb'), true);
});
await verificar('modelo de dimensão diferente precisa preparo, inferência não reindexa', async () => {
  const alternativo = motor.obter('modelo_ia', 'mod-emb-alt');
  assert.ok((await motor.salvar('modelo_ia', { ...alternativo.campos, ativo: true }, alternativo.id)).erros.length);
  await motor.indexar(alternativo.id, 'atividade_indice_semantico');
  assert.equal((await motor.salvar('modelo_ia', { ...alternativo.campos, ativo: true }, alternativo.id)).erros.length, 0);
  assert.equal(motor.registros('modelo_ia').filter((m) => m.campos.ativo && texto(m, 'finalidade') === 'embedding').length, 1);
  assert.equal((await motor.salvar('modelo_ia', { ...alternativo.campos, dimensao: '8' }, alternativo.id)).erros.length > 0, true);
  const indices = JSON.stringify(motor.estado.tabelas.atividade_indice_semantico);
  const textoAlt = motor.obter('modelo_ia', 'mod-text-alt');
  assert.equal((await motor.salvar('modelo_ia', { ...textoAlt.campos, ativo: true }, textoAlt.id)).erros.length, 0);
  assert.equal(JSON.stringify(motor.estado.tabelas.atividade_indice_semantico), indices);
});
await verificar('sugestão usa registros existentes e não soma cozinha com Paula', async () => {
  const rec = await motor.recomendar('dem-centro');
  const item = motor.filhos('recomendacao_itens', 'id_recomendacao', rec.id)[0];
  assert.equal(texto(item, 'quantidade_sugerida'), '0');
  assert.equal(motor.filhos('recomendacao_instituicoes', 'id_recomendacao_item', item.id).length, 1);
  assert.equal(motor.filhos('recomendacao_pessoas', 'id_recomendacao_item', item.id).length, 1);
  for (const candidato of motor.filhos('recomendacao_pessoas', 'id_recomendacao_item', item.id)) assert.ok(motor.obter('pessoas', texto(candidato, 'id_pessoa')));
});
await verificar('gerador não tem compatibilidade garantida; déficit de água é visível', async () => {
  const rec = await motor.recomendar('dem-encosta');
  const itens = motor.filhos('recomendacao_itens', 'id_recomendacao', rec.id);
  const gerador = itens.find((i) => texto(i, 'id_demanda_item') === 'item-e-gerador');
  assert.equal(texto(gerador, 'quantidade_sugerida'), '0'); assert.ok(motor.alertasCompartilhamento(rec.id).length);
  const total = motor.filhos('demanda_itens', 'id_tipo_recurso', 'tipo-agua').reduce((n, i) => n + Number(texto(i, 'quantidade_solicitada')), 0);
  assert.equal(total - Number(texto(motor.obter('recursos', 'r-agua'), 'quantidade_total')), 100);
});
await verificar('aprovação preserva recursos, pedido e missões; decisão não pode ser sobrescrita', async () => {
  const antes = JSON.stringify({ recursos: motor.estado.tabelas.recursos, itens: motor.estado.tabelas.demanda_itens, missoes: motor.estado.tabelas.missoes });
  const rec = await motor.recomendar('dem-varzea'); motor.decidir(rec.id, 'aprovada', 'Decisão demonstrativa');
  assert.equal(JSON.stringify({ recursos: motor.estado.tabelas.recursos, itens: motor.estado.tabelas.demanda_itens, missoes: motor.estado.tabelas.missoes }), antes);
  assert.throws(() => motor.decidir(rec.id, 'rejeitada', 'Outra decisão'));
  const outra = await motor.recomendar('dem-varzea'); assert.notEqual(outra.id, rec.id); assert.equal(texto(rec, 'situacao'), 'aprovada');
});
await verificar('pedido alterado exige outra análise antes de aprovação', async () => {
  const rec = await motor.recomendar('dem-varzea');
  const item = motor.obter('demanda_itens', 'item-v-agua');
  assert.equal((await motor.salvar('demanda_itens', { ...item.campos, quantidade_solicitada: '180' }, item.id)).erros.length, 0);
  assert.ok(motor.recomendacaoDesatualizada(rec)); assert.throws(() => motor.decidir(rec.id, 'aprovada', 'Não pode aprovar desatualizada'));
});
await verificar('referência inativada impede novo vínculo sem apagar histórico', async () => {
  await motor.inativar('profissoes', 'prof-condutor');
  assert.ok((await motor.salvar('pessoa_profissao', { pessoa_id: 'p-paula', profissao_id: 'prof-condutor', situacao_validacao: 'pendente' })).erros.length);
  assert.ok(motor.filhos('pessoa_profissao', 'profissao_id', 'prof-condutor').length);
});
await verificar('telas futuras cadastram rascunhos sem mover estoque', async () => {
  const agua = texto(motor.obter('recursos', 'r-agua'), 'quantidade_total');
  const resultado = await motor.salvar('movimentacoes_recurso', { id_recurso: 'r-agua', tipo: 'saida', quantidade: '10', realizada_em: '2026-10-08T12:00', justificativa: 'Rascunho de tela futura' });
  assert.equal(resultado.erros.length, 0); assert.equal(texto(motor.obter('recursos', 'r-agua'), 'quantidade_total'), agua);
});
process.stdout.write(`${total} verificações de domínio concluídas.\n`);
