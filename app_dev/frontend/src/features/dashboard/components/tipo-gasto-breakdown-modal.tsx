"use client"

import * as React from "react"
import { useState, useEffect } from "react"
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

interface SubgrupoItem {
  subgrupo: string
  valor: number
  percentual: number
}

interface TipoGastoBreakdownData {
  subgrupos: SubgrupoItem[]
  total_realizado: number
  total_planejado: number
}

interface TipoGastoBreakdownModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  grupo: string
  year: number
  month: number
}

export function TipoGastoBreakdownModal({
  open,
  onOpenChange,
  grupo,
  year,
  month
}: TipoGastoBreakdownModalProps) {
  const [data, setData] = useState<SubgrupoItem[]>([])
  const [totalPlanejado, setTotalPlanejado] = useState<number>(0)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (open && grupo) {
      fetchSubgrupos()
    }
  }, [open, grupo, year, month])

  const fetchSubgrupos = async () => {
    try {
      setLoading(true)
      const url = month === 0 
        ? `/api/dashboard/subgrupos-by-tipo?year=${year}&grupo=${encodeURIComponent(grupo)}&ytd=true`
        : `/api/dashboard/subgrupos-by-tipo?year=${year}&month=${month}&grupo=${encodeURIComponent(grupo)}`
      
      const response = await fetch(url)
      if (!response.ok) throw new Error('Erro ao buscar subgrupos')
      
      const result: TipoGastoBreakdownData = await response.json()
      setData(result.subgrupos || [])
      setTotalPlanejado(result.total_planejado || 0)
    } catch (error) {
      console.error('Erro ao buscar subgrupos:', error)
      setData([])
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const totalValor = data.reduce((sum, item) => sum + item.valor, 0)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Detalhamento - {grupo}</DialogTitle>
          <DialogDescription>
            Veja o detalhamento dos subgrupos que compõem &quot;{grupo}&quot;
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-muted-foreground">Carregando...</p>
            </div>
          ) : data.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Nenhum subgrupo encontrado</p>
            </div>
          ) : (
            <>
              {/* Tabela de subgrupos */}
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-muted">
                    <tr>
                      <th className="text-left p-3 text-sm font-medium">Subgrupo</th>
                      <th className="text-right p-3 text-sm font-medium">Valor</th>
                      <th className="text-right p-3 text-sm font-medium">% do Total</th>
                      <th className="text-center p-3 text-sm font-medium">Ações</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {data.map((item) => (
                      <tr key={item.subgrupo} className="hover:bg-muted/50 transition-colors">
                        <td className="p-3 text-sm font-medium">{item.subgrupo || 'Sem subgrupo'}</td>
                        <td className="p-3 text-sm text-right font-semibold">
                          {formatCurrency(item.valor)}
                        </td>
                        <td className="p-3 text-sm text-right text-muted-foreground">
                          {item.percentual.toFixed(1)}%
                        </td>
                        <td className="p-3 text-center">
                          <Link
                            href={
                              month === 0
                                ? `/transactions?year=${year}&grupo=${encodeURIComponent(grupo)}&subgrupo=${encodeURIComponent(item.subgrupo || '')}`
                                : `/transactions?year=${year}&month=${month}&grupo=${encodeURIComponent(grupo)}&subgrupo=${encodeURIComponent(item.subgrupo || '')}`
                            }
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
                  <p className="text-2xl font-bold">{formatCurrency(totalValor)}</p>
                  <p className="text-xs text-muted-foreground">Soma de {data.length} subgrupos</p>
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
                  <p className={`text-2xl font-bold ${totalValor > totalPlanejado ? 'text-red-600' : 'text-green-600'}`}>
                    {totalValor > totalPlanejado ? '+' : ''}{formatCurrency(totalValor - totalPlanejado)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {totalValor > totalPlanejado ? 'Acima' : 'Abaixo'} do planejado
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Percentual</p>
                  <p className={`text-2xl font-bold ${totalPlanejado > 0 && (totalValor / totalPlanejado * 100) >= 100 ? 'text-red-600' : 'text-green-600'}`}>
                    {totalPlanejado > 0 ? `${((totalValor / totalPlanejado) * 100).toFixed(1)}%` : 'N/A'}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Do orçamento utilizado
                  </p>
                </div>
              </div>
            </>
          )}

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
