"use client"

import * as React from "react"
import {
  BadgeCheck,
  Bell,
  ChevronsUpDown,
  CreditCard,
  LogIn,
  LogOut,
  Sparkles,
  User as UserIcon,
} from "lucide-react"
import { useRouter } from "next/navigation"

import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"
import { useAuth } from "@/contexts/AuthContext"

export function NavUser() {
  const { setOpen, setOpenMobile } = useSidebar()
  const { user, isAuthenticated, loading, logout } = useAuth()
  const router = useRouter()
  const [dropdownOpen, setDropdownOpen] = React.useState(false)
  const [userInitials, setUserInitials] = React.useState('')
  const [userName, setUserName] = React.useState('')
  const [userEmail, setUserEmail] = React.useState('')

  // Atualizar dados do usuário no client-side (evita hidratação diferente)
  React.useEffect(() => {
    if (user) {
      // Pega primeira letra de cada palavra (ex: "Administrador Sistema" -> "AS")
      const initials = user.nome
        .trim()
        .split(' ')
        .filter(n => n.length > 0)
        .map(n => n[0].toUpperCase())
        .join('')
        .slice(0, 2)
      
      setUserInitials(initials)
      setUserName(user.nome)
      setUserEmail(user.email)
    }
  }, [user])

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  const handleLogin = () => {
    router.push('/login')
  }

  const handleOpenChange = (open: boolean) => {
    setDropdownOpen(open)
    if (open) {
      setOpen(false)
      setOpenMobile(false)
    }
    // Notificar AppSidebar sobre estado do dropdown
    window.dispatchEvent(new CustomEvent('dropdown-state-change', { detail: { open } }))
  }

  // Durante carregamento, não mostrar nada (evita flash de "não autenticado")
  if (loading) {
    return null
  }

  // Se não autenticado, mostrar botão de login
  if (!isAuthenticated || !user) {
    return (
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton
            size="lg"
            onClick={handleLogin}
            className="hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
          >
            <Avatar className="h-8 w-8 rounded-lg bg-sidebar-accent">
              <AvatarFallback className="rounded-lg">
                <LogIn className="h-4 w-4" />
              </AvatarFallback>
            </Avatar>
            <div className="grid flex-1 text-left text-sm leading-tight">
              <span className="truncate font-medium">Fazer Login</span>
              <span className="truncate text-xs text-muted-foreground">
                Clique para entrar
              </span>
            </div>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    )
  }

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu modal={true} onOpenChange={handleOpenChange} open={dropdownOpen}>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
              onClick={(e) => e.stopPropagation()}
            >
              <Avatar className="h-8 w-8 rounded-lg">
                <AvatarFallback className="rounded-lg">{userInitials}</AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-medium">{userName}</span>
                <span className="truncate text-xs">{userEmail}</span>
              </div>
              <ChevronsUpDown className="ml-auto size-4" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg z-50"
            side="right"
            align="end"
            sideOffset={4}
          >
            <DropdownMenuLabel className="p-0 font-normal">
              <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                <Avatar className="h-8 w-8 rounded-lg">
                  <AvatarFallback className="rounded-lg">{userInitials}</AvatarFallback>
                </Avatar>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-medium">{userName}</span>
                  <span className="truncate text-xs">{userEmail}</span>
                </div>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem>
                <UserIcon />
                Perfil
              </DropdownMenuItem>
              <DropdownMenuItem>
                <BadgeCheck />
                Conta
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout} className="text-red-600 focus:text-red-600">
              <LogOut />
              Sair
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
