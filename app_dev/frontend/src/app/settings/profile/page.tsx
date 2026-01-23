"use client"

import * as React from "react"
import DashboardLayout from "@/components/dashboard-layout"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { User, Mail, Lock } from "lucide-react"
import { useAuth } from "@/contexts/AuthContext"
import { useRouter } from "next/navigation"

export default function ProfilePage() {
  const { user, token, isAuthenticated, loadUser } = useAuth()
  const router = useRouter()
  
  const [nome, setNome] = React.useState("")
  const [email, setEmail] = React.useState("")
  const [saving, setSaving] = React.useState(false)
  
  // Campos de senha
  const [currentPassword, setCurrentPassword] = React.useState("")
  const [newPassword, setNewPassword] = React.useState("")
  const [confirmPassword, setConfirmPassword] = React.useState("")
  const [changingPassword, setChangingPassword] = React.useState(false)

  // Carregar dados do usuário quando autenticado
  React.useEffect(() => {
    // TODO: Descomentar após implementar endpoints de perfil
    // if (!isAuthenticated) {
    //   router.push('/login')
    //   return
    // }
    
    if (user) {
      setNome(user.nome)
      setEmail(user.email)
    } else {
      // Fallback: dados mockados enquanto não há autenticação obrigatória
      setNome("Emanuel")
      setEmail("usuario@email.com")
    }
  }, [user, isAuthenticated, router])

  const handleSave = async () => {
    if (!token) {
      alert("Você precisa estar logado para atualizar o perfil")
      return
    }

    setSaving(true)
    try {
      const response = await fetch('/api/v1/auth/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ nome, email }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Erro ao atualizar perfil')
      }

      // Recarregar dados do usuário
      await loadUser()
      alert("Perfil atualizado com sucesso!")
    } catch (error) {
      console.error('Erro ao salvar perfil:', error)
      alert(error instanceof Error ? error.message : 'Erro ao atualizar perfil')
    } finally {
      setSaving(false)
    }
  }

  const handleChangePassword = async () => {
    if (!token) {
      alert("Você precisa estar logado para alterar a senha")
      return
    }

    // Validar senhas
    if (!currentPassword || !newPassword || !confirmPassword) {
      alert("Preencha todos os campos de senha")
      return
    }

    if (newPassword !== confirmPassword) {
      alert("Nova senha e confirmação não coincidem")
      return
    }

    if (newPassword.length < 6) {
      alert("Nova senha deve ter pelo menos 6 caracteres")
      return
    }

    setChangingPassword(true)
    try {
      const response = await fetch('/api/v1/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Erro ao alterar senha')
      }

      // Limpar campos
      setCurrentPassword("")
      setNewPassword("")
      setConfirmPassword("")
      alert("Senha alterada com sucesso!")
    } catch (error) {
      console.error('Erro ao alterar senha:', error)
      alert(error instanceof Error ? error.message : 'Erro ao alterar senha')
    } finally {
      setChangingPassword(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="flex flex-1 flex-col gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Perfil</h1>
          <p className="text-muted-foreground">
            Gerencie suas informações pessoais e de conta
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" />
                Informações Pessoais
              </CardTitle>
              <CardDescription>
                Atualize suas informações básicas de perfil
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="nome">Nome Completo</Label>
                <Input
                  id="nome"
                  value={nome}
                  onChange={(e) => setNome(e.target.value)}
                  placeholder="Seu nome completo"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">E-mail</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="seu@email.com"
                />
              </div>
              <Button onClick={handleSave} disabled={saving}>
                {saving ? "Salvando..." : "Salvar Alterações"}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="w-5 h-5" />
                Segurança
              </CardTitle>
              <CardDescription>
                Altere sua senha e configurações de segurança
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="current-password">Senha Atual</Label>
                <Input
                  id="current-password"
                  type="password"
                  placeholder="Digite sua senha atual"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new-password">Nova Senha</Label>
                <Input
                  id="new-password"
                  type="password"
                  placeholder="Digite sua nova senha"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm-password">Confirmar Nova Senha</Label>
                <Input
                  id="confirm-password"
                  type="password"
                  placeholder="Confirme sua nova senha"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>
              <Button 
                variant="outline" 
                onClick={handleChangePassword}
                disabled={changingPassword}
              >
                {changingPassword ? "Alterando..." : "Alterar Senha"}
              </Button>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Preferências</CardTitle>
            <CardDescription>
              Configure suas preferências de uso do sistema
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Notificações por E-mail</p>
                <p className="text-sm text-muted-foreground">
                  Receba notificações sobre novas transações e alertas
                </p>
              </div>
              <input type="checkbox" className="w-4 h-4" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Alertas de Gastos</p>
                <p className="text-sm text-muted-foreground">
                  Receba alertas quando ultrapassar o orçamento mensal
                </p>
              </div>
              <input type="checkbox" className="w-4 h-4" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Modo Escuro</p>
                <p className="text-sm text-muted-foreground">
                  Ativar tema escuro para o sistema
                </p>
              </div>
              <input type="checkbox" className="w-4 h-4" />
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
