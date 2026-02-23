'use client'

import React, { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Download, FileSpreadsheet, FileText, Loader2 } from 'lucide-react'
import { InvestimentoPortfolio } from '../types'

interface ExportInvestimentosProps {
  investimentos: InvestimentoPortfolio[]
  filtrosAtivos?: {
    searchTerm?: string
    selectedType?: string
    selectedCorretora?: string
  }
}

export function ExportInvestimentos({ investimentos, filtrosAtivos }: ExportInvestimentosProps) {
  const [exporting, setExporting] = useState(false)

  // Formatar data para exibição
  const formatarData = (dataStr?: string): string => {
    if (!dataStr) return '-'
    try {
      const date = new Date(dataStr)
      return date.toLocaleDateString('pt-BR')
    } catch {
      return dataStr
    }
  }

  // Formatar valor monetário
  const formatarValor = (valor?: string): string => {
    if (!valor) return '0,00'
    const num = parseFloat(valor)
    return num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  }

  // Converter dados para CSV
  const converterParaCSV = (dados: InvestimentoPortfolio[]): string => {
    const headers = [
      'ID',
      'Produto',
      'Corretora',
      'Tipo',
      'Classe',
      'Emissor',
      '% CDI',
      'Data Aplicação',
      'Data Vencimento',
      'Quantidade',
      'Valor Unitário',
      'Valor Total',
      'Status',
      'Criado em'
    ]

    const linhas = dados.map(inv => [
      inv.balance_id,
      `"${inv.nome_produto}"`,
      `"${inv.corretora}"`,
      `"${inv.tipo_investimento}"`,
      inv.classe_ativo ? `"${inv.classe_ativo}"` : '-',
      inv.emissor ? `"${inv.emissor}"` : '-',
      inv.percentual_cdi ? inv.percentual_cdi.toString() : '-',
      formatarData(inv.data_aplicacao),
      formatarData(inv.data_vencimento),
      inv.quantidade.toString(),
      formatarValor(inv.valor_unitario_inicial),
      formatarValor(inv.valor_total_inicial),
      inv.ativo ? 'Ativo' : 'Vencido',
      formatarData(inv.created_at)
    ])

    return [
      headers.join(','),
      ...linhas.map(linha => linha.join(','))
    ].join('\n')
  }

  // Converter dados para formato Excel (HTML table)
  const converterParaExcel = (dados: InvestimentoPortfolio[]): string => {
    const headers = [
      'ID',
      'Produto',
      'Corretora',
      'Tipo',
      'Classe',
      'Emissor',
      '% CDI',
      'Data Aplicação',
      'Data Vencimento',
      'Quantidade',
      'Valor Unitário',
      'Valor Total',
      'Status',
      'Criado em'
    ]

    const linhas = dados.map(inv => `
      <tr>
        <td>${inv.balance_id}</td>
        <td>${inv.nome_produto}</td>
        <td>${inv.corretora}</td>
        <td>${inv.tipo_investimento}</td>
        <td>${inv.classe_ativo || '-'}</td>
        <td>${inv.emissor || '-'}</td>
        <td>${inv.percentual_cdi ? inv.percentual_cdi.toString() : '-'}</td>
        <td>${formatarData(inv.data_aplicacao)}</td>
        <td>${formatarData(inv.data_vencimento)}</td>
        <td>${inv.quantidade}</td>
        <td>${formatarValor(inv.valor_unitario_inicial)}</td>
        <td>${formatarValor(inv.valor_total_inicial)}</td>
        <td>${inv.ativo ? 'Ativo' : 'Vencido'}</td>
        <td>${formatarData(inv.created_at)}</td>
      </tr>
    `).join('')

    return `
      <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel">
      <head>
        <meta charset="UTF-8">
        <style>
          table { border-collapse: collapse; width: 100%; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background-color: #4CAF50; color: white; font-weight: bold; }
          tr:nth-child(even) { background-color: #f2f2f2; }
        </style>
      </head>
      <body>
        <table>
          <thead>
            <tr>
              ${headers.map(h => `<th>${h}</th>`).join('')}
            </tr>
          </thead>
          <tbody>
            ${linhas}
          </tbody>
        </table>
      </body>
      </html>
    `
  }

  // Fazer download do arquivo
  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  // Exportar para CSV
  const exportarCSV = async () => {
    try {
      setExporting(true)
      
      const csv = converterParaCSV(investimentos)
      const timestamp = new Date().toISOString().split('T')[0]
      const filename = `investimentos_${timestamp}.csv`
      
      downloadFile(csv, filename, 'text/csv;charset=utf-8;')
      
      console.log(`✅ ${investimentos.length} investimentos exportados para CSV`)
      toast.success(`${investimentos.length} investimentos exportados para CSV`)
    } catch (error) {
      console.error('Erro ao exportar CSV:', error)
      toast.error('Não foi possível exportar os dados. Tente novamente.')
    } finally {
      setExporting(false)
    }
  }

  // Exportar para Excel
  const exportarExcel = async () => {
    try {
      setExporting(true)
      
      const excel = converterParaExcel(investimentos)
      const timestamp = new Date().toISOString().split('T')[0]
      const filename = `investimentos_${timestamp}.xls`
      
      downloadFile(excel, filename, 'application/vnd.ms-excel')
      
      console.log(`✅ ${investimentos.length} investimentos exportados para Excel`)
      toast.success(`${investimentos.length} investimentos exportados para Excel`)
    } catch (error) {
      console.error('Erro ao exportar Excel:', error)
      toast.error('Não foi possível exportar os dados. Tente novamente.')
    } finally {
      setExporting(false)
    }
  }

  // Construir descrição dos filtros ativos
  const getDescricaoFiltros = (): string | null => {
    if (!filtrosAtivos) return null

    const filtros: string[] = []
    
    if (filtrosAtivos.searchTerm) {
      filtros.push(`Busca: "${filtrosAtivos.searchTerm}"`)
    }
    
    if (filtrosAtivos.selectedType && filtrosAtivos.selectedType !== 'all') {
      filtros.push(`Tipo: ${filtrosAtivos.selectedType}`)
    }
    
    if (filtrosAtivos.selectedCorretora && filtrosAtivos.selectedCorretora !== 'all') {
      filtros.push(`Corretora: ${filtrosAtivos.selectedCorretora}`)
    }

    return filtros.length > 0 ? filtros.join(' | ') : null
  }

  const descricaoFiltros = getDescricaoFiltros()

  if (investimentos.length === 0) {
    return (
      <Button variant="outline" disabled>
        <Download className="h-4 w-4 mr-2" />
        Exportar (sem dados)
      </Button>
    )
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" disabled={exporting}>
          {exporting ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Exportando...
            </>
          ) : (
            <>
              <Download className="h-4 w-4 mr-2" />
              Exportar ({investimentos.length})
            </>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[280px]">
        <DropdownMenuLabel>
          Exportar Investimentos
        </DropdownMenuLabel>
        
        {descricaoFiltros && (
          <>
            <DropdownMenuSeparator />
            <div className="px-2 py-1.5 text-xs text-muted-foreground">
              <strong>Filtros aplicados:</strong>
              <div className="mt-1">{descricaoFiltros}</div>
            </div>
          </>
        )}
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem onClick={exportarExcel} disabled={exporting}>
          <FileSpreadsheet className="h-4 w-4 mr-2 text-green-600" />
          <div className="flex flex-col">
            <span>Exportar como Excel</span>
            <span className="text-xs text-muted-foreground">
              Formato .xls com formatação
            </span>
          </div>
        </DropdownMenuItem>
        
        <DropdownMenuItem onClick={exportarCSV} disabled={exporting}>
          <FileText className="h-4 w-4 mr-2 text-blue-600" />
          <div className="flex flex-col">
            <span>Exportar como CSV</span>
            <span className="text-xs text-muted-foreground">
              Formato texto separado por vírgulas
            </span>
          </div>
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        
        <div className="px-2 py-1.5 text-xs text-muted-foreground">
          <div className="flex items-center justify-between">
            <span>Total de registros:</span>
            <span className="font-semibold text-foreground">{investimentos.length}</span>
          </div>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
