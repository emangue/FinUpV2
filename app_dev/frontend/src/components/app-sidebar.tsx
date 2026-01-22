"use client"

import * as React from "react"
import { useAuth } from '@/contexts/AuthContext'
import { useState, useEffect } from 'react'
import {
  BarChart3,
  CreditCard,
  DollarSign,
  Home,
  LineChart,
  PieChart,
  Settings,
  Shield,
  TrendingUp,
  Upload,
  Wallet,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavProjects } from "@/components/nav-projects"
import { NavUser } from "@/components/nav-user"
import { TeamSwitcher } from "@/components/team-switcher"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar"

// Data para sidebar financeira
const data = {
  user: {
    name: "Emanuel",
    email: "emanuel@finanças.com",
    avatar: "/avatars/user.jpg",
  },
  teams: [
    {
      name: "Sistema Financeiro",
      logo: Wallet,
      plan: "Personal",
    },
  ],
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: Home,
      items: [
        {
          title: "Visão Geral",
          url: "/dashboard",
        },
        {
          title: "Métricas",
          url: "/dashboard/metrics",
        },
      ],
    },
    {
      title: "Transações",
      url: "/transactions",
      icon: CreditCard,
      items: [
        {
          title: "Todas",
          url: "/transactions?tab=all",
        },
        {
          title: "Receitas",
          url: "/transactions?tab=receitas",
        },
        {
          title: "Despesas",
          url: "/transactions?tab=despesas",
        },
        {
          title: "Migrações",
          url: "/transactions/migracoes",
        },
      ],
    },
    {
      title: "Orçamento",
      url: "/budget",
      icon: DollarSign,
      items: [
        {
          title: "Meta Geral",
          url: "/budget",
        },
        {
          title: "Meta Simples",
          url: "/budget/simples",
        },
        {
          title: "Meta Detalhada",
          url: "/budget/detalhada",
        },
        {
          title: "Planejamento",
          url: "/budget/planning",
        },
        {
          title: "Configurações",
          url: "/budget/configuracoes",
        },
      ],
    },
    {
      title: "Investimentos",
      url: "/investimentos",
      icon: LineChart,
      items: [
        {
          title: "Dashboard",
          url: "/investimentos",
        },
      ],
    },
    {
      title: "Relatórios",
      url: "/reports",
      icon: BarChart3,
      items: [
        {
          title: "Mensal",
          url: "/reports/monthly",
        },
        {
          title: "Anual",
          url: "/reports/yearly",
        },
        {
          title: "Categorias",
          url: "/reports/categories",
        },
      ],
    },
    {
      title: "Configurações",
      url: "/settings",
      icon: Settings,
      items: [
        {
          title: "Perfil",
          url: "/settings/profile",
        },
        {
          title: "Gestão de Cartões",
          url: "/settings/cartoes",
        },
        {
          title: "Gestão de Categorias",
          url: "/settings/categorias",
        },
        {
          title: "Gestão de Grupos",
          url: "/settings/grupos",
        },
        {
          title: "Regras de Exclusão",
          url: "/settings/exclusoes",
        },
      ],
    },
    {
      title: "Administração",
      url: "/admin",
      icon: Shield,
      items: [
        {
          title: "Contas",
          url: "/settings/admin",
        },
        {
          title: "Visibilidade de Telas",
          url: "/settings/screens",
        },
        {
          title: "Gestão de Bancos",
          url: "/settings/bancos",
        },
        {
          title: "Regras Genéricas",
          url: "/settings/categorias-genericas",
        },
        {
          title: "Backup",
          url: "/settings/backup",
        },
      ],
    },
  ],
  navSecondary: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: Home,
      status: 'P' as const,
      items: [
        {
          title: "Visão Geral",
          url: "/dashboard",
          status: 'P' as const,
        },
        {
          title: "Métricas",
          url: "/dashboard/metrics",
          status: 'P' as const,
        },
      ],
    },
    {
      title: "Transações",
      url: "/transactions",
      icon: CreditCard,
      status: 'P' as const,
      items: [
        {
          title: "Todas",
          url: "/transactions?tab=all",
          status: 'P' as const,
        },
        {
          title: "Receitas",
          url: "/transactions?tab=receitas",
          status: 'P' as const,
        },
        {
          title: "Despesas",
          url: "/transactions?tab=despesas",
          status: 'P' as const,
        },
        {
          title: "Migrações",
          url: "/transactions/migracoes",
          status: 'A' as const,
        },
      ],
    },
    {
      title: "Relatórios",
      url: "/reports",
      icon: BarChart3,
      status: 'A' as const,
      items: [
        {
          title: "Mensal",
          url: "/reports/monthly",
          status: 'A' as const,
        },
        {
          title: "Anual",
          url: "/reports/yearly",
          status: 'A' as const,
        },
        {
          title: "Categorias",
          url: "/reports/categories",
          status: 'A' as const,
        },
      ],
    },
    {
      title: "Configurações",
      url: "/settings",
      icon: Settings,
      status: 'P' as const,
      items: [
        {
          title: "Perfil",
          url: "/settings/profile",
          status: 'P' as const,
        },
        {
          title: "Gestão de Cartões",
          url: "/settings/cartoes",
          status: 'P' as const,
        },
        {
          title: "Gestão de Categorias",
          url: "/settings/categorias",
          status: 'P' as const,
        },
        {
          title: "Gestão de Grupos",
          url: "/settings/grupos",
          status: 'P' as const,
        },
        {
          title: "Regras de Exclusão",
          url: "/settings/exclusoes",
          status: 'P' as const,
        },
      ],
    },
    {
      title: "Administração",
      url: "/admin",
      icon: Shield,
      status: 'A' as const,
      items: [
        {
          title: "Contas",
          url: "/settings/admin",
          status: 'A' as const,
        },
        {
          title: "Visibilidade de Telas",
          url: "/settings/screens",
          status: 'A' as const,
        },
        {
          title: "Gestão de Bancos",
          url: "/settings/bancos",
          status: 'A' as const,
        },
        {
          title: "Regras Genéricas",
          url: "/settings/categorias-genericas",
          status: 'A' as const,
        },
        {
          title: "Backup",
          url: "/settings/backup",
          status: 'A' as const,
        },
      ],
    },
  ],
  projects: [
    {
      name: "Upload de Arquivos",
      url: "/upload",
      icon: Upload,
      status: 'P' as const,
    },
    {
      name: "Análise de Tendências",
      url: "/trends",
      icon: TrendingUp,
      status: 'D' as const,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { user } = useAuth()
  const [isAdmin, setIsAdmin] = useState(false)
  const [screenStatuses, setScreenStatuses] = React.useState<Record<string, 'P' | 'A' | 'D'>>({})

  // Atualizar isAdmin apenas no cliente para evitar hydration mismatch
  useEffect(() => {
    setIsAdmin(user?.role === 'admin')
  }, [user])

  React.useEffect(() => {
    // ✅ FASE 3 - Buscar status com autenticação
    const loadScreenStatuses = async () => {
      try {
        const token = localStorage.getItem('authToken')
        if (!token) {
          console.log('[AppSidebar] Sem token, não carregando status de telas')
          return
        }

        const response = await fetch('http://localhost:8000/api/v1/screens/admin/all', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (!response.ok) {
          console.error('[AppSidebar] Erro ao carregar status:', response.status)
          return
        }

        const screens = await response.json()
        
        // Validar que é um array
        if (!Array.isArray(screens)) {
          console.error('[AppSidebar] Resposta não é um array:', screens)
          return
        }

        const statuses: Record<string, 'P' | 'A' | 'D'> = {}
        screens.forEach(screen => {
          statuses[screen.screen_key] = screen.status
        })
        setScreenStatuses(statuses)
      } catch (err) {
        console.error('[AppSidebar] Erro ao carregar status:', err)
      }
    }

    loadScreenStatuses()
  }, [])

  // Função para extrair screen_key da URL
  const getScreenKey = (url: string, isSubItem = false, parentUrl = '') => {
    if (isSubItem) {
      const parent = parentUrl.replace('/', '')
      const fullPath = url.split('?')[0]
      
      // Casos especiais
      if (fullPath === parentUrl) return `${parent}-geral`
      
      // Extrair última parte do path
      const lastSegment = fullPath.split('/').pop() || ''
      
      // Mapear nome do segmento para screen_key
      const segmentMap: Record<string, string> = {
        'simples': 'simples',
        'detalhada': 'detalhada',
        'planning': 'planning',
        'configuracoes': 'configuracoes',
        'monthly': 'monthly',
        'yearly': 'yearly',
        'categories': 'categories',
        'profile': 'profile',
        'cartoes': 'cartoes',
        'categorias': 'categorias',
        'grupos': 'grupos',
        'exclusoes': 'exclusoes',
        'admin': 'contas',
        'bancos': 'bancos',
        'backup': 'backup',
        'screens': 'screens',
        'metrics': 'metrics',
        'migracoes': 'migracoes',
        'categorias-genericas': 'categorias-genericas'
      }
      
      const mapped = segmentMap[lastSegment] || lastSegment
      
      // Tratar query params (ex: ?tab=all, ?tab=cartoes)
      if (url.includes('?tab=')) {
        const tab = url.split('?tab=')[1]
        if (tab === 'all') return `${parent}-all`
        if (tab === 'receitas') return `${parent}-receitas`
        if (tab === 'despesas') return `${parent}-despesas`
        if (tab === 'cartoes') return `${parent}-cartoes`
      }
      
      return mapped === 'geral' ? `${parent}-geral` : `${parent}-${mapped}`
    }
    // Para items principais
    return url.replace('/', '')
  }

  // Atualizar items com status da API
  const navMainWithStatus = data.navMain.map(item => ({
    ...item,
    status: screenStatuses[getScreenKey(item.url)] || (item as any).status || 'P',
    items: item.items?.map(subItem => ({
      ...subItem,
      status: screenStatuses[getScreenKey(subItem.url, true, item.url)] || (subItem as any).status || 'P'
    }))
  }))
  
  // Filtrar items baseado em admin/status
  const filteredNavMain = navMainWithStatus
    .filter(item => {
      // Ocultar "Administração" completa se não for admin
      if (item.title === 'Administração' && !isAdmin) return false
      
      // Se item está como 'A' (Admin) e user não é admin, ocultar
      if (item.status === 'A' && !isAdmin) return false
      
      return true
    })
    .map(item => ({
      ...item,
      // Filtrar subitems também
      items: item.items?.filter(subItem => {
        // Ocultar subitems 'A' (Admin) se não for admin
        if (subItem.status === 'A' && !isAdmin) return false
        // Ocultar "Métricas" se não for admin (sempre dev/admin)
        if (subItem.title === 'Métricas' && !isAdmin) return false
        return true
      })
    }))

  // Atualizar projects com status da API
  const projectsWithStatus = data.projects.map(project => ({
    ...project,
    status: screenStatuses[getScreenKey(project.url)] || project.status
  }))
  
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <TeamSwitcher teams={data.teams} />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={filteredNavMain} isAdmin={isAdmin} />
        <NavProjects projects={projectsWithStatus} isAdmin={isAdmin} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
