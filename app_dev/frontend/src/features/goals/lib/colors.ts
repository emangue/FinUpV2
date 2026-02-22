/**
 * Paleta de cores para metas e grupos (Sprint C)
 * Gradiente azul do escuro ao claro - 11 tons distintos
 * Usada em Metas, Dashboard e Central de Grupos
 */
export const GOAL_COLORS = [
  '#001D39', // 1. navy escuro
  '#0A4174', // 2. azul profundo
  '#2D5A7B', // 3. interpolado
  '#49769F', // 4. azul médio
  '#4E8EA2', // 5. azul-teal
  '#5E9AB0', // 6. interpolado
  '#6EA2B3', // 7. azul acinzentado
  '#7BBDE8', // 8. azul céu
  '#9AC9E8', // 9. interpolado
  '#BDD8E9', // 10. azul claro
  '#D4E8F0', // 11. azul muito claro
] as const

export function getGoalColor(grupo: string, index: number): string {
  // Hash simples por nome para consistência entre telas
  const hash = grupo.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)
  const idx = (hash + index) % GOAL_COLORS.length
  return GOAL_COLORS[Math.abs(idx)]
}
