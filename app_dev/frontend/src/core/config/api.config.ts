/**
 * Configuração centralizada de APIs
 * 
 * ⚠️ ATENÇÃO: Este é o ÚNICO lugar onde URLs de backend devem ser definidas
 * Qualquer mudança de URL do backend deve ser feita APENAS aqui
 */

const isProduction = process.env.NODE_ENV === 'production';
const isDevelopment = !isProduction;

// URLs base do backend
export const API_CONFIG = {
  // Backend FastAPI
  BACKEND_URL: isDevelopment 
    ? process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
    : process.env.NEXT_PUBLIC_BACKEND_URL || 'https://api.financas.com',
  
  // Prefixo de API (se houver)
  API_PREFIX: '/api/v1',
  
  // Timeout padrão (ms)
  TIMEOUT: 30000,
  
  // Retry config
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000,
} as const;

// URLs completas dos endpoints
export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/auth/login`,
    REGISTER: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/auth/register`,
    LOGOUT: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/auth/logout`,
    ME: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/auth/me`,
  },
  
  // Transactions
  TRANSACTIONS: {
    BASE: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions`,
    LIST: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions/list`,
    FILTERED_TOTAL: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions/filtered-total`,
    UPDATE: (id: string) => `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions/update/${id}`,
    DELETE: (id: string) => `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions/${id}`,
  },
  
  // Dashboard
  DASHBOARD: {
    METRICS: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/dashboard/metrics`,
    CATEGORIES: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/dashboard/categories`,
    CHART_DATA: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/dashboard/chart/receitas-despesas`,
  },
  
  // Upload
  UPLOAD: {
    PROCESS: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/process`,
    VALIDATE: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/validate`,
    CONFIRM: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/confirm`,
    HISTORY: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/history`,
    SESSION: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/session`,
    PREVIEW: (sessionId: string) => `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/preview/${sessionId}`,
    CLASSIFY: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/classify`,
    PROCESS_CLASSIFY: (sessionId: string) => `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/process-classify/${sessionId}`,
  },
  
  // Categories (Marcações)
  CATEGORIES: {
    BASE: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/marcacoes`,
    BY_ID: (id: number) => `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/marcacoes/${id}`,
  },
  
  // Grupos
  GRUPOS: {
    BASE: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/grupos`,
  },
  
  // Cards (Cartões)
  CARDS: {
    BASE: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/cartoes`,
    BY_ID: (id: number) => `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/cartoes/${id}`,
  },
  
  // Exclusões
  EXCLUSOES: {
    BASE: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/exclusoes`,
    BY_ID: (id: number) => `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/exclusoes/${id}`,
  },
  
  // Compatibility (Bancos)
  COMPATIBILITY: {
    BASE: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/compatibility`,
    MANAGE: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/compatibility/manage`,
  },
  
  // Users
  USERS: {
    BASE: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/users`,
    BY_ID: (id: number) => `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/users/${id}`,
  },
  
  // Screen Visibility
  SCREENS: {
    BASE: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/screens`,
    LIST: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/screens/list`,
    ADMIN_ALL: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/screens/admin/all`,
    BY_KEY: (key: string) => `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/screens/${key}`,
    UPDATE: (id: number) => `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/screens/${id}`,
  },
  
  // Health
  HEALTH: `${API_CONFIG.BACKEND_URL}/api/health`,
  
  // Investimentos
  INVESTIMENTOS: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/investimentos`,
} as const;

// Helper para construir URL com query params
export function buildUrl(base: string, params?: Record<string, any>): string {
  if (!params || Object.keys(params).length === 0) {
    return base;
  }
  
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value));
    }
  });
  
  const queryString = searchParams.toString();
  return queryString ? `${base}?${queryString}` : base;
}

// Helper para validar se está no cliente ou servidor
export const isClient = typeof window !== 'undefined';
export const isServer = !isClient;
