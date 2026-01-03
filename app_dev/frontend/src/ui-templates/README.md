# UI Templates - shadcn/ui

Esta pasta armazena diferentes templates do shadcn/ui para referência e reutilização.

## Estrutura

- `dashboard-01/` - Template completo de dashboard com cards, gráficos e tabelas
- `sidebar-07/` - Sidebar colapsável com menu de navegação elegante

## Como usar

1. Navegue até a pasta do template desejado
2. Copie os componentes necessários para `src/components/`
3. Ajuste imports e personalize conforme necessário

## Templates disponíveis

### dashboard-01
- **Componentes:**
  - `app-sidebar.tsx` - Sidebar expandida
  - `chart-area-interactive.tsx` - Gráfico de área interativo
  - `data-table.tsx` - Tabela de dados com ordenação
  - `section-cards.tsx` - Cards de métricas
  - `site-header.tsx` - Cabeçalho do site
  - `nav-*.tsx` - Componentes de navegação

- **Características:**
  - Layout completo de dashboard
  - 4 cards de métricas principais
  - Gráfico de área com toggle de períodos
  - Tabela de dados paginada

### sidebar-07
- **Componentes:**
  - `app-sidebar.tsx` - Sidebar colapsável (apenas ícones)
  - `nav-main.tsx` - Navegação principal atualizada
  - `nav-user.tsx` - Menu de usuário com dropdown
  - `team-switcher.tsx` - Seletor de times/organizações

- **Características:**
  - Sidebar colapsável (`collapsible="icon"`)
  - Expande ao passar mouse (hover)
  - Design minimalista quando colapsada
  - Totalmente acessível

## Instalando novos templates

```bash
# Ver templates disponíveis
npx shadcn@latest add

# Instalar template específico
npx shadcn@latest add dashboard-02

# Depois de instalar, copiar para ui-templates
cp -r src/components/[novos-componentes] src/ui-templates/nome-template/
```

## Atualmente em uso

O projeto está usando uma combinação:
- **Sidebar:** sidebar-07 (colapsável, apenas ícones)
- **Layout:** dashboard-01 (cards, gráficos, tabelas)
- **Personalizado:** FinUp DEV branding e cores
