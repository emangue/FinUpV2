"use client"

import * as React from "react"
import Link from "next/link"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"

interface GrupoItem {
  grupo: string
  realizado: number
  planejado: number
  percentual: number
  diferenca: number
}

interface GrupoBreakdownModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  grupos: GrupoItem[]
  year: number
  month: number
}

export function GrupoBreakdownModal({
  open,
  onOpenChange,
  grupos,
  year,
  month
}: GrupoBreakdownModalProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  // Verificação de segurança para evitar erro
  const gruposSeguro = grupos || []
  const totalRealizado = gruposSeguro.reduce((sum, item) => sum + item.realizado, 0)
  const totalPlanejado = gruposSeguro.reduce((sum, item) => sum + item.planejado, 0)
  const totalTransacoes = gruposSeguro.length

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Detalhamento por Grupo</DialogTitle>
          <DialogDescription>
            Veja o detalhamento dos grupos de gasto e seus valores
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {/* Tabela de grupos */}
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted">
                <tr>
                  <th className="text-left p-3 text-sm font-medium">Grupo</th>
                  <th className="text-right p-3 text-sm font-medium">Valor Realizado</th>
                  <th className="text-right p-3 text-sm font-medium">Valor Planejado</th>
                  <th className="text-center p-3 text-sm font-medium">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {gruposSeguro.map((item) => (
                  <tr key={item.grupo} className="hover:bg-muted/50 transition-colors">
                    <td className="p-3 text-sm font-medium">{item.grupo}</td>
                    <td className="p-3 text-sm text-right font-semibold">
                      {formatCurrency(item.realizado)}
                    </td>
                    <td className="p-3 text-sm text-right text-muted-foreground">
                      {formatCurrency(item.planejado)}
                    </td>
                    <td className="p-3 text-center">
                      <Link
                        href={`/transactions?year=${year}&month=${month}&grupo=${encodeURIComponent(item.grupo)}`}
                        onClick={() => onOpenChange(false)}
                      >
                        <Button variant="ghost" size="sm" className="gap-2">
                          Ver Transações
                          <ArrowRight className="h-4 w-4" />
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Totais */}
          <div className="grid grid-cols-2 gap-4 pt-4 border-t">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Total Realizado</p>
              <p className="text-2xl font-bold">{formatCurrency(totalRealizado)}</p>
              <p className="text-xs text-muted-foreground">Soma de {gruposSeguro.length} grupos</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Total Planejado</p>
              <p className="text-2xl font-bold text-muted-foreground">{formatCurrency(totalPlanejado)}</p>
              <p className="text-xs text-muted-foreground">Orçamento definido</p>
            </div>
          </div>

          {/* Diferença e Percentual */}
          <div className="grid grid-cols-2 gap-4 pt-4 border-t">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Diferença</p>
              <p className={`text-2xl font-bold ${totalRealizado > totalPlanejado ? 'text-red-600' : 'text-green-600'}`}>
                {totalRealizado > totalPlanejado ? '+' : ''}{formatCurrency(totalRealizado - totalPlanejado)}
              </p>
              <p className="text-xs text-muted-foreground">
                {totalRealizado > totalPlanejado ? 'Acima' : 'Abaixo'} do planejado
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Percentual</p>
              <p className={`text-2xl font-bold ${totalPlanejado > 0 && (totalRealizado / totalPlanejado * 100) >= 100 ? 'text-red-600' : 'text-green-600'}`}>
                {totalPlanejado > 0 ? `${((totalRealizado / totalPlanejado) * 100).toFixed(1)}%` : 'N/A'}
              </p>
              <p className="text-xs text-muted-foreground">
                Do orçamento utilizado
              </p>
            </div>
          </div>

          {/* Botão fechar */}
          <div className="flex justify-end pt-4">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Fechar
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// Export com nome antigo para compatibilidade
export { GrupoBreakdownModal as DemaisBreakdownModal };
