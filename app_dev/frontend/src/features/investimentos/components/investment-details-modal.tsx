'use client'

/**
 * Componente - Modal de Detalhes do Investimento
 * Visualização completa de um investimento
 */

import React from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import type { InvestimentoPortfolio } from '../types'
import { 
  Building2, 
  Calendar, 
  TrendingUp, 
  Wallet, 
  Package,
  Hash,
  Percent,
  DollarSign 
} from 'lucide-react'

interface InvestmentDetailsModalProps {
  investment: InvestimentoPortfolio | null
  open: boolean
  onClose: () => void
}

export function InvestmentDetailsModal({
  investment,
  open,
  onClose,
}: InvestmentDetailsModalProps) {
  if (!investment) return null

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value)
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('pt-BR').format(date)
  }

  const getTipoColor = (tipo: string) => {
    const colors: Record<string, string> = {
      'Fundo Imobiliário': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      'Casa': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
      'Renda Fixa': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      'Apartamento': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'Previdência Privada': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      'Conta Corrente': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
      'Automóvel': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      'FGTS': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200',
      'Fundo de Investimento': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
      'Ação': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    }
    return colors[tipo] || 'bg-slate-100 text-slate-800'
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            {investment.nome_produto}
          </DialogTitle>
          <DialogDescription>
            Detalhes completos do investimento
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Tipo e Status */}
          <div className="flex items-center gap-2">
            <Badge className={getTipoColor(investment.tipo_investimento)}>
              {investment.tipo_investimento}
            </Badge>
            <Badge variant={investment.ativo ? 'default' : 'secondary'}>
              {investment.ativo ? 'Ativo' : 'Inativo'}
            </Badge>
          </div>

          <Separator />

          {/* Informações Básicas */}
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Building2 className="h-4 w-4" />
                <span>Corretora</span>
              </div>
              <p className="font-medium">{investment.corretora}</p>
            </div>

            {investment.emissor && (
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Building2 className="h-4 w-4" />
                  <span>Emissor</span>
                </div>
                <p className="font-medium">{investment.emissor}</p>
              </div>
            )}

            <div className="space-y-1">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Hash className="h-4 w-4" />
                <span>ID</span>
              </div>
              <p className="font-mono text-sm">{investment.id}</p>
            </div>

            {investment.classe_ativo && (
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Package className="h-4 w-4" />
                  <span>Classe</span>
                </div>
                <p className="font-medium">{investment.classe_ativo}</p>
              </div>
            )}
          </div>

          <Separator />

          {/* Valores */}
          <div>
            <h3 className="mb-4 flex items-center gap-2 font-semibold">
              <DollarSign className="h-4 w-4" />
              Valores
            </h3>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Quantidade</p>
                <p className="text-2xl font-bold">
                  {investment.quantidade.toFixed(2)}
                </p>
              </div>

              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Valor Unitário Inicial</p>
                <p className="text-2xl font-bold">
                  {formatCurrency(parseFloat(investment.valor_unitario_inicial || '0'))}
                </p>
              </div>

              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Valor Total Inicial</p>
                <p className="text-2xl font-bold text-primary">
                  {formatCurrency(parseFloat(investment.valor_total_inicial || '0'))}
                </p>
              </div>

              {investment.percentual_cdi !== null && (
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Percent className="h-4 w-4" />
                    <span>% CDI</span>
                  </div>
                  <p className="text-2xl font-bold">
                    {investment.percentual_cdi}%
                  </p>
                </div>
              )}
            </div>
          </div>

          <Separator />

          {/* Datas */}
          <div>
            <h3 className="mb-4 flex items-center gap-2 font-semibold">
              <Calendar className="h-4 w-4" />
              Datas
            </h3>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Data de Aplicação</p>
                <p className="font-medium">
                  {formatDate(investment.data_aplicacao || null)}
                </p>
              </div>

              {investment.data_vencimento && (
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Data de Vencimento</p>
                  <p className="font-medium">
                    {formatDate(investment.data_vencimento || null)}
                  </p>
                </div>
              )}

              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Criado em</p>
                <p className="text-sm text-muted-foreground">
                  {formatDate(investment.created_at)}
                </p>
              </div>

              {investment.updated_at && (
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Atualizado em</p>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(investment.updated_at)}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
