# 01_VISUAL_DECODER.md (Fase de Análise Visual)

## 🎯 OBJETIVO DESTA FASE
Traduzir a imagem fornecida em especificação textual detalhada, extraindo cores, tipografia, espaçamentos e elementos visuais complexos. **NÃO GERAR CÓDIGO NESTA ETAPA.**

---

## 📋 PROMPT DE ATIVAÇÃO (MELHORADO)
**Copie e cole no chat do Copilot/IA:**

```
Atue como UI/UX Designer Sênior especialista em Tailwind CSS e Design Systems.

TAREFA: Analise a imagem anexada PIXEL POR PIXEL com máxima precisão. 
Preencha o template 01_VISUAL_DECODER.md. Esta análise será usada por 
um desenvolvedor para implementar a interface IDÊNTICA.

⚠️ REGRAS CRÍTICAS:
- NÃO gere código React/CSS ainda - apenas análise descritiva
- Use CÓDIGOS HEX EXATOS (não estime - use color picker se necessário)
- Para CADA elemento visual, responda às perguntas do template
- Estime tamanhos usando a escala Tailwind (text-xs, p-4, h-2, h-12, etc)
- Seja obsessivamente específico sobre detalhes pequenos

🔍 FOCOS DE ATENÇÃO (onde a IA costuma errar):

1. **Gráficos Circulares:**
   - Dê ZOOM na imagem
   - Tem gaps brancos entre segmentos? Se sim, quantos pixels?
   - Pontas são arredondadas ou quadradas?
   - Qual a espessura do stroke em pixels?

2. **Progress Bars:**
   - Meça a altura (h-1? h-2? h-3? h-4?)
   - O texto da % está DENTRO ou FORA da barra?
   - Se dentro, qual a cor do texto?

3. **Sombras:**
   - Elas existem de verdade ou é só o fundo?
   - Estime a opacidade (rgba(0,0,0,0.03) ou 0.08?)

4. **Espaçamentos:**
   - Compare elementos: tem mais espaço entre A e B ou entre C e D?
   - Use gap-2, gap-3, gap-4 etc de forma precisa

5. **Cores:**
   - Não use "azul padrão" - pegue o HEX exato
   - Para backgrounds pastel, verifique se é -50 ou -100

FORMATO DE SAÍDA: Crie um novo arquivo chamado "VISUAL_ANALYSIS_[nome-da-tela].md" 
com TODAS as seções do template preenchidas. Não pule nenhuma pergunta.

ANTES DE FINALIZAR, revise a seção "Armadilhas Comuns" e confirme que 
você não caiu em nenhuma delas.
```

---

## 📊 TEMPLATE DE ANÁLISE VISUAL

### 1. DNA VISUAL

#### 1.1 Identidade Estética
- **Estilo Geral**: [Ex: Minimalista iOS, Corporate Clean, Neumorphic, Glassmorphism]
- **Mood**: [Ex: Profissional, Lúdico, Futurístico]
- **Referências**: [Ex: Nubank, Apple Health, Notion]

#### 1.2 Sistema de Cores
- **Background Principal**: `#______`
- **Background Secundário**: `#______`
- **Surface/Cards**: `#______`
- **Primary Brand**: `#______`
- **Secondary/Accent**: `#______`
- **Text High Contrast**: `#______`
- **Text Medium Contrast**: `#______`
- **Text Low Contrast/Disabled**: `#______`
- **Borders/Dividers**: `#______`
- **Success**: `#______`
- **Warning**: `#______`
- **Error**: `#______`

#### 1.3 Tipografia
- **Font Family**: [Ex: Inter, SF Pro, Geist Sans, Roboto]
- **Heading 1**: [Ex: text-3xl, font-bold, #111827]
- **Heading 2**: [Ex: text-2xl, font-semibold]
- **Heading 3**: [Ex: text-xl, font-semibold]
- **Body Large**: [Ex: text-base, font-normal]
- **Body Regular**: [Ex: text-sm, font-normal]
- **Caption/Label**: [Ex: text-xs, font-medium, uppercase, tracking-wide]

### 2. ELEMENTOS DE LAYOUT

#### 2.1 Espaçamento & Ritmo
- **Container Padding**: [Ex: px-6, py-8]
- **Gaps entre Seções**: [Ex: space-y-6]
- **Gaps entre Elementos**: [Ex: gap-4]
- **Margin Top/Bottom padrão**: [Ex: mb-4]

#### 2.2 Forma & Contornos
- **Border Radius Cards**: [Ex: rounded-3xl (24px)]
- **Border Radius Buttons**: [Ex: rounded-full]
- **Border Radius Inputs**: [Ex: rounded-xl]
- **Border Width**: [Ex: border, border-2]

#### 2.3 Profundidade & Efeitos
- **Sombras Cards**: [Ex: shadow-lg, shadow-slate-200/50]
- **Sombras Elevadas**: [Ex: shadow-2xl]
- **Hover States**: [Ex: hover:shadow-xl transition-all]
- **Gradientes**: [Descreva direção, cores, opacidade]
- **Blur Effects**: [Ex: backdrop-blur-md, bg-white/80]
- **Texturas**: [Ex: Noise overlay, grain, pattern]

### 3. COMPONENTES ESPECÍFICOS

#### 3.1 Navegação
- **Tipo**: [Ex: Bottom Tab Bar, Sidebar, Top Nav]
- **Estado Ativo**: [Descreva indicador visual]
- **Estado Inativo**: [Cor, opacidade]
- **Animações**: [Ex: Slide indicator, fade]

#### 3.2 Botões & Ações
- **Primary Button**: [Cor, tamanho, estilo]
- **Secondary Button**: [Outline, ghost, etc]
- **Icon Buttons**: [Tamanho, padding]
- **FAB (Floating)**: [Posição, cor, shadow]

#### 3.3 Cards & Containers
- **Card Style**: [Flat, elevated, bordered]
- **Header do Card**: [Tipografia, spacing]
- **Body do Card**: [Padding interno]

### 4. VISUALIZAÇÕES DE DADOS

#### 4.1 Inventário de Gráficos
Liste TODOS os gráficos/visualizações presentes:

**GRÁFICO 1:**
- **Tipo**: [Bar Chart, Line Chart, Donut, Pie, Gauge, etc]
- **Posição na Tela**: [Ex: Centro do Card principal]
- **Dimensões Estimadas**: [Ex: 250x250px, full-width]
- **Cores Usadas**: [Liste as cores dos segmentos/barras]

#### 🔍 ANÁLISE DETALHADA (CRÍTICO - NÃO PULE):

**Estrutura dos Segmentos:**
- [ ] Segmentos separados com gaps? [SIM/NÃO]
  - Se SIM, gap width: [Ex: "1-2px muito fino" ou "5-10px visível"]
  - Cor do gap: [Ex: Branco, transparente, cor de fundo]
- [ ] É gradiente contínuo sem separação? [SIM/NÃO]
- [ ] Pontas arredondadas? [SIM/NÃO]
  - Se SIM: Em todas as pontas ou só nas extremidades?
- [ ] Stroke ou Fill? [Stroke-based (anel), Fill-based (sólido)]
- [ ] Espessura do stroke/barra: [Ex: "14px grosso" ou "8px fino"]

**Texto Interno (se houver):**
- [ ] Texto centralizado no gráfico? [SIM/NÃO]
- [ ] Alinhamento: [Centro, Topo, Embaixo]
- [ ] Estilos: [Listar tamanhos e cores de cada linha de texto]

**Efeitos:**
- [ ] Sombra interna/externa? [SIM/NÃO]
- [ ] Glow colorido? [SIM/NÃO]
- [ ] Eixos visíveis? [X, Y, ambos, nenhum]
- [ ] Grid de fundo? [Sim/Não, estilo]
- [ ] Labels/Legendas? [Posição, estilo]
- [ ] Animação aparente? [Fade-in, grow, etc]

**GRÁFICO 2:** [Repetir estrutura acima]

#### 4.2 Elementos de Dados (Progress Bars, Badges, etc)

#### 🎯 PROGRESS BARS (Análise Milimétrica)

Para cada barra de progresso na interface:

**Dimensões:**
- **Altura da barra**: [Ex: "2px muito fino" ou "12px grosso"]
- **Largura**: [Full-width, fixed, responsive]
- **Border radius**: [Ex: "rounded-full", "rounded-md"]

**Estrutura de Camadas:**
- [ ] **Fundo (track)**: 
  - Cor: [HEX]
  - Opacidade aparente: [10%, 20%, etc]
- [ ] **Barra de progresso (fill)**:
  - Cor: [HEX]
  - Ocupa: [Ex: "60% do track"]

**⚠️ POSICIONAMENTO DE TEXTO (CRÍTICO):**
- [ ] Porcentagem está DENTRO da barra colorida? [SIM/NÃO]
- [ ] Porcentagem está FORA (ao lado)? [SIM/NÃO]
- [ ] Se dentro: Alinhamento: [Direita, Centro, Esquerda]
- [ ] Se dentro: Cor do texto: [Branco, Preto, outro]
- [ ] Se fora: Posição: [Topo direita, linha com a barra]
⚠️ ARMADILHAS COMUNS (Detalhes que a IA erra)

### 🎯 Checklist Anti-Erro:

**Gráficos Circulares (Donut/Pie):**
- [ ] Verifiquei se tem gaps entre segmentos (olhe COM ZOOM)
- [ ] Se tem gaps, medi a espessura aproximada (1px? 3px? 5px?)
- [ ] Confirmei se pontas são arredondadas ou quadradas
- [ ] Medi a espessura do stroke (não apenas "grosso" ou "fino")

**Progress Bars:**
- [ ] Medi a altura da barra (não chutei)
- [ ] Verifiquei ONDE está o texto da porcentagem:
  - [ ] Dentro da barra?
  - [ ] Fora da barra (direita)?
  - [ ] Acima/abaixo da barra?
- [ ] Se dentro, confirmei a cor do texto (branco, preto?)
- [ ] Comparei se todas as barras têm a mesma altura

**Sombras:**
- [ ] Não confundi "sombra suave" com "sem sombra"
- [ ] Testei mentalmente: "Se escurecer a tela, ainda vejo a sombra?"
- [ ] Estimei opacidade (3%? 5%? 10%?)

**Espaçamentos:**
- [ ] Não usei "p-4" como padrão para tudo
- [ ] Comparei visualmente elementos diferentes
- [ ] Notei se há "muito ar" ou "compacto"

---

## ✅ CHECKLIST DE QUALIDADE FINAL

Antes de avançar para a Fase 2, confirme:
- [ ] Todas as cores foram extraídas em HEX (não estimadas)
- [ ] Tipografia foi mapeada com tamanhos Tailwind
- [ ] Todos os gráficos foram identificados e descritos COM DETALHES
- [ ] Gaps, espessuras e posicionamento de texto foram medidos
- [ ] Efeitos especiais (sombras, blur, gradients) foram documentados
- [ ] Espaçamentos foram estimados na escala Tailwind
- [ ] Revisei a seção "Armadilhas Comuns" e confirmei tudo

**Badges/Tags**: [Formato, cores, posição]
**Números/Métricas**: [Tipografia, destaque, hierarquia]

### 5. INTERATIVIDADE PERCEBIDA

#### 5.1 Estados
- **Hover**: [O que muda? Cor, escala, shadow?]
- **Active/Selected**: [Como é indicado?]
- **Disabled**: [Opacidade, cor]

#### 5.2 Transições
- **Velocidade**: [Fast, Medium, Slow]
- **Easing**: [Linear, ease-out, spring]

### 6. RESPONSIVIDADE VISUAL

#### 6.1 Layout Mobile/Desktop
- **É Mobile-First?**: [Sim/Não]
- **Breakpoints Aparentes**: [Mudanças de layout visíveis]
- **Stack Direction**: [Column em mobile, row em desktop?]

---

## ✅ CHECKLIST DE QUALIDADE

Antes de avançar para a Fase 2, confirme:
- [ ] Todas as cores foram extraídas em HEX
- [ ] Tipografia foi mapeada com tamanhos Tailwind
- [ ] Todos os gráficos foram identificados e descritos
- [ ] Efeitos especiais (sombras, blur, gradients) foram documentados
- [ ] Espaçamentos foram estimados na escala Tailwind

---

## 🚀 PRÓXIMO PASSO
Após preencher este documento, avance para **02_ARCHITECT_PLAN.md**
