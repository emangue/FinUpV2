/**
 * Paleta de cores para metas (donut charts)
 * Usada em Metas e Dashboard para consistência visual
 */

export const GOAL_COLORS = [
  '#3b82f6', // blue-500
  '#10b981', // emerald-500
  '#f97316', // orange-500
  '#ec4899', // pink-500
  '#a855f7', // violet-500
  '#06b6d4', // cyan-500
  '#f59e0b', // amber-500
  '#84cc16', // lime-500
  '#6366f1', // indigo-500
  '#8b5cf6', // violet-400
  '#14b8a6', // teal-500
  '#f43f5e', // rose-500
] as const

export function getGoalColor(grupo: string, index: number): string {
  // Hash simples por nome para consistência entre telas
  const hash = grupo.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)
  const idx = (hash + index) % GOAL_COLORS.length
  return GOAL_COLORS[Math.abs(idx)]
}
