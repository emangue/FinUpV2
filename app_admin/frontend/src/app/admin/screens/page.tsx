"use client"

import { useEffect, useState } from "react"
import { fetchWithAuth } from "@/core/utils/api-client"
import { API_ENDPOINTS } from "@/core/config/api.config"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Eye, Save, RefreshCw, CheckCircle2, XCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

interface ScreenStatus {
  id: number
  screen_key: string
  screen_name: string
  status: "P" | "A" | "D"
  display_order?: number
}

const STATUS_LABELS = {
  P: { label: "Produção", badge: "bg-green-500" },
  A: { label: "Admin", badge: "bg-orange-500" },
  D: { label: "Development", badge: "bg-purple-500" },
}

export default function ScreensPage() {
  const [screens, setScreens] = useState<ScreenStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [changes, setChanges] = useState<Map<number, "P" | "A" | "D">>(new Map())
  const [notification, setNotification] = useState<{
    type: "success" | "error"
    message: string
  } | null>(null)

  const fetchScreens = async () => {
    try {
      setLoading(true)
      const response = await fetchWithAuth(API_ENDPOINTS.SCREENS.ADMIN_ALL)
      if (!response.ok) throw new Error("Erro ao carregar telas")
      const data = await response.json()
      setScreens(data)
      setChanges(new Map())
    } catch (error) {
      console.error("Erro ao buscar telas:", error)
      setNotification({
        type: "error",
        message:
          "Não foi possível carregar as telas. Verifique se o backend está rodando.",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchScreens()
  }, [])

  useEffect(() => {
    if (notification?.type === "error") {
      const t = setTimeout(() => setNotification(null), 5000)
      return () => clearTimeout(t)
    }
  }, [notification])

  const handleStatusChange = (id: number, newStatus: "P" | "A" | "D") => {
    setChanges((prev) => new Map(prev).set(id, newStatus))
  }

  const getCurrentStatus = (screen: ScreenStatus): "P" | "A" | "D" => {
    return changes.get(screen.id) ?? screen.status
  }

  const hasChanges = changes.size > 0

  const handleSave = async () => {
    if (!hasChanges) return
    try {
      setSaving(true)
      const promises = Array.from(changes.entries()).map(([id, status]) =>
        fetchWithAuth(API_ENDPOINTS.SCREENS.UPDATE(id), {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status }),
        })
      )
      const results = await Promise.all(promises)
      const allSuccess = results.every((r) => r.ok)
      if (allSuccess) {
        setNotification({
          type: "success",
          message: `${changes.size} tela(s) atualizada(s) com sucesso!`,
        })
        await fetchScreens()
      } else {
        throw new Error("Algumas atualizações falharam")
      }
    } catch (error) {
      setNotification({
        type: "error",
        message:
          error instanceof Error ? error.message : "Erro ao salvar alterações.",
      })
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => setChanges(new Map())

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[300px]">
        <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Eye className="h-6 w-6" />
            Visibilidade de Telas
          </h1>
          <p className="text-muted-foreground">
            Controle quais telas aparecem para diferentes tipos de usuários
          </p>
        </div>
        {hasChanges && (
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleReset} disabled={saving}>
              Cancelar
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  Salvando...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Salvar {changes.size} alteração(ões)
                </>
              )}
            </Button>
          </div>
        )}
      </div>

      {notification && (
        <Alert
          variant={notification.type === "success" ? "default" : "destructive"}
        >
          {notification.type === "success" ? (
            <CheckCircle2 className="h-4 w-4" />
          ) : (
            <XCircle className="h-4 w-4" />
          )}
          <AlertTitle>
            {notification.type === "success" ? "Sucesso!" : "Erro"}
          </AlertTitle>
          <AlertDescription>{notification.message}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Legenda de Status</CardTitle>
          <CardDescription>
            P = Produção (todos) | A = Admin | D = Development
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-4">
          {(["P", "A", "D"] as const).map((key) => (
            <div key={key} className="flex items-center gap-2">
              <Badge className={`${STATUS_LABELS[key].badge} text-white`}>
                {key}
              </Badge>
              <span className="text-sm">{STATUS_LABELS[key].label}</span>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Telas ({screens.length})</CardTitle>
          <CardDescription>
            Selecione o status de cada tela e clique em Salvar
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {screens
              .sort((a, b) => (a.display_order ?? 0) - (b.display_order ?? 0))
              .map((screen) => {
                const currentStatus = getCurrentStatus(screen)
                const hasChange = changes.has(screen.id)
                return (
                  <div
                    key={screen.id}
                    className={`flex items-center justify-between p-4 border rounded-lg ${
                      hasChange ? "bg-accent/50 border-primary" : ""
                    }`}
                  >
                    <div>
                      <div className="font-medium">{screen.screen_name}</div>
                      <div className="text-xs text-muted-foreground">
                        {screen.screen_key}
                      </div>
                    </div>
                    <Select
                      value={currentStatus}
                      onValueChange={(v: "P" | "A" | "D") =>
                        handleStatusChange(screen.id, v)
                      }
                    >
                      <SelectTrigger className="w-[140px]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="P">Produção</SelectItem>
                        <SelectItem value="A">Admin</SelectItem>
                        <SelectItem value="D">Development</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )
              })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
