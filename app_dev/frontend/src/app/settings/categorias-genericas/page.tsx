"use client"

import React, { useState, useEffect } from "react"
import DashboardLayout from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { AlertCircle, Edit, Eye, Plus, Search, Trash2, Upload, Download, TestTube } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

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
  case_sensitive: boolean
  match_completo: boolean
  created_at: string
  updated_at?: string
  created_by?: string
  total_matches: number
  last_match_at?: string
}

interface GenericRuleCreate {
  nome_regra: string
  descricao?: string
  keywords: string
  grupo: string
  subgrupo: string
  tipo_gasto: string
  prioridade?: number
  ativo?: boolean
  case_sensitive?: boolean
  match_completo?: boolean
}

interface TestResult {
  matched: boolean
  rule_id?: number
  rule_name?: string
  grupo?: string
  subgrupo?: string
  tipo_gasto?: string
  keywords_matched?: string[]
}

interface Stats {
  total_regras: number
  regras_ativas: number
  regras_inativas: number
  grupos_unicos: number
  grupos: string[]
  top_regras_usadas: Array<{
    id: number
    nome_regra: string
    total_matches: number
  }>
}

const API_BASE = "http://localhost:8000/api/v1/classification"

interface GrupoSubgrupoOption {
  grupo: string
  subgrupo: string
  tipo_gasto: string
  categoria_geral: string
}

export default function CategoriasGenericasPage() {
  const [rules, setRules] = useState<GenericRule[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [grupoOptions, setGrupoOptions] = useState<GrupoSubgrupoOption[]>([])
  
  // Filtros
  const [searchTerm, setSearchTerm] = useState("")
  const [filterGroup, setFilterGroup] = useState<string>("ALL")
  const [filterActive, setFilterActive] = useState<boolean | null>(null)
  
  // Modal states
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [isTestOpen, setIsTestOpen] = useState(false)
  const [editingRule, setEditingRule] = useState<GenericRule | null>(null)
  
  // Form states
  const [formData, setFormData] = useState<GenericRuleCreate>({
    nome_regra: "",
    keywords: "",
    grupo: "",
    subgrupo: "",
    tipo_gasto: "",
    ativo: true,
    case_sensitive: false,
    match_completo: false,
    prioridade: 50,
  })
  
  // Test states
  const [testText, setTestText] = useState("")
  const [testResult, setTestResult] = useState<TestResult | null>(null)

  // Carrega dados iniciais
  useEffect(() => {
    loadRules()
    loadStats()
    loadGrupoOptions()
  }, [])

  const loadRules = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/rules`)
      if (!response.ok) throw new Error('Erro ao carregar regras')
      const data = await response.json()
      setRules(data)
      setError(null)
    } catch (err) {
      console.error('Erro:', err)
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/stats`)
      if (!response.ok) throw new Error('Erro ao carregar estatísticas')
      const data = await response.json()
      setStats(data)
    } catch (err) {
      console.error('Erro ao carregar stats:', err)
    }
  }

  const loadGrupoOptions = async () => {
    try {
      // Busca combinações grupo/subgrupo das transações com seus tipos de gasto
      const response = await fetch(`${API_BASE}/groups-with-types`)
      if (!response.ok) throw new Error('Erro ao carregar grupos')
      const data = await response.json()
      setGrupoOptions(data.opcoes || [])
    } catch (err) {
      console.error('Erro ao carregar opções de grupo:', err)
    }
  }

  const createRule = async (data: GenericRuleCreate) => {
    try {
      // Buscar tipo_gasto da combinação grupo/subgrupo
      const matchingOption = grupoOptions.find(
        option => option.grupo === data.grupo && option.subgrupo === data.subgrupo
      )
      
      const finalData = {
        ...data,
        tipo_gasto: matchingOption?.tipo_gasto || 'Ajustável' // fallback
      }
      
      const response = await fetch(`${API_BASE}/rules`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(finalData)
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Erro ao criar regra')
      }
      
      await loadRules()
      await loadStats()
      setIsCreateOpen(false)
      resetForm()
    } catch (err) {
      console.error('Erro:', err)
      setError(err instanceof Error ? err.message : 'Erro ao criar regra')
    }
  }

  const updateRule = async (id: number, data: Partial<GenericRuleCreate>) => {
    try {
      const response = await fetch(`${API_BASE}/rules/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Erro ao atualizar regra')
      await loadRules()
      await loadStats()
      setIsEditOpen(false)
      setEditingRule(null)
      resetForm()
    } catch (err) {
      console.error('Erro:', err)
      setError(err instanceof Error ? err.message : 'Erro ao atualizar regra')
    }
  }

  const deleteRule = async (id: number) => {
    if (!confirm('Tem certeza que deseja deletar esta regra?')) return
    
    try {
      const response = await fetch(`${API_BASE}/rules/${id}`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('Erro ao deletar regra')
      await loadRules()
      await loadStats()
    } catch (err) {
      console.error('Erro:', err)
      setError(err instanceof Error ? err.message : 'Erro ao deletar regra')
    }
  }

  const testRule = async (text: string) => {
    try {
      const response = await fetch(`${API_BASE}/rules/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto: text })
      })
      if (!response.ok) throw new Error('Erro ao testar regra')
      const result = await response.json()
      setTestResult(result)
    } catch (err) {
      console.error('Erro:', err)
      setError(err instanceof Error ? err.message : 'Erro ao testar regra')
    }
  }

  const importHardcodedRules = async () => {
    if (!confirm('Importar regras hardcoded? Isso pode sobrescrever regras existentes.')) return
    
    try {
      const response = await fetch(`${API_BASE}/rules/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sobrescrever_existentes: false })
      })
      if (!response.ok) throw new Error('Erro ao importar regras')
      const result = await response.json()
      alert(`Importação concluída: ${result.stats.created} criadas, ${result.stats.updated} atualizadas, ${result.stats.skipped} ignoradas`)
      await loadRules()
      await loadStats()
    } catch (err) {
      console.error('Erro:', err)
      setError(err instanceof Error ? err.message : 'Erro ao importar regras')
    }
  }

  const resetForm = () => {
    setFormData({
      nome_regra: "",
      keywords: "",
      grupo: "",
      subgrupo: "",
      tipo_gasto: "", // Será preenchido automaticamente
      ativo: true,
      case_sensitive: false,
      match_completo: false,
      prioridade: 50,
    })
  }

  const handleEdit = (rule: GenericRule) => {
    setEditingRule(rule)
    setFormData({
      nome_regra: rule.nome_regra,
      descricao: rule.descricao,
      keywords: rule.keywords,
      grupo: rule.grupo,
      subgrupo: rule.subgrupo,
      tipo_gasto: rule.tipo_gasto,
      prioridade: rule.prioridade,
      ativo: rule.ativo,
      case_sensitive: rule.case_sensitive,
      match_completo: rule.match_completo,
    })
    setIsEditOpen(true)
  }

  // Filtrar regras
  const filteredRules = rules.filter(rule => {
    const matchesSearch = 
      rule.nome_regra.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rule.keywords.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rule.grupo.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesGroup = filterGroup === "ALL" || rule.grupo === filterGroup
    const matchesActive = filterActive === null || rule.ativo === filterActive
    
    return matchesSearch && matchesGroup && matchesActive
  })

  if (loading) {
    return <div className="p-6">Carregando...</div>
  }

  return (
    <DashboardLayout>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Categorias Genéricas</h1>
          <p className="text-muted-foreground">
            Configure regras automáticas de classificação de transações
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={importHardcodedRules} variant="outline">
            <Upload className="h-4 w-4 mr-2" />
            Importar Hardcoded
          </Button>
          <Button onClick={() => setIsTestOpen(true)} variant="outline">
            <TestTube className="h-4 w-4 mr-2" />
            Testar Regras
          </Button>
          <Button onClick={() => setIsCreateOpen(true)}>
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

      {/* Estatísticas */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total de Regras</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_regras}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Regras Ativas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.regras_ativas}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Regras Inativas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.regras_inativas}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Grupos Únicos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.grupos_unicos}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <Label htmlFor="search">Buscar</Label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Nome, keywords ou grupo..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <div className="w-[180px]">
              <Label htmlFor="group">Grupo</Label>
              <Select value={filterGroup} onValueChange={setFilterGroup}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os grupos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ALL">Todos os grupos</SelectItem>
                  {stats?.grupos.map(grupo => (
                    <SelectItem key={grupo} value={grupo}>{grupo}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="w-[120px]">
              <Label htmlFor="active">Status</Label>
              <Select value={filterActive?.toString() || "ALL"} onValueChange={(v) => setFilterActive(v === "ALL" ? null : v === "true")}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ALL">Todos</SelectItem>
                  <SelectItem value="true">Ativas</SelectItem>
                  <SelectItem value="false">Inativas</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Regras */}
      <div className="space-y-4">
        {filteredRules.map((rule) => (
          <Card key={rule.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-lg">{rule.nome_regra}</CardTitle>
                    <Badge variant={rule.ativo ? "default" : "secondary"}>
                      {rule.ativo ? "Ativa" : "Inativa"}
                    </Badge>
                    {rule.prioridade && (
                      <Badge variant="outline">Prioridade: {rule.prioridade}</Badge>
                    )}
                  </div>
                  {rule.descricao && (
                    <CardDescription>{rule.descricao}</CardDescription>
                  )}
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
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div>
                  <Label className="text-xs font-medium">Keywords</Label>
                  <div className="text-sm text-muted-foreground break-words">{rule.keywords}</div>
                </div>
                <div>
                  <Label className="text-xs font-medium">Classificação</Label>
                  <div className="text-sm">
                    <div>{rule.grupo} → {rule.subgrupo}</div>
                    <div className="text-muted-foreground">{rule.tipo_gasto}</div>
                  </div>
                </div>
                <div>
                  <Label className="text-xs font-medium">Configurações</Label>
                  <div className="text-sm space-y-1">
                    <div>Case sensitive: {rule.case_sensitive ? "Sim" : "Não"}</div>
                    <div>Match completo: {rule.match_completo ? "Sim" : "Não"}</div>
                  </div>
                </div>
                <div>
                  <Label className="text-xs font-medium">Estatísticas</Label>
                  <div className="text-sm text-muted-foreground">
                    <div>{rule.total_matches} matches</div>
                    {rule.last_match_at && (
                      <div>Último: {new Date(rule.last_match_at).toLocaleDateString()}</div>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredRules.length === 0 && (
        <Card>
          <CardContent className="p-6 text-center text-muted-foreground">
            Nenhuma regra encontrada com os filtros aplicados.
          </CardContent>
        </Card>
      )}

      {/* Dialog para criar regra */}
      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Nova Regra de Classificação</DialogTitle>
            <DialogDescription>
              Crie uma nova regra para classificar automaticamente transações
            </DialogDescription>
          </DialogHeader>
          <RuleForm 
            data={formData} 
            onChange={setFormData}
            grupoOptions={grupoOptions}
            onSubmit={() => createRule(formData)}
            onCancel={() => { setIsCreateOpen(false); resetForm(); }}
          />
        </DialogContent>
      </Dialog>

      {/* Dialog para editar regra */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Editar Regra</DialogTitle>
            <DialogDescription>
              Modifique os parâmetros da regra de classificação
            </DialogDescription>
          </DialogHeader>
          <RuleForm 
            data={formData} 
            onChange={setFormData}
            grupoOptions={grupoOptions}
            onSubmit={() => editingRule && updateRule(editingRule.id, formData)}
            onCancel={() => { setIsEditOpen(false); setEditingRule(null); resetForm(); }}
          />
        </DialogContent>
      </Dialog>

      {/* Dialog para testar regras */}
      <Dialog open={isTestOpen} onOpenChange={setIsTestOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Testar Regras</DialogTitle>
            <DialogDescription>
              Digite um texto para ver qual regra faria match
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="test-text">Texto de teste</Label>
              <Input
                id="test-text"
                placeholder="Ex: PIX UBER BRASIL"
                value={testText}
                onChange={(e) => setTestText(e.target.value)}
              />
            </div>
            {testResult && (
              <div className="p-4 border rounded-lg">
                {testResult.matched ? (
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-green-600">✓ Match encontrado!</div>
                    <div className="text-sm">
                      <div><strong>Regra:</strong> {testResult.rule_name}</div>
                      <div><strong>Grupo:</strong> {testResult.grupo}</div>
                      <div><strong>Subgrupo:</strong> {testResult.subgrupo}</div>
                      <div><strong>Tipo:</strong> {testResult.tipo_gasto}</div>
                      {testResult.keywords_matched && testResult.keywords_matched.length > 0 && (
                        <div><strong>Keywords:</strong> {testResult.keywords_matched.join(", ")}</div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground">Nenhuma regra encontrada</div>
                )}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsTestOpen(false)}>
              Fechar
            </Button>
            <Button onClick={() => testRule(testText)} disabled={!testText.trim()}>
              Testar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
    </DashboardLayout>
  )
}

// Componente de formulário reutilizável
function RuleForm({ 
  data, 
  onChange,
  grupoOptions,
  onSubmit, 
  onCancel 
}: { 
  data: GenericRuleCreate
  onChange: (data: GenericRuleCreate) => void
  grupoOptions: GrupoSubgrupoOption[]
  onSubmit: () => void
  onCancel: () => void
}) {
  const updateField = (field: keyof GenericRuleCreate, value: any) => {
    const newData = { ...data, [field]: value }
    
    // Se mudou grupo ou subgrupo, atualizar tipo_gasto automaticamente
    if (field === 'grupo' || field === 'subgrupo') {
      const matchingOption = grupoOptions.find(
        option => option.grupo === newData.grupo && option.subgrupo === newData.subgrupo
      )
      if (matchingOption) {
        newData.tipo_gasto = matchingOption.tipo_gasto
      }
    }
    
    onChange(newData)
  }

  // Obter grupos únicos
  const gruposUnicos = [...new Set(grupoOptions.map(opt => opt.grupo))]
  
  // Obter subgrupos para o grupo selecionado
  const subgruposDisponiveis = grupoOptions
    .filter(opt => opt.grupo === data.grupo)
    .map(opt => opt.subgrupo)
  
  // Obter tipo de gasto atual
  const tipoGastoAtual = grupoOptions.find(
    opt => opt.grupo === data.grupo && opt.subgrupo === data.subgrupo
  )?.tipo_gasto || 'Não definido'

  return (
    <div className="space-y-4">
      <div>
        <Label htmlFor="nome_regra">Nome da Regra</Label>
        <Input
          id="nome_regra"
          value={data.nome_regra}
          onChange={(e) => updateField('nome_regra', e.target.value)}
          placeholder="Ex: Classificação Uber"
        />
      </div>
      
      <div>
        <Label htmlFor="keywords">Keywords (separadas por vírgula)</Label>
        <Input
          id="keywords"
          value={data.keywords}
          onChange={(e) => updateField('keywords', e.target.value)}
          placeholder="Ex: UBER,UBER BRASIL,99TAXI"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="grupo">Grupo</Label>
          <Select value={data.grupo} onValueChange={(value) => updateField('grupo', value)}>
            <SelectTrigger>
              <SelectValue placeholder="Selecione o grupo" />
            </SelectTrigger>
            <SelectContent>
              {gruposUnicos.map((grupo) => (
                <SelectItem key={grupo} value={grupo}>{grupo}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label htmlFor="subgrupo">Subgrupo</Label>
          <Select 
            value={data.subgrupo} 
            onValueChange={(value) => updateField('subgrupo', value)}
            disabled={!data.grupo}
          >
            <SelectTrigger>
              <SelectValue placeholder="Selecione o subgrupo" />
            </SelectTrigger>
            <SelectContent>
              {subgruposDisponiveis.map((subgrupo) => (
                <SelectItem key={subgrupo} value={subgrupo}>{subgrupo}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Mostrar tipo de gasto calculado automaticamente */}
      {data.grupo && data.subgrupo && (
        <div className="p-3 bg-muted rounded-lg">
          <Label className="text-xs font-medium text-muted-foreground">Tipo de Gasto (automático)</Label>
          <div className="text-sm font-medium">{tipoGastoAtual}</div>
        </div>
      )}

      <div>
        <Label htmlFor="descricao">Descrição (opcional)</Label>
        <Input
          id="descricao"
          value={data.descricao || ""}
          onChange={(e) => updateField('descricao', e.target.value)}
          placeholder="Descrição da regra..."
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="prioridade">Prioridade</Label>
          <Input
            id="prioridade"
            type="number"
            min="1"
            max="100"
            value={data.prioridade || 50}
            onChange={(e) => updateField('prioridade', parseInt(e.target.value))}
          />
        </div>
        <div className="space-y-3 pt-6">
          <div className="flex items-center space-x-2">
            <Switch
              id="ativo"
              checked={data.ativo}
              onCheckedChange={(checked) => updateField('ativo', checked)}
            />
            <Label htmlFor="ativo">Regra ativa</Label>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center space-x-2">
          <Switch
            id="case_sensitive"
            checked={data.case_sensitive}
            onCheckedChange={(checked) => updateField('case_sensitive', checked)}
          />
          <Label htmlFor="case_sensitive">Case sensitive</Label>
        </div>
        <div className="flex items-center space-x-2">
          <Switch
            id="match_completo"
            checked={data.match_completo}
            onCheckedChange={(checked) => updateField('match_completo', checked)}
          />
          <Label htmlFor="match_completo">Match palavra completa</Label>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
        <Button onClick={onSubmit} disabled={!data.nome_regra || !data.keywords || !data.grupo || !data.subgrupo}>
          Salvar
        </Button>
      </DialogFooter>
    </div>
  )
}