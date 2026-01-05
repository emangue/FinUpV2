/**
 * Types compartilhados entre módulos
 * 
 * Este arquivo contém types que são usados em múltiplas features
 */

// ==================== API Response Types ====================

export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface ErrorResponse {
  detail: string;
  code?: string;
  field?: string;
}

// ==================== Common Entity Types ====================

export interface User {
  id: number;
  email: string;
  nome: string;
  data_criacao?: string;
  ultimo_acesso?: string;
}

export interface Transaction {
  IdTransacao: string;
  DATA: string;
  ESTABELECIMENTO: string;
  VALOR: number;
  TIPO: 'CREDITO' | 'DEBITO';
  GRUPO?: string;
  SUBGRUPO?: string;
  ORIGEM?: string;
  CARTAO?: string;
  TIPOGASTO?: string;
  user_id?: number;
}

export interface Category {
  id: number;
  GRUPO: string;
  SUBGRUPO: string;
  TIPOGASTO: string;
  user_id?: number;
}

export interface Card {
  id: number;
  nome: string;
  limite?: number;
  user_id?: number;
}

// ==================== Filter Types ====================

export interface DateFilter {
  year: number;
  month: number | 'all';
}

export interface TransactionFilters extends DateFilter {
  estabelecimento?: string;
  grupo?: string;
  subgrupo?: string;
  tipo?: string;
  cartao?: string;
  search?: string;
}

export interface PaginationParams {
  page: number;
  limit: number;
}

// ==================== Upload Types ====================

export interface UploadSession {
  session_id: string;
  filename: string;
  status: 'processing' | 'ready' | 'confirmed' | 'error';
  total_transactions?: number;
  created_at: string;
}

export interface PreviewTransaction extends Partial<Transaction> {
  confidence?: number;
  needs_review?: boolean;
}

// ==================== Dashboard Types ====================

export interface DashboardMetrics {
  total_receitas: number;
  total_despesas: number;
  saldo: number;
  total_transacoes: number;
  periodo: string;
}

export interface CategoryExpense {
  GRUPO: string;
  SUBGRUPO?: string;
  total: number;
  percentage: number;
  count: number;
}

export interface ChartData {
  labels: string[];
  receitas: number[];
  despesas: number[];
}

// ==================== Settings Types ====================

export interface BankCompatibility {
  id: number;
  banco: string;
  tipo_arquivo: string;
  formato: string;
  ativo: boolean;
  user_id?: number;
}

export interface ExclusionRule {
  id: number;
  estabelecimento: string;
  motivo?: string;
  user_id?: number;
}
