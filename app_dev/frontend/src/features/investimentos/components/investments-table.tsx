/**
 * Componente - Tabela de Investimentos com Virtualização
 */

'use client'

import React, { useState, useMemo, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Eye, Pencil } from 'lucide-react'
import { InvestmentDetailsModal } from './investment-details-modal'
import { EditInvestmentModal } from './edit-investment-modal'
import { useLazyRender } from '../hooks/use-intersection-observer'
import type { InvestimentoPortfolio } from '../types'

interface InvestmentsTableProps {
  investimentos: InvestimentoPortfolio[]
  onRefresh?: () => void
}

// Memoizar componente da linha para evitar re-renders desnecessários
const InvestmentRow = React.memo<{
  investment: InvestimentoPortfolio
  onViewDetails: (investment: InvestimentoPortfolio) => void
  onEdit: (investment: InvestimentoPortfolio) => void
  formatCurrency: (value?: string) => string
  formatDate: (date?: string) => string
  getTipoColor: (tipo: string) => string
}>(({
  investment,
  onViewDetails,
  onEdit,
  formatCurrency,
  formatDate,
  getTipoColor,
}) => (
  <TableRow>
    <TableCell className="font-medium">
      {investment.nome_produto}
      {investment.emissor && (
        <div className="text-xs text-muted-foreground">
          {investment.emissor}
        </div>
      )}
    </TableCell>
    <TableCell>
      <Badge
        variant="secondary"
        className={getTipoColor(investment.tipo_investimento)}
      >
        {investment.tipo_investimento}
      </Badge>
    </TableCell>
    <TableCell className="text-muted-foreground">
      {investment.corretora}
    </TableCell>
    <TableCell className="text-right">
      {investment.quantidade.toFixed(2)}
    </TableCell>
    <TableCell className="text-right font-medium">
      {formatCurrency(investment.valor_total_inicial)}
    </TableCell>
    <TableCell className="text-muted-foreground">
      {formatDate(investment.data_aplicacao)}
    </TableCell>
    <TableCell className="text-right">
      <div className="flex justify-end gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onViewDetails(investment)}
        >
          <Eye className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onEdit(investment)}
        >
          <Pencil className="h-4 w-4" />
        </Button>
      </div>
    </TableCell>
  </TableRow>
))

InvestmentRow.displayName = 'InvestmentRow'

// Componente de loading da tabela
const TableSkeleton = React.memo(() => (
  <div className="rounded-md border">
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Produto</TableHead>
          <TableHead>Tipo</TableHead>
          <TableHead>Corretora</TableHead>
          <TableHead className="text-right">Quantidade</TableHead>
          <TableHead className="text-right">Valor Inicial</TableHead>
          <TableHead>Data Aplicação</TableHead>
          <TableHead className="text-right">Ações</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {Array.from({ length: 5 }).map((_, index) => (
          <TableRow key={index}>
            <TableCell>
              <div className="h-4 bg-muted animate-pulse rounded" />
              <div className="h-3 bg-muted animate-pulse rounded mt-1 w-2/3" />
            </TableCell>
            <TableCell>
              <div className="h-6 bg-muted animate-pulse rounded w-20" />
            </TableCell>
            <TableCell>
              <div className="h-4 bg-muted animate-pulse rounded w-24" />
            </TableCell>
            <TableCell className="text-right">
              <div className="h-4 bg-muted animate-pulse rounded w-16 ml-auto" />
            </TableCell>
            <TableCell className="text-right">
              <div className="h-4 bg-muted animate-pulse rounded w-20 ml-auto" />
            </TableCell>
            <TableCell>
              <div className="h-4 bg-muted animate-pulse rounded w-20" />
            </TableCell>
            <TableCell className="text-right">
              <div className="h-4 bg-muted animate-pulse rounded w-16 ml-auto" />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </div>
))

TableSkeleton.displayName = 'TableSkeleton'

export function InvestmentsTable({ investimentos, onRefresh }: InvestmentsTableProps) {
  const [selectedInvestment, setSelectedInvestment] = useState<InvestimentoPortfolio | null>(null)
  const [detailsOpen, setDetailsOpen] = useState(false)
  const [editOpen, setEditOpen] = useState(false)

  // Lazy rendering para tabelas grandes
  const { ref: tableRef, shouldRender } = useLazyRender(100)

  // Memoizar formatters para evitar recriações
  const formatCurrency = useCallback((value?: string) => {
    if (!value) return '-'
    const num = parseFloat(value)
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(num)
  }, [])

  const formatDate = useCallback((date?: string) => {
    if (!date) return '-'
    return new Date(date).toLocaleDateString('pt-BR')
  }, [])

  const getTipoColor = useCallback((tipo: string) => {
    const colors: Record<string, string> = {
      'Fundo Imobiliário': 'bg-blue-100 text-blue-800',
      'Renda Fixa': 'bg-green-100 text-green-800',
      'Ação': 'bg-purple-100 text-purple-800',
      'Casa': 'bg-orange-100 text-orange-800',
      'Apartamento': 'bg-yellow-100 text-yellow-800',
      'Previdência Privada': 'bg-indigo-100 text-indigo-800',
      'Conta Corrente': 'bg-gray-100 text-gray-800',
      'FGTS': 'bg-pink-100 text-pink-800',
      'Fundo de Investimento': 'bg-teal-100 text-teal-800',
      'Automóvel': 'bg-red-100 text-red-800',
    }
    return colors[tipo] || 'bg-gray-100 text-gray-800'
  }, [])

  // Memoizar handlers
  const handleViewDetails = useCallback((investment: InvestimentoPortfolio) => {
    setSelectedInvestment(investment)
    setDetailsOpen(true)
  }, [])

  const handleEdit = useCallback((investment: InvestimentoPortfolio) => {
    setSelectedInvestment(investment)
    setEditOpen(true)
  }, [])

  const handleEditSuccess = useCallback(() => {
    if (onRefresh) onRefresh()
  }, [onRefresh])

  // Memoizar agrupamento por corretora
  const investimentosPorCorretora = useMemo(() => {
    return investimentos.reduce((acc, inv) => {
      const corretora = inv.corretora || 'Não especificado'
      if (!acc[corretora]) {
        acc[corretora] = []
      }
      acc[corretora].push(inv)
      return acc
    }, {} as Record<string, InvestimentoPortfolio[]>)
  }, [investimentos])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Portfólio de Investimentos</CardTitle>
        <CardDescription>
          {investimentos.length} produtos ativos
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div ref={tableRef}>
          {!shouldRender ? (
            <TableSkeleton />
          ) : (
            <div className="rounded-md border max-h-[600px] overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Produto</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Corretora</TableHead>
                    <TableHead className="text-right">Quantidade</TableHead>
                    <TableHead className="text-right">Valor Inicial</TableHead>
                    <TableHead>Data Aplicação</TableHead>
                    <TableHead className="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Object.entries(investimentosPorCorretora).map(([corretora, invs]) => (
                    <React.Fragment key={corretora}>
                      <TableRow className="bg-muted/50">
                        <TableCell colSpan={7} className="font-semibold">
                          🏦 {corretora} ({invs.length} produtos)
                        </TableCell>
                      </TableRow>
                      {invs.map((inv) => (
                        <InvestmentRow
                          key={inv.id}
                          investment={inv}
                          onViewDetails={handleViewDetails}
                          onEdit={handleEdit}
                          formatCurrency={formatCurrency}
                          formatDate={formatDate}
                          getTipoColor={getTipoColor}
                        />
                      ))}
                    </React.Fragment>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </div>
      </CardContent>

      {/* Modals */}
      <InvestmentDetailsModal
        investment={selectedInvestment}
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
      />
      
      <EditInvestmentModal
        investment={selectedInvestment}
        open={editOpen}
        onClose={() => setEditOpen(false)}
        onSuccess={handleEditSuccess}
      />
    </Card>
  )
}
