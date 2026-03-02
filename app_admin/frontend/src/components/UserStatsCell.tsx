"use client"

import useSWR from "swr"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { fetchWithAuth } from "@/core/utils/api-client"
import { API_CONFIG } from "@/core/config/api.config"

interface UserStats {
  total_transacoes: number
  total_uploads: number
  ultimo_upload_em: string | null
  total_grupos: number
  tem_plano: boolean
  tem_investimentos: boolean
}

const API_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`

const fetcher = (url: string) =>
  fetchWithAuth(url).then((r) => (r.ok ? r.json() : Promise.reject(new Error("Erro ao carregar stats"))))

export function UserStatsCell({ userId }: { userId: number }) {
  const { data, isLoading } = useSWR<UserStats>(`${API_URL}/users/${userId}/stats`, fetcher)

  if (isLoading) return <span className="text-sm text-muted-foreground">…</span>
  if (!data) return <span className="text-sm text-muted-foreground">Sem dados</span>

  const ultimo = data.ultimo_upload_em
    ? new Date(data.ultimo_upload_em).toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" })
    : "nunca"

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span className="cursor-help text-sm">
          {data.total_transacoes.toLocaleString()} tx · últ. {ultimo}
        </span>
      </TooltipTrigger>
      <TooltipContent>
        <p>
          {data.total_uploads} uploads · {data.total_grupos} grupos
        </p>
        <p>{data.tem_plano ? "✅ Tem plano" : "❌ Sem plano"}</p>
        <p>{data.tem_investimentos ? "✅ Tem investimentos" : "❌ Sem investimentos"}</p>
      </TooltipContent>
    </Tooltip>
  )
}
