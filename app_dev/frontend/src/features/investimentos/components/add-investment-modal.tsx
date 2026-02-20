'use client'

/**
 * Componente - Modal de Adicionar Investimento
 */

import React, { useState } from 'react'
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
import { createInvestimento } from '../services/investimentos-api'
import { useToastNotifications, TOAST_MESSAGES } from '../hooks/use-toast-notifications'
import type { CreateInvestimentoForm } from '../types'

interface AddInvestmentModalProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

export function AddInvestmentModal({
  open,
  onClose,
  onSuccess,
}: AddInvestmentModalProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const toast = useToastNotifications()
  
  const [formData, setFormData] = useState<CreateInvestimentoForm>({
    balance_id: '',
    nome_produto: '',
    corretora: '',
    emissor: '',
    tipo_investimento: 'Renda Fixa',
    classe_ativo: '',
    quantidade: 1,
    valor_unitario_inicial: 0,
    valor_total_inicial: 0,
    percentual_cdi: undefined,
    data_aplicacao: new Date().toISOString().split('T')[0],
    data_vencimento: undefined,
  })

  // Calcular valor total automaticamente
  const handleQuantityOrPriceChange = (field: 'quantidade' | 'valor_unitario_inicial', value: number) => {
    const newFormData = { ...formData, [field]: value }
    
    if (field === 'quantidade') {
      newFormData.valor_total_inicial = value * (formData.valor_unitario_inicial ?? 0)
    } else {
      newFormData.valor_total_inicial = (formData.quantidade ?? 0) * value
    }
    
    setFormData(newFormData)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const dataToSend = {
        ...formData,
        balance_id: formData.balance_id.trim() || `web-${Date.now()}-${crypto.randomUUID().replace(/-/g, '').slice(0, 8)}`,
      }
      await createInvestimento(dataToSend)
      toast.success(TOAST_MESSAGES.INVESTMENT_ADDED)
      onSuccess()
      onClose()
      
      // Reset form
      setFormData({
        balance_id: '',
        nome_produto: '',
        corretora: '',
        emissor: '',
        tipo_investimento: 'Renda Fixa',
        classe_ativo: '',
        quantidade: 1,
        valor_unitario_inicial: 0,
        valor_total_inicial: 0,
        percentual_cdi: undefined,
        data_aplicacao: new Date().toISOString().split('T')[0],
        data_vencimento: undefined,
      })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao criar investimento'
      setError(errorMessage)
      toast.error({ ...TOAST_MESSAGES.SAVE_ERROR, description: errorMessage })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Adicionar Novo Investimento</DialogTitle>
          <DialogDescription>
            Cadastre um novo investimento no seu portfólio
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
                placeholder="Ex: Tesouro IPCA+ 2045"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="corretora">Corretora *</Label>
              <Input
                id="corretora"
                value={formData.corretora}
                onChange={(e) => setFormData({ ...formData, corretora: e.target.value })}
                placeholder="Ex: XP Investimentos"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="emissor">Emissor</Label>
              <Input
                id="emissor"
                value={formData.emissor}
                onChange={(e) => setFormData({ ...formData, emissor: e.target.value })}
                placeholder="Ex: Tesouro Nacional"
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
              <Label htmlFor="classe_ativo">Classe do Ativo</Label>
              <Input
                id="classe_ativo"
                value={formData.classe_ativo}
                onChange={(e) => setFormData({ ...formData, classe_ativo: e.target.value })}
                placeholder="Ex: Ativo, Passivo"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="quantidade">Quantidade *</Label>
              <Input
                id="quantidade"
                type="number"
                step="0.01"
                value={formData.quantidade}
                onChange={(e) => handleQuantityOrPriceChange('quantidade', parseFloat(e.target.value) || 0)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="valor_unitario">Valor Unitário (R$) *</Label>
              <Input
                id="valor_unitario"
                type="number"
                step="0.01"
                value={formData.valor_unitario_inicial}
                onChange={(e) => handleQuantityOrPriceChange('valor_unitario_inicial', parseFloat(e.target.value) || 0)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="valor_total">Valor Total (R$)</Label>
              <Input
                id="valor_total"
                type="number"
                step="0.01"
                value={formData.valor_total_inicial}
                disabled
                className="bg-muted"
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
                  percentual_cdi: e.target.value ? parseFloat(e.target.value) : undefined 
                })}
                placeholder="Ex: 100"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="data_aplicacao">Data de Aplicação *</Label>
              <Input
                id="data_aplicacao"
                type="date"
                value={formData.data_aplicacao}
                onChange={(e) => setFormData({ ...formData, data_aplicacao: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="data_vencimento">Data de Vencimento</Label>
              <Input
                id="data_vencimento"
                type="date"
                value={formData.data_vencimento || ''}
                onChange={(e) => setFormData({ ...formData, data_vencimento: e.target.value || undefined })}
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Adicionar Investimento
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
