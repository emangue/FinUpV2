import { FileInfo, Transaction, PreviewStats, TabOption } from '../types';

// ============================================
// INFORMAÇÕES DO ARQUIVO
// ============================================

export const mockFileInfo: FileInfo = {
  banco: 'Itaú',
  cartao: '9266',
  arquivo: 'fatura-202601.csv',
  mesFatura: 'fevereiro de 2026',
  totalLancamentos: 58,
  somaTotal: -17064.96,
};

// ============================================
// GRUPOS E SUBGRUPOS (inicialmente vazios, serão carregados da API)
// ============================================

export let GRUPOS: string[] = [];
export let SUBGRUPOS: Record<string, string[]> = {};

// Função para popular grupos e subgrupos vindos da API
// API retorna: { grupos: string[], subgruposPorGrupo: Record<string, string[]> }
export function setGruposSubgrupos(data: { grupos: string[]; subgruposPorGrupo: Record<string, string[]> }) {
  GRUPOS = data.grupos || [];
  SUBGRUPOS = data.subgruposPorGrupo || {};
  
  console.log('✅ Grupos carregados:', GRUPOS.length);
  console.log('✅ Subgrupos por grupo:', Object.keys(SUBGRUPOS).length, 'grupos');
}

// ============================================
// TRANSAÇÕES MOCKADAS
// ============================================

export const mockTransactions: Transaction[] = [
  // Agrupadas - Não Classificadas
  {
    id: 'group-1',
    date: '',
    description: 'KEETA*KDJ ARABIC',
    value: -165.85,
    source: 'not_classified',
    occurrences: 2,
    items: [
      {
        id: 'tx-001',
        date: '12/02/2026',
        description: 'KEETA*KDJ ARABIC',
        value: -82.92,
        source: 'not_classified',
      },
      {
        id: 'tx-002',
        date: '15/02/2026',
        description: 'KEETA*KDJ ARABIC',
        value: -82.93,
        source: 'not_classified',
      },
    ],
  },
  {
    id: 'group-2',
    date: '',
    description: 'FABIO DOS SANTOS',
    value: -64.0,
    source: 'not_classified',
    occurrences: 2,
    items: [
      {
        id: 'tx-003',
        date: '10/02/2026',
        description: 'FABIO DOS SANTOS',
        value: -32.0,
        source: 'not_classified',
      },
      {
        id: 'tx-004',
        date: '18/02/2026',
        description: 'FABIO DOS SANTOS',
        value: -32.0,
        source: 'not_classified',
      },
    ],
  },

  // Agrupadas - Classificadas
  {
    id: 'group-3',
    date: '',
    description: 'IOF COMPRA INTERNACIONAL',
    value: -127.76,
    grupo: 'Serviços',
    subgrupo: 'IOF',
    source: 'journal_entries',
    occurrences: 4,
    items: [
      {
        id: 'tx-005',
        date: '05/02/2026',
        description: 'IOF COMPRA INTERNACIONAL',
        value: -31.94,
        grupo: 'Serviços',
        subgrupo: 'IOF',
        source: 'journal_entries',
      },
      {
        id: 'tx-006',
        date: '12/02/2026',
        description: 'IOF COMPRA INTERNACIONAL',
        value: -31.94,
        grupo: 'Serviços',
        subgrupo: 'IOF',
        source: 'journal_entries',
      },
      {
        id: 'tx-007',
        date: '18/02/2026',
        description: 'IOF COMPRA INTERNACIONAL',
        value: -31.94,
        grupo: 'Serviços',
        subgrupo: 'IOF',
        source: 'journal_entries',
      },
      {
        id: 'tx-008',
        date: '25/02/2026',
        description: 'IOF COMPRA INTERNACIONAL',
        value: -31.94,
        grupo: 'Serviços',
        subgrupo: 'IOF',
        source: 'journal_entries',
      },
    ],
  },
  {
    id: 'group-4',
    date: '',
    description: 'CONTA VIVO',
    value: -193.0,
    grupo: 'Casa',
    subgrupo: 'Celular',
    source: 'base_padroes',
    occurrences: 2,
    items: [
      {
        id: 'tx-009',
        date: '08/02/2026',
        description: 'CONTA VIVO',
        value: -96.5,
        grupo: 'Casa',
        subgrupo: 'Celular',
        source: 'base_padroes',
      },
      {
        id: 'tx-010',
        date: '22/02/2026',
        description: 'CONTA VIVO',
        value: -96.5,
        grupo: 'Casa',
        subgrupo: 'Celular',
        source: 'base_padroes',
      },
    ],
  },

  // Únicas - Não Classificada
  {
    id: 'tx-011',
    date: '08/02/2026',
    description: 'MERCADO LIVRE*COMPRA',
    value: -89.9,
    source: 'not_classified',
  },

  // Únicas - Classificada
  {
    id: 'tx-012',
    date: '15/02/2026',
    description: 'SPOTIFY BRASIL',
    value: -21.9,
    grupo: 'Lazer',
    subgrupo: 'Streaming',
    source: 'base_padroes',
  },
];

// ============================================
// ESTATÍSTICAS
// ============================================

export function calculateStats(transactions: Transaction[]): PreviewStats {
  const stats: PreviewStats = {
    total: 0,
    classificadas: 0,
    naoClassificadas: 0,
    baseParcelas: 0,
    basePadroes: 0,
    journalEntries: 0,
    regrasGenericas: 0,
    manual: 0,
  };

  const countTransaction = (tx: Transaction) => {
    stats.total++;

    if (tx.grupo && tx.subgrupo) {
      stats.classificadas++;

      switch (tx.source) {
        case 'base_parcelas':
          stats.baseParcelas++;
          break;
        case 'base_padroes':
          stats.basePadroes++;
          break;
        case 'journal_entries':
          stats.journalEntries++;
          break;
        case 'regras_genericas':
          stats.regrasGenericas++;
          break;
        case 'manual':
          stats.manual++;
          break;
      }
    } else {
      stats.naoClassificadas++;
    }
  };

  transactions.forEach((tx) => {
    if (tx.items && tx.items.length > 0) {
      tx.items.forEach(countTransaction);
    } else {
      countTransaction(tx);
    }
  });

  return stats;
}

// ============================================
// TABS
// ============================================

export function generateTabs(stats: PreviewStats): TabOption[] {
  return [
    { id: 'all', label: 'Todas', count: stats.total },
    { id: 'classificadas', label: 'Classificadas', count: stats.classificadas },
    { id: 'base_parcelas', label: 'Base Parcelas', count: stats.baseParcelas },
    { id: 'base_padroes', label: 'Base Padrões', count: stats.basePadroes },
    { id: 'journal_entries', label: 'Journal Entries', count: stats.journalEntries },
    { id: 'regras_genericas', label: 'Regras Genéricas', count: stats.regrasGenericas },
    { id: 'manual', label: 'Manual', count: stats.manual },
    { 
      id: 'not_classified', 
      label: 'Não Classificadas', 
      count: stats.naoClassificadas,
      variant: 'warning',
    },
  ];
}

// ============================================
// FORMATAÇÃO
// ============================================

export function formatCurrency(value: number): string {
  // Validação robusta para evitar NaN
  if (value === null || value === undefined || isNaN(value)) {
    return 'R$ 0,00';
  }
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numValue)) {
    return 'R$ 0,00';
  }
  
  const formatted = Math.abs(numValue).toFixed(2).replace('.', ',');
  return numValue < 0 ? `-R$ ${formatted}` : `R$ ${formatted}`;
}
