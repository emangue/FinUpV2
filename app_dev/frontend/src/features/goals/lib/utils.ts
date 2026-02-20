/**
 * Goals Utilities
 * Funções auxiliares para o sistema de metas
 */

import { Goal, GoalStatus, GoalProgress, calculateGoalProgress } from '../types'
import { format, parseISO, differenceInMonths, isBefore, startOfMonth } from 'date-fns'
import { ptBR } from 'date-fns/locale'

/**
 * Calcula o status da meta baseado em progresso e prazo
 * CORRETO: Usa campos do backend (mes_referencia, total_mensal, valor_planejado)
 */
export function calculateGoalStatus(goal: Goal): GoalStatus {
  const { percentual } = calculateGoalProgress(goal, goal.valor_realizado ?? 0)
  
  // Concluída: 100% ou mais
  if (percentual >= 100) return 'concluido'
  
  // Atrasada: mês de referência vencido e não concluída
  const prazoDate = parseISO(`${goal.mes_referencia}-01`)
  const now = new Date()
  if (isBefore(prazoDate, startOfMonth(now))) return 'atrasado'
  
  return 'ativo'
}

/**
 * Formata valor monetário
 */
export function formatCurrency(value: number): string {
  if (value === null || value === undefined || isNaN(value)) return 'R$ 0,00'
  
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value)
}

/**
 * Formata mês no formato "Janeiro 2026"
 */
export function formatMonth(prazo: string): string {
  try {
    const date = parseISO(`${prazo}-01`)
    return format(date, 'MMMM yyyy', { locale: ptBR })
  } catch {
    return prazo
  }
}

/**
 * Calcula meses restantes até o prazo
 */
export function calculateMonthsRemaining(prazo: string): number {
  try {
    const prazoDate = parseISO(`${prazo}-01`)
    const now = startOfMonth(new Date())
    return Math.max(0, differenceInMonths(prazoDate, now))
  } catch {
    return 0
  }
}

/**
 * Retorna cor baseada no status
 */
export function getStatusColor(status: GoalStatus): string {
  const colors: Record<GoalStatus, string> = {
    ativo: 'text-blue-600 bg-blue-50',
    concluido: 'text-green-600 bg-green-50',
    atrasado: 'text-red-600 bg-red-50',
    inativo: 'text-gray-600 bg-gray-50'
  }
  return colors[status]
}

/**
 * Retorna label do status
 */
export function getStatusLabel(status: GoalStatus): string {
  const labels: Record<GoalStatus, string> = {
    ativo: 'Ativo',
    concluido: 'Concluído',
    atrasado: 'Atrasado',
    inativo: 'Inativo'
  }
  return labels[status]
}

/**
 * Valida se meta pode ser excluída
 * CORRETO: Sempre permite exclusão (sem validação de progresso)
 */
export function canDeleteGoal(goal: Goal): boolean {
  // Sempre permite exclusão no sistema atual
  return true
}

/**
 * Calcula progresso percentual
 */
export function calculateProgress(valor_atual: number, valor_alvo: number): number {
  if (valor_alvo === 0) return 0
  return Math.round((valor_atual / valor_alvo) * 100)
}

/**
 * Retorna mensagem de progresso
 */
export function getProgressMessage(progresso: GoalProgress): string {
  if (progresso.percentual >= 100) {
    return 'Meta atingida! 🎉'
  }
  if (progresso.percentual >= 75) {
    return 'Quase lá! Continue assim 💪'
  }
  if (progresso.percentual >= 50) {
    return 'No caminho certo 📈'
  }
  if (progresso.percentual >= 25) {
    return 'Bom começo! 🚀'
  }
  return 'Começando a jornada 🌱'
}
