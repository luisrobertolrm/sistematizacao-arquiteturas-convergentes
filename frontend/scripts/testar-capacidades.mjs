/** Verificação da aplicação integrada. Chamado pelo PostgreSQL isolado com --frontend. */
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { createServer, request } from 'node:http';
import { dirname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { setTimeout as aguardar } from 'node:timers/promises';

const raiz = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const build = resolve(raiz, 'dist/redesolidaria/browser');
assert.ok(existsSync(resolve(build,'index.html')), 'Execute npm run build antes do teste.');
const api = new URL(process.env.UI_TEST_API || '');
assert.equal(api.hostname,'127.0.0.1');
assert.ok(process.env.UI_TEST_TOKEN, 'Use backend/scripts/test_postgres.py --frontend.');
const destino = resolve(raiz,'verificacao'); mkdirSync(destino,{recursive:true});
const perfil = resolve(raiz,'.teste/browser-'+Date.now()); mkdirSync(perfil,{recursive:true});
const navegador = [process.env.UI_TEST_BROWSER,'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','C:/Program Files/Google/Chrome/Application/chrome.exe'].filter(Boolean).find(existsSync);
assert.ok(navegador,'Defina UI_TEST_BROWSER com o executável de Edge/Chrome.');
const mime = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png'};
const servidor = createServer((req,res)=>{
  const caminho = new URL(req.url,'http://127.0.0.1').pathname;
  if(caminho.startsWith('/api/')) {
    const proxy = request(new URL(req.url,api),{method:req.method,headers:{...req.headers,host:api.host}},(r)=>{res.writeHead(r.statusCode || 502,r.headers);r.pipe(res);});
    proxy.on('error',()=>{res.writeHead(502);res.end();});req.pipe(proxy);return;
  }
  const arquivo = resolve(build,'.'+decodeURIComponent(caminho==='/'?'/index.html':caminho));
  if(!arquivo.startsWith(build+sep)||!existsSync(arquivo)){res.writeHead(404);res.end();return;}
  const extensao = arquivo.slice(arquivo.lastIndexOf('.'));
  res.writeHead(200,{'Content-Type':mime[extensao] || 'application/octet-stream'});res.end(readFileSync(arquivo));
});
await new Promise((res,rej)=>{servidor.once('error',rej);servidor.listen(0,'127.0.0.1',res);});
const endereco = servidor.address(); assert.ok(endereco && typeof endereco==='object');
const pagina = 'http://127.0.0.1:'+endereco.port;
const processo = spawn(navegador,['--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check','--disable-background-networking','--remote-debugging-address=127.0.0.1','--remote-debugging-port=0',`--user-data-dir=${perfil}`,'about:blank'],{windowsHide:true,stdio:'ignore'});
let socket, id=0, sessao=''; const pendentes=new Map(), excecoes=[], verificacoes=[];
function chamar(method,params={},sessionId=sessao){return new Promise((res,rej)=>{const n=++id;const timeout=setTimeout(()=>{pendentes.delete(n);rej(new Error('Timeout '+method));},15000);pendentes.set(n,{res,rej,timeout});socket.send(JSON.stringify({id:n,method,params,...(sessionId?{sessionId}:{})}));});}
async function avaliar(expression){const r=await chamar('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(r.exceptionDetails.text);return r.result.value;}
async function esperar(expression,motivo){const fim=Date.now()+15000;while(Date.now()<fim){if(await avaliar(expression))return;await aguardar(60);}throw new Error(motivo+': '+await avaliar('document.querySelector("main")?.innerText'));}
async function preencher(campo,valor){assert.ok(await avaliar(`(()=>{const e=document.getElementById(${JSON.stringify(campo)});if(!e)return false;e.value=${JSON.stringify(valor)};e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));return true})()`),'Campo '+campo);}
async function clicar(texto,seletor='button'){await esperar(`(()=>{const e=[...document.querySelectorAll(${JSON.stringify(seletor)})].find(e=>e.textContent.trim()===${JSON.stringify(texto)});return !!e&&!e.disabled})()`,'Ação '+texto);await avaliar(`(()=>{const e=[...document.querySelectorAll(${JSON.stringify(seletor)})].find(e=>e.textContent.trim()===${JSON.stringify(texto)});e.click()})()`);}
async function verificar(nome,acao){await acao();verificacoes.push(nome);process.stdout.write('OK '+nome+'\n');}
async function captura(nome){const r=await chamar('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});writeFileSync(resolve(destino,nome),Buffer.from(r.data,'base64'));}
async function registros(){await esperar('!document.querySelector("app-capacidades [aria-busy=true]")','Fim da operação');}
async function selecionar(rotulo){await clicar(rotulo);await esperar(`document.querySelector('app-capacidades .directory h2')?.textContent.trim()===${JSON.stringify(rotulo)}`,'Tela '+rotulo);await registros();}
const verificacoesVisuais=[];
async function viewport(largura,altura=1100) {
  await chamar('Emulation.setDeviceMetricsOverride',{width:largura,height:altura,deviceScaleFactor:1,mobile:largura<=760});
  await avaliar('window.scrollTo(0,0)');
}
async function layout(nome) {
  const estado=await avaliar(`(()=>{
    const largura=document.documentElement.clientWidth;
    const fora=[...document.querySelectorAll('main input,main select,main textarea,main button')].filter(e=>{
      const r=e.getBoundingClientRect();
      return r.width>0 && (r.left < -1 || r.right > largura+1);
    }).map(e=>e.id || e.textContent.trim());
    return {largura,conteudo:document.documentElement.scrollWidth,fora};
  })()`);
  assert.ok(estado.conteudo<=estado.largura+1, nome+': rolagem horizontal '+JSON.stringify(estado));
  assert.deepEqual(estado.fora,[],nome+': controles fora da tela');
  verificacoesVisuais.push({tela:nome,...estado});
}

try {
  const arquivo=resolve(perfil,'DevToolsActivePort');const fim=Date.now()+20000;
  while(!existsSync(arquivo)&&Date.now()<fim)await aguardar(100);
  assert.ok(existsSync(arquivo),'Navegador não iniciou.');
  const [porta,caminho]=readFileSync(arquivo,'utf8').trim().split(/\r?\n/);
  socket=new WebSocket(`ws://127.0.0.1:${porta}${caminho}`);
  await new Promise((res,rej)=>{socket.addEventListener('open',res,{once:true});socket.addEventListener('error',rej,{once:true});});
  socket.addEventListener('message',(evento)=>{const d=JSON.parse(evento.data);if(d.id){const p=pendentes.get(d.id);if(p){clearTimeout(p.timeout);pendentes.delete(d.id);d.error?p.rej(new Error(d.error.message)):p.res(d.result);}}if(d.method==='Fetch.requestPaused')void chamar('Fetch.fulfillRequest',{requestId:d.params.requestId,responseCode:200,responseHeaders:[{name:'Content-Type',value:'image/svg+xml'}],body:Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256"><rect width="256" height="256" fill="#e9edee"/><path d="M0 128H256M128 0V256" stroke="#b6c0c2"/><text x="12" y="28" fill="#53666c" font-size="12">Fundo simulado no teste</text></svg>').toString('base64')}).catch(()=>{});if(d.method==='Runtime.exceptionThrown')excecoes.push(d.params.exceptionDetails.exception?.description||d.params.exceptionDetails.text);if(d.method==='Page.javascriptDialogOpening')void chamar('Page.handleJavaScriptDialog',{accept:true});});
  const alvo=await chamar('Target.createTarget',{url:pagina},'');sessao=(await chamar('Target.attachToTarget',{targetId:alvo.targetId,flatten:true},'')).sessionId;
  await chamar('Runtime.enable');await chamar('Page.enable');await chamar('Fetch.enable',{patterns:[{urlPattern:'https://tile.openstreetmap.org/*'}]});await chamar('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false});
  await esperar('!!document.getElementById("token")','Acesso Angular');
  await layout('Acesso desktop');await captura('estilo-acesso-desktop.png');
  await viewport(390,844);await layout('Acesso celular');await captura('estilo-acesso-mobile.png');await viewport(1440);
  await preencher('token',process.env.UI_TEST_TOKEN);await clicar('Acessar cadastros');
  await esperar('[...document.querySelectorAll(".app-sidebar nav button")].some(e=>e.textContent==="Atividades e unidades" && !e.disabled)','Autenticação');
  await esperar('!document.querySelector("main > .workspace [aria-busy=true]")','Cadastros');await layout('Instituições desktop');await captura('estilo-cadastros-desktop.png');
  await clicar('Atividades e unidades');
  await registros();
  await verificar('cadastro de unidade e categoria pela API real',async()=>{
    await preencher('capacidade-codigo','viagem-ui');await preencher('capacidade-nome','Viagem de teste UI');await preencher('capacidade-simbolo','v');await clicar('Salvar capacidade');await registros();
    await esperar('document.querySelector("app-capacidades .directory")?.innerText.includes("Viagem de teste UI")','Unidade criada');
    await selecionar('Categorias de atividade');await preencher('capacidade-codigo','logistica-ui');await preencher('capacidade-nome','Logística de teste UI');await preencher('capacidade-descricao','Categoria fictícia do teste');await clicar('Salvar capacidade');await registros();
    await esperar('document.querySelector("app-capacidades .directory")?.innerText.includes("Logística de teste UI")','Categoria criada');
  });
  await verificar('atividade com referências e busca textual pelos termos',async()=>{
    await selecionar('Atividades');await preencher('capacidade-codigo','transporte-ui');await preencher('capacidade-nome','Transporte de teste UI');await preencher('capacidade-descricao','Transportar carga seca');
    await esperar('[...document.querySelectorAll("#categoria-ref-id option")].some(e=>e.textContent==="Logística de teste UI") && [...document.querySelectorAll("#unidade-ref-id option")].some(e=>e.textContent==="Viagem de teste UI")','Referências paginadas');
    const cat=await avaliar('[...document.querySelectorAll("#categoria-ref-id option")].find(e=>e.textContent==="Logística de teste UI").value');const un=await avaliar('[...document.querySelectorAll("#unidade-ref-id option")].find(e=>e.textContent==="Viagem de teste UI").value');
    await preencher('categoria-ref-id',cat);await preencher('unidade-ref-id',un);await clicar('Salvar capacidade');await registros();
    await esperar('document.querySelector("app-capacidades .directory")?.innerText.includes("Transporte de teste UI")','Atividade criada');
    await preencher('capacidade-busca','transporte-ui');await clicar('Buscar');await registros();
    await clicar('Termos e sinônimos');await esperar('!!document.getElementById("atividade-termo") && !document.querySelector("app-termos [aria-busy=true]")','Tela de termos');
    const hashInicial=await avaliar('document.querySelector("app-termos code").textContent');await preencher('atividade-termo','  REMESSA   Solidária  ');await clicar('Salvar termo');
    await esperar('document.querySelector("app-termos .directory")?.innerText.includes("remessa solidária") && !document.querySelector("app-termos [aria-busy=true]")','Termo normalizado');
    assert.notEqual(await avaliar('document.querySelector("app-termos code").textContent'),hashInicial);await clicar('Voltar às atividades');await registros();
    await preencher('capacidade-busca','remessa');await clicar('Buscar');await registros();assert.ok(await avaliar('document.querySelector("app-capacidades .directory")?.innerText.includes("Transporte de teste UI")'));
    await captura('incremento-3-atividades.png');
  });
  await verificar('edição, conflito e inativação dos termos preservam histórico',async()=>{
    await clicar('Termos e sinônimos');await esperar('!!document.getElementById("atividade-termo") && !document.querySelector("app-termos [aria-busy=true]")','Termos');
    await preencher('atividade-termo','Remessa solidária');await clicar('Salvar termo');await esperar('!!document.querySelector("app-termos [role=alert]") && !document.querySelector("app-termos [aria-busy=true]")','Conflito de duplicidade');
    assert.equal(await avaliar('document.querySelectorAll("app-termos .record").length'),1);
    await clicar('Editar termo');await preencher('atividade-termo','entrega de suprimentos ui');await clicar('Salvar termo');await esperar('document.querySelector("app-termos .directory")?.innerText.includes("entrega de suprimentos ui") && !document.querySelector("app-termos [aria-busy=true]")','Termo alterado');
    await clicar('Inativar termo');await esperar('document.querySelectorAll("app-termos .record").length===0 && !document.querySelector("app-termos [aria-busy=true]")','Termo inativado');
    await avaliar('document.getElementById("termos-historico").click()');await esperar('document.querySelector("app-termos .directory")?.innerText.includes("Inativado") && !document.querySelector("app-termos [aria-busy=true]")','Histórico do termo');
    await captura('incremento-3-termos.png');await clicar('Voltar às atividades');await registros();
    await preencher('capacidade-busca','transporte-ui');await clicar('Buscar');await registros();await clicar('Editar','app-capacidades .record button');
    assert.ok(await avaliar('document.getElementById("capacidade-codigo").readOnly'));await preencher('capacidade-nome','Transporte corrigido UI');await clicar('Salvar capacidade');await registros();
    await esperar('document.querySelector("app-capacidades .directory")?.innerText.includes("Transporte corrigido UI")','Atividade corrigida');
    await clicar('Inativar','app-capacidades .record button');await registros();await avaliar('document.getElementById("capacidade-historico").click()');
    await esperar('document.querySelector("app-capacidades .directory")?.innerText.includes("Inativado") && !document.querySelector("app-capacidades [aria-busy=true]")','Histórico da atividade');
    assert.deepEqual(excecoes,[]);
  });
  writeFileSync(resolve(destino,'incremento-3.json'),JSON.stringify({executado_em:new Date().toISOString(),navegador,integracao:'Angular + FastAPI + PostgreSQL exclusivo de testes',verificacoes,excecoes},null,2)+'\n');
  async function prontoRecursos() { await esperar('!!document.querySelector("app-recursos .directory") && !document.querySelector("app-recursos [aria-busy=true]")', 'Operação de recursos'); }
  async function opcao(campo, nome) {
    await esperar(`[...document.querySelectorAll('#${campo} option')].some(e=>e.textContent.trim()===${JSON.stringify(nome)})`, 'Referência '+nome);
    const valor = await avaliar(`[...document.querySelectorAll('#${campo} option')].find(e=>e.textContent.trim()===${JSON.stringify(nome)}).value`);
    await preencher(campo, valor);
  }
  async function abaRecurso(nome) {
    await clicar(nome, 'app-recursos nav button'); await prontoRecursos();
    await esperar(`document.querySelector('app-recursos .directory h2')?.textContent.trim()===${JSON.stringify(nome)}`, 'Tela '+nome);
  }
  await verificar('pessoa, tipo e recurso individual com validação pela API', async()=>{
    await clicar('Pessoas', '.toolbar nav button');
    await esperar('!document.querySelector("app-root > main > .workspace [aria-busy=true]") && !!document.getElementById("cadastro-nome")', 'Pessoas');
    await preencher('cadastro-nome','Responsável teste UI recursos'); await preencher('municipio','3550308'); await preencher('uf','SP'); await clicar('Cadastrar');
    await esperar('document.querySelector("app-root > main > .workspace .directory")?.innerText.includes("Responsável teste UI recursos") && !document.querySelector("app-root > main > .workspace [aria-busy=true]")', 'Responsável cadastrado');
    await clicar('Recursos e ofertas'); await prontoRecursos();
    await preencher('recurso-nome','Gerador individual UI'); await opcao('recurso-ref-id','Viagem de teste UI'); await clicar('Salvar cadastro'); await prontoRecursos();
    await esperar('document.querySelector("app-recursos .directory")?.innerText.includes("Gerador individual UI")','Tipo individual salvo');
    await abaRecurso('Recursos'); await preencher('recurso-nome','Gerador portátil UI'); await opcao('recurso-ref-id','Gerador individual UI');
    await preencher('recurso-dono-tipo','pessoas'); await opcao('responsavel-ref-id','Responsável teste UI recursos');
    await preencher('recurso-municipio','3550308'); await preencher('recurso-quantidade','2'); await clicar('Salvar cadastro');
    await esperar('document.querySelector("app-recursos [role=alert]")?.innerText.includes("igual a 1") && !document.querySelector("app-recursos [aria-busy=true]")','Quantidade individual rejeitada');
    await preencher('recurso-quantidade','1'); await clicar('Salvar cadastro'); await prontoRecursos();
    await esperar('document.querySelector("app-recursos .directory")?.innerText.includes("Gerador portátil UI")','Recurso salvo');
    await preencher('recurso-busca','Gerador portátil UI'); await clicar('Buscar','app-recursos .directory button'); await prontoRecursos();
    await clicar('Editar','app-recursos .record button'); assert.ok(await avaliar('document.getElementById("recurso-ref-id").disabled'));
    await preencher('recurso-identificacao','PATR-UI-01'); await clicar('Salvar cadastro'); await prontoRecursos();
    await esperar('document.querySelector("app-recursos .directory")?.innerText.includes("PATR-UI-01")','Identificação editada');
    await captura('incremento-4-recursos.png');
  });
  await verificar('oferta de pessoa validada com capacidade na unidade da atividade',async()=>{
    await clicar('Atividades e unidades', '.toolbar nav button'); await selecionar('Atividades');
    await preencher('capacidade-codigo','atividade-oferta-ui'); await preencher('capacidade-nome','Oferta de transporte UI'); await preencher('capacidade-descricao','Transporte de apoio ao teste de ofertas');
    await opcao('categoria-ref-id','Logística de teste UI'); await opcao('unidade-ref-id','Viagem de teste UI'); await clicar('Salvar capacidade'); await registros();
    await esperar('document.querySelector("app-capacidades .directory")?.innerText.includes("Oferta de transporte UI")','Atividade para oferta');
    await clicar('Recursos e ofertas'); await prontoRecursos(); await abaRecurso('Ofertas de atividades');
    await opcao('recurso-ref-id','Oferta de transporte UI'); await preencher('recurso-dono-tipo','pessoas'); await opcao('responsavel-ref-id','Responsável teste UI recursos');
    await preencher('recurso-municipio','3550308'); await preencher('oferta-capacidade','2.5'); await preencher('oferta-validacao','validada'); await clicar('Salvar cadastro'); await prontoRecursos();
    await esperar('document.querySelector("app-recursos .directory")?.innerText.includes("Validada em")','Oferta validada');
    await preencher('recurso-busca','Oferta de transporte UI'); await clicar('Buscar','app-recursos .directory button'); await prontoRecursos();
    assert.ok(await avaliar('document.querySelector("app-recursos .directory").innerText.includes("2.5000")'));
    await opcao('recurso-ref-id','Oferta de transporte UI'); await preencher('recurso-dono-tipo','pessoas'); await opcao('responsavel-ref-id','Responsável teste UI recursos'); await preencher('recurso-municipio','3550308');
    await clicar('Salvar cadastro'); await esperar('!!document.querySelector("app-recursos [role=alert]") && !document.querySelector("app-recursos [aria-busy=true]")','Duplicidade da oferta');
    assert.equal(await avaliar('document.querySelectorAll("app-recursos .directory .record").length'),1);
    await captura('incremento-4-ofertas.png');
  });
  await verificar('vínculo de recurso com escopo da oferta, quantidade e conflito',async()=>{
    await clicar('Recursos da oferta','app-recursos .record button');
    await esperar('!!document.querySelector("app-oferta-recursos") && !document.querySelector("app-oferta-recursos [aria-busy=true]")','Vínculos da oferta');
    await opcao('oferta-recurso-ref-id','Gerador portátil UI'); await preencher('oferta-recurso-quantidade','0.5'); await clicar('Salvar vínculo');
    await esperar('document.querySelector("app-oferta-recursos [role=alert]")?.innerText.includes("quantidade 1") && !document.querySelector("app-oferta-recursos [aria-busy=true]")','Quantidade do vínculo');
    await preencher('oferta-recurso-quantidade','1'); await clicar('Salvar vínculo');
    await esperar('document.querySelector("app-oferta-recursos .directory")?.innerText.includes("Gerador portátil UI") && !document.querySelector("app-oferta-recursos [aria-busy=true]")','Vínculo criado');
    await opcao('oferta-recurso-ref-id','Gerador portátil UI'); await clicar('Salvar vínculo');
    await esperar('!!document.querySelector("app-oferta-recursos [role=alert]") && !document.querySelector("app-oferta-recursos [aria-busy=true]")','Duplicidade do vínculo');
    assert.equal(await avaliar('document.querySelectorAll("app-oferta-recursos .record").length'),1);
    await clicar('Editar vínculo'); assert.ok(await avaliar('document.getElementById("oferta-recurso-ref-id").disabled')); await clicar('Salvar vínculo');
    await esperar('!document.querySelector("app-oferta-recursos [aria-busy=true]")','Vínculo editado');
    await captura('incremento-4-vinculos.png');
  });
  await verificar('histórico de oferta inativa permite encerrar vínculos',async()=>{
    await clicar('Voltar às ofertas'); await prontoRecursos(); await clicar('Inativar','app-recursos .record button'); await prontoRecursos();
    await avaliar('document.getElementById("recurso-historico").click()');
    await esperar('document.querySelector("app-recursos .directory")?.innerText.includes("Inativado") && !document.querySelector("app-recursos [aria-busy=true]")','Oferta inativa');
    await clicar('Recursos da oferta','app-recursos .record button'); await esperar('!!document.querySelector("app-oferta-recursos") && !document.querySelector("app-oferta-recursos [aria-busy=true]")','Histórico dos vínculos');
    assert.ok(await avaliar('document.querySelector("app-oferta-recursos fieldset").disabled'));
    assert.ok(await avaliar('document.getElementById("oferta-recurso-historico").disabled'));
    await clicar('Inativar vínculo'); await esperar('document.querySelector("app-oferta-recursos .directory")?.innerText.includes("Vínculo inativado") && !document.querySelector("app-oferta-recursos [aria-busy=true]")','Vínculo inativado no histórico');
    assert.deepEqual(excecoes,[]);
  });
  writeFileSync(resolve(destino,'incremento-4.json'),JSON.stringify({executado_em:new Date().toISOString(),navegador,integracao:'Angular + FastAPI + PostgreSQL exclusivo de testes',verificacoes,excecoes},null,2)+'\n');
  async function prontoDesastres() { await esperar('!!document.querySelector("app-desastres .directory") && !document.querySelector("app-desastres [aria-busy=true]")','Operação territorial'); }
  async function prontoAreas() { await esperar('!!document.querySelector("app-areas .directory") && !document.querySelector("app-areas [aria-busy=true]")','Operação da área'); }
  async function desenhar(pontos) {
    await clicar('Desenhar nova delimitação');
    await avaliar('document.querySelector(".mapa-area").scrollIntoView({block:"center"})');
    const caixa = await avaliar('(()=>{const r=document.querySelector(".mapa-area").getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})()');
    for (const [x,y] of pontos) {
      const pos = {x:caixa.x+x*caixa.w,y:caixa.y+y*caixa.h};
      await chamar('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,...pos});
      await chamar('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,...pos});
    }
    await esperar(`document.querySelector('app-mapa-areas [role=status]')?.innerText.includes('Vértices do desenho: ${pontos.length}')`,'Pontos no mapa');
    await clicar('Concluir delimitação');
  }
  await verificar('catálogo, ocorrência e troca da classificação principal',async()=>{
    await clicar('Instituições','.toolbar nav button');
    await esperar('!!document.getElementById("cadastro-nome") && !document.querySelector("app-root > main > .workspace [aria-busy=true]")','Instituições');
    await preencher('cadastro-nome','Coordenação fictícia UI'); await preencher('municipio','3550308'); await preencher('uf','SP'); await clicar('Cadastrar');
    await esperar('document.querySelector("app-root > main > .workspace .directory")?.innerText.includes("Coordenação fictícia UI") && !document.querySelector("app-root > main > .workspace [aria-busy=true]")','Coordenadora');
    await clicar('Desastres e áreas'); await prontoDesastres(); await clicar('Tipos de desastre','app-desastres nav button'); await prontoDesastres();
    for (const [codigo,nome] of [['inundacao-ui','Inundação fictícia UI'],['deslizamento-ui','Deslizamento fictício UI']]) {
      await preencher('desastre-codigo',codigo); await preencher('desastre-nome',nome); await preencher('desastre-descricao','Tipo local para teste'); await clicar('Salvar desastre'); await prontoDesastres();
      await esperar(`document.querySelector('app-desastres .directory')?.innerText.includes(${JSON.stringify(nome)})`,'Tipo cadastrado');
    }
    await clicar('Ocorrências','app-desastres nav button'); await prontoDesastres();
    await preencher('desastre-nome','Inundação Vale UI'); await preencher('desastre-descricao','Ocorrência fictícia com áreas afetadas'); await preencher('desastre-inicio','2026-10-09T09:00'); await preencher('desastre-situacao','em_resposta');
    await opcao('coordenadora-ref-id','Coordenação fictícia UI');
    await opcao('classificacao-ref-id','Inundação fictícia UI'); await clicar('Adicionar classificação');
    await opcao('classificacao-ref-id','Deslizamento fictício UI'); await clicar('Adicionar classificação');
    await clicar('Salvar desastre'); await prontoDesastres();
    await preencher('desastre-busca','Inundação Vale UI'); await clicar('Buscar','app-desastres .directory button'); await prontoDesastres();
    await esperar('document.querySelector("app-desastres .directory")?.innerText.includes("Inundação Vale UI")','Ocorrência cadastrada');
    await clicar('Editar ocorrência','app-desastres .record button');
    await avaliar('[...document.querySelectorAll("app-desastres .editor input[type=radio]")][1].click()'); await clicar('Salvar desastre'); await prontoDesastres();
    await esperar('document.querySelector("app-desastres .directory")?.innerText.includes("Deslizamento fictício UI (principal)")','Tipo principal trocado');
    await captura('incremento-5-ocorrencias.png'); await clicar('Áreas e mapa','app-desastres .record button'); await prontoAreas();
    await esperar('!!document.querySelector(".leaflet-container .leaflet-control-attribution")','Leaflet inicializado');
  });
  await verificar('área desenhada no mapa, edição e avaliação independente',async()=>{
    await preencher('area-nome','Várzea fictícia UI'); await preencher('area-descricao','Área delimitada no teste'); await preencher('area-municipio','3550308'); await preencher('area-gravidade','alta'); await preencher('area-situacao','em_resposta');
    await desenhar([[0.25,0.3],[0.7,0.3],[0.7,0.75]]); await clicar('Salvar área'); await prontoAreas();
    await esperar('document.querySelector("app-areas .directory")?.innerText.includes("Várzea fictícia UI")','Área persistida');
    await clicar('Editar área');
    await esperar('document.querySelector("app-mapa-areas [role=status]")?.innerText.includes("Delimitação pronta")','Geometria carregada do banco');
    const avaliacao = await avaliar('document.querySelector("app-areas .record p:last-of-type").textContent');
    await preencher('area-nome','Várzea corrigida UI'); await clicar('Salvar área'); await prontoAreas();
    assert.equal(await avaliar('document.querySelector("app-areas .record p:last-of-type").textContent'),avaliacao);
    await clicar('Editar área'); await preencher('area-gravidade','critica'); await clicar('Salvar área'); await prontoAreas();
    await esperar('document.querySelector("app-areas .directory")?.innerText.includes("critica")','Gravidade alterada');
    await clicar('Confirmar avaliação atual'); await prontoAreas(); await esperar('document.querySelector("app-areas [role=status]")?.innerText.includes("Avaliação confirmada")','Reavaliação');
    await clicar('Ver delimitação'); await avaliar('document.querySelector("app-mapa-areas").scrollIntoView({block:"start"})'); await captura('incremento-5-mapa.png');
  });
  await verificar('polígono cruzado é rejeitado e desenho pode ser corrigido',async()=>{
    await clicar('Limpar área'); await preencher('area-nome','Encosta fictícia UI'); await preencher('area-descricao','Segunda área para validar geometria'); await preencher('area-municipio','3550308');
    await desenhar([[0.25,0.3],[0.7,0.75],[0.25,0.75],[0.7,0.3]]); await clicar('Salvar área');
    await esperar('!!document.querySelector("app-areas [role=alert]") && !document.querySelector("app-areas [aria-busy=true]")','Geometria inválida recusada');
    assert.equal(await avaliar('document.querySelectorAll("app-areas .record").length'),1);
    await desenhar([[0.25,0.3],[0.7,0.3],[0.7,0.75]]); await clicar('Salvar área'); await prontoAreas();
    await esperar('document.querySelectorAll("app-areas .record").length===2','Geometria corrigida');
    await clicar('Enquadrar áreas da página');
  });
  await verificar('histórico territorial preservado após inativar ocorrência',async()=>{
    await clicar('Voltar às ocorrências'); await prontoDesastres(); await clicar('Inativar ocorrência','app-desastres .record button'); await prontoDesastres();
    await avaliar('document.getElementById("desastre-historico").click()'); await prontoDesastres();
    await esperar('document.querySelector("app-desastres .directory")?.innerText.includes("Inativada")','Ocorrência inativa');
    await clicar('Áreas e mapa','app-desastres .record button'); await prontoAreas();
    assert.ok(await avaliar('document.querySelector("app-areas fieldset").disabled'));
    assert.ok(await avaliar('document.getElementById("area-historico").disabled'));
    await clicar('Inativar área','app-areas .record button'); await prontoAreas();
    await esperar('document.querySelector("app-areas .directory")?.innerText.includes("Inativada")','Área inativa preservada');
    assert.deepEqual(excecoes,[]);
  });
  writeFileSync(resolve(destino,'incremento-5.json'),JSON.stringify({executado_em:new Date().toISOString(),navegador,integracao:'Angular + FastAPI + PostgreSQL exclusivo de testes',fundo_cartografico:'Tiles simulados via CDP; não acessa OpenStreetMap no teste',verificacoes,excecoes},null,2)+'\n');
  async function apiJson(rota, method='GET', dados) {
    const resposta=await fetch(new URL('/api/v1/'+rota,api),{method,headers:{Authorization:'Bearer '+process.env.UI_TEST_TOKEN,'Content-Type':'application/json'},...(dados?{body:JSON.stringify(dados)}:{})});
    const corpo=await resposta.json();assert.ok(resposta.ok,JSON.stringify(corpo));return corpo.data;
  }
  async function prontoIA() { await esperar('!!document.querySelector("app-ia-configuracao .directory") && !document.querySelector("app-ia-configuracao [aria-busy=true]")','Operação de IA'); }
  async function prontoDemandas() { await esperar('!!document.querySelector("app-demandas .directory") && !document.querySelector("app-demandas [aria-busy=true]")','Operação de demanda'); }
  let modeloEmbedding, atividadeDemanda, tipoDemanda, recursoDemanda, pessoaDemanda;
  await verificar('conexão de IA com credencial protegida criada pela interface',async()=>{
    assert.ok(process.env.UI_TEST_IA_URL);
    await clicar('Configuração de IA','.toolbar nav button');await prontoIA();
    await preencher('ia-nome','Conexão teste UI');await preencher('ia-url',process.env.UI_TEST_IA_URL);await preencher('ia-token','credencial-ficticia-ui');await clicar('Salvar conexão');await prontoIA();
    await esperar('document.querySelector("app-ia-configuracao .directory")?.innerText.includes("Conexão teste UI")','Conexão salva');
    const conexoes=await apiJson('conexoes-ia?busca=Conexão teste UI');assert.equal(conexoes.length,1);assert.equal(conexoes[0].tem_token,true);assert.ok(!JSON.stringify(conexoes).includes('credencial-ficticia-ui'));
  });
  await verificar('modelos distintos de embedding e inferência cadastrados',async()=>{
    await clicar('Modelos de IA','app-ia-configuracao nav button');await prontoIA();
    await opcao('modelo-conexao-id','Conexão teste UI');await preencher('modelo-identificador','embedding-teste-ui');await preencher('modelo-dimensao','3');await clicar('Salvar modelo');await prontoIA();
    await esperar('document.querySelector("app-ia-configuracao .directory")?.innerText.includes("embedding-teste-ui")','Modelo embedding');
    await opcao('modelo-conexao-id','Conexão teste UI');await preencher('modelo-identificador','texto-teste-ui');await preencher('modelo-finalidade','inferencia_texto');await avaliar('document.getElementById("modelo-ativo").click()');await clicar('Salvar modelo');await prontoIA();
    const modelos=await apiJson('modelos-ia');modeloEmbedding=modelos.find(m=>m.identificador_modelo==='embedding-teste-ui');assert.ok(modeloEmbedding);assert.equal(modelos.find(m=>m.identificador_modelo==='texto-teste-ui').ativo,true);
  });
  await verificar('indexação e busca usam os adaptadores LangChain com provedor HTTP fictício',async()=>{
    await clicar('Índices de atividades','app-ia-configuracao nav button');await prontoIA();
    await opcao('indice-modelo-id','embedding-teste-ui');
    const atividades=await apiJson('atividades?limite=100');assert.ok(atividades.length>0 && atividades.length<=50);atividadeDemanda=atividades[0];
    for(const a of atividades){await opcao('indice-atividade-id',a.nome);await clicar('Adicionar ao lote');}
    await clicar('Indexar lote');await prontoIA();await esperar('document.querySelector("app-ia-configuracao [role=status]")?.innerText.includes("Lote indexado")','Lote persistido');
    await clicar('Modelos de IA','app-ia-configuracao nav button');await prontoIA();await preencher('ia-busca','embedding-teste-ui');await clicar('Buscar','app-ia-configuracao .directory button');await prontoIA();
    await clicar('Editar seleção');await avaliar('document.getElementById("modelo-ativo").click()');await clicar('Salvar modelo');await prontoIA();
    await clicar('Índices de atividades','app-ia-configuracao nav button');await prontoIA();await preencher('ia-consulta','transporte de apoio');await clicar('Buscar por significado');await prontoIA();
    await esperar('document.querySelector("app-ia-configuracao .editor")?.innerText.includes("Similaridade")','Resultado vetorial');await captura('incremento-6-indices.png');
  });
  await verificar('demanda com itens de atividade e recurso criada e editada',async()=>{
    const pessoas=await apiJson('pessoas?busca=Responsável teste UI recursos');assert.equal(pessoas.length,1);pessoaDemanda=pessoas[0];
    await apiJson('pessoas/'+pessoaDemanda.id,'PUT',{nome:pessoaDemanda.nome,municipio_codigo_ibge:'3550308',uf:'SP',situacao_cadastral:'validada'});
    tipoDemanda=(await apiJson('tipos-recurso?busca=Gerador individual UI'))[0];assert.ok(tipoDemanda);
    recursoDemanda=(await apiJson('recursos?busca=Gerador portátil UI'))[0];assert.ok(recursoDemanda);
    await apiJson('ofertas-atividade','POST',{atividade_id:atividadeDemanda.id,pessoa_id:pessoaDemanda.id,municipio_atendimento_codigo_ibge:'3550308',situacao_validacao:'validada'});
    const inst=await apiJson('instituicoes','POST',{nome:'Coordenação demanda UI',municipio_codigo_ibge:'3550308',uf:'SP',tipo:'orgao_publico'});
    const tipo=await apiJson('tipos-desastre','POST',{codigo:'demanda-ui',nome:'Fenômeno demanda UI',descricao:'Cenário fictício'});
    const desastre=await apiJson('desastres','POST',{titulo:'Ocorrência demanda UI',descricao:'Teste do fluxo de decisão',inicio_em:'2026-10-09T09:00:00-03:00',situacao:'em_resposta',id_instituicao_coordenadora:inst.id,classificacoes:[{id_tipo_desastre:tipo.id,principal:true}]});
    await apiJson(`desastres/${desastre.id}/areas`,'POST',{nome:'Área demanda UI',descricao:'Área fictícia para pedidos',municipio_codigo_ibge:'3550308',gravidade:'alta',situacao:'em_resposta',geometria:{type:'Polygon',coordinates:[[[-46.64,-23.55],[-46.63,-23.55],[-46.63,-23.54],[-46.64,-23.55]]]}});
    await clicar('Demandas e recomendações','.toolbar nav button');await prontoDemandas();
    await opcao('demanda-area-id','Área demanda UI');await opcao('demanda-pessoa-id',pessoaDemanda.nome);await preencher('demanda-titulo','Demanda UI com IA');await preencher('demanda-descricao','Transporte e energia para atendimento');await preencher('demanda-inicio','2026-10-09T09:00');await preencher('demanda-prazo','2026-10-09T14:00');
    await opcao('item-necessidade-0-id',atividadeDemanda.nome);const unidades=await apiJson('unidades-medida?limite=100');const u=unidades.find(x=>x.id===atividadeDemanda.id_unidade_capacidade);assert.ok(u);await opcao('item-unidade-0-id',u.nome);
    await clicar('Adicionar item');await preencher('item-tipo-1','recurso');await opcao('item-necessidade-1-id',tipoDemanda.nome);const ur=unidades.find(x=>x.id===tipoDemanda.id_unidade_medida);assert.ok(ur);await opcao('item-unidade-1-id',ur.nome);await preencher('item-quantidade-1','2');await clicar('Salvar demanda');await prontoDemandas();
    await esperar('document.querySelector("app-demandas .directory")?.innerText.includes("Demanda UI com IA")','Pedido salvo');
    await preencher('demanda-busca','Demanda UI com IA');await clicar('Buscar','app-demandas .directory button');await prontoDemandas();await clicar('Editar demanda');await preencher('demanda-descricao','Transporte e energia, análise revisada');await clicar('Salvar demanda');await prontoDemandas();
    const demandas=await apiJson('demandas?busca=Demanda UI com IA');assert.equal(demandas.length,1);assert.equal(demandas[0].itens.length,2);assert.equal(demandas[0].descricao,'Transporte e energia, análise revisada');await captura('incremento-6-demandas.png');
  });
  await verificar('recomendação por LangGraph gera candidatos e decisão sem alterar quantidades',async()=>{
    await clicar('Recomendações e decisões','app-demandas .record button');await esperar('!!document.querySelector("app-recomendacoes") && !document.querySelector("app-recomendacoes [aria-busy=true]")','Histórico de análises');
    const antes=await apiJson('demandas?busca=Demanda UI com IA');const recursoAntes=await apiJson('recursos/'+recursoDemanda.id);
    await clicar('Gerar recomendação por IA');await esperar('document.querySelector("app-recomendacoes .editor")?.innerText.includes("Resultado da IA") && !document.querySelector("app-recomendacoes [aria-busy=true]")','Sugestão gerada');
    await esperar(`document.querySelector('app-recomendacoes .editor')?.innerText.includes(${JSON.stringify(pessoaDemanda.nome)})`,'Nome do candidato');
    await preencher('decisao-justificativa','Sugestão revisada para planejamento');await clicar('Aprovar sugestão');await esperar('document.querySelector("app-recomendacoes [role=status]")?.innerText.includes("Decisão registrada") && !document.querySelector("app-recomendacoes [aria-busy=true]")','Decisão');
    assert.deepEqual(await apiJson('demandas?busca=Demanda UI com IA'),antes);assert.equal((await apiJson('recursos/'+recursoDemanda.id)).quantidade_total,recursoAntes.quantidade_total);await captura('incremento-6-recomendacoes.png');
  });
  await verificar('nova análise e rejeição preservam decisão anterior no histórico',async()=>{
    await clicar('Gerar recomendação por IA');await esperar('!!document.getElementById("decisao-justificativa") && !document.querySelector("app-recomendacoes [aria-busy=true]")','Nova análise');await preencher('decisao-justificativa','Solicitar confirmação de disponibilidade');await clicar('Rejeitar sugestão');await esperar('document.querySelector("app-recomendacoes .editor")?.innerText.includes("Resultado da IA — rejeitada") && !document.querySelector("app-recomendacoes [aria-busy=true]")','Rejeição');assert.equal(await avaliar('document.querySelectorAll("app-recomendacoes .directory .record").length'),2);assert.deepEqual(excecoes,[]);
  });
  writeFileSync(resolve(destino,'incremento-6.json'),JSON.stringify({executado_em:new Date().toISOString(),navegador,integracao:'Angular + FastAPI + PostgreSQL + LangChain/LangGraph',ia:'Provedor HTTP fictício local; não valida qualidade ou serviço externo real',fundo_cartografico:'Tiles simulados via CDP',verificacoes,excecoes},null,2)+'\n');
  process.stdout.write('17 cenários de interface integrada passaram.\n');
  await viewport(390,844);await layout('Recomendações celular');await captura('estilo-recomendacoes-mobile.png');
  await chamar('Page.bringToFront');
  await avaliar('document.querySelector(".menu-toggle").focus()');
  assert.equal(await avaliar('document.activeElement===document.querySelector(".menu-toggle")'),true,'Menu recebe foco no celular');
  await chamar('Input.dispatchKeyEvent',{type:'rawKeyDown',key:' ',code:'Space',windowsVirtualKeyCode:32});
  await chamar('Input.dispatchKeyEvent',{type:'keyUp',key:' ',code:'Space',windowsVirtualKeyCode:32});
  await esperar('document.querySelector(".menu-toggle").getAttribute("aria-expanded")==="true" && getComputedStyle(document.querySelector(".app-sidebar")).display!=="none"','Menu móvel por teclado');
  await captura('estilo-menu-mobile.png');
  await clicar('Pessoas','.app-sidebar nav button');
  await esperar('document.querySelector(".menu-toggle").getAttribute("aria-expanded")==="false" && document.querySelector("main h1").textContent==="Pessoas" && !document.querySelector("main > .workspace [aria-busy=true]")','Navegação móvel');
  assert.equal(await avaliar('document.querySelector(".app-sidebar [aria-current=page]").textContent.trim()'),'Pessoas');
  await layout('Pessoas celular');await captura('estilo-cadastros-mobile.png');
  for (const largura of [768,1024,1440,1920]) { await viewport(largura);await layout('Pessoas '+largura+'px'); }
  await viewport(1440);
  for (const [nome,host] of [['Profissões e cursos','app-catalogos'],['Atividades e unidades','app-capacidades'],['Recursos e ofertas','app-recursos'],['Desastres e áreas','app-desastres'],['Configuração de IA','app-ia-configuracao'],['Demandas e recomendações','app-demandas']]) {
    await clicar(nome,'.app-sidebar nav button');
    await esperar(`!!document.querySelector('${host} .directory') && !document.querySelector('${host} [aria-busy=true]')`,'Tela '+nome);
    await layout(nome+' desktop');
    await viewport(390,844);await layout(nome+' celular');await viewport(1440);
  }
  assert.deepEqual(excecoes,[]);
  writeFileSync(resolve(destino,'estilizacao.json'),JSON.stringify({executado_em:new Date().toISOString(),referencia:'prototipo/src/styles.css',navegador,verificacoes:verificacoesVisuais,menu:'Abre pelo teclado e recolhe após navegar no celular',excecoes},null,2)+'\n');
  process.stdout.write('Layout responsivo e navegação por teclado passaram.\n');
}finally{
  if(socket?.readyState===WebSocket.OPEN){await chamar('Browser.close',{},'').catch(()=>{});socket.close();}
  if(processo.exitCode===null)processo.kill();
  for(const p of pendentes.values()){clearTimeout(p.timeout);p.rej(new Error('Teste encerrado'));}
  await new Promise(res=>servidor.close(res));
}
