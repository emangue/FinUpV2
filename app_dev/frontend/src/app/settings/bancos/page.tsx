"use client"

import * as React from "react"
import DashboardLayout from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Plus } from "lucide-react"
import { useBanks, BankFormModal, BanksTable, BankCompatibility } from "@/features/banks"

export default function BancosPage() {
  const { banks, loading, error, updateBank } = useBanks()
  const [modalOpen, setModalOpen] = React.useState(false)
  const [editingBank, setEditingBank] = React.useState<BankCompatibility | null>(null)

  const handleEdit = (bank: BankCompatibility) => {
    setEditingBank(bank)
    setModalOpen(true)
  }

  const handleSave = async (data: { status: 'OK' | 'WIP' | 'TBD' }) => {
    if (editingBank) {
      await updateBank(editingBank.id, data.status)
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

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Bancos Compatíveis</CardTitle>
              <CardDescription>
                {loading ? 'Carregando...' : `${banks.length} bancos/formatos cadastrados`}
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            {error && (
              <div className="mb-4 p-4 bg-yellow-50 text-yellow-800 rounded-md text-sm">
                ⚠️ {error}
              </div>
            )}
            <BanksTable 
              banks={banks}
              onEdit={handleEdit}
            />
          </CardContent>
        </Card>

        <BankFormModal
          open={modalOpen}
          onOpenChange={setModalOpen}
          bank={editingBank}
          onSave={handleSave}
        />
      </div>
    </DashboardLayout>
  )
}
