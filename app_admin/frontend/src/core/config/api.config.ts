const API_BASE =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"
const API_PREFIX = "/api/v1"

export const API_CONFIG = {
  BACKEND_URL: API_BASE,
  API_PREFIX,
  FULL_URL: `${API_BASE}${API_PREFIX}`,
} as const

export const API_ENDPOINTS = {
  SCREENS: {
    ADMIN_ALL: `${API_BASE}${API_PREFIX}/screens/admin/all`,
    UPDATE: (id: number) => `${API_BASE}${API_PREFIX}/screens/${id}`,
  },
  COMPATIBILITY: {
    BASE: `${API_BASE}${API_PREFIX}/compatibility/`,
    BY_ID: (id: number) => `${API_BASE}${API_PREFIX}/compatibility/${id}`,
  },
  CLASSIFICATION: {
    RULES: `${API_BASE}${API_PREFIX}/classification/rules`,
    RULES_BY_ID: (id: number) => `${API_BASE}${API_PREFIX}/classification/rules/${id}`,
    STATS: `${API_BASE}${API_PREFIX}/classification/stats`,
    GROUPS_WITH_TYPES: `${API_BASE}${API_PREFIX}/classification/groups-with-types`,
    TEST: `${API_BASE}${API_PREFIX}/classification/rules/test`,
    IMPORT: `${API_BASE}${API_PREFIX}/classification/rules/import`,
  },
} as const
