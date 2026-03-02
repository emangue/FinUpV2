"use client"

import { useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface Usuario {
  id: number
  nome: string
  email: string
}

interface UserStats {
  total_transacoes: number
  total_uploads: number
  total_grupos: number
  tem_investimentos: boolean
}

interface PurgeUserModalProps {
  user: Usuario
  stats: UserStats
  open: boolean
  onClose: () => void
  onConfirm: (userId: number, email: string) => Promise<void>
}

export function PurgeUserModal({ user, stats, open, onClose, onConfirm }: PurgeUserModalProps) {
  const [step, setStep] = useState<1 | 2>(1)
  const [emailInput, setEmailInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const emailOk = emailInput.trim().toLowerCase() === user.email.toLowerCase()

  const handleClose = () => {
    setStep(1)
    setEmailInput("")
    setError(null)
    onClose()
  }

  const handleConfirm = async () => {
    if (!emailOk) return
    setLoading(true)
    setError(null)
    try {
      await onConfirm(user.id, emailInput.trim())
      handleClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao excluir")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={(o) => (!o ? handleClose() : null)}>
      <DialogContent>
        {step === 1 ? (
          <>
            <DialogHeader>
              <DialogTitle>⚠️ Excluir permanentemente: {user.nome}</DialogTitle>
            </DialogHeader>
            <ul className="mt-2 space-y-1 text-sm">
              <li>🗂 {stats.total_transacoes.toLocaleString()} transações</li>
              <li>📤 {stats.total_uploads} uploads</li>
              <li>📋 {stats.total_grupos} grupos</li>
              {stats.tem_investimentos && (
                <li className="text-amber-600">
                  ⚠️ Investimentos vinculados — também removidos
                </li>
              )}
            </ul>
            <div className="mt-4 flex justify-end gap-2">
              <Button variant="outline" onClick={handleClose}>
                Cancelar
              </Button>
              <Button variant="destructive" onClick={() => setStep(2)}>
                Continuar →
              </Button>
            </div>
          </>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle>⚠️ Confirmar exclusão permanente</DialogTitle>
            </DialogHeader>
            <p className="text-sm">Digite o e-mail do usuário:</p>
            {error && (
              <p className="mt-2 text-sm text-destructive">{error}</p>
            )}
            <Input
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
              placeholder={user.email}
              className="mt-2"
            />
            <div className="mt-4 flex justify-end gap-2">
              <Button variant="outline" onClick={() => setStep(1)}>
                ← Voltar
              </Button>
              <Button
                variant="destructive"
                disabled={!emailOk || loading}
                onClick={handleConfirm}
              >
                🗑 Excluir Permanentemente
              </Button>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
