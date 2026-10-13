# Limites e particularidades da interface atual

Esta lista evita que o harness confunda intenção documentada, pré-condição ausente e comportamento ainda não implementado. Não introduz requisitos aprovados para nova implementação.

| Tema | Comportamento observado no código | Como avaliar |
|---|---|---|
| Navegação | Signals trocam componentes; URL permanece a mesma. | Conferir raiz/título/aba; não esperar rota hash. |
| Acesso | Token entra na memória antes da primeira consulta; erro 401/403 não encerra sessão automaticamente. | Sucesso exige resposta autorizada. Teste negativo deve conferir alerta e permitir Sair. |
| Recarga | Memória da sessão é perdida. Link da marca faz navegação para `/`. | Reautenticar após recarga; não esperar persistência em localStorage. |
| Estado de edição | Troca de módulo/aba pode descartar rascunho sem diálogo. | Confirmar comportamento de descarte; não esperar modal de alterações pendentes inexistente. |
| Validação | Há regras somente na API: unidade exata, quantidade individual, token bearer, imutabilidade e datas/referências. | Botão habilitado não garante dados válidos; verificar recusa e ausência de gravação parcial. |
| Textos de unidade | Código é fixo; nome/símbolo da unidade continuam editáveis no serviço atual. A proteção do ID de unidade em atividade/tipo utilizado é outra regra. | Não presumir que editar símbolo/nome será recusado só porque a unidade está em uso; registrar divergência caso a intenção do produto exija essa estabilidade. |
| Cadastros principais | Pessoas/instituições não têm busca ou histórico próprios. | Paginar ou usar base isolada; não procurar campos inexistentes. |
| Catálogos de qualificação | Profissões/cursos têm busca, sem histórico próprio na tela. | Consultar vínculos históricos pela pessoa quando necessário. |
| Referência fora da página | Seletores preservam option selecionada fora do resultado atual. | Conferir value/ID; o texto pode ser fallback quando nome indisponível. |
| Referências bloqueadas | Alguns campos continuam visualmente pesquisáveis embora o select principal seja bloqueado. | Afirmar bloqueio da alteração do ID; não presumir que toda a instância esteja disabled. |
| Mensagens antigas | Algumas operações não limpam todas as mensagens/resultados anteriores. | Vincular evidência à resposta e ao estado da operação atual. |
| IA: conexão | Não existe botão de testar conectividade; URL/autenticação de conexão utilizada podem continuar editáveis visualmente. | API protege identidade com 409; cadastro bem-sucedido não comprova provedor funcionando. |
| IA: modelo | Identidade e dimensão fixas após criar; ativo é seleção por finalidade. | Troca de versão/dimensão requer outro cadastro; não tratar ativo como inativação. |
| IA: seletor de indexação | Lista inclui modelos de ambas as finalidades; não filtra a listagem à esquerda. | Selecionar embedding correto e conferir id_modelo no índice. Modelo de texto é recusado ao indexar. |
| IA: lote | Até 50 IDs distintos; lote permanece após indexar e trocar abas. | Remover entradas individualmente se necessário; não presumir limpeza/seleção automática. |
| IA: execução | Fluxo síncrono; sem fila, progresso persistido, estado processando ou retry automático. | Esperar resposta/estado final; falha não significa resultado parcial válido. |
| Busca vetorial | Somente atividades; modelo selecionado e cobertura integral; até 5000 vetores atuais. | Não exigir RAG de profissões/cursos/recursos nesta tela. |
| Mapa: fundo | Tiles OpenStreetMap externos; falha do fundo é informada e desenho segue disponível. | Separar falha externa de falha Leaflet. Teste controlado de tiles não mede disponibilidade/precisão cartográfica. |
| Mapa: seleção | Ver delimitação muda geometria compartilhada, sem preencher editor/ID. | Para editar usar Editar área; para criar usar Limpar área. |
| Mapa: território | Sem geocodificação de município, rotas ou GIS avançado; apenas polígonos da página. | Desenhar/centralizar por controles existentes; não esperar mapa nacional consolidado. |
| Avaliação territorial | Correção cadastral preserva data da avaliação; mudar gravidade/situação ou confirmar avaliação atual gera avaliação. | Comparar ultima_avaliacao_em, distinguindo-a de atualizado_em. |
| Demanda | Cancelamento é estado salvo em edição; sem reabertura/atendimento/conclusão operacional. | Não confundir Limpar formulário com cancelar pedido. |
| Recomendação | Aprovação/rejeição únicas; nova análise mantém histórico. | Não tentar decidir novamente uma análise finalizada. |
| Quantidade de serviços | Candidatos podem ser indicados com cobertura quantitativa zero. | Não afirmar ausência de candidatos só pela quantidade zero. |
| Aprovação | Registra decisão, sem reserva, missão, entrega ou débito. | Comparar pedido/estoque e histórico; não esperar tela de despacho. |
| Aptidão | Profissões/cursos/agenda/rotas/equipe não são critérios operacionais completos da recomendação atual. | Não declarar validação de habilitação ou disponibilidade. |

Alterações de comportamento desejadas devem ser registradas como novas decisões de produto e refletidas nas specs/código. O harness deve reportar uma divergência observada com IDs/evidências; este pacote não transforma limitações atuais em validação positiva de funcionalidades futuras.
