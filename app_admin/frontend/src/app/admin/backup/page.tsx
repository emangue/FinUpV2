"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Database } from "lucide-react"

export default function BackupPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Backup</h1>
        <p className="text-muted-foreground">Exportar dados do sistema</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Backup
          </CardTitle>
          <CardDescription>
            Endpoint de backup ainda não implementado no backend
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Para criar backup, use scripts no servidor ou copie manualmente o
            arquivo database/financas_dev.db (ou o banco PostgreSQL em produção).
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
