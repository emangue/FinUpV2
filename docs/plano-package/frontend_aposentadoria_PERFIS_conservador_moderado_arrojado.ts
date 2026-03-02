import type { PlanoProfile, PlanoProfileData } from '../types'

export const planProfiles: Record<PlanoProfile, PlanoProfileData> = {
  conservador: { retorno: 6, inflacao: 4 },
  moderado: { retorno: 10, inflacao: 4.5 },
  arrojado: { retorno: 14, inflacao: 5 },
}
