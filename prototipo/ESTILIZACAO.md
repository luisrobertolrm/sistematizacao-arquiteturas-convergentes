# Passagem para a IA de interface

Estilizar o protótipo Angular preservando os fluxos e regras em [CONTEXTO.md](CONTEXTO.md). A aparência atual é simples para avaliar o funcionamento antes do design. Trabalhar dentro de `prototipo/`, independente das pastas irmãs de backend/frontend integrado.

## Organização

| Arquivo em `src/` | Responsabilidade |
|---|---|
| `styles.css` | CSS mínimo global; ponto de partida para o estilo. |
| `app/app.html` e `app.ts` | Layout/menu, rotas por hash, visão geral, acesso, listas, formulários reativos, detalhes, associações, histórico e exportação. |
| `app/mapa.html` e `mapa.ts` | Seleção/desenho de polígonos, edição, avaliação e demandas da área. |
| `app/recomendacao.html` e `recomendacao.ts` | Candidatos e pendências por item, decisão justificada e nova análise. |
| `app/indices.ts` | Preparação de índices simulados, modelos e hashes. |
| `app/estado.ts` | Estado compartilhado, inicialização e operações em andamento. |
| `app/dominio/contratos.ts` | Tipos explícitos, incluindo objetos dinâmicos tipados. |
| `app/dominio/telas.ts` | Metadados das 50 tabelas: campos, referências, etapas e relações. |
| `app/dominio/cenario.ts` | Dados fictícios utilizados em todas as telas. |
| `app/dominio/motor.ts` | CRUD, validações, hashes, índices, sugestões e decisões. |

Formulários são gerados pelos metadados. Uma alteração de disposição/estilo atende várias telas sem duplicar o motor. Manter TypeScript/templates estritos e versões exatas, atualizando o lock se adicionar dependência.

## Funcionamento a preservar

- Menu, relacionamentos, links diretos, cancelar/voltar e histórico do navegador.
- Busca, consulta de inativados, inclusão, edição, mensagens, validação e estado de operação em andamento.
- Bindings `formControlName`, `formControl`, `ngSubmit`, callbacks e parâmetros das rotas. IDs dos campos são utilizados pelos testes.
- Dados compartilhados: editar um cadastro atualiza as referências nas demais telas; não substituir por nomes fixos.
- Associações com referência preenchida e retorno ao cadastro principal. Classificação controlada no desastre.
- Mapa ligado à ocorrência; selecionar, desenhar, desfazer ponto, salvar, avaliar e abrir demandas. Desenho permite pontos sobre áreas existentes.
- Sugestões por demanda/item, motivo obrigatório e decisões anteriores preservadas. Trocar a análise limpa o motivo ainda não submetido.
- Avisos de dados fictícios, IA simulada, mapa esquemático e evolução futura; manter as etapas do inventário visíveis.
- Hash na origem e índice por modelo; alterações tornam índices pendentes. Descrições permanecem no catálogo.
- Exportar e reiniciar a sessão.

Podem mudar composição, cores, tipografia, espaçamento e componentes visuais. Manter rótulos associados aos campos, mensagens legíveis, foco visível, teclado e usabilidade em telas menores. Botões/links continuam executando suas ações.

## Verificação da estilização

1. Cobrir [TELAS.md](TELAS.md), incluindo listas, formulários, detalhes e associações.
2. Executar `npm test`, `npm run typecheck` e `npm run build`.
3. Percorrer cadastro → mapa → demanda/item → sugestão → decisão → histórico em navegador. Usar `scripts/testar-navegacao.mjs`; ajustar seletores se o markup mudar, preservando as verificações de negócio.
4. Rever estado vazio, erro de validação, registro inativo, pedido sem itens, análise desatualizada, decisão registrada e índice pendente.

API, provedor real de IA, persistência, login real e biblioteca cartográfica são trabalhos posteriores. Esta entrega trata da apresentação do protótipo funcional.
