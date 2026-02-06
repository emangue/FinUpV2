export interface User {
  id: string;
  name: string;
  avatar: string; // URL
}

export interface Category {
  id: string;
  label: string;
  color: string; // HEX color
  percentage: number; // 0-100
  type: 'savings' | 'expenses';
  value: number; // Valor em R$
  count: number; // Quantidade de ativos/itens
}

export interface WalletData {
  month: string; // "September 2026"
  saved: number; // 327.50
  total: number; // 1000
  categories: Category[];
}

export interface DonutChartData {
  label: string;
  value: number; // valor monetário
  color: string; // HEX
  percentage: number; // calculado
}

export interface NavTab {
  id: string;
  icon: React.ElementType; // Lucide icon
  label: string;
  active: boolean;
}
