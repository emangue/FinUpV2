"use client"

import React, { useState, useCallback } from "react"
import useSWR from "swr"
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
import { Plus, Edit, Key, Trash2, Copy, RefreshCw, UserPlus, UserMinus } from "lucide-react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { UserStatsCell } from "@/components/UserStatsCell"
import { PurgeUserModal } from "@/components/PurgeUserModal"

interface Usuario {
  id: number
  nome: string
  email: string
  role: string
  ativo: number
  created_at?: string
}

const API_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`

const usersFetcher = (url: string) =>
  fetchWithAuth(url).then((r) => (r.ok ? r.json() : Promise.reject(new Error("Erro ao carregar usuários"))))

interface SystemStats {
  total_usuarios: number
  total_usuarios_ativos: number
  total_uploads: number
  total_transacoes: number
  total_planos: number
}

function generatePassword(length = 12): string {
  const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%"
  let result = ""
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

export default function ContasPage() {
  const [verInativos, setVerInativos] = useState(false)
  const { data, error, isLoading, mutate } = useSWR<{ users: Usuario[]; total: number }>(
    `${API_URL}/users/?apenas_ativos=${!verInativos}`,
    usersFetcher
  )
  const usuarios = data?.users ?? []

  const [modalOpen, setModalOpen] = useState(false)
  const [senhaModalOpen, setSenhaModalOpen] = useState(false)
  const [nome, setNome] = useState("")
  const [email, setEmail] = useState("")
  const [senha, setSenha] = useState("")
  const [role, setRole] = useState("user")
  const [editingUsuario, setEditingUsuario] = useState<Usuario | null>(null)
  const [senhaUsuarioId, setSenhaUsuarioId] = useState<number | null>(null)
  const [novaSenha, setNovaSenha] = useState("")
  const [formError, setFormError] = useState<string | null>(null)
  const [purgeModalOpen, setPurgeModalOpen] = useState(false)
  const [purgeUser, setPurgeUser] = useState<Usuario | null>(null)
  const [purgeStats, setPurgeStats] = useState<{
    total_transacoes: number
    total_uploads: number
    total_grupos: number
    tem_investimentos: boolean
  } | null>(null)

  const fetchUsuarios = useCallback(() => mutate(), [mutate])

  const { data: systemStats } = useSWR<SystemStats>(
    `${API_URL}/users/stats/summary`,
    (url) => fetchWithAuth(url).then((r) => (r.ok ? r.json() : Promise.reject(new Error("Erro ao carregar stats"))))
  )

  const handleAdd = () => {
    setNome("")
    setEmail("")
    setSenha("")
    setRole("user")
    setEditingUsuario(null)
    setFormError(null)
    setModalOpen(true)
  }

  const handleEdit = (usuario: Usuario) => {
    setEditingUsuario(usuario)
    setNome(usuario.nome)
    setEmail(usuario.email)
    setSenha("")
    setRole(usuario.role)
    setFormError(null)
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
      setFormError("Nome e email são obrigatórios")
      return
    }
    if (!editingUsuario && !senha.trim()) {
      setFormError("Senha é obrigatória para novos usuários")
      return
    }

    setFormError(null)
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
        setFormError(errData.detail || errData.error || "Erro ao salvar")
      }
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Erro ao salvar")
    }
  }

  const handleDesativar = async (id: number) => {
    if (id === 1) {
      setFormError("Não é possível desativar o usuário administrador principal")
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

  const handleReativar = async (id: number) => {
    try {
      const response = await fetchWithAuth(`${API_URL}/users/${id}/reativar`, {
        method: "POST",
      })
      if (response.ok) {
        fetchUsuarios()
      } else {
        const errData = await response.json()
        alert(errData.detail || errData.error || "Erro ao reativar")
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro ao reativar")
    }
  }

  const handleOpenPurge = async (u: Usuario) => {
    try {
      const r = await fetchWithAuth(`${API_URL}/users/${u.id}/stats`)
      if (!r.ok) throw new Error("Erro ao carregar stats")
      const stats = await r.json()
      setPurgeUser(u)
      setPurgeStats({
        total_transacoes: stats.total_transacoes,
        total_uploads: stats.total_uploads,
        total_grupos: stats.total_grupos,
        tem_investimentos: stats.tem_investimentos,
      })
      setPurgeModalOpen(true)
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro ao carregar dados")
    }
  }

  const handleConfirmPurge = async (userId: number, emailUsuario: string) => {
    const response = await fetchWithAuth(`${API_URL}/users/${userId}/purge`, {
      method: "DELETE",
      body: JSON.stringify({
        confirmacao: "EXCLUIR PERMANENTEMENTE",
        email_usuario: emailUsuario,
      }),
    })
    if (!response.ok) {
      const errData = await response.json()
      throw new Error(errData.detail || errData.error || "Erro ao excluir")
    }
    fetchUsuarios()
  }

  const handleAlterarSenha = (id: number) => {
    setSenhaUsuarioId(id)
    setNovaSenha("")
    setFormError(null)
    setSenhaModalOpen(true)
  }

  const handleSalvarNovaSenha = async () => {
    if (!novaSenha.trim()) {
      setFormError("Digite a nova senha")
      return
    }
    if (novaSenha.length < 6) {
      setFormError("A senha deve ter no mínimo 6 caracteres")
      return
    }
    if (!senhaUsuarioId) return

    setFormError(null)
    try {
      const response = await fetchWithAuth(`${API_URL}/users/${senhaUsuarioId}`, {
        method: "PUT",
        body: JSON.stringify({ password: novaSenha }),
      })
      if (response.ok) {
        setSenhaModalOpen(false)
      } else {
        const errData = await response.json()
        setFormError(errData.detail || errData.error || "Erro ao alterar senha")
      }
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Erro ao alterar senha")
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    alert("Copiado!")
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold">Contas</h1>
        <p className="text-sm text-muted-foreground">Gerencie usuários do sistema</p>
      </div>

      {systemStats && (
        <div className="rounded-lg border bg-muted/50 p-4">
          <p className="font-medium text-muted-foreground mb-3 text-sm">Indicadores do sistema</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <span className="text-xs text-muted-foreground block">Usuários ativos</span>
              <p className="font-semibold text-lg">{systemStats.total_usuarios_ativos}</p>
            </div>
            <div>
              <span className="text-xs text-muted-foreground block">Uploads</span>
              <p className="font-semibold text-lg">{systemStats.total_uploads.toLocaleString("pt-BR")}</p>
            </div>
            <div>
              <span className="text-xs text-muted-foreground block">Transações</span>
              <p className="font-semibold text-lg">{systemStats.total_transacoes.toLocaleString("pt-BR")}</p>
            </div>
            <div>
              <span className="text-xs text-muted-foreground block">Planos</span>
              <p className="font-semibold text-lg">{systemStats.total_planos.toLocaleString("pt-BR")}</p>
            </div>
          </div>
        </div>
      )}

      <Card>
        <CardHeader className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle className="text-lg">Usuários</CardTitle>
            <CardDescription>{usuarios.length} usuário(s) cadastrado(s)</CardDescription>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
            <label className="flex cursor-pointer items-center gap-2 text-sm min-h-[44px]">
              <input
                type="checkbox"
                checked={verInativos}
                onChange={(e) => setVerInativos(e.target.checked)}
                className="w-4 h-4"
              />
              Ver inativos
            </label>
            <Button onClick={handleAdd} className="min-h-[44px] w-full sm:w-auto">
              <Plus className="mr-2 h-4 w-4" />
              Novo Usuário
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {error && !modalOpen && (
            <div className="mb-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              {error.message}
              <Button variant="ghost" size="sm" className="ml-2 min-h-[44px]" onClick={fetchUsuarios}>
                <RefreshCw className="mr-1 h-3 w-3" />
                Tentar novamente
              </Button>
            </div>
          )}
          {isLoading ? (
            <div className="py-8 text-center text-muted-foreground">Carregando...</div>
          ) : (
            <>
              {/* Mobile: lista em cards */}
              <div className="md:hidden space-y-3">
                {usuarios.map((u) => (
                  <div
                    key={u.id}
                    className={`rounded-lg border p-4 ${!u.ativo ? "bg-muted/50 opacity-75" : "bg-card"}`}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="font-medium truncate">{u.nome}</span>
                          {!u.ativo && (
                            <Badge variant="outline" className="shrink-0">INATIVA</Badge>
                          )}
                          <Badge variant={u.role === "admin" ? "default" : "secondary"} className="shrink-0">
                            {u.role === "admin" ? "Admin" : "Usuário"}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground truncate mt-0.5">{u.email}</p>
                      </div>
                      <Badge variant={u.ativo ? "default" : "destructive"} className="shrink-0">
                        {u.ativo ? "Ativo" : "Inativo"}
                      </Badge>
                    </div>
                    <div className="text-xs text-muted-foreground mb-3">
                      <UserStatsCell userId={u.id} />
                    </div>
                    <div className="flex gap-1 flex-wrap">
                      <Button variant="ghost" size="icon" className="h-11 w-11 shrink-0" onClick={() => handleEdit(u)} title="Editar">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-11 w-11 shrink-0" onClick={() => handleAlterarSenha(u.id)} title="Alterar Senha">
                        <Key className="h-4 w-4" />
                      </Button>
                      {u.id !== 1 && u.ativo && (
                        <Button variant="ghost" size="icon" className="h-11 w-11 shrink-0" onClick={() => handleDesativar(u.id)} title="Desativar">
                          <UserMinus className="h-4 w-4" />
                        </Button>
                      )}
                      {u.id !== 1 && !u.ativo && (
                        <Button variant="ghost" size="icon" className="h-11 w-11 shrink-0" onClick={() => handleReativar(u.id)} title="Reativar">
                          <UserPlus className="h-4 w-4" />
                        </Button>
                      )}
                      {u.id !== 1 && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-11 w-11 shrink-0"
                          onClick={() => handleOpenPurge(u)}
                          title="Excluir permanentemente"
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Desktop: tabela */}
              <div className="hidden md:block overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nome</TableHead>
                      <TableHead>E-mail</TableHead>
                      <TableHead>Perfil</TableHead>
                      <TableHead>Stats</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="w-[180px]">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {usuarios.map((u) => (
                      <TableRow
                        key={u.id}
                        className={!u.ativo ? "bg-muted/50 opacity-75" : ""}
                      >
                        <TableCell className="font-medium">
                          {u.nome}
                          {!u.ativo && (
                            <Badge variant="outline" className="ml-2">
                              INATIVA
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell>{u.email}</TableCell>
                        <TableCell>
                          <Badge variant={u.role === "admin" ? "default" : "secondary"}>
                            {u.role === "admin" ? "Admin" : "Usuário"}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <UserStatsCell userId={u.id} />
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
                          {u.id !== 1 && u.ativo && (
                            <Button variant="ghost" size="icon" onClick={() => handleDesativar(u.id)} title="Desativar">
                              <UserMinus className="h-4 w-4" />
                            </Button>
                          )}
                          {u.id !== 1 && !u.ativo && (
                            <Button variant="ghost" size="icon" onClick={() => handleReativar(u.id)} title="Reativar">
                              <UserPlus className="h-4 w-4" />
                            </Button>
                          )}
                          {u.id !== 1 && (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleOpenPurge(u)}
                              title="Excluir permanentemente"
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </>
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
            {formError && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">{formError}</div>
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
            {formError && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">{formError}</div>
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

      {purgeUser && purgeStats && (
        <PurgeUserModal
          user={purgeUser}
          stats={purgeStats}
          open={purgeModalOpen}
          onClose={() => {
            setPurgeModalOpen(false)
            setPurgeUser(null)
            setPurgeStats(null)
          }}
          onConfirm={handleConfirmPurge}
        />
      )}
    </div>
  )
}
