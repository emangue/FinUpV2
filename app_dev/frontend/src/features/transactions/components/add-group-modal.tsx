"use client"

import * as React from "react"
import { fetchWithAuth } from '@/core/utils/api-client';
import { toast } from 'sonner'
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
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

interface AddGroupModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  tipo: 'grupo' | 'subgrupo'
  grupoAtual?: string  // Grupo selecionado na transação (para contexto)
  onSuccess: () => void
}

export function AddGroupModal({
  open,
  onOpenChange,
  tipo,
  grupoAtual,
  onSuccess
}: AddGroupModalProps) {
  const [nome, setNome] = React.useState("")
  const [grupo, setGrupo] = React.useState(grupoAtual || "")
  const [tipoGasto, setTipoGasto] = React.useState("")
  const [categoriaGeral, setCategoriaGeral] = React.useState("Despesa")
  const [grupos, setGrupos] = React.useState<any[]>([])
  const [tiposGastoDisponiveis, setTiposGastoDisponiveis] = React.useState<string[]>([])
  const [categoriasDisponiveis, setCategoriasDisponiveis] = React.useState<string[]>([])
  const [loading, setLoading] = React.useState(false)

  // Carregar grupos existentes se for criar subgrupo
  React.useEffect(() => {
    if (tipo === 'subgrupo') {
      fetchGrupos()
    } else {
      fetchOpcoes()
    }
  }, [tipo])

  // Atualizar grupo quando grupoAtual mudar
  React.useEffect(() => {
    if (grupoAtual && tipo === 'subgrupo') {
      setGrupo(grupoAtual)
    }
  }, [grupoAtual, tipo])

  // Quando selecionar grupo, buscar TipoGasto e CategoriaGeral da base_grupos_config
  React.useEffect(() => {
    if (tipo === 'subgrupo' && grupo && grupos.length > 0) {
      const grupoConfig = grupos.find(g => g.nome_grupo === grupo)
      if (grupoConfig) {
        setTipoGasto(grupoConfig.tipo_gasto_padrao || '')
        setCategoriaGeral(grupoConfig.categoria_geral || 'Despesa')
      }
    }
  }, [grupo, grupos, tipo])

  const fetchGrupos = async () => {
    try {
      const response = await fetchWithAuth('/api/grupos')
      if (response.ok) {
        const data = await response.json()
        setGrupos(data.grupos)
      }
    } catch (error) {
      // Erro silencioso - grupos não carregados
    }
  }

  const fetchOpcoes = async () => {
    try {
      const response = await fetchWithAuth('/api/grupos/opcoes')
      if (response.ok) {
        const data = await response.json()
        setTiposGastoDisponiveis(data.tipos_gasto || [])
        setCategoriasDisponiveis(data.categorias_gerais || [])
      }
    } catch (error) {
      // Fallback para valores padrão
      setTiposGastoDisponiveis(['Fixo', 'Ajustável', 'Investimentos', 'Sem Categoria'])
      setCategoriasDisponiveis(['Despesa', 'Receita', 'Investimento', 'Transferência'])
    }
  }

  const handleSave = async () => {
    if (!nome.trim()) {
      toast.error('Por favor, insira um nome')
      return
    }

    setLoading(true)
    try {
      if (tipo === 'grupo') {
        // Criar GRUPO na base_grupos_config
        const response = await fetchWithAuth('/api/grupos', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            nome_grupo: nome.trim(),
            tipo_gasto_padrao: tipoGasto || 'Ajustável',
            categoria_geral: categoriaGeral
          })
        })

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Erro ao criar grupo')
        }
      } else {
        // Criar SUBGRUPO na base_marcacoes
        if (!grupo) {
          toast.error('Selecione um grupo primeiro')
          return
        }
        if (!tipoGasto) {
          toast.error('Selecione um tipo de gasto')
          return
        }

        const response = await fetchWithAuth('/api/v1/categories', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            GRUPO: grupo,
            SUBGRUPO: nome.trim(),
            TipoGasto: tipoGasto
          })
        })

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Erro ao criar subgrupo')
        }
      }

      setNome("")
      setGrupo(grupoAtual || "")
      setTipoGasto("")
      onSuccess()
      onOpenChange(false)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Erro ao criar ' + (tipo === 'grupo' ? 'grupo' : 'subgrupo'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            Adicionar Novo {tipo === 'grupo' ? 'Grupo' : 'Subgrupo'}
          </DialogTitle>
          <DialogDescription>
            Crie um novo {tipo === 'grupo' ? 'grupo' : 'subgrupo'} para categorizar suas transações.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          {tipo === 'subgrupo' && (
            <div className="grid gap-2">
              <Label htmlFor="grupo">Grupo *</Label>
              <Select value={grupo} onValueChange={setGrupo}>
                <SelectTrigger id="grupo">
                  <SelectValue placeholder="Selecione o grupo" />
                </SelectTrigger>
                <SelectContent>
                  {grupos.map((g) => (
                    <SelectItem key={g.nome_grupo} value={g.nome_grupo}>{g.nome_grupo}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          <div className="grid gap-2">
            <Label htmlFor="nome">Nome do {tipo === 'grupo' ? 'Grupo' : 'Subgrupo'} *</Label>
            <Input
              id="nome"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              placeholder={`Ex: ${tipo === 'grupo' ? 'Lazer, Saúde, Educação' : 'Cinema, Academia, Cursos'}`}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="tipoGasto">Tipo de Gasto *</Label>
            <Select 
              value={tipoGasto} 
              onValueChange={setTipoGasto}
              disabled={tipo === 'subgrupo'}
            >
              <SelectTrigger id="tipoGasto">
                <SelectValue placeholder="Selecione o tipo" />
              </SelectTrigger>
              <SelectContent>
                {tiposGastoDisponiveis.map((t) => (
                  <SelectItem key={t} value={t}>{t}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {tipo === 'subgrupo' && tipoGasto && (
              <p className="text-xs text-muted-foreground">
                Herdado do grupo "{grupo}"
              </p>
            )}
          </div>

          {tipo === 'grupo' && (
            <div className="grid gap-2">
              <Label htmlFor="categoriaGeral">Categoria Geral *</Label>
              <Select value={categoriaGeral} onValueChange={setCategoriaGeral}>
                <SelectTrigger id="categoriaGeral">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {categoriasDisponiveis.map((c) => (
                    <SelectItem key={c} value={c}>{c}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button 
            onClick={handleSave} 
            disabled={loading || !nome.trim() || !tipoGasto || (tipo === 'subgrupo' && !grupo)}
          >
            {loading ? 'Criando...' : 'Criar'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
