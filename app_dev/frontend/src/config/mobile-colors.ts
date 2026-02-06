// src/config/mobile-colors.ts
// Mobile Experience V1.0 - Design Tokens: Colors
// Data: 01/02/2026

export type CategoryColor = 'purple' | 'blue' | 'pink' | 'stone' | 'amber' | 'green';

export interface ColorScheme {
  bg: string;
  icon: string;
  progress: string;
  tailwind: {
    bg: string;
    icon: string;
    progress: string;
  };
}

export const categoryColors: Record<CategoryColor, ColorScheme> = {
  purple: {
    bg: '#DDD6FE',
    icon: '#6B21A8',
    progress: '#9F7AEA',
    tailwind: {
      bg: 'bg-purple-200',
      icon: 'text-purple-800',
      progress: 'bg-purple-500',
    }
  },
  blue: {
    bg: '#DBEAFE',
    icon: '#1E40AF',
    progress: '#60A5FA',
    tailwind: {
      bg: 'bg-blue-200',
      icon: 'text-blue-800',
      progress: 'bg-blue-400',
    }
  },
  pink: {
    bg: '#FCE7F3',
    icon: '#BE185D',
    progress: '#F472B6',
    tailwind: {
      bg: 'bg-pink-200',
      icon: 'text-pink-800',
      progress: 'bg-pink-400',
    }
  },
  stone: {
    bg: '#E7E5E4',
    icon: '#78716C',
    progress: '#A8A29E',
    tailwind: {
      bg: 'bg-stone-200',
      icon: 'text-stone-600',
      progress: 'bg-stone-400',
    }
  },
  amber: {
    bg: '#FEF3C7',
    icon: '#D97706',
    progress: '#FCD34D',
    tailwind: {
      bg: 'bg-amber-200',
      icon: 'text-amber-700',
      progress: 'bg-amber-400',
    }
  },
  green: {
    bg: '#D1FAE5',
    icon: '#047857',
    progress: '#6EE7B7',
    tailwind: {
      bg: 'bg-green-200',
      icon: 'text-green-700',
      progress: 'bg-green-400',
    }
  },
};

// Helper function: mapear categoria → cor
export function getCategoryColor(categoryName: string): CategoryColor {
  const map: Record<string, CategoryColor> = {
    'Casa': 'purple',
    'Moradia': 'purple',
    'Aluguel': 'purple',
    'Alimentação': 'blue',
    'Restaurante': 'blue',
    'Compras': 'pink',
    'Shopping': 'green',
    'Transporte': 'stone',
    'Combustível': 'stone',
    'Contas': 'amber',
    'Utilidades': 'amber',
    'Saúde': 'pink',
    'Viagens': 'blue',
    'Trabalho': 'stone',
  };
  
  return map[categoryName] || 'stone'; // Default: stone
}

// Helper function: obter progress color
export function getProgressColor(categoryName: string): string {
  const colorKey = getCategoryColor(categoryName);
  return categoryColors[colorKey].progress;
}
