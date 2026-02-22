# 🎯 WORKFLOW: Imagem → Código Pixel-Perfect

> **Sistema de 3 Fases para transformar qualquer design em código React/Next.js sem alucinações da IA**

---

## 📖 Visão Geral

Este workflow elimina o problema de "pedir código direto da imagem" e a IA gerar algo completamente diferente. 

**O Segredo:** Quebrar o processo em 3 checkpoints de qualidade.

```
📸 IMAGEM
   ↓
🎨 FASE 1: Análise Visual (Decoder)
   ↓ [gera VISUAL_ANALYSIS_*.md]
   ↓
🏗️ FASE 2: Arquitetura Técnica (Architect)  
   ↓ [gera ARCHITECTURE_*.md]
   ↓
🛠️ FASE 3: Construção Guiada (Builder)
   ↓
✅ CÓDIGO PRONTO
```

**Por que funciona?**
- Se as cores estiverem erradas, você corrige na Fase 1 (antes de codar)
- Se a biblioteca escolhida for ruim, você corrige na Fase 2 (antes de codar)
- O código final (Fase 3) sai quase perfeito porque tem contexto completo

---

## 🚀 Quick Start (5 passos)

### 1️⃣ Prepare sua imagem
- Tenha a imagem do design aberta (Figma export, screenshot, etc)
- Nome sugerido: `design-[nome-da-tela].png`

### 2️⃣ Execute a Fase 1 (Análise Visual)
**Abra:** [01_VISUAL_DECODER.md](01_VISUAL_DECODER.md)

**Copie este prompt e cole no chat do Copilot:**
```
Atue como UI/UX Designer Sênior especialista em Tailwind CSS e Design Systems.

TAREFA: Analise a imagem anexada pixel por pixel e preencha o template do arquivo 01_VISUAL_DECODER.md com extrema precisão.

REGRAS:
- NÃO gere código React/CSS ainda
- Use códigos HEX para cores
- Estime tamanhos usando a escala Tailwind (text-xs, p-4, rounded-lg, etc)
- Seja específico sobre sombras, gradientes e efeitos especiais
- Identifique TODOS os gráficos/visualizações presentes

FORMATO DE SAÍDA: Crie um novo arquivo chamado "VISUAL_ANALYSIS_[nome-da-tela].md" com o conteúdo preenchido seguindo exatamente a estrutura do template.
```

**Cole a imagem** no chat junto com o prompt.

**✅ Checkpoint:** Revise o arquivo gerado. Cores corretas? Gráficos identificados? Se sim, avance.

---

### 3️⃣ Execute a Fase 2 (Arquitetura)
**Abra:** [02_ARCHITECT_PLAN.md](02_ARCHITECT_PLAN.md)

**Copie este prompt:**
```
Atue como Tech Lead e Arquiteto de Software especialista em React/Next.js.

CONTEXTO: Você acabou de receber a análise visual completa no arquivo "VISUAL_ANALYSIS_[nome-da-tela].md".

TAREFA: Com base naquela análise, preencha o template do arquivo 02_ARCHITECT_PLAN.md definindo:
1. A estrutura de componentes (Atomic Design)
2. A estratégia para implementar gráficos/visualizações (SVG vs Biblioteca)
3. As interfaces TypeScript dos dados
4. As decisões técnicas críticas

REGRAS:
- Priorize reutilização e manutenibilidade
- Para gráficos, escolha entre SVG Puro vs Bibliotecas e JUSTIFIQUE
- Defina tipos TypeScript completos
- Considere performance e acessibilidade

FORMATO DE SAÍDA: Crie um novo arquivo chamado "ARCHITECTURE_[nome-da-tela].md" com o conteúdo preenchido.
```

**✅ Checkpoint:** A decisão sobre gráficos (SVG vs Recharts) faz sentido? Componentes estão bem estruturados? Se sim, avance.

---

### 4️⃣ Execute a Fase 3 (Construção)
**Abra:** [03_CONSTRUCTION_GUIDE.md](03_CONSTRUCTION_GUIDE.md)

**Copie este prompt inicial:**
```
Atue como Senior Full-Stack Developer especialista em React/Next.js e Tailwind CSS.

CONTEXTO: 
- Análise visual: VISUAL_ANALYSIS_[nome-da-tela].md
- Arquitetura: ARCHITECTURE_[nome-da-tela].md

TAREFA: Implementar a interface seguindo o roteiro de passos no arquivo 03_CONSTRUCTION_GUIDE.md.

REGRAS CRÍTICAS:
- Execute UM PASSO POR VEZ e aguarde minha confirmação antes de avançar
- Use EXATAMENTE as cores, espaçamentos e tipografia definidos na Fase 1
- Siga a arquitetura de componentes definida na Fase 2
- Para gráficos, use a estratégia (SVG ou Lib) decidida na Fase 2
- Código deve ser TypeScript, limpo e comentado

Diga "PRONTO" quando entender. Depois disso, vou pedir para você executar o PASSO SETUP.
```

Depois que a IA confirmar, vá executando passo a passo:
- `"Execute o PASSO SETUP"`
- `"Execute o PASSO 1"` (Átomos)
- `"Execute o PASSO 2"` (Moléculas)
- `"Execute o PASSO 3"` (Gráficos - O DESAFIO)
- `"Execute o PASSO 4"` (Organismos)
- `"Execute o PASSO 5"` (Layout)
- `"Execute o PASSO 6"` (Polimento)

**✅ Checkpoint Final:** Comparar o resultado com a imagem original lado a lado.

---

### 5️⃣ Debug (se necessário)
Se algo não ficou igual, use os prompts de debug na seção final do [03_CONSTRUCTION_GUIDE.md](03_CONSTRUCTION_GUIDE.md):
- Cores erradas
- Espaçamento incorreto
- Gráfico não renderiza
- Layout quebrado

---

## 🎯 Quando Usar Este Workflow?

### ✅ Use quando:
- Você tem um design "artístico" (Dribbble, Figma, Behance)
- O layout é complexo (gráficos customizados, animações)
- Você já tentou pedir código direto e saiu errado
- Quer código organizado (Atomic Design) e escalável
- Precisa de TypeScript bem tipado

### ❌ Não precisa usar quando:
- É uma tela simples (formulário básico, lista de texto)
- Você está só testando uma ideia rápida
- O design é "padrão" (Bootstrap-like, Material Design)

---

## 📂 Arquivos Gerados (Estrutura Esperada)

Durante o processo, você terá:

```
/LeitorImagem
  ├── WORKFLOW.md                           ← Você está aqui
  ├── 01_VISUAL_DECODER.md                  ← Template Fase 1
  ├── 02_ARCHITECT_PLAN.md                  ← Template Fase 2
  ├── 03_CONSTRUCTION_GUIDE.md              ← Template Fase 3
  │
  ├── VISUAL_ANALYSIS_wallet.md             ← Output Fase 1 (exemplo)
  ├── ARCHITECTURE_wallet.md                ← Output Fase 2 (exemplo)
  │
  ├── /components                           ← Código gerado na Fase 3
  │   ├── /atoms
  │   ├── /molecules
  │   ├── /organisms
  ├── /types
  ├── /lib
  └── page.tsx ou app.tsx
```

---

## 🔧 Troubleshooting

### Problema: "A IA não está seguindo o template"
**Solução:** No prompt, adicione:
```
IMPORTANTE: Siga EXATAMENTE a estrutura de seções e subseções do template. Não pule nenhuma seção.
```

### Problema: "Ela está gerando código na Fase 1"
**Solução:** Reforce no prompt:
```
PROIBIDO gerar código React/CSS/TypeScript nesta fase. Apenas análise descritiva em Markdown.
```

### Problema: "O gráfico ficou completamente diferente"
**Solução:** Volte para a Fase 2 e mude a decisão:
- Se escolheu Recharts → Mude para SVG Puro
- Se escolheu SVG → Pode usar Recharts com customização pesada

### Problema: "As cores não batem"
**Solução:** Na Fase 1, use uma ferramenta de color picker (Digital Color Meter no Mac, PowerToys no Windows) para extrair HEX exato da imagem.

---

## 💡 Dicas Pro

### 1. Use @workspace no Copilot
Quando for para a Fase 2, digite `@workspace` antes do prompt. Isso força a IA a ler o arquivo da Fase 1.

### 2. Salve os outputs da Fase 1 e 2
Não delete os arquivos `VISUAL_ANALYSIS_*.md` e `ARCHITECTURE_*.md`. Eles servem como documentação do projeto.

### 3. Para designs similares, reaproveite
Se você vai fazer 3 telas de um mesmo app (Dashboard, Perfil, Configurações), faça a Fase 1 de todas primeiro. Muitas cores/espaçamentos vão se repetir.

### 4. Gráficos complexos? Sempre SVG
Se o gráfico tem:
- Gradientes não-lineares
- Glow/sombras coloridas
- Formas orgânicas/curvas bézier custom

→ Escolha SVG Puro na Fase 2, mesmo que dê mais trabalho. O resultado é pixel-perfect.

### 5. Teste mobile durante a Fase 3
Entre os passos 4 e 5, use o Device Mode do navegador (F12 → Toggle Device Toolbar) para ver se está responsivo.

---

## 🎨 Exemplos de Uso

### Exemplo 1: Tela de Wallet (iOS Style)
- **Desafio:** Donut chart com pontas arredondadas, glassmorphism no menu
- **Decisão Fase 2:** SVG Puro para o gráfico
- **Resultado:** Pixel-perfect em 1h

### Exemplo 2: Dashboard Analytics (B&W)
- **Desafio:** Gráfico de barras com eixos complexos
- **Decisão Fase 2:** Recharts (eixos automáticos)
- **Resultado:** Funcional em 45min

---

## 🚨 Regras de Ouro

1. **Nunca pule fases.** Cada fase valida a anterior.
2. **Checkpoint em cada fase.** Se errou, volte e corrija antes de avançar.
3. **Um passo por vez na Fase 3.** Não deixe a IA fazer tudo de uma vez.
4. **Documente as decisões.** Os arquivos de Fase 1 e 2 são a "memória" do projeto.

---

## 📚 Referências dos Templates

- **Fase 1:** [01_VISUAL_DECODER.md](01_VISUAL_DECODER.md) - Extração visual
- **Fase 2:** [02_ARCHITECT_PLAN.md](02_ARCHITECT_PLAN.md) - Decisões técnicas
- **Fase 3:** [03_CONSTRUCTION_GUIDE.md](03_CONSTRUCTION_GUIDE.md) - Implementação

---

## 🎉 Pronto para Começar?

1. Pegue uma imagem de design
2. Cole no chat do Copilot
3. Use o prompt da **Fase 1** (seção 2️⃣ acima)
4. Siga o fluxo até o código final

**Boa construção!** 🚀
