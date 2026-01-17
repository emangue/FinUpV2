'use client'

/**
 * Componente - Modal de Edição de Investimento
 */

import React, { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Loader2 } from 'lucide-react'
import type { InvestimentoPortfolio } from '../types'
import { updateInvestimento } from '../services/investimentos-api'

interface EditInvestmentModalProps {
  investment: InvestimentoPortfolio | null
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

export function EditInvestmentModal({
  investment,
  open,
  onClose,
  onSuccess,
}: EditInvestmentModalProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    nome_produto: '',
    corretora: '',
    emissor: '',
    tipo_investimento: '',
    classe_ativo: '',
    quantidade: 0,
    valor_unitario_inicial: 0,
    percentual_cdi: null as number | null,
    data_aplicacao: '',
    data_vencimento: '',
    ativo: true,
  })

  useEffect(() => {
    if (investment) {
      setFormData({
        nome_produto: investment.nome_produto,
        corretora: investment.corretora,
        emissor: investment.emissor || '',
        tipo_investimento: investment.tipo_investimento,
        classe_ativo: investment.classe_ativo || '',
        quantidade: investment.quantidade ?? 0,
        valor_unitario_inicial: parseFloat(investment.valor_unitario_inicial || '0'),
        percentual_cdi: investment.percentual_cdi ?? null,
        data_aplicacao: investment.data_aplicacao || '',
        data_vencimento: investment.data_vencimento || '',
        ativo: investment.ativo,
      })
    }
  }, [investment])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!investment) return

    setLoading(true)
    setError(null)

    try {
      // Convert formData to match CreateInvestimentoForm types
      const updateData = {
        ...formData,
        percentual_cdi: formData.percentual_cdi ?? undefined,
      }
      
      await updateInvestimento(investment.id, updateData)
      onSuccess()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao atualizar investimento')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Editar Investimento</DialogTitle>
          <DialogDescription>
            Atualize as informações do investimento
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              {error}
            </div>
          )}

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="nome_produto">Nome do Produto *</Label>
              <Input
                id="nome_produto"
                value={formData.nome_produto}
                onChange={(e) => setFormData({ ...formData, nome_produto: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="corretora">Corretora *</Label>
              <Input
                id="corretora"
                value={formData.corretora}
                onChange={(e) => setFormData({ ...formData, corretora: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="emissor">Emissor</Label>
              <Input
                id="emissor"
                value={formData.emissor}
                onChange={(e) => setFormData({ ...formData, emissor: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="tipo_investimento">Tipo de Investimento *</Label>
              <Select
                value={formData.tipo_investimento}
                onValueChange={(value) => setFormData({ ...formData, tipo_investimento: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Fundo Imobiliário">Fundo Imobiliário</SelectItem>
                  <SelectItem value="Renda Fixa">Renda Fixa</SelectItem>
                  <SelectItem value="Ação">Ação</SelectItem>
                  <SelectItem value="Casa">Casa</SelectItem>
                  <SelectItem value="Apartamento">Apartamento</SelectItem>
                  <SelectItem value="Previdência Privada">Previdência Privada</SelectItem>
                  <SelectItem value="Conta Corrente">Conta Corrente</SelectItem>
                  <SelectItem value="Automóvel">Automóvel</SelectItem>
                  <SelectItem value="FGTS">FGTS</SelectItem>
                  <SelectItem value="Fundo de Investimento">Fundo de Investimento</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="quantidade">Quantidade *</Label>
              <Input
                id="quantidade"
                type="number"
                step="0.01"
                value={formData.quantidade}
                onChange={(e) => setFormData({ ...formData, quantidade: parseFloat(e.target.value) })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="valor_unitario">Valor Unitário *</Label>
              <Input
                id="valor_unitario"
                type="number"
                step="0.01"
                value={formData.valor_unitario_inicial}
                onChange={(e) => setFormData({ ...formData, valor_unitario_inicial: parseFloat(e.target.value) })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="percentual_cdi">% CDI</Label>
              <Input
                id="percentual_cdi"
                type="number"
                step="0.01"
                value={formData.percentual_cdi || ''}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  percentual_cdi: e.target.value ? parseFloat(e.target.value) : null 
                })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="data_aplicacao">Data de Aplicação</Label>
              <Input
                id="data_aplicacao"
                type="date"
                value={formData.data_aplicacao}
                onChange={(e) => setFormData({ ...formData, data_aplicacao: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="ativo">Status</Label>
              <Select
                value={formData.ativo ? 'true' : 'false'}
                onValueChange={(value) => setFormData({ ...formData, ativo: value === 'true' })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="true">Ativo</SelectItem>
                  <SelectItem value="false">Inativo</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Salvar alterações
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
