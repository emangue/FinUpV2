# 📦 Projetos Next.js - Exportação para Projeto Principal

Esta pasta contém 4 projetos Next.js prontos para serem adaptados e integrados ao seu projeto principal.

## 📂 Estrutura

```
export-to-main-project/
├── metas/              # Sistema de metas (gastos e investimentos)
├── upload/             # Upload de arquivos
├── preview-upload/     # Preview e classificação de arquivos
├── dashboard/          # Dashboard com estatísticas
└── README.md           # Este arquivo
```

---

## 🎯 Projetos Incluídos

### 1. **Metas** (Gerenciamento de Orçamentos)
- **Descrição**: Sistema completo de gerenciamento de metas financeiras (gastos e investimentos)
- **Portas**: Configurado para rodar na porta 3004
- **Páginas**:
  - `/` - Listagem de metas com donut chart
  - `/detalhes-meta` - Detalhes de uma meta específica
  - `/editar-meta` - Formulário de edição de metas
  - `/gerenciar-metas` - Gerenciamento avançado
- **Componentes**: 6 atoms, 5 molecules, 4 organisms, 4 templates
- **Mock Data**: 6 metas (4 gastos + 2 investimentos), 5 transações

### 2. **Upload** (Upload de Arquivos)
- **Descrição**: Interface de upload de arquivos com drag & drop
- **Portas**: Configurado para rodar na porta 3001
- **Páginas**:
  - `/` - Upload de arquivos
- **Componentes**: Atomic Design completo

### 3. **Preview Upload** (Classificação de Arquivos)
- **Descrição**: Preview e classificação de arquivos enviados
- **Portas**: Configurado para rodar na porta 3003
- **Páginas**:
  - `/` - Preview com modal de classificação
- **Componentes**: Atomic Design completo

### 4. **Dashboard** (Estatísticas)
- **Descrição**: Dashboard com estatísticas e visualizações
- **Portas**: Configurado para rodar na porta 3000
- **Páginas**:
  - `/` - Dashboard principal
- **Componentes**: Atomic Design completo

---

## 🚀 Como Usar

### 1. Instalação Individual

Para rodar cada projeto separadamente:

```bash
cd metas
npm install
npm run dev
```

O projeto rodará em `http://localhost:3004` (ou porta configurada)

### 2. Integração ao Projeto Principal

#### Opção A: Copiar Componentes
```bash
# Copiar componentes para seu projeto
cp -r metas/src/components/* seu-projeto/src/components/
cp -r metas/src/types/* seu-projeto/src/types/
cp -r metas/src/lib/* seu-projeto/src/lib/
```

#### Opção B: Integrar como Rotas
```bash
# Copiar páginas para seu projeto Next.js
cp -r metas/app/* seu-projeto/app/metas/
```

---

## 📦 Estrutura de Cada Projeto

Todos seguem o padrão Atomic Design:

```
projeto/
├── app/                     # Next.js App Router
│   ├── layout.tsx
│   ├── globals.css
│   └── page.tsx
├── src/
│   ├── types/               # TypeScript interfaces
│   │   └── index.ts
│   ├── lib/                 # Constants e utils
│   │   └── constants.ts
│   └── components/          # Atomic Design
│       ├── atoms/
│       ├── molecules/
│       ├── organisms/
│       └── templates/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

---

## 🛠️ Dependências

Todos os projetos usam:

- **Next.js**: 14.2.18
- **React**: 18.3.1
- **TypeScript**: 5
- **Tailwind CSS**: 3.4.17

---

## 🎨 Design System

Todos os projetos seguem:

- **Atomic Design**: Atoms → Molecules → Organisms → Templates → Pages
- **Tailwind CSS**: Utilitário-first, mobile-first
- **TypeScript**: 100% tipado (zero `any`)
- **Responsivo**: Mobile-first design

---

## 📝 Adaptação para Seu Projeto

### 1. Ajustar Portas

Se precisar mudar as portas, edite `package.json`:

```json
{
  "scripts": {
    "dev": "next dev -p 3000"  // Mude aqui
  }
}
```

### 2. Integrar Rotas

Para integrar as rotas no seu projeto:

```bash
# Exemplo: Integrar metas como subrotas
cp -r metas/app/* seu-projeto/app/metas/
```

### 3. Compartilhar Componentes

Os componentes são reutilizáveis. Você pode:

1. Copiar atoms/molecules para uma biblioteca compartilhada
2. Importar onde necessário
3. Ajustar tipos conforme seu backend

### 4. Conectar Backend

Substitua os mock data em `src/lib/constants.ts` por chamadas de API:

```typescript
// Antes (mock)
import { mockGoals } from '../lib/constants';

// Depois (API)
const response = await fetch('/api/goals');
const goals = await response.json();
```

---

## 🔗 Navegação Entre Projetos

Para criar navegação entre os projetos no seu sistema principal:

```typescript
// components/Navigation.tsx
import Link from 'next/link';

export default function Navigation() {
  return (
    <nav>
      <Link href="/metas">Metas</Link>
      <Link href="/upload">Upload</Link>
      <Link href="/preview-upload">Preview</Link>
      <Link href="/dashboard">Dashboard</Link>
    </nav>
  );
}
```

---

## ✅ Checklist de Integração

- [ ] Instalar dependências (`npm install` em cada projeto)
- [ ] Testar localmente cada projeto
- [ ] Ajustar portas se necessário
- [ ] Copiar componentes para projeto principal
- [ ] Copiar rotas para projeto principal
- [ ] Ajustar imports (caminhos relativos)
- [ ] Conectar com backend/API
- [ ] Testar navegação entre páginas
- [ ] Ajustar estilos (globals.css)
- [ ] Configurar variáveis de ambiente

---

## 📖 Documentação Adicional

Cada projeto tem:
- Mock data em `src/lib/constants.ts`
- Tipos TypeScript em `src/types/index.ts`
- Componentes documentados com interfaces

Para mais detalhes, veja:
- `projects/[nome]/docs/README.md` no projeto original
- Código-fonte dos componentes (auto-documentados)

---

## 🎯 Próximos Passos

1. **Testar localmente**: Rode `npm run dev` em cada projeto
2. **Analisar estrutura**: Veja como os componentes se relacionam
3. **Planejar integração**: Defina como integrar ao seu projeto
4. **Adaptar estilos**: Ajuste cores/espaçamentos conforme seu design system
5. **Conectar backend**: Substitua mock data por API calls

---

**Data de Exportação**: 05/02/2026  
**Versão**: 1.0  
**Projetos**: Metas, Upload, Preview Upload, Dashboard
