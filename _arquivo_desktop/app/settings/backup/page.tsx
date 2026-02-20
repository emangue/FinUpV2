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
import { Button } from "@/components/ui/button"
import { Download, Upload, Database, Calendar } from "lucide-react"

interface Backup {
  id: number
  filename: string
  date: string
  size: string
}

export default function BackupPage() {
  const [backups, setBackups] = React.useState<Backup[]>([
    {
      id: 1,
      filename: "financas_backup_2025-01-15.db",
      date: "15/01/2025 14:30",
      size: "2.4 MB"
    },
    {
      id: 2,
      filename: "financas_backup_2025-01-01.db",
      date: "01/01/2025 00:00",
      size: "2.2 MB"
    }
  ])

  const handleCreateBackup = () => {
    const now = new Date()
    const filename = `financas_backup_${now.toISOString().split('T')[0]}.db`
    const newBackup: Backup = {
      id: backups.length + 1,
      filename,
      date: now.toLocaleString('pt-BR'),
      size: "2.5 MB"
    }
    setBackups([newBackup, ...backups])
    alert("Backup criado com sucesso!")
  }

  const handleDownloadBackup = (backup: Backup) => {
    alert(`Download iniciado: ${backup.filename}`)
    // TODO: Implementar download real
  }

  const handleRestoreBackup = (backup: Backup) => {
    if (confirm(`Tem certeza que deseja restaurar o backup ${backup.filename}? Todos os dados atuais serão substituídos.`)) {
      alert(`Restaurando backup: ${backup.filename}`)
      // TODO: Implementar restauração real
    }
  }

  return (
    <DashboardLayout>
      <div className="flex flex-1 flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Backup e Restauração</h1>
            <p className="text-muted-foreground">
              Gerencie backups do banco de dados
            </p>
          </div>
          <Button onClick={handleCreateBackup} className="gap-2">
            <Database className="w-4 h-4" />
            Criar Novo Backup
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Backups Disponíveis</CardTitle>
            <CardDescription>
              Lista de todos os backups criados do sistema
            </CardDescription>
          </CardHeader>
          <CardContent>
            {backups.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                Nenhum backup disponível
              </div>
            ) : (
              <div className="space-y-2">
                {backups.map((backup) => (
                  <div
                    key={backup.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex items-center gap-4">
                      <Database className="w-8 h-8 text-blue-600" />
                      <div>
                        <p className="font-medium">{backup.filename}</p>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {backup.date}
                          </span>
                          <span>{backup.size}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownloadBackup(backup)}
                        className="gap-2"
                      >
                        <Download className="w-4 h-4" />
                        Download
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRestoreBackup(backup)}
                        className="gap-2"
                      >
                        <Upload className="w-4 h-4" />
                        Restaurar
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Backup Automático</CardTitle>
            <CardDescription>
              Configure backups automáticos do sistema
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Ativar Backup Automático</p>
                <p className="text-sm text-muted-foreground">
                  Criar backup automaticamente em intervalos regulares
                </p>
              </div>
              <input type="checkbox" className="w-4 h-4" />
            </div>
            <div className="space-y-2">
              <Label>Frequência de Backup</Label>
              <select className="w-full border rounded-md p-2">
                <option>Diário</option>
                <option>Semanal</option>
                <option>Mensal</option>
              </select>
            </div>
            <div className="space-y-2">
              <Label>Manter Últimos</Label>
              <input
                type="number"
                defaultValue={5}
                className="w-full border rounded-md p-2"
                placeholder="Quantidade de backups a manter"
              />
              <p className="text-xs text-muted-foreground">
                Backups mais antigos serão automaticamente removidos
              </p>
            </div>
            <Button>Salvar Configurações</Button>
          </CardContent>
        </Card>

        <Card className="border-yellow-200 bg-yellow-50">
          <CardHeader>
            <CardTitle className="text-yellow-800">⚠️ Importante</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside space-y-1 text-sm text-yellow-800">
              <li>Faça backups regulares antes de realizar operações importantes</li>
              <li>Guarde os backups em um local seguro, fora do servidor</li>
              <li>Teste a restauração dos backups periodicamente</li>
              <li>A restauração substitui TODOS os dados atuais - use com cuidado</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

function Label({ children }: { children: React.ReactNode }) {
  return <label className="text-sm font-medium">{children}</label>
}
