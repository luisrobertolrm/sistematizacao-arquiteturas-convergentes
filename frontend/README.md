# RedeSolidária — Angular

Até o incremento 6: cadastros, qualificações/vínculos, unidades, atividades/termos, recursos/ofertas, desastres/áreas no mapa, conexões/modelos de IA, índices/busca, demandas/itens e recomendações/decisões. Formulários tipados, templates estritos, busca/paginação e contrato `{data,messages?}`/ProblemDetails. Token administrativo somente em memória, enviado apenas para URLs relativas `/api/`.

A interface integrada adota o visual de `prototipo/`: tema claro azul, marca/ faixa superior, navegação lateral por grupos, painéis brancos, formulários e mensagens padronizados. A identidade está em [src/styles.css](src/styles.css), com os mesmos tokens de cor, tipografia, bordas e sombras do protótipo. Aprovar usa verde; rejeitar/inativar usam vermelho. Em telas menores, **Menu** abre/recolhe a navegação; os formulários passam para uma coluna. Foco visível, indicação da página atual e link para pular ao conteúdo estão disponíveis.

As [specs de intenção e operação das telas](../specs/README.md) detalham campos, botões, confirmações, resultados, destinos e cenários do frontend integrado. Incluem catálogo JSON e contrato para adaptação do harness Playwright; a navegação interna é identificada pelo componente/título, sem rotas por funcionalidade.

```powershell
npm ci --ignore-scripts
npm start
```

Node testado: 22.22.2. O servidor abre em `http://localhost:4200` e encaminha a API para `http://127.0.0.1:8000`. Para gerar token local e preparar o PostgreSQL, seguir [backend/README.md](../backend/README.md).

Em **Profissões e cursos**, mantenha os catálogos. Em **Pessoas → Vínculos e formação**, registre vínculos institucionais, profissões e conclusões/renovações de cursos. A consulta de histórico inclui inativados e referências inativas. Para encerrar participação, edite a data de encerramento; inativar preserva o registro. Comprovante é uma referência textual, sem upload/download nesta etapa.

Em **Atividades e unidades**, cadastrar unidades e categorias antes das atividades. Código único fica fixo após criar. Seletores de referências ativas possuem busca/paginação; referências inativadas são indicadas para correção. **Atividades → Termos e sinônimos** inclui edição, inativação e histórico dos termos. Alterações dos textos/termos atualizam o hash da atividade no servidor. A busca deste cadastro é textual por nome, código, descrição e termo; **Configuração de IA** oferece indexação e busca semântica separadas.

Em **Recursos e ofertas**, cadastre tipos (unidade/modo individual ou estoque), recursos com responsável pessoa/instituição e ofertas com capacidade/validação. **Ofertas de atividades → Recursos da oferta** permite vínculos com quantidades previstas. Ofertas inativadas preservam histórico e permitem inativar vínculos. Referências principais ficam fixas após cadastrar; unidades já usadas são protegidas contra alteração de significado. Quantidade prevista não reserva estoque, e capacidade declarada não é disponibilidade. Detalhes em [D013](../docs/decisoes-modelagem.md#d013--recursos-e-ofertas-incremento-4).

Em **Desastres e áreas**, cadastre os tipos e a ocorrência com coordenadora, datas/situação e classificações; selecione exatamente um tipo principal. **Ocorrências → Áreas e mapa** permite desenhar um polígono, desfazer pontos, concluir, revisar e salvar a delimitação junto do município, gravidade e situação. As cores representam a gravidade; o mapa mostra as áreas da página atual. Para revisar a mesma avaliação sem mudar os valores, use **Confirmar avaliação atual**; editar somente metadados/geometria preserva sua data.

Leaflet 1.9.4 e `@types/leaflet` 1.9.22 têm versões fixas. O fundo OpenStreetMap depende de conexão externa e mantém atribuição visível; falha de tiles é informada e não impede a edição das geometrias. Há centralização manual por coordenadas, sem geocodificação do município. Polígono simples, sem buracos, de 3–200 vértices; validação e demais limites em [D014](../docs/decisoes-modelagem.md#d014--desastres-e-território-incremento-5). Ocorrências inativadas permitem consulta de histórico e inativação de áreas, com formulário/desenho bloqueados.

Em **Configuração de IA**, cadastre conexão e modelos de embeddings/texto. Token informado é enviado ao backend para cifragem; edição em branco preserva a credencial. Gere índices de todas as atividades ativas em lotes de até 50 antes de selecionar o modelo de embeddings. A busca semântica informa o modelo e os resultados; textos permanecem no catálogo.

Em **Demandas e recomendações**, selecione área/solicitante, informe janela/prioridade e adicione itens com quantidade/unidade compatíveis. Solicite análise, revise pessoas/instituições/recursos e pendências, e aprove ou rejeite com justificativa. Nova análise conserva o histórico. Aprovar não reserva ou entrega recursos nem altera estoque/pedido. Serviços são candidatos com cobertura numérica zero, pois capacidade por período ainda não foi definida.

O backend exige endpoint explicitamente permitido e configuração válida. A verificação usa IA fictícia; para uso real é necessário escolher/configurar provedor compatível. [Sequência e limites completos](../docs/ia-demandas-recomendacoes.md).

Build: `npm run build`. Tipos/templates: `npm run typecheck`. Dependências diretas exatas em `package.json`, transitivas em `package-lock.json`. As funcionalidades do escopo inicial estão integradas; falta avaliar modelos reais e medir o indicador acadêmico.

Verificação em navegador com a API e PostgreSQL exclusivos: compilar este projeto e executar `.venv\Scripts\python.exe scripts/test_postgres.py --frontend` dentro de `backend`. Usa Edge/Chrome com perfil próprio; `UI_TEST_BROWSER` pode indicar o executável. 17 cenários passaram, incluindo LangChain/LangGraph com provedor HTTP fictício local; tiles são simulados somente no teste, sem comprovar disponibilidade/precisão do fundo externo. Após a estilização, também passaram 21 verificações de layout em viewports de 390 a 1920 px e abertura do menu móvel pelo teclado, com recolhimento após navegar. Não precisa manter servidores locais em execução para esse teste. [Resultados e capturas](verificacao/README.md).
