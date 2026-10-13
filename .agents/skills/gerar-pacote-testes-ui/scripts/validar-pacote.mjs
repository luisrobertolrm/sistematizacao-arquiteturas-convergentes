// Validador portátil da Suíte de Testes (v3.0.0): Node.js puro sem dependências externas.
import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const actions = new Set(['goto', 'reload', 'click', 'fill', 'select', 'check', 'uncheck', 'press', 'visible', 'hidden', 'text', 'value', 'count', 'url']);
const assertions = new Set(['visible', 'hidden', 'text', 'value', 'count', 'url']);
const targets = ['role', 'label', 'text', 'testId', 'css'];

function assertRule(condition, msg) {
  if (!condition) throw new Error(msg);
}

export function validateStep(s, at = 'passo') {
  assertRule(s && typeof s === 'object', `${at}: passo deve ser um objeto.`);
  const action = s.acao || s.action;
  assertRule(action && actions.has(action), `${at}: ação inválida ou ausente: "${action}".`);

  const target = s.alvo || s.target;
  const value = s.valor !== undefined ? s.valor : (s.value !== undefined ? s.value : (s.rota !== undefined ? s.rota : (s.texto !== undefined ? s.texto : undefined)));
  const dialog = s.dialog;

  if (!['goto', 'url', 'reload'].includes(action)) {
    assertRule(target && typeof target === 'object', `${at}: informe um alvo/target com role, label, text, testId ou css.`);
    const matching = targets.filter(k => Object.hasOwn(target, k));
    assertRule(matching.length === 1 && typeof target[matching[0]] === 'string' && target[matching[0]].trim(), `${at}: alvo deve conter exatamente um seletor não vazio entre: ${targets.join(', ')}.`);
    if (target.name !== undefined) assertRule(typeof target.name === 'string', `${at}: name do seletor deve ser texto.`);
  } else {
    assertRule(target === undefined, `${at}: ação "${action}" não recebe alvo.`);
  }

  if (['goto', 'fill', 'select', 'press', 'text', 'value', 'url'].includes(action)) {
    assertRule(typeof value === 'string', `${at}: ação "${action}" exige valor/texto em string.`);
  }
  if (action === 'count') {
    assertRule(Number.isInteger(value) && value >= 0, `${at}: count exige inteiro >= 0.`);
  }
  if (dialog !== undefined) {
    assertRule(action === 'click', `${at}: dialog permitido somente na ação click.`);
    assertRule(['accept', 'dismiss'].includes(dialog), `${at}: dialog deve ser accept ou dismiss.`);
  }

  return { action, target, value, dialog };
}

export function validateFeatureSpec(spec, filePath = '') {
  assertRule(spec && typeof spec === 'object', `Spec inválida em ${filePath}: esperado objeto JSON.`);
  const feature = spec.funcionalidade || {};
  const featureId = feature.id || spec.id;
  const featureName = feature.nome || spec.nome || featureId;
  const objetivo = feature.objetivo || spec.objetivo;

  assertRule(featureId && typeof featureId === 'string', `Spec em ${filePath}: id da funcionalidade é obrigatório.`);
  assertRule(objetivo && typeof objetivo === 'string' && objetivo.trim(), `Spec em ${filePath} (${featureId}): seção "objetivo" é obrigatória.`);
  assertRule(Array.isArray(spec.fluxos) && spec.fluxos.length > 0, `Spec em ${filePath} (${featureId}): deve conter ao menos um fluxo.`);

  const flowIds = new Set();
  let totalAssertions = 0;
  let totalExceptions = 0;

  for (const [i, fluxo] of spec.fluxos.entries()) {
    const fAt = `[${featureId}] Fluxo ${i + 1}`;
    assertRule(fluxo && typeof fluxo === 'object', `${fAt}: deve ser um objeto.`);
    const flowId = fluxo.id;
    assertRule(flowId && typeof flowId === 'string' && !flowIds.has(flowId), `${fAt}: id único é obrigatório.`);
    flowIds.add(flowId);

    const titulo = fluxo.titulo || fluxo.nome;
    assertRule(titulo && typeof titulo === 'string', `${fAt} (${flowId}): título é obrigatório.`);
    assertRule(Array.isArray(fluxo.passos) && fluxo.passos.length > 0, `${fAt} (${flowId}): deve conter lista de passos.`);
    fluxo.passos.forEach((p, idx) => validateStep(p, `${fAt} (${flowId}) passo ${idx + 1}`));

    assertRule(fluxo.resultado_esperado && typeof fluxo.resultado_esperado === 'object', `${fAt} (${flowId}): "resultado_esperado" é obrigatório.`);
    const verificacoes = fluxo.resultado_esperado.verificacoes;
    assertRule(Array.isArray(verificacoes) && verificacoes.length > 0, `${fAt} (${flowId}): "resultado_esperado.verificacoes" deve conter ao menos uma verificação.`);
    verificacoes.forEach((v, idx) => {
      const norm = validateStep(v, `${fAt} (${flowId}) verificação ${idx + 1}`);
      if (assertions.has(norm.action)) totalAssertions++;
    });

    const excecoes = fluxo.excecoes || fluxo.fluxos_excecoes || [];
    assertRule(Array.isArray(excecoes), `${fAt} (${flowId}): exceções deve ser um array.`);
    const excIds = new Set();

    for (const [eIdx, exc] of excecoes.entries()) {
      const eAt = `${fAt} (${flowId}), Exceção ${eIdx + 1}`;
      assertRule(exc && typeof exc === 'object', `${eAt}: deve ser um objeto.`);
      const excId = exc.id;
      assertRule(excId && typeof excId === 'string' && !excIds.has(excId), `${eAt}: id único é obrigatório.`);
      excIds.add(excId);

      assertRule(Array.isArray(exc.passos) && exc.passos.length > 0, `${eAt} (${excId}): passos obrigatórios.`);
      exc.passos.forEach((p, idx) => validateStep(p, `${eAt} (${excId}) passo ${idx + 1}`));

      assertRule(exc.resultado_esperado && typeof exc.resultado_esperado === 'object', `${eAt} (${excId}): "resultado_esperado" obrigatório.`);
      const excVerificacoes = exc.resultado_esperado.verificacoes;
      assertRule(Array.isArray(excVerificacoes) && excVerificacoes.length > 0, `${eAt} (${excId}): verificações obrigatórias.`);
      excVerificacoes.forEach((v, idx) => {
        const norm = validateStep(v, `${eAt} (${excId}) verificação ${idx + 1}`);
        if (assertions.has(norm.action)) totalAssertions++;
      });
      totalExceptions++;
    }
  }

  assertRule(totalAssertions > 0, `Spec em ${filePath} (${featureId}): nenhuma asserção observável foi encontrada.`);

  return {
    featureId,
    featureName,
    totalFlows: spec.fluxos.length,
    totalExceptions,
    totalAssertions
  };
}

export function validateSuite(mapeamentoPath) {
  const fullPath = resolve(mapeamentoPath);
  const root = dirname(fullPath);
  assertRule(existsSync(fullPath), `Arquivo de mapeamento não encontrado: ${fullPath}`);

  const manifest = JSON.parse(readFileSync(fullPath, 'utf8'));
  assertRule(manifest && typeof manifest === 'object', 'mapeamento.json deve ser um objeto JSON.');
  assertRule(Array.isArray(manifest.funcionalidades) && manifest.funcionalidades.length > 0, 'mapeamento.json: deve conter funcionalidades não vazio.');

  const results = [];
  const ids = new Set();

  for (const item of manifest.funcionalidades) {
    assertRule(item && item.id && !ids.has(item.id), `Funcionalidade com id duplicado ou ausente: ${item?.id}`);
    ids.add(item.id);

    const specRel = item.arquivo_spec || item.spec || (item.pasta ? join(item.pasta, 'spec.json') : 'spec.json');
    const specPath = resolve(root, specRel);
    assertRule(existsSync(specPath), `Arquivo spec.json não encontrado: ${specPath}`);

    const specRaw = JSON.parse(readFileSync(specPath, 'utf8'));
    const validated = validateFeatureSpec(specRaw, specPath);

    // Valida também se o arquivo de histórico existe ou se o caminho é válido
    const histRel = item.arquivo_historico || (item.pasta ? join(item.pasta, 'historico.json') : join(dirname(specRel), 'historico.json'));
    const histPath = resolve(root, histRel);
    if (existsSync(histPath)) {
      try {
        const histData = JSON.parse(readFileSync(histPath, 'utf8'));
        assertRule(Array.isArray(histData.execucoes), `historico.json em ${histPath}: "execucoes" deve ser um array.`);
      } catch (err) {
        throw new Error(`historico.json inválido em ${histPath}: ${err.message}`);
      }
    }

    results.push(validated);
  }

  return {
    projeto: manifest.projeto?.nome || 'Suíte de Testes',
    totalFeatures: results.length,
    features: results
  };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const targetPath = process.argv[2] || 'specs/mapeamento.json';
    const resolved = resolve(targetPath);
    if (resolved.endsWith('spec.json')) {
      const spec = JSON.parse(readFileSync(resolved, 'utf8'));
      const res = validateFeatureSpec(spec, resolved);
      console.log(`✓ Spec "${res.featureName}" válida: ${res.totalFlows} fluxos, ${res.totalExceptions} exceções, ${res.totalAssertions} asserções.`);
    } else {
      const suite = validateSuite(resolved);
      const totalFlows = suite.features.reduce((acc, f) => acc + f.totalFlows, 0);
      const totalExceptions = suite.features.reduce((acc, f) => acc + f.totalExceptions, 0);
      console.log(`✓ Suíte "${suite.projeto}" válida: ${suite.totalFeatures} funcionalidades, ${totalFlows} fluxos, ${totalExceptions} exceções.`);
    }
  } catch (error) {
    console.error(`✗ Erro na validação: ${error.message}`);
    process.exitCode = 2;
  }
}
