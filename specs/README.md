# Specs de intenção da interface — RedeSolidária

Especificações da aplicação integrada em `frontend/`, referência **09/10/2026**. Este pacote descreve o que o usuário pretende realizar, como operar os controles e qual resultado observar, inclusive quando a ação abre outro componente. Serve à revisão do produto e à adaptação do harness de interface real com Playwright.

São **26 funcionalidades**, **4 componentes compartilhados**, **281 ações** e **97 cenários de aceitação**. A cobertura estática relaciona **166 botões, links e expansores `summary`** declarados nos templates às ações documentadas. Controles gerados pelo Leaflet estão descritos na spec do mapa. Essa contagem não significa que os 97 cenários foram executados.

## Por onde começar

Para adaptar este pacote à ferramenta multi-LLM, consultar a
[avaliação de prontidão](../testes/registros/avaliacao-prontidao-testes.md), o
[padrão dos documentos](../testes/guias/padrao-documentos-testes.md) e o
[modelo de funcionalidade](../testes/guias/modelos/funcionalidade.template.md).
Os exemplos normalizados são propostas documentais; exigem integração ao runner.

1. [Índice por funcionalidade](indice.md): um arquivo para cada cadastro/fluxo e para cada seletor compartilhado.
2. [Contrato para o harness](contrato-harness.md): contexto de tela, seletores, diálogos, esperas, exemplos Playwright e evidências.
3. [Dados e dependências dos cenários](dados-cenarios.md): preparação reproduzível dos cadastros e pré-condições de IA.
4. [Fluxos integrados](fluxos-integrados.md): sequências de ida/volta entre telas e critérios finais.
5. [Limites e divergências conhecidas](limites-interface.md): comportamento atual que o harness precisa reconhecer, sem presumir funcionalidades futuras.

## Arquivos para consumo por IA/harness

| Arquivo | Uso |
|---|---|
| [catalogo.json](catalogo.json) | Fonte editável: intenção, entrada, campos, ações, pré-condições, destinos e cenários em estrutura JSON. |
| [inventario-controles.json](inventario-controles.json) | Vínculo dos controles declarados à documentação, com arquivo/linha, expressão Angular de ação/bloqueio e hashes das fontes. |
| `funcionalidades/*.md` | Leitura humana gerada do mesmo catálogo; não editar diretamente. |
| [scripts/sincronizar.py](scripts/sincronizar.py) | Geração e verificação local dos artefatos, destinos e cobertura documental. |

O JSON é um contrato documental independente. Não foi fornecido um schema do harness existente; será necessário adaptar sua leitura desse catálogo. O pacote não instala Playwright, não substitui o harness e não executa testes de navegador por si só.

## Escopo e critério de verdade

O escopo é a interface funcional em `http://127.0.0.1:4200/`, com API e PostgreSQL. O protótipo independente em `prototipo/`, normalmente na porta 4300, usa outros fluxos e dados e não é o destino destas specs.

Os resultados esperados foram extraídos dos componentes Angular, serviços HTTP e regras implementadas. Futuras funcionalidades não foram apresentadas como existentes. Cada spec contém as fontes usadas e explicita suas particularidades. Uma mudança de intenção deve atualizar o catálogo e orientar a alteração da aplicação; não basta atualizar a spec para considerar um teste aprovado.

Navegação interna troca componentes e mantém a URL. Os identificadores `INS`, `VIN-CUR`, `ARE`, `RCO` etc. são IDs documentais de contexto, não rotas. A identificação combina raiz, título/controle específico e, quando disponível, aba com `aria-current="page"`.

## Atualizar e verificar

Na raiz do repositório, usando o Python 3.13 já disponível no backend:

```powershell
# Após editar catalogo.json:
backend\.venv\Scripts\python.exe specs/scripts/sincronizar.py --gerar

# Conferência sem escrever arquivos ou acessar API/banco/navegador:
backend\.venv\Scripts\python.exe specs/scripts/sincronizar.py
```

A geração verifica IDs únicos, arquivos de fonte, destinos, pré-condições/resultados e a existência de referência documental para os controles declarados. O modo de conferência detecta catálogo/Markdown/inventário desatualizados. A conferência estática não prova que os seletores resolvem no DOM de todas as condições, nem executa as regras de negócio; essas verificações pertencem ao harness.

Para a primeira execução real, siga as pré-condições em [dados-cenarios.md](dados-cenarios.md). O banco local foi migrado, mas isso não implica que existam cadastros, modelos ou dados de demonstração.
