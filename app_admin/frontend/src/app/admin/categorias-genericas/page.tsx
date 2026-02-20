"use client"

import React, { useState, useEffect } from "react"
import { fetchWithAuth } from "@/core/utils/api-client"
import { API_ENDPOINTS } from "@/core/config/api.config"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  AlertCircle,
  Edit,
  Plus,
  Search,
  Trash2,
  Upload,
  TestTube,
  RefreshCw,
} from "lucide-react"

interface GenericRule {
  id: number
  nome_regra: string
  descricao?: string
  keywords: string
  grupo: string
  subgrupo: string
  tipo_gasto: string
  prioridade?: number
  ativo: boolean
  total_matches?: number
}

interface GrupoSubgrupoOption {
  grupo: string
  subgrupo: string
  tipo_gasto: string
  categoria_geral: string
}

interface Stats {
  total_regras: number
  regras_ativas: number
  regras_inativas: number
  grupos_unicos: number
  grupos: string[]
}

export default function CategoriasGenericasPage() {
  const [rules, setRules] = useState<GenericRule[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [grupoOptions, setGrupoOptions] = useState<GrupoSubgrupoOption[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [filterGroup, setFilterGroup] = useState<string>("ALL")
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [isTestOpen, setIsTestOpen] = useState(false)
  const [editingRule, setEditingRule] = useState<GenericRule | null>(null)
  const [testText, setTestText] = useState("")
  const [testResult, setTestResult] = useState<{
    matched: boolean
    rule_name?: string
    grupo?: string
    subgrupo?: string
    tipo_gasto?: string
  } | null>(null)
  const [formData, setFormData] = useState({
    nome_regra: "",
    keywords: "",
    grupo: "",
    subgrupo: "",
    tipo_gasto: "",
    ativo: true,
    prioridade: 50,
  })

  const loadRules = async () => {
    try {
      setLoading(true)
      const response = await fetchWithAuth(API_ENDPOINTS.CLASSIFICATION.RULES)
      if (!response.ok) throw new Error("Erro ao carregar regras")
      const data = await response.json()
      setRules(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro desconhecido")
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await fetchWithAuth(API_ENDPOINTS.CLASSIFICATION.STATS)
      if (!response.ok) return
      const data = await response.json()
      setStats(data)
    } catch {
      /* ignore */
    }
  }

  const loadGrupoOptions = async () => {
    try {
      const response = await fetchWithAuth(
        API_ENDPOINTS.CLASSIFICATION.GROUPS_WITH_TYPES
      )
      if (!response.ok) return
      const data = await response.json()
      setGrupoOptions(data.opcoes || [])
    } catch {
      /* ignore */
    }
  }

  useEffect(() => {
    loadRules()
    loadStats()
    loadGrupoOptions()
  }, [])

  const createRule = async () => {
    if (!formData.nome_regra || !formData.keywords || !formData.grupo || !formData.subgrupo)
      return
    try {
      const opt = grupoOptions.find(
        (o) => o.grupo === formData.grupo && o.subgrupo === formData.subgrupo
      )
      const response = await fetchWithAuth(API_ENDPOINTS.CLASSIFICATION.RULES, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          tipo_gasto: opt?.tipo_gasto || "Ajustável",
        }),
      })
      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || "Erro ao criar")
      }
      await loadRules()
      await loadStats()
      setIsCreateOpen(false)
      setFormData({
        nome_regra: "",
        keywords: "",
        grupo: "",
        subgrupo: "",
        tipo_gasto: "",
        ativo: true,
        prioridade: 50,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao criar")
    }
  }

  const updateRule = async () => {
    if (!editingRule) return
    try {
      const response = await fetchWithAuth(
        API_ENDPOINTS.CLASSIFICATION.RULES_BY_ID(editingRule.id),
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        }
      )
      if (!response.ok) throw new Error("Erro ao atualizar")
      await loadRules()
      await loadStats()
      setIsEditOpen(false)
      setEditingRule(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao atualizar")
    }
  }

  const deleteRule = async (id: number) => {
    if (!confirm("Tem certeza que deseja deletar esta regra?")) return
    try {
      const response = await fetchWithAuth(
        API_ENDPOINTS.CLASSIFICATION.RULES_BY_ID(id),
        { method: "DELETE" }
      )
      if (!response.ok) throw new Error("Erro ao deletar")
      await loadRules()
      await loadStats()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao deletar")
    }
  }

  const testRule = async () => {
    if (!testText.trim()) return
    try {
      const response = await fetchWithAuth(API_ENDPOINTS.CLASSIFICATION.TEST, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto: testText }),
      })
      if (!response.ok) throw new Error("Erro ao testar")
      const result = await response.json()
      setTestResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao testar")
    }
  }

  const importRules = async () => {
    if (!confirm("Importar regras hardcoded?")) return
    try {
      const response = await fetchWithAuth(API_ENDPOINTS.CLASSIFICATION.IMPORT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sobrescrever_existentes: false }),
      })
      if (!response.ok) throw new Error("Erro ao importar")
      const result = await response.json()
      alert(
        `Importação: ${result.stats?.created || 0} criadas, ${result.stats?.updated || 0} atualizadas`
      )
      await loadRules()
      await loadStats()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao importar")
    }
  }

  const filteredRules = rules.filter((r) => {
    const matchSearch =
      r.nome_regra.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.keywords.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.grupo.toLowerCase().includes(searchTerm.toLowerCase())
    const matchGroup = filterGroup === "ALL" || r.grupo === filterGroup
    return matchSearch && matchGroup
  })

  const handleEdit = (rule: GenericRule) => {
    setEditingRule(rule)
    setFormData({
      nome_regra: rule.nome_regra,
      keywords: rule.keywords,
      grupo: rule.grupo,
      subgrupo: rule.subgrupo,
      tipo_gasto: rule.tipo_gasto,
      ativo: rule.ativo,
      prioridade: rule.prioridade || 50,
    })
    setIsEditOpen(true)
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Categorias Genéricas</h1>
          <p className="text-muted-foreground">
            Regras automáticas de classificação de transações
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" onClick={importRules}>
            <Upload className="h-4 w-4 mr-2" />
            Importar
          </Button>
          <Button variant="outline" size="sm" onClick={() => setIsTestOpen(true)}>
            <TestTube className="h-4 w-4 mr-2" />
            Testar
          </Button>
          <Button size="sm" onClick={() => setIsCreateOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Nova Regra
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_regras}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Ativas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {stats.regras_ativas}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Inativas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {stats.regras_inativas}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Grupos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.grupos_unicos}</div>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <Label>Buscar</Label>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Nome, keywords ou grupo..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8"
              />
            </div>
          </div>
          <div className="w-[180px]">
            <Label>Grupo</Label>
            <Select value={filterGroup} onValueChange={setFilterGroup}>
              <SelectTrigger>
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todos</SelectItem>
                {stats?.grupos.map((g) => (
                  <SelectItem key={g} value={g}>
                    {g}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {filteredRules.map((rule) => (
          <Card key={rule.id}>
            <CardHeader>
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <CardTitle className="text-lg">{rule.nome_regra}</CardTitle>
                    <Badge variant={rule.ativo ? "default" : "secondary"}>
                      {rule.ativo ? "Ativa" : "Inativa"}
                    </Badge>
                  </div>
                  <CardDescription className="mt-1">
                    {rule.keywords} → {rule.grupo} / {rule.subgrupo} ({rule.tipo_gasto})
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(rule)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => deleteRule(rule.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>

      {filteredRules.length === 0 && (
        <Card>
          <CardContent className="p-6 text-center text-muted-foreground">
            Nenhuma regra encontrada.
          </CardContent>
        </Card>
      )}

      {/* Dialog Criar */}
      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nova Regra</DialogTitle>
            <DialogDescription>Crie uma regra de classificação</DialogDescription>
          </DialogHeader>
          <RuleForm
            formData={formData}
            setFormData={setFormData}
            grupoOptions={grupoOptions}
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateOpen(false)}>
              Cancelar
            </Button>
            <Button
              onClick={createRule}
              disabled={
                !formData.nome_regra ||
                !formData.keywords ||
                !formData.grupo ||
                !formData.subgrupo
              }
            >
              Criar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog Editar */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar Regra</DialogTitle>
          </DialogHeader>
          <RuleForm
            formData={formData}
            setFormData={setFormData}
            grupoOptions={grupoOptions}
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={updateRule}>Salvar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog Testar */}
      <Dialog open={isTestOpen} onOpenChange={setIsTestOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Testar Regras</DialogTitle>
            <DialogDescription>
              Digite um texto para ver qual regra faria match
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Texto</Label>
              <Input
                placeholder="Ex: PIX UBER BRASIL"
                value={testText}
                onChange={(e) => setTestText(e.target.value)}
              />
            </div>
            {testResult && (
              <div className="p-4 border rounded-lg">
                {testResult.matched ? (
                  <div className="text-sm space-y-1 text-green-600">
                    <div>✓ Match: {testResult.rule_name}</div>
                    <div>
                      {testResult.grupo} → {testResult.subgrupo} ({testResult.tipo_gasto})
                    </div>
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground">
                    Nenhuma regra encontrada
                  </div>
                )}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsTestOpen(false)}>
              Fechar
            </Button>
            <Button onClick={testRule} disabled={!testText.trim()}>
              Testar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

function RuleForm({
  formData,
  setFormData,
  grupoOptions,
}: {
  formData: {
    nome_regra: string
    keywords: string
    grupo: string
    subgrupo: string
    tipo_gasto: string
    ativo: boolean
    prioridade: number
  }
  setFormData: (d: typeof formData) => void
  grupoOptions: GrupoSubgrupoOption[]
}) {
  const grupos = [...new Set(grupoOptions.map((o) => o.grupo))]
  const subgrupos = grupoOptions
    .filter((o) => o.grupo === formData.grupo)
    .map((o) => o.subgrupo)

  const update = (k: keyof typeof formData, v: unknown) => {
    const next = { ...formData, [k]: v }
    if (k === "grupo" || k === "subgrupo") {
      const opt = grupoOptions.find(
        (o) => o.grupo === next.grupo && o.subgrupo === next.subgrupo
      )
      if (opt) next.tipo_gasto = opt.tipo_gasto
    }
    setFormData(next)
  }

  return (
    <div className="space-y-4">
      <div>
        <Label>Nome</Label>
        <Input
          value={formData.nome_regra}
          onChange={(e) => update("nome_regra", e.target.value)}
          placeholder="Ex: Classificação Uber"
        />
      </div>
      <div>
        <Label>Keywords (vírgula)</Label>
        <Input
          value={formData.keywords}
          onChange={(e) => update("keywords", e.target.value)}
          placeholder="UBER, UBER BRASIL"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Grupo</Label>
          <Select value={formData.grupo} onValueChange={(v) => update("grupo", v)}>
            <SelectTrigger>
              <SelectValue placeholder="Selecione" />
            </SelectTrigger>
            <SelectContent>
              {grupos.map((g) => (
                <SelectItem key={g} value={g}>
                  {g}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label>Subgrupo</Label>
          <Select
            value={formData.subgrupo}
            onValueChange={(v) => update("subgrupo", v)}
            disabled={!formData.grupo}
          >
            <SelectTrigger>
              <SelectValue placeholder="Selecione" />
            </SelectTrigger>
            <SelectContent>
              {subgrupos.map((s) => (
                <SelectItem key={s} value={s}>
                  {s}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
      {formData.grupo && formData.subgrupo && (
        <div className="p-2 bg-muted rounded text-sm">
          Tipo: {formData.tipo_gasto}
        </div>
      )}
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="ativo"
          checked={formData.ativo}
          onChange={(e) => update("ativo", e.target.checked)}
          className="w-4 h-4"
        />
        <Label htmlFor="ativo">Regra ativa</Label>
      </div>
    </div>
  )
}
