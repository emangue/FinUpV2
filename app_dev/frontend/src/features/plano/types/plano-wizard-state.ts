/**
 * PlanoWizardState — contrato de estado compartilhado entre as 4 etapas do wizard.
 * Fase 0: definição do contrato. Conteúdo real será preenchido nas fases seguintes.
 */

export interface GastosPorGrupo {
  grupo: string;
  valor_planejado: number;
  mes_referencia: string; // YYYY-MM
}

export interface GastoSazonal {
  mes: string; // YYYY-MM
  descricao: string;
  valor: number;
}

export interface PlanoWizardState {
  /** Etapa 1: Renda mensal + ganhos extraordinários (13º, bônus) */
  renda_mensal: number;
  ganhos_extras: { descricao: string; valor: number }[];

  /** Etapa 2: Gastos base por grupo (metas) */
  gastos_por_grupo: GastosPorGrupo[];

  /** Etapa 3: Gastos sazonais (IPVA, IPTU, etc.) */
  sazonais: GastoSazonal[];

  /** Etapa 4: Aporte planejado mensal */
  aporte: number;
}

export const initialPlanoWizardState: PlanoWizardState = {
  renda_mensal: 0,
  ganhos_extras: [],
  gastos_por_grupo: [],
  sazonais: [],
  aporte: 0,
};
