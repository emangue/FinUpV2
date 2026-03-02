"use client"

/**
 * AddGroupDialog - Modal para criar grupo/subgrupo
 * Usado por: upload (confirm), preview (TransactionCard)
 * Preview faz parte do fluxo de upload (preview → confirm) - import permitido.
 * @see docs/architecture/PROPOSTA_MODULARIDADE_PRAGMATICA.md
 */

import * as React from "react"
import { Plus, Loader2 } from "lucide-react"
import { fetchWithAuth } from "@/core/utils/api-client"
import { API_CONFIG } from "@/core/config/api.config"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"

interface AddGroupDialogProps {
  onGroupAdded: () => void
  existingGroups?: string[]
  compact?: boolean  // Modo compacto (só ícone)
  /** + do Grupo: "grupo" (texto para grupo e subgrupo). + do Subgrupo: "subgrupo" com grupo pré-preenchido, ou "grupo" se nada selecionado */
  initialMode?: "grupo" | "subgrupo"
  /** Grupo já selecionado no dropdown (para + do Subgrupo) */
  initialGrupo?: string
  /** Chamado após criar com sucesso - permite selecionar na transação (grupo, subgrupo) */
  onCreated?: (grupo: string, subgrupo: string) => void
}

export function AddGroupDialog({ onGroupAdded, existingGroups = [], compact = false, initialMode = "grupo", initialGrupo = "", onCreated }: AddGroupDialogProps) {
  const [open, setOpen] = React.useState(false)
  const [loading, setLoading] = React.useState(false)
  const [mode, setMode] = React.useState<"grupo" | "subgrupo">("grupo")
  
  // Grupo novo
  const [nomeGrupo, setNomeGrupo] = React.useState("")
  const [nomeSubgrupo, setNomeSubgrupo] = React.useState("")
  const [tipoGasto, setTipoGasto] = React.useState("")
  const [categoriaGeral, setCategoriaGeral] = React.useState("Despesa")
  
  // Subgrupo para grupo existente
  const [grupoSelecionado, setGrupoSelecionado] = React.useState("")
  const [nomeSubgrupoNovo, setNomeSubgrupoNovo] = React.useState("")

  // Ao abrir o dialog: aplicar initialMode e initialGrupo
  React.useEffect(() => {
    if (open) {
      const effectiveMode = initialMode === "subgrupo" && initialGrupo ? "subgrupo" : "grupo"
      setMode(effectiveMode)
      setGrupoSelecionado(effectiveMode === "subgrupo" ? initialGrupo : "")
    }
  }, [open, initialMode, initialGrupo])

  const resetForm = () => {
    setNomeGrupo("")
    setNomeSubgrupo("")
    setTipoGasto("")
    setCategoriaGeral("Despesa")
    setGrupoSelecionado("")
    setNomeSubgrupoNovo("")
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      if (mode === "grupo") {
        // Criar grupo novo + primeiro subgrupo
        const response = await fetchWithAuth(
          `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/marcacoes/grupos`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              grupo: nomeGrupo.trim(),
              subgrupo: nomeSubgrupo.trim(),
              tipo_gasto: tipoGasto,
              categoria_geral: categoriaGeral,
            }),
          }
        )

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || "Erro ao criar grupo")
        }

        toast.success(`Grupo criado: ${nomeGrupo} / ${nomeSubgrupo}`)
        onCreated?.(nomeGrupo.trim(), nomeSubgrupo.trim())
      } else {
        // Criar subgrupo para grupo existente
        const response = await fetchWithAuth(
          `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/marcacoes/grupos/${encodeURIComponent(grupoSelecionado)}/subgrupos`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              subgrupo: nomeSubgrupoNovo.trim(),
            }),
          }
        )

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || "Erro ao criar subgrupo")
        }

        toast.success(`Subgrupo criado: ${nomeSubgrupoNovo} → ${grupoSelecionado}`)
        onCreated?.(grupoSelecionado, nomeSubgrupoNovo.trim())
      }

      // Fechar modal e notificar parent
      setOpen(false)
      resetForm()
      onGroupAdded()
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Erro desconhecido')
    } finally {
      setLoading(false)
    }
  }

  const isFormValid = () => {
    if (mode === "grupo") {
      return (
        nomeGrupo.trim().length > 0 &&
        nomeSubgrupo.trim().length > 0 &&
        tipoGasto.length > 0
      )
    } else {
      return (
        grupoSelecionado.length > 0 &&
        nomeSubgrupoNovo.trim().length > 0
      )
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {compact ? (
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0 flex-shrink-0">
            <Plus className="h-4 w-4" />
          </Button>
        ) : (
          <Button variant="outline" size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Adicionar Grupo/Subgrupo
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Adicionar Grupo ou Subgrupo</DialogTitle>
            <DialogDescription>
              Crie novos grupos e subgrupos durante a revisão de transações
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            {/* Modo: Grupo novo ou Subgrupo */}
            <div className="space-y-2">
              <Label>O que deseja criar?</Label>
              <RadioGroup value={mode} onValueChange={(v) => setMode(v as "grupo" | "subgrupo")}>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="grupo" id="mode-grupo" />
                  <Label htmlFor="mode-grupo" className="cursor-pointer">
                    Grupo novo (com primeiro subgrupo)
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="subgrupo" id="mode-subgrupo" />
                  <Label htmlFor="mode-subgrupo" className="cursor-pointer">
                    Subgrupo para grupo existente
                  </Label>
                </div>
              </RadioGroup>
            </div>

            {mode === "grupo" ? (
              <>
                {/* Criar grupo novo */}
                <div className="grid gap-2">
                  <Label htmlFor="nome-grupo">Nome do Grupo *</Label>
                  <Input
                    id="nome-grupo"
                    placeholder="Ex: Assinaturas"
                    value={nomeGrupo}
                    onChange={(e) => setNomeGrupo(e.target.value)}
                    required
                  />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="nome-subgrupo">Primeiro Subgrupo *</Label>
                  <Input
                    id="nome-subgrupo"
                    placeholder="Ex: Streaming"
                    value={nomeSubgrupo}
                    onChange={(e) => setNomeSubgrupo(e.target.value)}
                    required
                  />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="tipo-gasto">Tipo de Gasto *</Label>
                  <Select value={tipoGasto} onValueChange={setTipoGasto}>
                    <SelectTrigger id="tipo-gasto">
                      <SelectValue placeholder="Selecione o tipo" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Fixo">Fixo</SelectItem>
                      <SelectItem value="Ajustável">Ajustável</SelectItem>
                      <SelectItem value="Variável">Variável</SelectItem>
                      <SelectItem value="Essencial">Essencial</SelectItem>
                      <SelectItem value="Não Essencial">Não Essencial</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="categoria-geral">Categoria Geral *</Label>
                  <Select value={categoriaGeral} onValueChange={setCategoriaGeral}>
                    <SelectTrigger id="categoria-geral">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Despesa">Despesa</SelectItem>
                      <SelectItem value="Receita">Receita</SelectItem>
                      <SelectItem value="Investimento">Investimento</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </>
            ) : (
              <>
                {/* Criar subgrupo para grupo existente */}
                <div className="grid gap-2">
                  <Label htmlFor="grupo-existente">Grupo *</Label>
                  {grupoSelecionado ? (
                    <div className="rounded-md border bg-muted/50 px-3 py-2 text-sm font-medium">
                      {grupoSelecionado}
                    </div>
                  ) : (
                    <Select value={grupoSelecionado} onValueChange={setGrupoSelecionado}>
                      <SelectTrigger id="grupo-existente">
                        <SelectValue placeholder="Selecione o grupo" />
                      </SelectTrigger>
                      <SelectContent>
                        {existingGroups.map((grupo) => (
                          <SelectItem key={grupo} value={grupo}>
                            {grupo}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="subgrupo-novo">Nome do Subgrupo *</Label>
                  <Input
                    id="subgrupo-novo"
                    placeholder="Ex: Games"
                    value={nomeSubgrupoNovo}
                    onChange={(e) => setNomeSubgrupoNovo(e.target.value)}
                    required
                  />
                  <p className="text-xs text-muted-foreground">
                    O subgrupo herdará as configurações do grupo selecionado
                  </p>
                </div>
              </>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setOpen(false)
                resetForm()
              }}
              disabled={loading}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={!isFormValid() || loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {mode === "grupo" ? "Criar Grupo" : "Adicionar Subgrupo"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
