"use client"

import * as React from "react"
import DashboardLayout from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Plus, Edit, Eye, EyeOff, Key, Trash } from "lucide-react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface Usuario {
  id: number
  nome: string
  email: string
  role: string
  ativo: number
  created_at: string
}

export default function AdminPage() {
  const [usuarios, setUsuarios] = React.useState<Usuario[]>([])
  const [loading, setLoading] = React.useState(true)
  const [modalOpen, setModalOpen] = React.useState(false)
  const [senhaModalOpen, setSenhaModalOpen] = React.useState(false)
  const [nome, setNome] = React.useState('')
  const [email, setEmail] = React.useState('')
  const [senha, setSenha] = React.useState('')
  const [role, setRole] = React.useState('user')
  const [editingUsuario, setEditingUsuario] = React.useState<Usuario | null>(null)
  const [senhaUsuarioId, setSenhaUsuarioId] = React.useState<number | null>(null)
  const [novaSenha, setNovaSenha] = React.useState('')
  const [mostrarSenha, setMostrarSenha] = React.useState(false)

  React.useEffect(() => {
    fetchUsuarios()
  }, [])

  const fetchUsuarios = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/users')
      if (response.ok) {
        const data = await response.json()
        setUsuarios(data.users || [])
      }
    } catch (error) {
      console.error('Erro ao buscar usuários:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setNome('')
    setEmail('')
    setSenha('')
    setRole('user')
    setEditingUsuario(null)
    setModalOpen(true)
  }

  const handleEdit = (usuario: Usuario) => {
    console.log('Editando usuário:', usuario)
    setEditingUsuario(usuario)
    setNome(usuario.nome)
    setEmail(usuario.email)
    setSenha('')
    setRole(usuario.role)
    setModalOpen(true)
  }

  const handleSave = async () => {
    console.log('Salvando usuário. Modo edição:', !!editingUsuario)
    
    if (!nome.trim() || !email.trim()) {
      alert('Nome e email são obrigatórios')
      return
    }

    if (!editingUsuario && !senha.trim()) {
      alert('Senha é obrigatória para novos usuários')
      return
    }

    try {
      const url = editingUsuario && editingUsuario.id 
        ? `/api/users/${editingUsuario.id}` 
        : '/api/users'
      const method = editingUsuario && editingUsuario.id ? 'PUT' : 'POST'
      
      console.log('URL:', url)
      console.log('Method:', method)
      
      const body: any = {
        nome: nome.trim(),
        email: email.trim(),
        role: role
      }
      
      // Só envia senha se for novo usuário ou se foi preenchida
      if (senha.trim()) {
        body.password = senha.trim()
      }
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      if (response.ok) {
        fetchUsuarios()
        setModalOpen(false)
      } else {
        try {
          const errorData = await response.json()
          console.error('Erro do servidor:', errorData)
          let errorMsg = 'Erro desconhecido'
          if (typeof errorData === 'string') {
            errorMsg = errorData
          } else if (errorData.detail) {
            errorMsg = errorData.detail
          } else if (errorData.error) {
            errorMsg = errorData.error
          } else if (errorData.message) {
            errorMsg = errorData.message
          } else {
            errorMsg = JSON.stringify(errorData)
          }
          alert(`Erro ao salvar: ${errorMsg}`)
        } catch (parseError) {
          alert(`Erro ao salvar (Status ${response.status})`)
        }
      }
    } catch (error) {
      console.error('Erro ao salvar usuário:', error)
      const errorMsg = error instanceof Error ? error.message : String(error)
      alert(`Erro ao salvar usuário: ${errorMsg}`)
    }
  }

  const handleDelete = async (id: number) => {
    if (id === 1) {
      alert('Não é possível deletar o usuário administrador principal')
      return
    }

    if (!confirm('Deseja realmente desativar este usuário?')) return

    try {
      const response = await fetch(`/api/users/${id}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        fetchUsuarios()
      } else {
        const errorData = await response.json()
        alert(errorData.error || 'Erro ao deletar usuário')
      }
    } catch (error) {
      console.error('Erro ao deletar usuário:', error)
      alert('Erro ao deletar usuário')
    }
  }

  const handleAlterarSenha = (id: number) => {
    setSenhaUsuarioId(id)
    setNovaSenha('')
    setMostrarSenha(false)
    setSenhaModalOpen(true)
  }

  const handleSalvarNovaSenha = async () => {
    if (!novaSenha.trim()) {
      alert('Digite a nova senha')
      return
    }

    if (novaSenha.length < 6) {
      alert('A senha deve ter no mínimo 6 caracteres')
      return
    }

    try {
      const response = await fetch(`/api/users/${senhaUsuarioId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: novaSenha })
      })

      if (response.ok) {
        alert('Senha alterada com sucesso!')
        setSenhaModalOpen(false)
      } else {
        const errorData = await response.json()
        alert(errorData.error || errorData.detail || 'Erro ao alterar senha')
      }
    } catch (error) {
      console.error('Erro ao alterar senha:', error)
      alert('Erro ao alterar senha')
    }
  }

  return (
    <DashboardLayout>
      <div className="flex flex-1 flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Administração</h1>
            <p className="text-muted-foreground">
              Gerencie usuários do sistema
            </p>
          </div>
        </div>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Usuários</CardTitle>
              <CardDescription>
                {usuarios.length} usuário(s) cadastrado(s)
              </CardDescription>
            </div>
            <Button onClick={handleAdd}>
              <Plus className="mr-2 h-4 w-4" />
              Novo Usuário
            </Button>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">Carregando...</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nome Completo</TableHead>
                    <TableHead>E-mail</TableHead>
                    <TableHead>Perfil</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-[150px]">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {usuarios.map((usuario) => (
                    <TableRow key={usuario.id}>
                      <TableCell className="font-medium">{usuario.nome}</TableCell>
                      <TableCell>{usuario.email}</TableCell>
                      <TableCell>
                        <span className={`text-sm px-2 py-1 rounded ${
                          usuario.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {usuario.role === 'admin' ? 'Administrador' : 'Usuário'}
                        </span>
                      </TableCell>
                      <TableCell>
                        <span className={`text-sm px-2 py-1 rounded ${
                          usuario.ativo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {usuario.ativo ? 'Ativo' : 'Inativo'}
                        </span>
                      </TableCell>
                      <TableCell className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleEdit(usuario)}
                          title="Editar"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleAlterarSenha(usuario.id)}
                          title="Alterar Senha"
                        >
                          <Key className="h-4 w-4" />
                        </Button>
                        {usuario.id !== 1 && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDelete(usuario.id)}
                            title="Desativar"
                          >
                            <Trash className="h-4 w-4" />
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Modal de Adicionar/Editar Usuário */}
        <Dialog open={modalOpen} onOpenChange={setModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingUsuario ? 'Editar' : 'Adicionar'} Usuário
              </DialogTitle>
              <DialogDescription>
                {editingUsuario ? 'Altere' : 'Insira'} os dados do usuário
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="nome">Nome Completo</Label>
                <Input
                  id="nome"
                  value={nome}
                  onChange={(e) => setNome(e.target.value)}
                  placeholder="Nome do usuário"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">E-mail</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="email@exemplo.com"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="senha">
                  {editingUsuario ? 'Nova Senha (deixe em branco para manter)' : 'Senha'}
                </Label>
                <Input
                  id="senha"
                  type="password"
                  value={senha}
                  onChange={(e) => setSenha(e.target.value)}
                  placeholder={editingUsuario ? "Deixe em branco para não alterar" : "Digite a senha"}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="role">Perfil</Label>
                <Select value={role} onValueChange={setRole}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="user">Usuário</SelectItem>
                    <SelectItem value="admin">Administrador</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setModalOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSave}>
                {editingUsuario ? 'Salvar' : 'Adicionar'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Modal de Alterar Senha */}
        <Dialog open={senhaModalOpen} onOpenChange={setSenhaModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Alterar Senha</DialogTitle>
              <DialogDescription>
                Digite a nova senha para o usuário
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="novaSenha">Nova Senha</Label>
                <div className="relative">
                  <Input
                    id="novaSenha"
                    type={mostrarSenha ? "text" : "password"}
                    value={novaSenha}
                    onChange={(e) => setNovaSenha(e.target.value)}
                    placeholder="Digite a nova senha (mínimo 6 caracteres)"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0"
                    onClick={() => setMostrarSenha(!mostrarSenha)}
                  >
                    {mostrarSenha ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setSenhaModalOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSalvarNovaSenha}>
                Alterar Senha
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  )
}
