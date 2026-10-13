# Contexto da simulação — RedeSolidária, escopo inicial

Este pacote complementa o entendimento do negócio para pessoas e outras IAs. A execução é um exercício determinístico em memória do modelo D001–D009, com recortes tipados. Não é o backend, um banco de dados, um protótipo Angular ou uma avaliação de LLM/RAG.

A aplicação avançou até D017, com 29 tabelas, API, Angular, mapa e fluxo integrado de IA/demandas/recomendações. Este exercício mantém seu recorte D009 e não testa automaticamente os contratos posteriores. Para a evidência de PostgreSQL, migrações, concorrência, geometria e autenticação, consultar [estado da implementação](../../docs/implementacao-inicial.md) e `backend/tests`.

## Leitura e arquivos

| Arquivo | O que contém |
|---|---|
| [modelos.py](modelos.py) | Dataclasses tipadas dos 29 grupos de tabelas iniciais, com campos reduzidos; agregados e identidade administrativa auxiliares são explicitamente separados de tabelas. |
| [cenario.py](cenario.py) | Dados de entrada fictícios, determinísticos e comentados; IDs `uid(n)` são UUIDs criados a partir do inteiro n. |
| [simular_desastre.py](simular_desastre.py) | Validações, recuperação vetorial artificial, adaptador de sugestão, decisões e geração dos resultados. |
| [resultados/relatorio.md](resultados/relatorio.md) | Relatório legível da última execução, com evidências, rejeições e limites. |
| [resultados/resultado.json](resultados/resultado.json) | Mesmo resultado em formato estruturado: versões, hashes das fontes, verificações, sugestões e decisões. Quantidades decimais são strings. |

Referências de modelagem: [escopo D009](../../docs/escopo-inicial.md), [decisões D001–D009](../../docs/decisoes-modelagem.md), [entidades e integridade](../../docs/modelo-entidades.md), [tabelas operacionais futuras](../../docs/modelo-operacional-proposto.md) e [controle de tarefas/finalidade das 50 tabelas](../../docs/controle-tarefas.md).

Os documentos registram decisões humanas e propostas ainda em discussão. As convenções do exercício não aprovam campos, estados ou regras pendentes. A execução produz evidências sobre seus recortes; não redefine requisitos.

## Negócio e cenário

Instituições e pessoas oferecem capacidades. Atividade descreve o serviço; oferta identifica o ofertante. Profissão e curso pertencem ao catálogo, enquanto os vínculos com pessoas registram qualificação individual. Recursos são bens/lotes com responsável exclusivo. Uma ocorrência reúne tipos de desastre e áreas; demandas pertencem às áreas e seus itens pedem uma atividade **ou** um tipo de recurso.

A primeira entrega apoia a decisão: área → demanda → consulta de capacidades → sugestão → avaliação administrativa. Aprovar preserva a decisão e não reduz quantidades do pedido ou estoque. Agenda, aceite, missões, reservas, movimentos, entrega e atendimento parcial permanecem futuros.

O cenário ocorre em **08/10/2026 às 09h UTC−03:00**, no município fictício **Vale Azul**, código ilustrativo `0000001`. Códigos e nomes não representam uma localidade oficial. Há uma ocorrência com inundação principal e deslizamento associado, três áreas com polígonos distintos, três instituições, quatro pessoas, três demandas e seis itens.

| Elemento | Dados fictícios / motivo |
|---|---|
| Instituições `uid(1..3)` | Defesa Civil coordena; cozinha oferta alimentação; associação oferta logística. |
| Pessoas `uid(30..33)` | João tem formação validada e vigente; Carlos tem formação vencida; Marta tem formação pendente; Paula integra a cozinha e tem oferta pessoal. Os cursos são exemplos, sem afirmar requisitos profissionais reais. |
| Áreas `uid(20..22)` | Várzea e Encosta com gravidade alta, Centro moderada. Todas as demandas são urgentes para mostrar que urgência não é cópia da gravidade. Escalas ainda não são contratos finais. |
| Várzea, demanda `uid(200)` | Uma viagem e 200 L de água, até as 11h. |
| Encosta, demanda `uid(201)` | Uma viagem, 200 L de água e um gerador; observação exige 5 kVA, até as 11h. |
| Centro, demanda `uid(202)` | 100 refeições, até as 17h; período-base da capacidade ainda precisa ser definido. |
| Recursos `uid(60..62)` | Um caminhão, um lote de 300 L e um gerador de 2 kVA descrito em texto. |
| Ofertas `uid(80..82)` | Associação oferece transporte; cozinha declara 80 refeições; Paula declara 40. Vínculo de Paula com cozinha sugere risco de sobreposição, mas não prova composição da oferta. |
| Modelos `uid(90..93)` | Embedding ativo de 3 dimensões e texto ativo; embedding alternativo de 4 dimensões parcialmente preparado e texto alternativo, ambos não selecionados inicialmente. |

## Como o exercício funciona

1. Valida relações e regras essenciais em Python, incluindo itens exclusivos, unidades, prazo, responsáveis e seleção de modelos.
2. Consulta vetores artificiais por cosseno. Vetores de consulta são fixtures; não existe geração de embedding do texto da demanda.
3. Gera sugestões com um adaptador determinístico que conhece os casos do cenário. Pessoas, instituições/ofertas e recursos são IDs existentes, com justificativas e pendências.
4. Valida as referências e critérios implementados da sugestão. As quantidades zero em alimentação/energia expressam cobertura não validada/ausência de candidato, como convenção de demonstração; a aplicação possui seus próprios contratos em D017.
5. Registra uma aprovação e uma rejeição, recusa decisões indevidas e registra nova análise sem apagar a anterior. Auditoria/identidade administrativas são estruturas auxiliares, sem definir tabela de usuário ou autenticação.
6. Compara pedidos/recursos antes e depois da decisão para verificar que suas quantidades e situações foram preservadas.
7. Exercita configurações de modelos, hashes e dimensões, incluindo troca lógica apenas do modelo de texto. O exercício não verifica a gestão administrativa e a seleção transacional já implementadas na aplicação em D015.

**O filtro de curso de transporte é escolhido manualmente no cenário.** A sugestão de João é um candidato, não uma comprovação de aptidão. As tabelas de requisitos e registros profissionais completos não foram implementados. Tampouco a participação numa instituição comprova composição de equipe.

## Resultados esperados e limites

O relatório deve terminar com zero falhas de verificação; rejeitar entrada inválida é uma verificação OK. `LIMITE` documenta trabalho não coberto e não conta como teste aprovado. Uma falha gera código de saída 1; uso/runtime incompatível gera código 2.

As sugestões independentes para Várzea/Encosta indicam 200 L cada, mas o lote tem somente 300 L. O exercício calcula o déficit global de 100 L e explicita que os 400 L sugeridos não constituem plano reservado. O caminhão e João também aparecem nas duas janelas sobrepostas. A primeira entrega apresenta candidatos e pendências, sem resolver alocação concorrente.

As capacidades 80/40 não são somadas como 120 comprovadas. Alimentação permanece com candidatos e cobertura quantitativa não validada. O gerador não é sugerido como compatível: a comparação 2/5 kVA é um caso conhecido do adaptador, e não um validador técnico genérico que extrai potência de texto.

Não foram testados PostgreSQL, pgvector, migrações Alembic, FKs SQL, transações, concorrência, JWT, criptografia de tokens, Angular, mapa real, topologia/CRS, rotas, LLM, LangChain/LangGraph ou eficácia de RAG. A conexão usa `https://provedor.invalid`, sem chamadas de rede e sem credenciais. Não houve medição do indicador de redução de tempo.

Este exercício mantém um hash simplificado do recorte. Na aplicação integrada, o incremento 3 já implementa o contrato canônico v1 e atualização transacional por textos/termos, conforme D012; categoria/unidade ficam fora dessa entrada v1. A simulação não adota automaticamente esse contrato. O incremento 4 implementa recursos/ofertas e o hash canônico do tipo de recurso conforme D013, com regras de unidade/controle que este exercício separado não verifica. O incremento 5 implementa classificações, datas, avaliação das áreas e geometria tipada/mapa conforme D014; este exercício em memória não verifica seu contrato de bordas, limites ou transações. O incremento 6 implementa geração/publicação de índices e recomendações conforme D015–D017, com vetores em arrays e chamadas externas fora das transações. Este exercício não verifica essas garantias; consultar os testes PostgreSQL e os 17 cenários de navegador, que usam LangChain/LangGraph com provedor HTTP fictício. Índices de profissão, curso e tipo de recurso não são exercitados aqui, seguindo D009.

## Executar e reproduzir

Na raiz do projeto, com **Python >=3.13,<3.14**, somente biblioteca padrão:

```powershell
python simulacoes/escopo_inicial/simular_desastre.py --salvar
```

Também é possível executar a partir desta pasta: `python simular_desastre.py --salvar`. O script independe do diretório atual. Sem `--salvar`, só imprime o relatório. Com a opção, substitui os dois arquivos de resultados nesta pasta; o estado de negócio continua exclusivamente em memória.

O JSON registra a versão real do interpretador, instante UTC da execução e hashes SHA-256 dos documentos/código utilizados. A data fixa do desastre e a data real da execução são conceitos distintos. Reexecutar mantém dados, UUIDs e verificações; o instante da execução muda. Os hashes ajudam a detectar resultados desatualizados após alterações nas fontes.

O exercício anterior permanece em [simular_desastre.py](../simular_desastre.py), com [relatório histórico](../../docs/simulacao-desastre.md). Ele apontou lacunas posteriormente tratadas por D008/D009; use este pacote para o recorte atual.
