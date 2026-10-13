/** Testa somente a aplicação local em navegador headless com perfil próprio. */
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { setTimeout as aguardar } from 'node:timers/promises';

const raiz = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const destino = resolve(raiz, 'verificacao'); mkdirSync(destino, { recursive: true });
const perfil = resolve(raiz, '.teste/navegador-' + Date.now()); mkdirSync(perfil, { recursive: true });
const candidatos = [process.env.PROTOTIPO_BROWSER, 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Google/Chrome/Application/chrome.exe'].filter(Boolean);
const executavel = candidatos.find((p) => existsSync(p));
if (!executavel) throw new Error('Defina PROTOTIPO_BROWSER com o caminho de Chrome/Edge para este teste.');
const processo = spawn(executavel, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--disable-background-networking', '--disable-component-update', '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=0', `--user-data-dir=${perfil}`, 'about:blank'], { windowsHide: true, stdio: 'ignore' });
const excecoes = [], verificacoes = [];
let socket, contador = 0, sessao = '';
const pendentes = new Map();
function chamar(method, params = {}, sessionId = sessao) {
  const id = ++contador;
  return new Promise((res, rej) => {
    const timeout = setTimeout(() => { pendentes.delete(id); rej(new Error(`Timeout: ${method}`)); }, 15000);
    pendentes.set(id, { res, rej, timeout }); socket.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
  });
}
async function avaliar(expression) {
  const resposta = await chamar('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (resposta.exceptionDetails) throw new Error(resposta.exceptionDetails.text);
  return resposta.result.value;
}
async function esperar(expression, motivo) {
  const limite = Date.now() + 15000;
  while (Date.now() < limite) { if (await avaliar(expression)) return; await aguardar(80); }
  throw new Error(`Espera falhou: ${motivo}. URL: ${await avaliar('location.href')}. DOM: ${await avaliar('document.body.innerText')}. Exceções: ${JSON.stringify(excecoes)}`);
}
async function navegar(hash, titulo) {
  await avaliar(`location.hash=${JSON.stringify(hash)}`);
  await esperar(`document.querySelector('main h1')?.textContent?.includes(${JSON.stringify(titulo)})`, hash);
}
async function clicar(texto, tag = 'button') {
  const encontrado = await avaliar(`(()=>{const e=[...document.querySelectorAll('main ${tag}')].find(e=>e.textContent.trim()===${JSON.stringify(texto)});if(!e||e.disabled)return false;e.click();return true;})()`);
  assert.equal(encontrado, true, `Ação ausente/desabilitada: ${texto}`);
}
async function preencher(id, valor) {
  assert.equal(await avaliar(`(()=>{const e=document.getElementById(${JSON.stringify(id)});if(!e)return false;e.value=${JSON.stringify(valor)};e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));return true;})()`), true, `Campo ausente: ${id}`);
}
async function captura(nome) {
  const imagem = await chamar('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  writeFileSync(resolve(destino, nome), Buffer.from(imagem.data, 'base64'));
}
async function verificar(nome, acao) { await acao(); verificacoes.push(nome); process.stdout.write(`OK ${nome}\n`); }

try {
  const arquivoPorta = resolve(perfil, 'DevToolsActivePort'); const limite = Date.now() + 20000;
  while (!existsSync(arquivoPorta) && Date.now() < limite) await aguardar(100);
  if (!existsSync(arquivoPorta)) throw new Error('O navegador headless não iniciou.');
  const [porta, caminho] = readFileSync(arquivoPorta, 'utf8').trim().split(/\r?\n/);
  socket = new WebSocket(`ws://127.0.0.1:${porta}${caminho}`);
  await new Promise((res, rej) => { socket.addEventListener('open', res, { once: true }); socket.addEventListener('error', rej, { once: true }); });
  socket.addEventListener('message', (evento) => {
    const dado = JSON.parse(evento.data);
    if (dado.id) { const p = pendentes.get(dado.id); if (p) { clearTimeout(p.timeout); pendentes.delete(dado.id); dado.error ? p.rej(new Error(dado.error.message)) : p.res(dado.result); } }
    if (dado.method === 'Runtime.exceptionThrown') excecoes.push(dado.params.exceptionDetails.exception?.description || dado.params.exceptionDetails.text);
    if (dado.method === 'Runtime.consoleAPICalled' && dado.params.type === 'error') excecoes.push(dado.params.args.map(a => a.description || a.value).join(' '));
    if (dado.method === 'Page.javascriptDialogOpening') void chamar('Page.handleJavaScriptDialog', { accept: true });
  });
  const alvo = await chamar('Target.createTarget', { url: 'http://127.0.0.1:4300/#/inicio' }, '');
  const ligacao = await chamar('Target.attachToTarget', { targetId: alvo.targetId, flatten: true }, ''); sessao = ligacao.sessionId;
  await chamar('Runtime.enable'); await chamar('Page.enable');
  await chamar('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
  await esperar('document.querySelector("main h1")?.textContent.includes("Visão do projeto")', 'Inicialização Angular');
  await captura('visao-geral.png');
  const require = createRequire(import.meta.url), { TELAS } = require(resolve(raiz, '.teste/dominio/telas.js'));
  const { criarEstado } = require(resolve(raiz, '.teste/dominio/cenario.js'));
  const { MotorPrototipo } = require(resolve(raiz, '.teste/dominio/motor.js'));
  const referenciaInicial = new MotorPrototipo(criarEstado());
  let formularios = 0, detalhes = 0;
  await verificar('50 listas, formulários, detalhes e seis telas complementares renderizam', async () => {
    for (const tela of TELAS) {
      await navegar('/' + tela.chave, tela.nome);
      if (!tela.somenteLeitura && tela.chave !== 'areas_afetadas') {
        await navegar('/' + tela.chave + '/novo', 'Cadastrar ' + tela.singular);
        assert.ok(await avaliar('!!document.querySelector("main form")'), tela.chave); formularios++;
      }
      const registro = criarEstado().tabelas[tela.chave]?.[0];
      if (registro) {
        await avaliar(`location.hash=${JSON.stringify('/' + tela.chave + '/' + registro.id)}`);
        await esperar(`document.querySelector("main h1")?.textContent.trim()===${JSON.stringify(referenciaInicial.nome(tela.chave, registro.id))} && !document.querySelector("main form")`, 'Detalhe de ' + tela.chave);
        assert.equal(await avaliar('document.querySelector("main h1").textContent.includes("não encontrado")'), false, tela.chave); detalhes++;
      }
    }
    for (const [rota, titulo] of [['/projeto','Todas as telas'],['/historico','Histórico de análises'],['/acesso','Acesso demonstrativo'],['/indices','Índices semânticos'],['/mapa','Mapa da ocorrência'],['/inicio','Visão do projeto']]) await navegar(rota, titulo);
    await navegar('/pessoas', 'Pessoas'); await navegar('/instituicoes','Instituições');
    await avaliar('history.back()'); await esperar('document.querySelector("main h1")?.textContent.includes("Pessoas")','Voltar do navegador');
    await avaliar('history.forward()'); await esperar('document.querySelector("main h1")?.textContent.includes("Instituições")','Avançar do navegador');
  });
  await verificar('CRUD de instituição pela interface e busca na lista', async () => {
    await navegar('/instituicoes/novo', 'Cadastrar instituição');
    await preencher('campo-nome','Instituição de teste UI — fictícia'); await preencher('campo-municipio_codigo_ibge','0000001'); await preencher('campo-uf','SP');
    await clicar('Salvar na sessão'); await esperar('document.querySelector("main h1")?.textContent.includes("Instituição de teste UI")', 'Salvar instituição');
    await clicar('Editar','a'); await esperar('document.querySelector("main h1")?.textContent.includes("Editar instituição")', 'Editar instituição');
    await preencher('campo-nome','Instituição corrigida UI — fictícia'); await clicar('Salvar na sessão');
    await esperar('document.querySelector("main h1")?.textContent.includes("Instituição corrigida UI")','Atualização');
    await clicar('Inativar'); await esperar('document.querySelector("main")?.innerText.includes("Registro inativado;")','Inativação');
    await navegar('/instituicoes','Instituições'); await preencher('busca','corrigida UI');
    assert.equal(await avaliar('document.querySelector("tbody")?.innerText.includes("corrigida UI")'), false);
    await avaliar('document.querySelector("main input[type=checkbox]").click()');
    await esperar('document.querySelector("tbody")?.innerText.includes("corrigida UI")','Consulta de inativados');
  });
  await verificar('demanda, item, sugestão e aprovação pelo navegador', async () => {
    await navegar('/demandas/novo?id_area_afetada=area-centro','Cadastrar demanda');
    await preencher('campo-titulo','Pedido pela interface — fictício'); await preencher('campo-descricao','Pedido criado no teste de navegação');
    await preencher('campo-inicio_previsto_em','2026-10-08T09:00'); await preencher('campo-prazo_em','2026-10-08T14:00'); await preencher('campo-id_pessoa_solicitante','p-paula');
    await clicar('Salvar na sessão'); await esperar('document.querySelector("main h1")?.textContent.includes("Pedido pela interface")','Demanda salva');
    assert.ok(await avaliar('document.querySelector("main")?.innerText.includes("Rascunho")'));
    await clicar('Adicionar item','a'); await esperar('document.querySelector("main h1")?.textContent.includes("Cadastrar item")','Novo item');
    await preencher('campo-id_tipo_recurso','tipo-agua'); await preencher('campo-quantidade_solicitada','25'); await preencher('campo-id_unidade_medida','u-litro');
    await clicar('Salvar na sessão'); await esperar('document.querySelector("main h1")?.textContent.includes("Pedido pela interface")','Item salvo');
    await clicar('Gerar recomendação simulada'); await esperar('document.querySelector("main h1")?.textContent.includes("Análise da recomendação")','Sugestão');
    await esperar('document.querySelector("main")?.innerText.includes("quantidade potencial sugerida: 25")','Quantidade informada');
    await preencher('decisao','Aprovação fictícia no teste de interface'); await clicar('Aprovar recomendação');
    await esperar('document.querySelector("main")?.innerText.includes("Decisão registrada")','Decisão');
    await captura('recomendacao.png');
    const anterior = await avaliar('location.hash'); await clicar('Gerar outra análise simulada');
    await esperar(`location.hash!==${JSON.stringify(anterior)} && !!document.getElementById('decisao')`,'Nova análise');
    assert.equal(await avaliar('document.getElementById("decisao").value'),'');
    await preencher('decisao','Rejeição fictícia para preservar histórico'); await clicar('Rejeitar recomendação');
    await esperar('document.querySelector("main")?.innerText.includes("Decisão registrada")','Rejeição');
    await navegar('/recursos/r-agua','Lote de água');
    assert.equal(await avaliar('[...document.querySelectorAll("main dt")].find(e=>e.textContent.trim()==="Quantidade total")?.nextElementSibling?.textContent.trim()'),'300');
  });
  await verificar('mapa desenha dentro de outra área e salva avaliação', async () => {
    await navegar('/areas_afetadas/area-encosta', 'Encosta'); await clicar('Abrir mapa','a');
    await esperar('document.querySelector("main h1")?.textContent.includes("Mapa da ocorrência") && document.getElementById("area-nome")?.value==="Encosta"','Contexto da área no mapa');
    await navegar('/inicio','Visão do projeto'); await navegar('/mapa','Mapa da ocorrência'); await captura('mapa.png'); await clicar('Desenhar nova área');
    const retangulo = await avaliar('(()=>{const r=document.querySelector("svg").getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()');
    for (const [x,y] of [[.20,.30],[.30,.30],[.25,.40]]) {
      const ponto = { x: retangulo.x + retangulo.w*x, y: retangulo.y + retangulo.h*y, button:'left', clickCount:1 };
      await chamar('Input.dispatchMouseEvent',{ ...ponto, type:'mousePressed' }); await chamar('Input.dispatchMouseEvent',{ ...ponto, type:'mouseReleased' });
    }
    await esperar('document.querySelector("main")?.innerText.includes("3 vértices")','Vértices no polígono');
    await preencher('area-nome','Área criada pelo navegador — fictícia'); await clicar('Salvar área e avaliação');
    await esperar('document.querySelector("main")?.innerText.includes("Área e avaliação salvas")','Área salva');
    assert.equal(await avaliar('document.querySelectorAll("svg polygon").length'),4);
  });
  await verificar('histórico preserva as decisões e fluxo usa somente a aplicação local', async () => {
    await navegar('/historico','Histórico de análises');
    assert.ok(await avaliar('document.querySelector("main")?.innerText.includes("aprovada") && document.querySelector("main")?.innerText.includes("rejeitada")'));
    const acessos = await avaliar('performance.getEntriesByType("resource").map(e=>e.name)');
    assert.ok(acessos.every((url)=>new URL(url).hostname==='127.0.0.1'));
    assert.deepEqual(excecoes, []);
  });
  writeFileSync(resolve(destino,'navegacao.json'), JSON.stringify({ executado_em:new Date().toISOString(), navegador:executavel, listas:50, formularios, detalhes, complementares:6, verificacoes, excecoes },null,2)+'\n');
  process.stdout.write(`${verificacoes.length} cenários de navegador passaram; capturas em verificacao/.\n`);
} finally {
  if (socket?.readyState===WebSocket.OPEN) {
    await chamar('Browser.close', {}, '').catch(()=>{}); socket.close();
  }
  if (processo.exitCode===null) processo.kill();
  for (const p of pendentes.values()) { clearTimeout(p.timeout); p.rej(new Error('Teste encerrado.')); }
}
