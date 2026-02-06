// ============================================
// TIPOS DE CLASSIFICAÇÃO
// ============================================

export type ClassificationSource =
  | 'base_parcelas'
  | 'base_padroes'
  | 'journal_entries'
  | 'regras_genericas'
  | 'manual'
  | 'not_classified';

export const CLASSIFICATION_SOURCE_LABELS: Record<ClassificationSource, string> = {
  base_parcelas: 'Base Parcelas',
  base_padroes: 'Base Padrões',
  journal_entries: 'Journal Entries',
  regras_genericas: 'Regras Genéricas',
  manual: 'Manual',
  not_classified: 'Não Classificado',
};

export const CLASSIFICATION_SOURCE_COLORS: Record<ClassificationSource, string> = {
  base_parcelas: 'text-indigo-700 bg-indigo-50',
  base_padroes: 'text-purple-700 bg-purple-50',
  journal_entries: 'text-blue-700 bg-blue-50',
  regras_genericas: 'text-cyan-700 bg-cyan-50',
  manual: 'text-blue-700 bg-blue-50',
  not_classified: 'text-orange-700 bg-orange-50 border-orange-200',
};

// ============================================
// TRANSAÇÃO
// ============================================

export interface Transaction {
  id: string;
  date: string;
  description: string;
  value: number;
  grupo?: string;
  subgrupo?: string;
  source: ClassificationSource;
  occurrences?: number; // Para transações agrupadas
  items?: Transaction[]; // Itens individuais quando agrupado
}

// ============================================
// INFORMAÇÕES DO ARQUIVO
// ============================================

export interface FileInfo {
  banco: string;
  cartao: string;
  arquivo: string;
  mesFatura: string;
  totalLancamentos: number;
  somaTotal: number;
}

// ============================================
// ESTATÍSTICAS
// ============================================

export interface PreviewStats {
  total: number;
  classificadas: number;
  naoClassificadas: number;
  baseParcelas: number;
  basePadroes: number;
  journalEntries: number;
  regrasGenericas: number;
  manual: number;
}

// ============================================
// FILTROS DE TAB
// ============================================

export type TabFilter = 
  | 'all'
  | 'classificadas'
  | 'base_parcelas'
  | 'base_padroes'
  | 'journal_entries'
  | 'regras_genericas'
  | 'manual'
  | 'not_classified';

export interface TabOption {
  id: TabFilter;
  label: string;
  count: number;
  variant?: 'default' | 'warning';
}

// ============================================
// MODAL DE CLASSIFICAÇÃO
// ============================================

export interface ClassificationData {
  grupo: string;
  subgrupo: string;
}
