"use client"

import * as React from "react"
import {
  BarChart3,
  CreditCard,
  DollarSign,
  Home,
  PieChart,
  Settings,
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
      isActive: true,
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
          title: "Categorias",
          url: "/settings/categories",
        },
        {
          title: "Backup",
          url: "/settings/backup",
        },
      ],
    },
  ],
  projects: [
    {
      name: "Upload de Arquivos",
      url: "/upload",
      icon: Upload,
    },
    {
      name: "Análise de Tendências",
      url: "/trends",
      icon: TrendingUp,
    },
    {
      name: "Orçamento",
      url: "/budget",
      icon: DollarSign,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <TeamSwitcher teams={data.teams} />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavProjects projects={data.projects} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
