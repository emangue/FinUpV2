/**
 * Preview Types
 * Tipos para transações de preview (pré-visualização antes de confirmar)
 */

export interface PreviewTransaction {
  id: number;
  data: string; // DD/MM/YYYY
  lancamento: string;
  valor: number;
  banco: string;
  cartao?: string;
  mes_fatura?: string;
  nome_arquivo: string;
  created_at?: string;
  
  // Identificação
  IdTransacao?: string;
  IdParcela?: string;
  EstabelecimentoBase?: string;
  ParcelaAtual?: number;
  TotalParcelas?: number;
  ValorPositivo?: number;
  
  // Classificação
  GRUPO?: string;
  SUBGRUPO?: string;
  TipoGasto?: string;
  CategoriaGeral?: string;
  origem_classificacao?: string;
  padrao_buscado?: string;
  MarcacaoIA?: string;
  
  // Deduplicação
  is_duplicate?: boolean;
  duplicate_reason?: string;
}

export interface ClassificationStats {
  total: number;
  base_parcelas?: number;
  base_padroes?: number;
  journal_entries?: number;
  regras_genericas?: number;
  nao_classificado?: number;
}

export interface BalanceValidation {
  saldo_inicial?: number;
  saldo_final?: number;
  soma_transacoes?: number;
  is_valid?: boolean;
  diferenca?: number;
}

export interface PreviewData {
  success: boolean;
  sessionId: string;
  totalRegistros: number;
  dados: PreviewTransaction[];
  banco?: string;
  tipo_documento?: string;
  nome_arquivo?: string;
  nome_cartao?: string;
  mes_fatura?: string;
  balance_validation?: BalanceValidation;
}

export interface PreviewGroup {
  estabelecimento: string;
  transacoes: PreviewTransaction[];
  totalGrupo: number;
  tipoGasto?: string;
  expanded?: boolean; // Para controle de UI
}

export interface PreviewStats {
  total: number;
  receitas: number;
  despesas: number;
  totalValor: number;
  receitasValor: number;
  despesasValor: number;
}
