# EXECUTIVE UI SKILL — Documento Completo

> Cole este conteúdo no Claude Code como contexto/instrução de projeto.
> Os três blocos abaixo são: SKILL.md principal + 2 arquivos de referência.

-----

# ARQUIVO 1: SKILL.md

-----

## name: executive-ui
description: >
Transforms visual references (screenshots, mockups, or app prints) into polished, executive-grade
React/Next.js UI proposals. Use this skill whenever the user uploads a screenshot of an existing
interface, a reference image, or asks to redesign/improve a UI component. Triggers on: "melhora
esse layout", "refaz mais profissional", "cria uma versão executiva", "redesign", "me mostra
como ficaria mais limpo", "analisa esse print e propõe algo novo", "quero uma versão mais clean",
"como ficaria isso com mais qualidade", or any time an image of a UI is shared with intent to
improve, replicate, or evolve it. Always use this skill before writing any frontend code when a
visual reference is provided. Also triggers when user asks to build a new screen/component and
wants it to look professional — even without a reference image.

# Executive UI Skill

Transforma referências visuais em propostas React/Next.js executivas — clean, profissionais, com
identidade visual forte. O output é sempre **cinco entregas**: log de estudo, guia de design,
pesquisa de componentes, código funcional, e nota de implementação.

-----

## PASSO 0 — PERGUNTAR ONDE SALVAR (SEMPRE, ANTES DE TUDO)

**Esta é a primeira coisa a fazer**, antes de qualquer análise.

Perguntar ao usuário:

> "Antes de começar — onde você quer que eu salve os arquivos desse redesign?
> Pode ser um caminho do seu projeto (ex: `src/components/dashboard/`) ou só um nome de pasta
> (ex: `redesign-transacoes`). Se preferir, deixo tudo na raiz e você organiza depois."

Aguardar a resposta. Usar o caminho informado como `SAVE_PATH` em todos os arquivos gerados.
Se o usuário disser "tanto faz" ou não especificar, usar `./executive-ui-output/[NomeDoComponente]/`.

**Estrutura de arquivos a criar em `SAVE_PATH`:**

```
[SAVE_PATH]/
├── [NomeDoComponente].jsx        ← código React
├── design-guide.md               ← tokens + decisões
└── study-log.md                  ← processo completo documentado
```

-----

## MODOS DE INPUT

A skill opera em três modos. Identificar o modo antes de prosseguir:

### Modo A — Print do app atual SOMENTE

O usuário quer evoluir uma tela existente.
→ Analisar o que existe, identificar fraquezas, propor versão executiva.
→ Preservar a função; elevar a forma.

### Modo B — Print do app atual + print de inspiração externa

O usuário quer aplicar a linguagem visual de uma referência ao seu app.
→ Passo 1: extrair DNA da referência externa (paleta, tipo, ritmo, componentes)
→ Passo 2: reinterpretar esse DNA no contexto e conteúdo do app atual
→ NÃO copiar — traduzir e adaptar

### Modo C — Apenas print de inspiração (nova tela)

O usuário quer criar uma tela nova inspirada em algo que viu.
→ Usar a referência como direção estética
→ Construir conteúdo e estrutura adequados ao projeto do usuário
→ A tela resultante é nova, não uma cópia

Em todos os modos: o resultado final deve ser **único** — não uma réplica de nada.

-----

## FASE 1 — ANÁLISE DA REFERÊNCIA

Ao receber uma imagem (print de app, screenshot, mockup):

### 1.1 Decifrar o DNA visual

Examinar com atenção:

- **Layout:** Grid usado, hierarquia visual, densidade de informação
- **Tipografia:** Famílias aparentes, tamanhos, pesos, contraste
- **Paleta:** Cores dominantes, acentos, backgrounds, bordas
- **Componentes:** Cards, tabelas, menus, botões, badges, forms
- **Estilo geral:** Flat / neumorphic / glassmorphism / brutalist / minimal?
- **O que funciona bem:** Preservar conscientemente
- **O que está fraco:** Identificar sem julgamento — espaçamentos apertados, hierarquia confusa,
  fontes genéricas, excesso de bordas, cores sem coerência

### 1.2 Classificar o contexto

Determinar o tipo de interface:

- **Dashboard** (dados, KPIs, gráficos)
- **Form / CRUD** (entrada de dados, tabelas)
- **Landing / Marketing** (impressão, conversão)
- **Operacional** (ateliê, gestão, tarefas)
- **Financeiro** (transações, relatórios, categorias)

Isso define o tom: financeiro pede austeridade e precisão; operacional pede clareza e velocidade.

-----

## FASE 2 — PESQUISA DE COMPONENTES (web search)

Antes de escrever qualquer código, **pesquisar componentes prontos** nas bibliotecas certas.
O objetivo é partir de uma base sólida e testada, não reinventar a roda.

### 2.1 Escolher a biblioteca certa por tipo de componente

|Componente necessário      |Biblioteca prioritária|URL de referência                       |
|---------------------------|----------------------|----------------------------------------|
|Tabelas, gráficos, KPIs    |**Tremor**            |`https://tremor.so/components`          |
|Componentes acessíveis base|**shadcn/ui**         |`https://ui.shadcn.com/docs/components` |
|Animações / efeitos visuais|**Aceternity UI**     |`https://ui.aceternity.com/components`  |
|Motion e microinterações   |**MagicUI**           |`https://magicui.design/docs/components`|
|Componentes expressivos    |**Origin UI**         |`https://originui.com`                  |

### 2.2 Processo de pesquisa

1. Identificar os 2-4 componentes principais que a tela precisa (ex: tabela de dados, card de KPI, filtro de datas)
1. Para cada componente, buscar na biblioteca mais adequada:
- Verificar se a implementação é simples (evitar componentes que exigem 5+ dependências)
- Verificar se é customizável com CSS variables / Tailwind
- Verificar se funciona bem em Next.js App Router
1. Anotar no guia de design: "Componente X baseado em [Biblioteca] — [URL específica]"

### 2.3 Critérios de seleção

**Usar o componente da lib quando:**

- A lógica de acessibilidade é complexa (dropdowns, modals, tooltips)
- O componente tem estado interno não-trivial (tabela com sort/filter, datepicker)
- A lib é shadcn/ui — o código é copiado e modificado, não é dependência runtime

**Construir do zero quando:**

- O componente é simples (card estático, badge, label)
- A lib adicionaria overhead desnecessário
- O design precisa de algo muito específico que a lib não suporta

### 2.4 Regra de ouro

**Nunca adicionar uma dependência inteira para usar um único componente simples.**
shadcn/ui é a exceção — por ser copy-paste, não aumenta bundle.

-----

## FASE 3 — GUIA DE DESIGN

Gerar um **Design Token Sheet** com as decisões para o redesign.
Salvar como `design-guide.md` e apresentar ao usuário antes de codar.

### Estrutura do guia:

```markdown
## Design Guide — [Nome do Componente]

### Conceito
[Uma frase: qual é a alma desse redesign? Ex: "Clareza cirúrgica com hierarquia respirada"]

### Modo de input utilizado
[A / B / C — e breve justificativa]

### Paleta
| Token           | Hex       | Uso                          |
|-----------------|-----------|------------------------------|
| --color-bg      | #0f1117   | Fundo principal              |
| --color-surface | #1a1d27   | Cards, painéis               |
| --color-border  | #2a2d3e   | Divisores sutis              |
| --color-text    | #e2e8f0   | Texto principal              |
| --color-muted   | #6b7280   | Labels, legendas             |
| --color-accent  | #4f8ef7   | CTAs, highlights, links      |
| --color-success | #34d399   | Status positivo              |
| --color-danger  | #f87171   | Alertas, negativos           |

### Tipografia
| Papel         | Fonte         | Peso  | Tamanho |
|---------------|---------------|-------|---------|
| Display/Title | [Fonte]       | 700   | 28-32px |
| Heading       | [Fonte]       | 600   | 18-22px |
| Body          | [Fonte]       | 400   | 14-15px |
| Label/Caption | [Fonte]       | 500   | 11-12px |
| Mono/Data     | [Fonte Mono]  | 400   | 13px    |

### Espaçamento
Usar escala de 4px: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64

### Componentes-chave
- Cards: border-radius 12px, sem sombra pesada, border sutil
- Tabelas: row height 48px, zebragem leve, hover sutil
- Botões: 36px height, padding 12-24px, sem outline ao redor do mundo
- Badges: 20px height, pill shape, cor semântica

### Fontes de componentes utilizadas
| Componente    | Origem        | Notas de customização         |
|---------------|---------------|-------------------------------|
| Tabela        | shadcn/ui     | Cor de header alterada        |
| KPI Card      | Tremor        | Removido ícone padrão         |
| [etc]         | [lib ou zero] | [o que foi alterado]          |

### Princípios aplicados
1. [Princípio 1 específico deste redesign]
2. [Princípio 2]
3. [Princípio 3]
```

-----

## FASE 4 — CÓDIGO REACT

### 4.1 Regras de execução

**SEMPRE:**

- Usar CSS Variables para todos os tokens de design
- Componente self-contained — zero dependências externas além do React
- Tailwind apenas para utilidades básicas; estilos críticos inline ou CSS-in-JS
- Fontes via Google Fonts import no topo (ex: `@import url(...)`)
- Dados mockados realistas — não usar "Lorem ipsum" nem "Item 1, Item 2"
- TypeScript-ready (props tipadas mesmo em .jsx)

**NUNCA:**

- Usar Inter, Roboto ou Arial como fonte principal
- Cores sem semântica (evitar `#333`, `#666` soltos — sempre tokens)
- Padding/margin hardcoded sem justificativa
- Componentes com mais de 200 linhas — dividir em sub-componentes
- Bordas grossas ou sombras box-shadow exageradas
- Gradientes desnecessários em elementos funcionais

### 4.2 Estrutura do output de código

```jsx
// ============================================================
// [NomeDoComponente].jsx
// Design: [Conceito em uma frase]
// Stack: React + CSS Variables + Google Fonts
// ============================================================

import { useState } from "react"

// --- DESIGN TOKENS ---
const tokens = {
  bg: "#0f1117",
  surface: "#1a1d27",
  // ... todos os tokens do guia
}

// --- ESTILOS BASE ---
const globalStyles = `
  @import url('https://fonts.googleapis.com/...');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --color-bg: ${tokens.bg};
    --color-surface: ${tokens.surface};
    /* ... */
  }
`

// --- SUB-COMPONENTES ---
const MetricCard = ({ label, value, delta }) => { ... }
const DataTable = ({ rows }) => { ... }

// --- COMPONENTE PRINCIPAL ---
export default function [NomeDoComponente]() {
  return (
    <>
      <style>{globalStyles}</style>
      <div style={{ background: "var(--color-bg)", ... }}>
        {/* layout aqui */}
      </div>
    </>
  )
}
```

### 4.3 Padrões por tipo de interface

**Dashboard financeiro:**

- Dark mode preferencial (`#0f1117` base)
- Números em fonte mono (JetBrains Mono, Fira Code)
- KPI cards com delta colorido (verde/vermelho semântico)
- Tabela principal ocupa 60% do espaço
- Sidebar ou topbar com navegação clara

**Form / CRUD operacional:**

- Light mode (`#fafaf9` base)
- Inputs com label flutuante ou acima (nunca placeholder como label)
- Botão primário isolado, hierarquia clara
- Feedback de estado (loading, sucesso, erro) sempre presente

**Relatório / listagem:**

- Tipografia editorial (Playfair Display, DM Serif para títulos)
- Espaçamento generoso — respiração é profissionalismo
- Filtros compactos no topo, não em sidebar separada
- Empty states desenhados, não texto genérico

-----

## FASE 5 — STUDY LOG

Gerar `study-log.md` — documentação completa do processo de decisão.
Este arquivo é o "diário" do redesign: por que cada escolha foi feita, o que foi descartado e por quê.

### Estrutura do study-log.md:

```markdown
# Study Log — [NomeDoComponente]
**Data:** [data]
**Modo:** [A / B / C]
**Salvo em:** [SAVE_PATH]

---

## 1. O que foi recebido
[Descrição objetiva das imagens/prints fornecidos pelo usuário]

## 2. Primeira leitura — impressões brutas
[Observações livres da primeira análise, antes de qualquer decisão]
Ex: "A tela tem muita informação na parte superior, criando peso visual desnecessário.
A paleta de cores usa azul genérico sem hierarquia clara..."

## 3. O que funciona — preservar
- [Item que estava bom e foi mantido]
- [Item que estava bom e foi mantido]

## 4. O que foi repensado — e por quê
| Elemento original     | Problema identificado           | Solução adotada              |
|-----------------------|---------------------------------|------------------------------|
| [ex: fonte Arial]     | Sem personalidade, muito usada  | Syne + DM Sans               |
| [ex: bordas 2px]      | Peso visual desnecessário       | Border 1px com opacidade 40% |
| [etc]                 | [...]                           | [...]                        |

## 5. Alternativas consideradas e descartadas
### Paleta
- **Tentativa 1:** [paleta] — descartada porque [motivo]
- **Escolha final:** [paleta] — escolhida porque [motivo]

### Tipografia
- **Tentativa 1:** [fonte] — descartada porque [motivo]
- **Escolha final:** [fonte] — escolhida porque [motivo]

### Layout
- **Opção A:** [descrição] — descartada porque [motivo]
- **Opção adotada:** [descrição] — adotada porque [motivo]

## 6. Componentes pesquisados
| Componente     | Libs consultadas          | Escolha final     | Justificativa              |
|----------------|---------------------------|-------------------|----------------------------|
| Tabela         | shadcn/ui, Tremor         | shadcn/ui         | Mais customizável           |
| KPI Card       | Tremor, construído zero   | Construído zero   | Tremor rígido demais        |

## 7. Decisões de design — raciocínio
[Parágrafo livre explicando o conceito central do redesign e como ele se conecta
com o contexto do projeto. Por que essa direção e não outra?]

## 8. Próximos passos sugeridos
- [ ] [Sugestão 1 — ex: aplicar essa paleta também na tela X]
- [ ] [Sugestão 2 — ex: criar variante dark/light]
- [ ] [Sugestão 3 — ex: componentizar o KPI card para reutilizar]
```

-----

## FASE 6 — APRESENTAÇÃO

Entregar **sempre nesta ordem**:

1. **Confirmação do local de salvamento** — "Salvando em `[SAVE_PATH]`"
1. **Modo identificado** (A, B ou C) com 1 linha de explicação
1. **Arquivo `study-log.md`** — processo completo documentado
1. **Arquivo `design-guide.md`** — tokens, decisões e tabela de componentes
1. **Arquivo `[NomeDoComponente].jsx`** — código completo funcional
1. **Nota de implementação inline** — como integrar no Next.js (fonts no `layout.tsx`,
   variáveis globais no `globals.css`, dependências a instalar se necessário)

**Regra:** Nunca entregar só o código sem o study-log e o design-guide.
Os três arquivos caminham juntos — são um pacote, não peças separadas.

-----

## REFERÊNCIAS INTERNAS

Ver seção "ARQUIVO 2" abaixo para catálogo de direções estéticas por tipo de produto.
Ver seção "ARQUIVO 3" abaixo para combinações de fontes testadas e aprovadas.

-----

-----

# ARQUIVO 2: references/aesthetic-directions.md

# Direções Estéticas por Tipo de Produto

Catálogo de direções aprovadas para uso na skill executive-ui.
Cada direção inclui: conceito, paleta base, fontes, e quando usar.

-----

## 1. OBSIDIAN FINANCE

**Conceito:** Dados como matéria-prima. Controle total sem ruído.
**Quando usar:** Dashboards financeiros, tracking de investimentos, relatórios de gastos
**Paleta:**

- BG: `#0a0c10`
- Surface: `#13161e`
- Border: `#1f2330`
- Text: `#e2e8f0`
- Muted: `#64748b`
- Accent: `#3b82f6`
- Success: `#22c55e`
- Danger: `#ef4444`

**Fontes:** Syne (display) + DM Sans (corpo) + JetBrains Mono (números)
**Princípios:** Zero decoração; cada pixel tem função; números são heróis

-----

## 2. CHALK & LINEN

**Conceito:** Clareza editorial. Inteligência sem intimidação.
**Quando usar:** Apps operacionais, gestão de pedidos, formulários, ateliê
**Paleta:**

- BG: `#fafaf8`
- Surface: `#ffffff`
- Border: `#e5e7eb`
- Text: `#111827`
- Muted: `#6b7280`
- Accent: `#2563eb`
- Success: `#059669`
- Danger: `#dc2626`

**Fontes:** Fraunces (títulos) + Inter Display (corpo — exceção justificada pelo pareamento)
**Princípios:** Espaçamento generoso; tipografia como estrutura; cor usada com parcimônia

-----

## 3. SLATE EXECUTIVE

**Conceito:** Autoridade discreta. O design que não grita, mas comanda.
**Quando usar:** Relatórios executivos, dashboards B2B, painéis de gestão
**Paleta:**

- BG: `#f8f9fb`
- Surface: `#ffffff`
- Border: `#dde1ea`
- Text: `#1e293b`
- Muted: `#94a3b8`
- Accent: `#0f172a`
- Accent2: `#3b82f6`
- Success: `#10b981`
- Danger: `#f43f5e`

**Fontes:** Instrument Serif (headings) + Geist (corpo) + Geist Mono (dados)
**Princípios:** Hierarquia clara; acento escuro transmite seriedade; accent2 azul para ações

-----

## 4. COPPER & INK

**Conceito:** Sofisticação artesanal. Precisão com alma.
**Quando usar:** Apps de ateliê, moda, estúdios criativos, pequenos negócios premium
**Paleta:**

- BG: `#1c1814`
- Surface: `#252018`
- Border: `#3a3228`
- Text: `#f5f0e8`
- Muted: `#9c9080`
- Accent: `#c9a96e` (cobre)
- Success: `#6fba8a`
- Danger: `#d4706a`

**Fontes:** Cormorant Garamond (display) + Nunito (corpo)
**Princípios:** Warm dark mode; cobre como elemento premium; elegância com funcionalidade

-----

## 5. ARCTIC MINIMAL

**Conceito:** Frieza produtiva. O vazio como resposta.
**Quando usar:** Apps de produtividade, to-do, ferramentas de foco, note-taking
**Paleta:**

- BG: `#f0f4f8`
- Surface: `#ffffff`
- Border: `#cbd5e1`
- Text: `#0f172a`
- Muted: `#64748b`
- Accent: `#0ea5e9`
- Success: `#0d9488`
- Danger: `#e11d48`

**Fontes:** Space Grotesk (headings — contexto justificado) + Figtree (corpo)
**Princípios:** Máximo espaço negativo; cores apenas onde há intenção; componentes quase invisíveis

-----

## Combinações a EVITAR

|Combinação proibida                      |Por quê                       |
|-----------------------------------------|------------------------------|
|Purple gradient + white bg               |Clichê absoluto de "app de IA"|
|Inter + Roboto                           |Genérico sem personalidade    |
|Border-radius 4px em tudo                |Parece bootstrap padrão       |
|Sombra box-shadow em card dentro de card |Excesso visual                |
|`#333333` como cor de texto              |Sem semântica, sem sistema    |
|Botão com outline + filled no mesmo nível|Hierarquia quebrada           |

-----

-----

# ARQUIVO 3: references/font-pairings.md

# Combinações de Fontes Aprovadas

Pares testados e aprovados para uso na skill executive-ui.
Todas disponíveis no Google Fonts. Nenhuma é Arial, Roboto ou Inter padrão.

-----

## TIER 1 — Alta Personalidade

### Syne + DM Sans

```
Display/Title: Syne 700-800
Body: DM Sans 400-500
Data/Mono: JetBrains Mono 400
```

**Melhor para:** Fintech, dashboards dark, apps de dados
**Caráter:** Geométrico moderno, sem ser frio
**Import:**

```
https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap
```

-----

### Fraunces + DM Sans

```
Display/Title: Fraunces 700 (optical: 144)
Body: DM Sans 400-500
```

**Melhor para:** Apps operacionais, ateliê, gestão clean light
**Caráter:** Editorial inteligente — serif expressivo com sans funcional
**Import:**

```
https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,700&family=DM+Sans:wght@400;500;600&display=swap
```

-----

### Instrument Serif + Geist

```
Display/Title: Instrument Serif 400 (itálico para destaque)
Body: Geist 400-500
Data/Mono: Geist Mono 400
```

**Melhor para:** B2B executivo, relatórios, painéis de gestão
**Caráter:** Autoridade refinada — serif clássico com sans moderno
**Import:**

```
https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;500;600&display=swap
```

> Nota: Geist também disponível via `next/font` no Next.js

-----

### Cormorant Garamond + Nunito

```
Display/Title: Cormorant Garamond 600-700
Body: Nunito 400-500
```

**Melhor para:** Ateliê, moda, negócios premium, apps com alma
**Caráter:** Elegância artesanal — alto contraste serif + rounded sans
**Import:**

```
https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Nunito:wght@400;500;600&display=swap
```

-----

## TIER 2 — Versáteis e Confiáveis

### Plus Jakarta Sans (solo)

```
Todos os pesos: 300-700
```

**Melhor para:** Apps que precisam de consistência sem drama
**Caráter:** Moderno humanista — personalidade sutil, extremamente legível
**Import:**

```
https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap
```

-----

### Outfit + Fira Code

```
Display/Body: Outfit 400-700
Data/Mono: Fira Code 400-500
```

**Melhor para:** Fintech light mode, dashboards analíticos
**Caráter:** Clean geométrico com dados bem ancorados em mono
**Import:**

```
https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap
```

-----

### Figtree + Space Mono

```
Body/UI: Figtree 400-600
Dados/Código: Space Mono 400
```

**Melhor para:** Ferramentas, dev tools, fintech técnico
**Caráter:** Amigável mas sério — mono adiciona credibilidade técnica
**Import:**

```
https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap
```

-----

## Regras de Uso

1. **Máximo 2 famílias** por interface (exceto quando mono é a terceira para dados)
1. **Display** = títulos, KPIs, números grandes — pode ser mais expressivo
1. **Body** = tudo que o usuário vai ler corrido — priorizar legibilidade
1. **Mono** = valores numéricos, IDs, códigos, datas alinhadas — sempre que houver tabela com números
1. **Tamanho mínimo** = 12px para qualquer texto funcional
1. **Line-height padrão** = 1.5 para corpo, 1.2 para headings
1. **Letter-spacing** = 0.02-0.05em em maiúsculas/labels pequenos; 0 para corpo
