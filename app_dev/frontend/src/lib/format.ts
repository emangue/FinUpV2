/**
 * Formatação padronizada para o app
 * UX Fundação - B4.01
 */

export function formatBRL(value: number | null | undefined): string {
  if (value == null) return 'R$ —'
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
  }).format(value)
}
