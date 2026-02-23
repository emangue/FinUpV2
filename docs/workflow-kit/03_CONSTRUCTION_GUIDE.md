# 03_CONSTRUCTION_GUIDE.md (Fase de Construção)

## 🎯 OBJETIVO DESTA FASE
Executar a implementação seguindo um roteiro ordenado, passo a passo, evitando retrabalho e alucinações da IA.

---

## 📋 PROMPT DE ATIVAÇÃO GERAL
**Copie e cole no chat do Copilot/IA antes de começar:**

```
Atue como Senior Full-Stack Developer especialista em React/Next.js e Tailwind CSS.

CONTEXTO: 
- Você tem acesso ao arquivo VISUAL_ANALYSIS_[nome].md (Fase 1)
- Você tem acesso ao arquivo ARCHITECTURE_[nome].md (Fase 2)

TAREFA: Implementar a interface seguindo estritamente o roteiro de passos no arquivo 03_CONSTRUCTION_GUIDE.md.

REGRAS CRÍTICAS:
- Execute UM PASSO POR VEZ e aguarde minha confirmação antes de avançar
- Use EXATAMENTE as cores, espaçamentos e tipografia definidos na Fase 1
- Siga a arquitetura de componentes definida na Fase 2
- Para gráficos, use a estratégia (SVG ou Lib) decidida na Fase 2
- Código deve ser TypeScript, limpo e comentado
- Siga convenções de nomenclatura consistentes

IMPORTANTE: Não pule etapas. Se eu disser "Next", avance para o próximo passo.
```

---

## 🛠️ ROTEIRO DE EXECUÇÃO

### ⚙️ SETUP: Preparação do Ambiente

#### PROMPT PARA A IA:
```
PASSO SETUP: Configure o ambiente de desenvolvimento.

1. Se necessário, instale dependências:
   - lucide-react (ícones)
   - [biblioteca de gráficos escolhida na Fase 2, se houver]
   - framer-motion (se animações foram planejadas)

2. Configure o Tailwind:
   - Adicione cores customizadas ao tailwind.config.ts (se houver HEX específicos fora da paleta padrão)
   - Configure fonte escolhida (Inter/Geist no globals.css ou layout)

3. Crie a estrutura de pastas definida na Fase 2:
   - /components/atoms
   - /components/molecules
   - /components/organisms
   - /types
   - /lib

4. Crie o arquivo /types/index.ts com todas as interfaces TypeScript da Fase 2.

5. Crie o arquivo /lib/constants.ts com os dados mockados da Fase 2.

Mostre-me o código dos arquivos types/index.ts e lib/constants.ts.
```

**✅ VALIDAÇÃO**: Confirmar que interfaces e mocks estão corretos.

---

### 🧱 PASSO 1: Átomos (Componentes Base)

#### PROMPT PARA A IA:
```
PASSO 1: Crie os componentes Átomos listados na Fase 2.

Para cada átomo:
- Use TypeScript com interface de Props
- Siga o design system da Fase 1 (cores, border-radius, sombras)
- Mantenha componentes pequenos e reutilizáveis
- Use Tailwind CSS exclusivamente

Átomos a criar: [Liste aqui os átomos da Fase 2]

Exemplo esperado:
```tsx
// components/atoms/Button.tsx
interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
}

export default function Button({ children, variant = 'primary', ... }: ButtonProps) {
  // Implementação com classes Tailwind
}
```

Gere o código de TODOS os átomos agora.
```

**✅ VALIDAÇÃO**: Revisar se estilos batem com a análise visual.

---

### 🔬 PASSO 2: Moléculas (Componentes Compostos)

#### PROMPT PARA A IA:
```
PASSO 2: Crie os componentes Moléculas listados na Fase 2.

Cada molécula deve:
- Compor Átomos criados no Passo 1
- Receber dados via props (tipados)
- Ser responsiva e acessível

Moléculas a criar: [Liste aqui as moléculas da Fase 2]

Exemplo de molécula:
```tsx
// components/molecules/CategoryRow.tsx
import { CategoryIcon } from '@/components/atoms/CategoryIcon';

interface CategoryRowProps {
  label: string;
  icon: React.ElementType;
  percent: number;
  color: string;
}

export default function CategoryRow({ label, icon, percent, color }: CategoryRowProps) {
  // Implementação com progress bar customizada
}
```

Gere o código de TODAS as moléculas agora.
```

**✅ VALIDAÇÃO**: Testar composição e props.

---

### 📊 PASSO 3: O DESAFIO - Visualizações de Dados

Este é o passo mais crítico. Use um dos prompts abaixo conforme a estratégia escolhida na Fase 2:

#### OPÇÃO A: Se escolheu SVG Artesanal

**PROMPT PARA A IA:**
```
PASSO 3: Crie o componente de gráfico usando SVG PURO (sem bibliotecas).

Gráfico a criar: [Nome do gráfico - Ex: DonutChart]

Requisitos baseados na Fase 1:
- Tipo: [Donut, Bar, Line, etc]
- Cores: [Listar cores exatas]
- Características especiais: [Pontas arredondadas, stroke-linecap, etc]

ESTRATÉGIA SVG:
1. Use viewBox="0 0 100 100" para responsividade
2. Para Donut/Pie: Use <circle> com stroke-dasharray e stroke-dashoffset
3. Para Barras: Use <rect> com rounded corners
4. Para Linhas: Use <path> com curvas bézier
5. Adicione <filter> para sombras/glow se necessário

IMPORTANTE:
- stroke-linecap="round" para pontas arredondadas
- Calcule os offsets corretamente para os segmentos
- Use transform-origin para rotações

Gere o código do componente [NomeDoGrafico].tsx com TypeScript completo.
```

#### OPÇÃO B: Se escolheu Biblioteca (Recharts/etc)

**PROMPT PARA A IA:**
```
PASSO 3: Crie o componente de gráfico usando [nome da biblioteca].

Gráfico a criar: [Nome do gráfico]

Requisitos baseados na Fase 1:
- Tipo: [BarChart, LineChart, PieChart]
- Cores: [Listar cores exatas]
- Eixos: [Quais são visíveis, formatação]

CUSTOMIZAÇÕES OBRIGATÓRIAS (para ficar igual ao design):
1. Remova elementos desnecessários:
   - CartesianGrid: {vertical: false} (ou remover completamente)
   - Tooltip: Estilizar custom
   - Legend: Posicionar conforme design

2. Estilize barras/linhas:
   - Para barras: radius={[top, top, 0, 0]} para arredondar só o topo
   - Cores exatas da Fase 1

3. Customize Eixos:
   - Fonte: text-xs
   - Cor: text-gray-400
   - Remova tickLine se o design não tem

EXEMPLO BASE:
```tsx
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer } from 'recharts';

export default function CustomBarChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Bar dataKey="value" fill="#000000" radius={[8, 8, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

Gere o código do componente [NomeDoGrafico].tsx customizado conforme o design.
```

**✅ VALIDAÇÃO**: Este é o momento crítico. Testar visualmente se ficou idêntico.

---

### 🏢 PASSO 4: Organismos (Seções Grandes)

#### PROMPT PARA A IA:
```
PASSO 4: Crie os componentes Organismos listados na Fase 2.

Cada organismo deve:
- Compor Moléculas e Átomos
- Implementar lógica de estado (useState) se necessário
- Seguir o layout da Fase 1

Organismos a criar: [Liste aqui os organismos da Fase 2]

Exemplo de organismo:
```tsx
// components/organisms/WalletCard.tsx
import DonutChart from '@/components/organisms/DonutChart';
import CategoryRow from '@/components/molecules/CategoryRow';

export default function WalletCard() {
  const [activeTab, setActiveTab] = useState('Savings');
  
  return (
    <div className="bg-white rounded-3xl p-6 shadow-lg">
      {/* Header com dropdown */}
      {/* DonutChart */}
      {/* Tab Switcher */}
      {/* Lista de CategoryRows */}
    </div>
  );
}
```

Gere o código de TODOS os organismos agora.
```

**✅ VALIDAÇÃO**: Verificar composição e estado.

---

### 📱 PASSO 5: Layout & Página Principal

#### PROMPT PARA A IA:
```
PASSO 5: Monte a página completa (page.tsx ou App.tsx).

Estrutura baseada na Fase 1:
1. Layout container:
   - Fundo: [cor da Fase 1]
   - Centralizado: max-w-md mx-auto (para simular mobile)
   - min-h-screen

2. Header: [Componente Header se houver]

3. Main Content:
   - Padding: [da Fase 1]
   - Componentes Organismos na ordem visual

4. Bottom Navigation (se houver):
   - position: fixed bottom-0
   - Glassmorphism: backdrop-blur-md bg-white/80
   - Safe area: pb-safe

5. Efeitos especiais:
   - Adicione gradientes de fundo se identificados na Fase 1
   - Adicione animações de entrada (fade-in, slide-up)

Gere o código completo do page.tsx.
```

**✅ VALIDAÇÃO**: Testar scroll, responsividade e layout geral.

---

### 🎨 PASSO 6: Polimento & Refinamento

#### PROMPT PARA A IA:
```
PASSO 6: Refinamentos finais para pixel-perfect.

Checklist de polimento:
1. **Espaçamentos**: Verificar se todos os gaps/paddings batem com a Fase 1
2. **Hover States**: Adicionar efeitos hover nos botões/cards
3. **Animações**:
   - Fade-in suave ao carregar a página
   - Animação de crescimento nos gráficos (0% -> 100%)
   - Transitions suaves (transition-all duration-300)
4. **Sombras**: Verificar se as shadows estão corretas
5. **Responsive**: Testar em mobile (< 640px) e ajustar se necessário
6. **Acessibilidade**:
   - Adicionar aria-label nos gráficos
   - Garantir contraste de cores
   - Tab order correto

Revise o código e implemente esses refinamentos.
```

**✅ VALIDAÇÃO FINAL**: Comparar lado a lado com a imagem original.

---

## 🐛 SEÇÃO DE DEBUG

Se algo não ficou como esperado, use estes prompts:

### Debug: Cores Erradas
```
"As cores do [componente] não estão batendo com o design. Revise o arquivo VISUAL_ANALYSIS e corrija os valores HEX para serem EXATAMENTE: [listar cores]."
```

### Debug: Espaçamento
```
"O espaçamento entre [elemento A] e [elemento B] está muito apertado/largo. Na análise visual está definido como [valor]. Ajuste para ficar idêntico."
```

### Debug: Gráfico não renderiza
```
"O gráfico [nome] não está aparecendo. Verifique:
1. Os dados mockados estão no formato correto?
2. O ResponsiveContainer tem altura definida?
3. Console tem erros?
Debugue e corrija."
```

### Debug: Layout quebrado em mobile
```
"O layout está quebrando em telas < 640px. Ajuste o [componente] para:
- Mudar de row para column
- Reduzir padding de [valor atual] para [valor mobile]
- Esconder [elemento] em mobile"
```

---

## ✅ CHECKLIST FINAL DE QUALIDADE

Antes de considerar completo:
- [ ] Todos os componentes foram criados (Átomos → Organismos)
- [ ] Gráficos estão renderizando corretamente
- [ ] Cores são exatamente as da análise visual
- [ ] Espaçamentos e tipografia batem com o design
- [ ] Layout é responsivo (mobile + desktop)
- [ ] Hover states funcionam
- [ ] Não há erros no console
- [ ] Código está limpo e comentado
- [ ] TypeScript sem erros

---

## 🎉 CONCLUSÃO

Ao completar todos os passos, você terá:
- ✅ Componentes organizados e reutilizáveis
- ✅ UI pixel-perfect baseada no design
- ✅ Código TypeScript tipado e limpo
- ✅ Arquitetura escalável (Atomic Design)

**Próximos passos opcionais:**
- Conectar a APIs reais (substituir mocks)
- Adicionar testes (Jest, Testing Library)
- Otimizar performance (Lighthouse)
- Deploy (Vercel, Netlify)
