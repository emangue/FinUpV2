"use client"

import React, { useState, useEffect, useCallback } from "react"
import { fetchWithAuth } from "@/core/utils/api-client"
import { API_ENDPOINTS } from "@/core/config/api.config"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Building2, RefreshCw } from "lucide-react"

type StatusType = "OK" | "WIP" | "TBD"

interface BankCompatibility {
  id: number
  bank_name: string
  csv_status: StatusType
  excel_status: StatusType
  pdf_status: StatusType
  ofx_status: StatusType
}

const FORMAT_FIELD_MAP: Record<string, keyof BankCompatibility> = {
  csv: "csv_status",
  excel: "excel_status",
  pdf: "pdf_status",
  ofx: "ofx_status",
}

export default function BancosPage() {
  const [banks, setBanks] = useState<BankCompatibility[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [updateStatus, setUpdateStatus] = useState<string | null>(null)

  const fetchBanks = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetchWithAuth(API_ENDPOINTS.COMPATIBILITY.BASE)
      if (!response.ok) throw new Error("Erro ao carregar bancos")
      const data = await response.json()
      setBanks(data.banks || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro desconhecido")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchBanks()
  }, [fetchBanks])

  const handleUpdateFormat = async (
    id: number,
    format: string,
    newStatus: StatusType
  ) => {
    const fieldName = FORMAT_FIELD_MAP[format.toLowerCase()]
    if (!fieldName) return
    try {
      const response = await fetchWithAuth(
        API_ENDPOINTS.COMPATIBILITY.BY_ID(id),
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ [fieldName]: newStatus }),
        }
      )
      if (!response.ok) throw new Error("Erro ao atualizar")
      await fetchBanks()
      setUpdateStatus(`✅ ${format.toUpperCase()} atualizado para ${newStatus}`)
      setTimeout(() => setUpdateStatus(null), 3000)
    } catch (err) {
      setUpdateStatus(
        `❌ Erro: ${err instanceof Error ? err.message : "Erro desconhecido"}`
      )
      setTimeout(() => setUpdateStatus(null), 5000)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Building2 className="h-6 w-6" />
          Gestão de Bancos
        </h1>
        <p className="text-muted-foreground">
          Configure a compatibilidade de formatos de arquivo por banco
        </p>
      </div>

      {updateStatus && (
        <div className="p-3 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-md text-sm">
          {updateStatus}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Bancos Compatíveis</CardTitle>
          <CardDescription>
            {loading
              ? "Carregando..."
              : `${banks.length} bancos cadastrados`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 p-4 bg-destructive/10 text-destructive rounded-md text-sm">
              ⚠️ {error}
              <button
                onClick={fetchBanks}
                className="ml-2 underline font-medium"
              >
                Tentar novamente
              </button>
            </div>
          )}
          {loading ? (
            <div className="flex justify-center py-8">
              <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[200px]">Banco</TableHead>
                    <TableHead className="text-center">CSV</TableHead>
                    <TableHead className="text-center">Excel</TableHead>
                    <TableHead className="text-center">PDF</TableHead>
                    <TableHead className="text-center">OFX</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {banks.length === 0 ? (
                    <TableRow>
                      <TableCell
                        colSpan={5}
                        className="text-center text-muted-foreground h-32"
                      >
                        Nenhum banco cadastrado
                      </TableCell>
                    </TableRow>
                  ) : (
                    banks.map((bank) => (
                      <TableRow key={bank.id}>
                        <TableCell className="font-medium">
                          {bank.bank_name}
                        </TableCell>
                        {(["csv", "excel", "pdf", "ofx"] as const).map(
                          (fmt) => (
                            <TableCell key={fmt} className="text-center">
                              <Select
                                value={
                                  bank[
                                    FORMAT_FIELD_MAP[fmt] as keyof BankCompatibility
                                  ] as StatusType
                                }
                                onValueChange={(v: StatusType) =>
                                  handleUpdateFormat(bank.id, fmt, v)
                                }
                              >
                                <SelectTrigger className="w-[100px] mx-auto">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="OK">OK</SelectItem>
                                  <SelectItem value="WIP">WIP</SelectItem>
                                  <SelectItem value="TBD">TBD</SelectItem>
                                </SelectContent>
                              </Select>
                            </TableCell>
                          )
                        )}
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="text-sm text-muted-foreground space-y-1">
        <p>
          <strong>Legenda:</strong>
        </p>
        <ul className="ml-4 space-y-1">
          <li>
            <span className="font-semibold text-green-600">OK</span> - Formato
            suportado e testado
          </li>
          <li>
            <span className="font-semibold text-yellow-600">WIP</span> - Em
            desenvolvimento
          </li>
          <li>
            <span className="font-semibold text-red-600">TBD</span> - A ser
            desenvolvido
          </li>
        </ul>
      </div>
    </div>
  )
}
