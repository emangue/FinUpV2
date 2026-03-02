/** Aporte extraordinário para o plano de aposentadoria */
export interface AporteExtraordinario {
  id: string
  mesAno: number
  valor: number
  descricao: string
  recorrencia: 'unico' | 'trimestral' | 'semestral' | 'anual'
  evoluir: boolean
  evolucaoValor: number
  evolucaoTipo: 'percentual' | 'nominal'
}

/** Perfil de risco do plano de aposentadoria */
export type PlanoProfile = 'conservador' | 'moderado' | 'arrojado'

/** Dados de retorno por perfil */
export interface PlanoProfileData {
  retorno: number
  inflacao: number
}
