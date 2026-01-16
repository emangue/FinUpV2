"use client"

import { useState, useEffect } from "react"
import DashboardLayout from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, Plus, AlertTriangle, CheckCircle2, Loader2 } from "lucide-react"
import { API_CONFIG } from "@/core/config/api.config"

interface GrupoSubgrupoOption {
  grupo: string
  subgrupo: string | null
  total_transacoes: number
}

interface MigrationPreview {
  total_transacoes: number
  grupo_origem: string
  subgrupo_origem: string | null
  grupo_destino: string
  subgrupo_destino: string | null
  tipo_gasto_destino: string
  categoria_geral_destino: string
}

interface MigrationResult {
  success: boolean
  total_transacoes_atualizadas: number
  grupo_origem: string
  subgrupo_origem: string | null
  grupo_destino: string
  subgrupo_destino: string | null
  tipo_gasto_destino: string
  categoria_geral_destino: string
  grupos_recalculados: string[]
}

export default function MigracoesPage() {
  const [opcoes, setOpcoes] = useState<GrupoSubgrupoOption[]>([])
  const [gruposUnicos, setGruposUnicos] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  
  // Origem
  const [grupoOrigem, setGrupoOrigem] = useState("")
  const [subgrupoOrigem, setSubgrupoOrigem] = useState<string | null>(null)
  const [subgruposOrigem, setSubgruposOrigem] = useState<string[]>([])
  
  // Destino
  const [grupoDestino, setGrupoDestino] = useState("")
  const [subgrupoDestino, setSubgrupoDestino] = useState<string | null>(null)
  const [subgruposDestino, setSubgruposDestino] = useState<string[]>([])
  const [novoSubgrupoDestino, setNovoSubgrupoDestino] = useState("")
  const [mostrarInputNovoSubgrupo, setMostrarInputNovoSubgrupo] = useState(false)
  
  // Preview e execução
  const [preview, setPreview] = useState<MigrationPreview | null>(null)
  const [loadingPreview, setLoadingPreview] = useState(false)
  const [executando, setExecutando] = useState(false)
  const [resultado, setResultado] = useState<MigrationResult | null>(null)
  const [erro, setErro] = useState<string | null>(null)

  // Carregar opções iniciais
  useEffect(() => {
    loadOpcoes()
  }, [])

  // Atualizar subgrupos quando grupo origem mudar
  useEffect(() => {
    if (grupoOrigem) {
      const subs = opcoes
        .filter(o => o.grupo === grupoOrigem && o.subgrupo)
        .map(o => o.subgrupo!)
      setSubgruposOrigem(subs)
      setSubgrupoOrigem(null)
    }
  }, [grupoOrigem, opcoes])

  // Atualizar subgrupos quando grupo destino mudar
  useEffect(() => {
    if (grupoDestino) {
      const subs = opcoes
        .filter(o => o.grupo === grupoDestino && o.subgrupo)
        .map(o => o.subgrupo!)
      setSubgruposDestino(subs)
      setSubgrupoDestino(null)
      setMostrarInputNovoSubgrupo(false)
      setNovoSubgrupoDestino("")
    }
  }, [grupoDestino, opcoes])

  async function loadOpcoes() {
    try {
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions/migration/grupos-subgrupos`,
        { credentials: "include" }
      )
      
      if (!response.ok) throw new Error("Erro ao carregar opções")
      
      const data = await response.json()
      setOpcoes(data.opcoes)
      
      // Extrair grupos únicos
      const grupos = Array.from(new Set(data.opcoes.map((o: GrupoSubgrupoOption) => o.grupo)))
      setGruposUnicos(grupos)
    } catch (error) {
      console.error("Erro ao carregar opções:", error)
      setErro("Erro ao carregar opções de grupos")
    } finally {
      setLoading(false)
    }
  }

  async function handlePreview() {
    if (!grupoOrigem || !grupoDestino) {
      setErro("Selecione grupo de origem e destino")
      return
    }

    setLoadingPreview(true)
    setErro(null)
    setPreview(null)
    setResultado(null)

    try {
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions/migration/preview`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            grupo_origem: grupoOrigem,
            subgrupo_origem: subgrupoOrigem,
            grupo_destino: grupoDestino,
            subgrupo_destino: mostrarInputNovoSubgrupo ? novoSubgrupoDestino : subgrupoDestino
          })
        }
      )

      if (!response.ok) throw new Error("Erro ao gerar preview")

      const data = await response.json()
      setPreview(data)
    } catch (error) {
      console.error("Erro ao gerar preview:", error)
      setErro("Erro ao gerar preview da migração")
    } finally {
      setLoadingPreview(false)
    }
  }

  async function handleExecutar() {
    if (!preview) return

    setExecutando(true)
    setErro(null)
    setResultado(null)

    try {
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions/migration/execute`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            grupo_origem: grupoOrigem,
            subgrupo_origem: subgrupoOrigem,
            grupo_destino: grupoDestino,
            subgrupo_destino: mostrarInputNovoSubgrupo ? novoSubgrupoDestino : subgrupoDestino
          })
        }
      )

      if (!response.ok) throw new Error("Erro ao executar migração")

      const data = await response.json()
      setResultado(data)
      setPreview(null)
      
      // Recarregar opções após migração
      await loadOpcoes()
      
      // Limpar formulário
      setGrupoOrigem("")
      setSubgrupoOrigem(null)
      setGrupoDestino("")
      setSubgrupoDestino(null)
      setNovoSubgrupoDestino("")
      setMostrarInputNovoSubgrupo(false)
    } catch (error) {
      console.error("Erro ao executar migração:", error)
      setErro("Erro ao executar migração")
    } finally {
      setExecutando(false)
    }
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="container mx-auto py-8 px-4 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Migração de Transações</h1>
        <p className="text-muted-foreground mt-2">
          Migre transações em massa de um grupo/subgrupo para outro
        </p>
      </div>

      {erro && (
        <Alert variant="destructive" className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{erro}</AlertDescription>
        </Alert>
      )}

      {resultado && (
        <Alert className="mb-6 border-green-500 bg-green-50">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            <div className="font-semibold mb-2">Migração concluída com sucesso!</div>
            <div className="space-y-1 text-sm">
              <div>✅ {resultado.total_transacoes_atualizadas} transações atualizadas</div>
              <div>📊 Tipo Gasto: {resultado.tipo_gasto_destino}</div>
              <div>📁 Categoria Geral: {resultado.categoria_geral_destino}</div>
              <div>🔄 Grupos recalculados: {resultado.grupos_recalculados.join(", ")}</div>
            </div>
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* ORIGEM */}
        <Card>
          <CardHeader>
            <CardTitle>De (Origem)</CardTitle>
            <CardDescription>Selecione o grupo/subgrupo de origem</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="grupo-origem">Grupo</Label>
              <Select value={grupoOrigem} onValueChange={setGrupoOrigem}>
                <SelectTrigger id="grupo-origem">
                  <SelectValue placeholder="Selecione o grupo" />
                </SelectTrigger>
                <SelectContent>
                  {gruposUnicos.map((grupo) => (
                    <SelectItem key={grupo} value={grupo}>
                      {grupo}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {grupoOrigem && (
              <div className="space-y-2">
                <Label htmlFor="subgrupo-origem">Subgrupo (opcional)</Label>
                <Select
                  value={subgrupoOrigem || "__TODOS__"}
                  onValueChange={(v) => setSubgrupoOrigem(v === "__TODOS__" ? null : v)}
                >
                  <SelectTrigger id="subgrupo-origem">
                    <SelectValue placeholder="Todos os subgrupos" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="__TODOS__">Todos os subgrupos</SelectItem>
                    {subgruposOrigem.map((sub) => (
                      <SelectItem key={sub} value={sub}>
                        {sub}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {grupoOrigem && (
              <div className="pt-2">
                <Badge variant="secondary">
                  {opcoes.find(o => o.grupo === grupoOrigem && o.subgrupo === subgrupoOrigem)?.total_transacoes || 
                   opcoes.filter(o => o.grupo === grupoOrigem && !subgrupoOrigem).reduce((sum, o) => sum + o.total_transacoes, 0)} transações
                </Badge>
              </div>
            )}
          </CardContent>
        </Card>

        {/* DESTINO */}
        <Card>
          <CardHeader>
            <CardTitle>Para (Destino)</CardTitle>
            <CardDescription>Selecione o grupo/subgrupo de destino</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="grupo-destino">Grupo</Label>
              <Select value={grupoDestino} onValueChange={setGrupoDestino}>
                <SelectTrigger id="grupo-destino">
                  <SelectValue placeholder="Selecione o grupo" />
                </SelectTrigger>
                <SelectContent>
                  {gruposUnicos.map((grupo) => (
                    <SelectItem key={grupo} value={grupo}>
                      {grupo}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {grupoDestino && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="subgrupo-destino">Subgrupo (opcional)</Label>
                  {!mostrarInputNovoSubgrupo && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => setMostrarInputNovoSubgrupo(true)}
                    >
                      <Plus className="h-4 w-4 mr-1" />
                      Novo
                    </Button>
                  )}
                </div>

                {mostrarInputNovoSubgrupo ? (
                  <div className="space-y-2">
                    <Input
                      placeholder="Digite o novo subgrupo"
                      value={novoSubgrupoDestino}
                      onChange={(e) => setNovoSubgrupoDestino(e.target.value)}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setMostrarInputNovoSubgrupo(false)
                        setNovoSubgrupoDestino("")
                      }}
                    >
                      Cancelar
                    </Button>
                  </div>
                ) : (
                  <Select
                    value={subgrupoDestino || "__SEM_SUBGRUPO__"}
                    onValueChange={(v) => setSubgrupoDestino(v === "__SEM_SUBGRUPO__" ? null : v)}
                  >
                    <SelectTrigger id="subgrupo-destino">
                      <SelectValue placeholder="Sem subgrupo" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="__SEM_SUBGRUPO__">Sem subgrupo</SelectItem>
                      {subgruposDestino.map((sub) => (
                        <SelectItem key={sub} value={sub}>
                          {sub}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Preview */}
      {preview && (
        <Card className="mb-6 border-orange-500 bg-orange-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Confirmação de Migração
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 bg-white rounded-lg">
                <div>
                  <div className="font-semibold">{preview.grupo_origem}</div>
                  {preview.subgrupo_origem && (
                    <div className="text-sm text-muted-foreground">{preview.subgrupo_origem}</div>
                  )}
                </div>
                <ArrowRight className="h-6 w-6 text-muted-foreground" />
                <div>
                  <div className="font-semibold">{preview.grupo_destino}</div>
                  {preview.subgrupo_destino && (
                    <div className="text-sm text-muted-foreground">{preview.subgrupo_destino}</div>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 p-4 bg-white rounded-lg">
                <div>
                  <div className="text-sm text-muted-foreground">Transações afetadas</div>
                  <div className="text-2xl font-bold">{preview.total_transacoes}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Tipo Gasto</div>
                  <div className="font-semibold">{preview.tipo_gasto_destino}</div>
                </div>
                <div className="col-span-2">
                  <div className="text-sm text-muted-foreground">Categoria Geral</div>
                  <div className="font-semibold">{preview.categoria_geral_destino}</div>
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <Button
                  onClick={handleExecutar}
                  disabled={executando}
                  className="flex-1"
                >
                  {executando && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Confirmar Migração
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setPreview(null)}
                  disabled={executando}
                >
                  Cancelar
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Botão Preview */}
      {!preview && (
        <div className="flex justify-center">
          <Button
            onClick={handlePreview}
            disabled={!grupoOrigem || !grupoDestino || loadingPreview}
            size="lg"
          >
            {loadingPreview && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Visualizar Impacto
          </Button>
        </div>
      )}
      </div>
    </DashboardLayout>
  )
}
