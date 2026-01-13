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

interface TipoGastoItem {
  tipo_gasto: string
  realizado: number
  planejado: number
  percentual: number
  diferenca: number
}

interface DemaisBreakdownModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  tipos: TipoGastoItem[]
  year: number
  month: number
}

export function DemaisBreakdownModal({
  open,
  onOpenChange,
  tipos,
  year,
  month
}: DemaisBreakdownModalProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const totalRealizado = tipos.reduce((sum, item) => sum + item.realizado, 0)
  const totalPlanejado = tipos.reduce((sum, item) => sum + item.planejado, 0)
  const totalTransacoes = tipos.length

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Detalhamento - Demais</DialogTitle>
          <DialogDescription>
            Veja o detalhamento dos tipos de gasto que compõem &quot;Demais&quot;
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {/* Tabela de tipos */}
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted">
                <tr>
                  <th className="text-left p-3 text-sm font-medium">Tipo de Gasto</th>
                  <th className="text-right p-3 text-sm font-medium">Valor Realizado</th>
                  <th className="text-right p-3 text-sm font-medium">Valor Planejado</th>
                  <th className="text-center p-3 text-sm font-medium">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {tipos.map((item) => (
                  <tr key={item.tipo_gasto} className="hover:bg-muted/50 transition-colors">
                    <td className="p-3 text-sm font-medium">{item.tipo_gasto}</td>
                    <td className="p-3 text-sm text-right font-semibold">
                      {formatCurrency(item.realizado)}
                    </td>
                    <td className="p-3 text-sm text-right text-muted-foreground">
                      {formatCurrency(item.planejado)}
                    </td>
                    <td className="p-3 text-center">
                      <Link
                        href={`/transactions?year=${year}&month=${month}&tipo_gasto=${encodeURIComponent(item.tipo_gasto)}`}
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
              <p className="text-xs text-muted-foreground">Soma de {tipos.length} tipos</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Total Planejado</p>
              <p className="text-2xl font-bold text-muted-foreground">{formatCurrency(totalPlanejado)}</p>
              <p className="text-xs text-muted-foreground">Orçamento definido</p>
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
