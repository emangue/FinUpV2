import { User, WalletData, Category } from '@/types/wallet';

export const MOCK_USER: User = {
  id: '1',
  name: 'Vadim Portnyagin',
  avatar: 'https://i.pravatar.cc/150?u=vadim'
};

export const MOCK_CATEGORIES: Category[] = [
  {
    id: '1',
    label: 'Apartamento',
    color: '#F59E0B', // amarelo/dourado
    percentage: 43,
    type: 'savings',
    value: 52036.88,
    count: 2
  },
  {
    id: '2',
    label: 'FGTS',
    color: '#EC4899', // rosa
    percentage: 25,
    type: 'savings',
    value: 25290.61,
    count: 1
  },
  {
    id: '3',
    label: 'Casa',
    color: '#F97316', // laranja
    percentage: 20,
    type: 'expenses',
    value: 24128.52,
    count: 2
  },
  {
    id: '4',
    label: 'Automóvel',
    color: '#EF4444', // vermelho
    percentage: 8,
    type: 'expenses',
    value: 16367.17,
    count: 1
  },
  {
    id: '5',
    label: 'Renda Fixa',
    color: '#10B981', // verde
    percentage: 4,
    type: 'expenses',
    value: 10368.33,
    count: 4
  }
];

export const MOCK_WALLET_DATA: WalletData = {
  month: 'September 2026',
  saved: 327.50,
  total: 1000,
  categories: MOCK_CATEGORIES
};

// Cores da paleta (para fácil referência)
export const COLORS = {
  background: '#F7F8FA',
  surface: '#FFFFFF',
  primary: '#3B82F6',
  success: '#10B981',
  purple: '#8B5CF6',
  orange: '#F97316',
  pink: '#EC4899',
  textPrimary: '#111827',
  textSecondary: '#6B7280',
  textDisabled: '#9CA3AF',
  border: '#E5E7EB'
} as const;
