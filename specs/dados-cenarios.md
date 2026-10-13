# Dados e dependências dos cenários

## Ambiente e identificação

O harness precisa de frontend integrado, API disponível, banco migrado até `0009_recomendacoes` e token administrativo válido. Comandos de preparação estão em [backend/README.md](../backend/README.md). As specs não autorizam assumir credenciais ou importar dados do protótipo para a aplicação.

Preferir banco exclusivo da execução do harness. Se o harness for executado contra uma base de trabalho, usar entidades de teste identificadas e não inativar cadastros que não pertençam ao cenário. Este pedido gerou documentação; nenhuma fixture foi inserida no banco.

Use `RUN_ID` único, por exemplo `20261009T150000Z-a1b2`, e nomes `SPEC {RUN_ID} Instituição A`. Códigos exigem caracteres alfanuméricos, hífen ou sublinhado: `SPEC-a1b2-UN`, sem espaços/acento e com no máximo 50 posições. UUIDs são obtidos ao cadastrar; nunca fixados por ordem da lista.

## Ordem mínima de criação

| Ordem | Entidade / spec | Dados úteis | Dependências |
|---|---|---|---|
| 1 | Instituição / INS | Nome exclusivo, IBGE `3550308`, UF `SP`, tipo `associacao`, situação `validada` | Token |
| 2 | Pessoa / PES | Nome exclusivo, mesmo IBGE/UF, situação `validada` | Token |
| 3 | Profissão / PRO | Nome exclusivo; CBO opcional `123456` somente como dado de formato | Nenhuma referência |
| 4 | Curso / CUR | Nome exclusivo, tipo `tecnico` | Nenhuma referência |
| 5 | Vínculos / VIN-* | Instituição, profissão, conclusão de curso com emissor | Pessoa + referências |
| 6 | Unidade / UNI | Ex.: nome `Litro {RUN_ID}`, código único, símbolo `L` | Nenhuma referência |
| 7 | Outra unidade / UNI | Ex.: unidade de contagem, símbolo `un` | Usada para individual e teste de unidade incompatível |
| 8 | Categoria / CAT | Nome/código exclusivos | Nenhuma referência |
| 9 | Atividade / ATV | Nome/código exclusivos, descrição, categoria e unidade de contagem | Categoria + unidade |
| 10 | Termo / TRM | Ex.: `distribuicao spec {RUN_ID}` | Atividade |
| 11 | Tipos de recurso / TIR | Água: `insumo/estoque/L`; gerador: `equipamento/individual/un` | Unidades |
| 12 | Recursos / REC | Água: quantidade `300`; gerador: `1`; estado `operacional`, responsável validado, mesmo município | Tipos + responsável |
| 13 | Oferta / OFE | Atividade exata, responsável validado, mesmo município, validação `validada` | Atividade + responsável |
| 14 | Recurso da oferta / OFR | Quantidade positiva; individual `1` | Oferta + recurso |
| 15 | Tipo de desastre / TDE | Nome/descrição/código únicos, ex.: inundação de teste | Nenhuma referência |
| 16 | Ocorrência / OCO | Coordenadora, início, situação `em_resposta`, tipo principal | Instituição + tipos |
| 17 | Área / ARE + MAP | Nome/descrição/IBGE, triângulo simples, gravidade `alta`, situação `em_resposta` | Ocorrência |
| 18 | Conexão / CON | Endpoint do provedor do ambiente, autenticação compatível | Configuração de IA no backend |
| 19 | Modelos / MOD | Embedding não selecionado com dimensão correta; inferência selecionada | Conexão |
| 20 | Índices / IND | Todas as atividades ativas do banco, em lotes de até 50 | Embedding + provedor |
| 21 | Seleção de embedding / MOD | Marcar selecionado após cobertura integral | Índices atuais |
| 22 | Busca / BUS | Necessidade textual conhecida | Embedding selecionado |
| 23 | Demanda / DEM | Área, solicitante, janela, item de atividade e item de água com unidades exatas | Área + pessoa + catálogos |
| 24 | Recomendação / RCO | Gerar, revisar e decidir | Demanda aberta + modelos + candidatos |

Quantidade/capacidade cadastradas não são disponibilidade confirmada. Para obter candidatos, as ofertas precisam ser validadas e os responsáveis ativos/validados; recursos precisam ser operacionais com total positivo, tipo/unidade/responsável válidos e município compatível. Similaridade entre atividades não substitui a correspondência exata exigida pelas ofertas.

## Valores e datas

- Campos decimais usam ponto, sem separador de milhar: `1`, `300`, `2.5000`. Não enviar vírgula para os campos textuais de quantidade.
- Datas de vínculo/conclusão/validade usam `YYYY-MM-DD`. Encerramento do vínculo não antecede início; validade do curso não antecede conclusão.
- Datas de ocorrência/demanda usam `datetime-local`, por exemplo `2026-10-09T09:00`. O navegador converte seu fuso para ISO UTC. Fixar timezone do contexto do harness, preferencialmente `America/Sao_Paulo`, e comparar instantes quando necessário.
- Preferir datas construídas pelo cenário, sem comparar literalmente horários local e UTC. Janela do pedido deve ter prazo igual ou posterior ao início.
- Email/comprovante opcionais podem ficar vazios. Comprovante é texto opaco como `documento:spec-a1b2`, sem query, credenciais ou upload.
- Coordenadas de contato/recurso são opcionais e devem ser informadas em par. Município não é consultado em serviço IBGE nem geocodificado pelo mapa.

## Preparação de IA

O provedor precisa atender aos contratos de embeddings e inferência estruturada usados pelo backend. A URL precisa estar explicitamente autorizada em `REDE_IA_URLS_PERMITIDAS`; conexões bearer precisam de chave Fernet válida. Valores de exemplo não são endpoints utilizáveis.

A dimensão do modelo deve coincidir exatamente com a resposta do provedor. O padrão `3` no formulário de modelos é útil para vetores artificiais de teste, não uma recomendação para modelo real. A API não envia `dimensions` para ajustar o provedor automaticamente.

No ambiente integrado existente, o teste em [frontend/scripts/testar-capacidades.mjs](../frontend/scripts/testar-capacidades.mjs) usa LangChain/LangGraph reais com [backend/tests/provedor_http.py](../backend/tests/provedor_http.py) como provedor HTTP fictício local. O runner [backend/scripts/test_postgres.py](../backend/scripts/test_postgres.py) prepara e remove infraestrutura exclusiva. Esses arquivos servem de referência de contrato; não são o harness Playwright do usuário.

Para teste determinístico de interface, o harness pode preparar provedor controlado e identificadores compatíveis, mantendo o tráfego UI → API → banco real. Não basta interceptar a resposta de recomendação no navegador para afirmar que ela foi persistida. Para LLM externo real, conferir estrutura, nomes/IDs elegíveis, decisões e persistência; pertinência e redação exata são avaliações separadas.

A cobertura de embedding é de **todas as atividades ativas do banco**, não apenas das fixtures desta execução. Um ambiente com atividades anteriores pode impedir seleção/busca; registrar essa pré-condição ou preparar a cobertura correspondente. Trocar somente inferência não exige indexar novamente.

## Paginação e recuperação

Criar 51 registros/opções somente em cenário específico de paginação, com nomes/códigos exclusivos. Não presumir ordem de retorno ou visibilidade de um novo registro numa base grande. Usar busca quando existente; nas listas principais de pessoas/instituições, percorrer páginas.

Após erro de validação, corrigir o rascunho e salvar novamente. Após inativação, usar histórico onde disponível; não há reativação pela interface inicial. Não reutilizar uma entidade inativada como pré-condição de criação ativa.

Planejar a sequência de inativação por último: inativar ocorrência bloqueia novos cadastros/edições de suas áreas; inativar catálogo retira referências dos seletores; inativar modelo selecionado interrompe busca/análise até nova seleção. Executar a limpeza somente sobre entidades do `RUN_ID`, conforme política do harness.
