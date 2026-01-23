"use client"

import * as React from "react"
import DashboardLayout from "@/components/dashboard-layout"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useBanks, BanksTable, StatusType } from "@/features/banks"

export default function BancosPage() {
  const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1` : "http://localhost:8000/api/v1"
  const { banks, loading, error, fetchBanks } = useBanks()
  const [updateStatus, setUpdateStatus] = React.useState<string | null>(null)

  const handleUpdateFormat = async (id: number, format: string, newStatus: StatusType) => {
    try {
      // Mapear formato para nome do campo
      const formatFieldMap: Record<string, string> = {
        'csv': 'csv_status',
        'excel': 'excel_status',
        'pdf': 'pdf_status',
        'ofx': 'ofx_status'
      }
      
      const fieldName = formatFieldMap[format.toLowerCase()]
      if (!fieldName) {
        throw new Error(`Formato inválido: ${format}`)
      }

      // Atualizar via API
      const response = await fetch(`${apiUrl}/compatibility/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [fieldName]: newStatus })
      })

      if (!response.ok) {
        throw new Error('Erro ao atualizar status')
      }

      // Recarregar dados
      await fetchBanks()

      // Mostrar feedback
      setUpdateStatus(`✅ ${format.toUpperCase()} atualizado para ${newStatus}`)
      setTimeout(() => setUpdateStatus(null), 3000)
    } catch (err: any) {
      setUpdateStatus(`❌ Erro: ${err.message || 'Erro desconhecido'}`)
      setTimeout(() => setUpdateStatus(null), 5000)
    }
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Gestão de Bancos</h1>
            <p className="text-muted-foreground">
              Configure a compatibilidade de formatos de arquivo por banco
            </p>
          </div>
        </div>

        {updateStatus && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-md text-sm text-blue-800">
            {updateStatus}
          </div>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Bancos Compatíveis</CardTitle>
            <CardDescription>
              {loading ? 'Carregando...' : `${banks.length} bancos cadastrados`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <div className="mb-4 p-4 bg-yellow-50 text-yellow-800 rounded-md text-sm">
                ⚠️ {error}
              </div>
            )}
            <BanksTable 
              banks={banks}
              onUpdateFormat={handleUpdateFormat}
            />
          </CardContent>
        </Card>

        <div className="text-sm text-muted-foreground space-y-1">
          <p>📋 <strong>Legenda:</strong></p>
          <ul className="ml-4 space-y-1">
            <li>• <span className="font-semibold text-green-600">OK</span> - Formato suportado e testado</li>
            <li>• <span className="font-semibold text-yellow-600">WIP</span> - Em desenvolvimento</li>
            <li>• <span className="font-semibold text-red-600">TBD</span> - A ser desenvolvido</li>
          </ul>
          <p className="mt-2 text-xs">
            💡 Clique nos dropdowns para alterar o status de cada formato
          </p>
        </div>
      </div>
    </DashboardLayout>
  )
}
