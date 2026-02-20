"use client"

import React, { useState, useCallback } from "react"
import { fetchWithAuth } from "@/core/utils/api-client"
import { API_CONFIG } from "@/core/config/api.config"
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
import { Badge } from "@/components/ui/badge"
import { Plus, Edit, Key, Trash2, Copy, RefreshCw } from "lucide-react"
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
  created_at?: string
}

const API_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`

function generatePassword(length = 12): string {
  const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%"
  let result = ""
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

export default function ContasPage() {
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [senhaModalOpen, setSenhaModalOpen] = useState(false)
  const [nome, setNome] = useState("")
  const [email, setEmail] = useState("")
  const [senha, setSenha] = useState("")
  const [role, setRole] = useState("user")
  const [editingUsuario, setEditingUsuario] = useState<Usuario | null>(null)
  const [senhaUsuarioId, setSenhaUsuarioId] = useState<number | null>(null)
  const [novaSenha, setNovaSenha] = useState("")
  const [error, setError] = useState<string | null>(null)

  const fetchUsuarios = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetchWithAuth(`${API_URL}/users/`)
      if (response.ok) {
        const data = await response.json()
        setUsuarios(data.users || [])
      } else {
        setError(`Erro ${response.status}: ${response.statusText}`)
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err)
      setError(msg)
      console.error("Erro ao buscar usuários:", err)
    } finally {
      setLoading(false)
    }
  }, [])

  React.useEffect(() => {
    fetchUsuarios()
  }, [fetchUsuarios])

  const handleAdd = () => {
    setNome("")
    setEmail("")
    setSenha("")
    setRole("user")
    setEditingUsuario(null)
    setError(null)
    setModalOpen(true)
  }

  const handleEdit = (usuario: Usuario) => {
    setEditingUsuario(usuario)
    setNome(usuario.nome)
    setEmail(usuario.email)
    setSenha("")
    setRole(usuario.role)
    setError(null)
    setModalOpen(true)
  }

  const handleGeneratePassword = () => {
    setSenha(generatePassword())
  }

  const handleGenerateNovaSenha = () => {
    setNovaSenha(generatePassword())
  }

  const handleSave = async () => {
    if (!nome.trim() || !email.trim()) {
      setError("Nome e email são obrigatórios")
      return
    }
    if (!editingUsuario && !senha.trim()) {
      setError("Senha é obrigatória para novos usuários")
      return
    }

    setError(null)
    try {
      const url = editingUsuario
        ? `${API_URL}/users/${editingUsuario.id}`
        : `${API_URL}/users/`
      const method = editingUsuario ? "PUT" : "POST"
      const body: Record<string, unknown> = {
        nome: nome.trim(),
        email: email.trim(),
        role,
      }
      if (senha.trim()) (body as Record<string, string>).password = senha.trim()

      const response = await fetchWithAuth(url, {
        method,
        body: JSON.stringify(body),
      })

      if (response.ok) {
        fetchUsuarios()
        setModalOpen(false)
      } else {
        const errData = await response.json()
        setError(errData.detail || errData.error || "Erro ao salvar")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao salvar")
    }
  }

  const handleDelete = async (id: number) => {
    if (id === 1) {
      setError("Não é possível desativar o usuário administrador principal")
      return
    }
    if (!confirm("Deseja realmente desativar este usuário?")) return

    try {
      const response = await fetchWithAuth(`${API_URL}/users/${id}`, {
        method: "DELETE",
      })
      if (response.ok) {
        fetchUsuarios()
      } else {
        const errData = await response.json()
        alert(errData.detail || errData.error || "Erro ao desativar")
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro ao desativar")
    }
  }

  const handleAlterarSenha = (id: number) => {
    setSenhaUsuarioId(id)
    setNovaSenha("")
    setError(null)
    setSenhaModalOpen(true)
  }

  const handleSalvarNovaSenha = async () => {
    if (!novaSenha.trim()) {
      setError("Digite a nova senha")
      return
    }
    if (novaSenha.length < 6) {
      setError("A senha deve ter no mínimo 6 caracteres")
      return
    }
    if (!senhaUsuarioId) return

    setError(null)
    try {
      const response = await fetchWithAuth(`${API_URL}/users/${senhaUsuarioId}`, {
        method: "PUT",
        body: JSON.stringify({ password: novaSenha }),
      })
      if (response.ok) {
        setSenhaModalOpen(false)
      } else {
        const errData = await response.json()
        setError(errData.detail || errData.error || "Erro ao alterar senha")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao alterar senha")
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    alert("Copiado!")
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Contas</h1>
        <p className="text-muted-foreground">Gerencie usuários do sistema</p>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Usuários</CardTitle>
            <CardDescription>{usuarios.length} usuário(s) cadastrado(s)</CardDescription>
          </div>
          <Button onClick={handleAdd}>
            <Plus className="mr-2 h-4 w-4" />
            Novo Usuário
          </Button>
        </CardHeader>
        <CardContent>
          {error && !modalOpen && (
            <div className="mb-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              {error}
              <Button variant="ghost" size="sm" className="ml-2" onClick={fetchUsuarios}>
                <RefreshCw className="mr-1 h-3 w-3" />
                Tentar novamente
              </Button>
            </div>
          )}
          {loading ? (
            <div className="py-8 text-center text-muted-foreground">Carregando...</div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nome</TableHead>
                    <TableHead>E-mail</TableHead>
                    <TableHead>Perfil</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-[140px]">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {usuarios.map((u) => (
                    <TableRow key={u.id}>
                      <TableCell className="font-medium">{u.nome}</TableCell>
                      <TableCell>{u.email}</TableCell>
                      <TableCell>
                        <Badge variant={u.role === "admin" ? "default" : "secondary"}>
                          {u.role === "admin" ? "Admin" : "Usuário"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={u.ativo ? "default" : "destructive"}>
                          {u.ativo ? "Ativo" : "Inativo"}
                        </Badge>
                      </TableCell>
                      <TableCell className="flex gap-1">
                        <Button variant="ghost" size="icon" onClick={() => handleEdit(u)} title="Editar">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => handleAlterarSenha(u.id)} title="Alterar Senha">
                          <Key className="h-4 w-4" />
                        </Button>
                        {u.id !== 1 && (
                          <Button variant="ghost" size="icon" onClick={() => handleDelete(u.id)} title="Desativar">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal Adicionar/Editar */}
      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingUsuario ? "Editar" : "Adicionar"} Usuário</DialogTitle>
            <DialogDescription>
              {editingUsuario ? "Altere" : "Insira"} os dados do usuário
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {error && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">{error}</div>
            )}
            <div className="space-y-2">
              <Label htmlFor="nome">Nome Completo</Label>
              <Input id="nome" value={nome} onChange={(e) => setNome(e.target.value)} placeholder="Nome" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">E-mail</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="email@exemplo.com" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="senha">
                {editingUsuario ? "Nova Senha (deixe em branco para manter)" : "Senha"}
              </Label>
              <div className="flex gap-2">
                <Input
                  id="senha"
                  type="text"
                  value={senha}
                  onChange={(e) => setSenha(e.target.value)}
                  placeholder={editingUsuario ? "Deixe em branco para não alterar" : "Digite a senha"}
                />
                <Button type="button" variant="outline" size="icon" onClick={handleGeneratePassword} title="Gerar senha">
                  <RefreshCw className="h-4 w-4" />
                </Button>
                {senha && (
                  <Button type="button" variant="outline" size="icon" onClick={() => copyToClipboard(senha)} title="Copiar">
                    <Copy className="h-4 w-4" />
                  </Button>
                )}
              </div>
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
            <Button variant="outline" onClick={() => setModalOpen(false)}>Cancelar</Button>
            <Button onClick={handleSave}>{editingUsuario ? "Salvar" : "Adicionar"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal Alterar Senha */}
      <Dialog open={senhaModalOpen} onOpenChange={setSenhaModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Alterar Senha</DialogTitle>
            <DialogDescription>Digite a nova senha para o usuário</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {error && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">{error}</div>
            )}
            <div className="space-y-2">
              <Label htmlFor="novaSenha">Nova Senha</Label>
              <div className="flex gap-2">
                <Input
                  id="novaSenha"
                  type="text"
                  value={novaSenha}
                  onChange={(e) => setNovaSenha(e.target.value)}
                  placeholder="Mínimo 6 caracteres"
                />
                <Button type="button" variant="outline" size="icon" onClick={handleGenerateNovaSenha} title="Gerar senha">
                  <RefreshCw className="h-4 w-4" />
                </Button>
                {novaSenha && (
                  <Button type="button" variant="outline" size="icon" onClick={() => copyToClipboard(novaSenha)} title="Copiar">
                    <Copy className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSenhaModalOpen(false)}>Cancelar</Button>
            <Button onClick={handleSalvarNovaSenha}>Alterar Senha</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
