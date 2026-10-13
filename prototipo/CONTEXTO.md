# Negócio representado

RedeSolidária propõe cadastrar voluntários institucionais, pessoas, qualificações e recursos para apoiar a resposta a desastres. Referência acadêmica: Meta 3.1.3 do PN-PDC, criação de cadastro nacional de voluntários institucionais. O protótipo local demonstra a proposta, sem representar o cadastro nacional criado.

Primeiro escopo: **área afetada → demanda → capacidades candidatas → recomendação → decisão administrativa**. Operações são evolução futura. Os documentos completos estão em `../docs/`; os pontos necessários para trabalhar nesta pasta estão abaixo.

## Distinções do negócio

| Conceito | Significado |
|---|---|
| Instituição e pessoa | Organização e indivíduo possuem cadastros próprios; vínculo institucional registra período e validação. |
| Profissão e curso | Catálogos; registro profissional, conclusão, emissor, validade e validação pertencem à qualificação individual. |
| Atividade e oferta | Atividade descreve o serviço; oferta indica quem fornece, localização, capacidade e condições. |
| Tipo e recurso | Tipo classifica bem, unidade e controle; recurso identifica equipamento ou lote concreto, quantidade, responsável e condição. |
| Desastre e área | Ocorrência reúne coordenação e fenômenos, com um principal; áreas delimitam impactos, município e avaliação. |
| Gravidade e prioridade | Gravidade da área é independente da prioridade do pedido. |
| Demanda e item | Pedido tem solicitante e prazo; cada item solicita uma atividade **ou** tipo de recurso, com quantidade positiva e unidade. |
| Sugestão e execução | Candidato/quantidade potencial não constituem reserva, entrega ou comprovação de aptidão. |

Inativados e referências históricas permanecem consultáveis; referências novas precisam estar ativas. CNPJ é único. Períodos do vínculo na mesma instituição não se sobrepõem e incluem seus extremos. Renovação de curso gera outra conclusão; não se troca a pessoa dona de um vínculo durante edição.

Oferta/recurso possui responsável exclusivo: pessoa ou instituição. Vínculo institucional não torna a pessoa automaticamente integrante da oferta. O item pede atividade ou tipo de recurso, com unidade compatível. Pedido sem itens é rascunho e não gera análise.

Cada análise captura modelos e hash da demanda. Alterar o pedido impede aprovar a análise antiga. Aprovar/rejeitar exige motivo; decisões anteriores ficam preservadas. Gerar novamente acrescenta outra análise. A decisão não altera demanda, estoque, missão ou reserva.

## Modelos e índices

Conexões, modelos e índices são separados. Modelo tem finalidade, revisão e dimensão se for embedding. Existe seleção operacional por finalidade, além da inativação cadastral. Texto e embedding usam o mesmo catálogo com finalidades distintas.

Índice referencia origem/modelo e guarda hash da origem/estado da preparação. Descrição e hash corrente permanecem no catálogo. Alterar atividade, termos ou categoria invalida os índices anteriores. Outro embedding exige cobertura atualizada das atividades antes da seleção; trocar modelo de texto não altera os índices.

Atividades são a busca semântica inicial; índices de profissões, cursos e tipos de recurso são futuros. Dimensões diferentes são mostradas por modelo, mas não há vetor físico/índice PostgreSQL aqui. Preparar índice apenas simula seu estado, sem gerar embeddings.

## Cenário e candidatos

Vale Azul tem Várzea, Encosta e Centro. Pedidos de água somam 400 L para um lote de 300 L. Um caminhão é compartilhado entre análises. Paula também integra a cozinha; não se somam suas capacidades sem conferir composição/período. Gerador declara 2 kVA para pedido que menciona 5 kVA.

O motor usa IDs exatos e filtros locais de atividade/tipo, município, validação e situação operacional. Expõe qualificações para conferência, sem escolher equipe pelo vínculo ou calcular agenda. Serviço não vira quantidade garantida; bem tem quantidade potencial sem dedução de estoque. O aviso técnico do gerador é uma heurística demonstrativa, sem avaliador genérico de requisitos.

## Fronteiras dos contratos

- Memória da sessão: recarregar/reiniciar restaura o cenário. Exportação JSON é de consulta, sem importação.
- IDs dos exemplos são legíveis, como `p-joao`; novos registros usam UUID. JSON não é carga compatível com a API.
- Números dos formulários são strings tipadas; cálculos ilustrativos usam `Number`, sem precisão/transação Decimal do backend.
- Hash SHA-256 real do navegador; serialização canônica própria do protótipo, sem equivalência garantida ao backend.
- Acesso troca o responsável demonstrativo. Eventos são locais, sem auditoria persistente.
- Endpoints `.invalid` e indicador fictício de credencial; nenhum segredo coletado, criptografado ou enviado.
- Mapa usa pontos SVG: três vértices e área positiva; sem topologia completa, georreferenciamento ou análise de acesso.
- Campos/enums sem API, especialmente futuros, são propostas para discussão. Navegação não aprova contratos de produção.

A aplicação integrada segue em outra etapa: sete das 29 tabelas iniciais implementadas em Python/PostgreSQL e Angular; demais APIs e integrações pendentes.
