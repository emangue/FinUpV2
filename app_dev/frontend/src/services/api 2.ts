import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para adicionar token em todas as requisições
api.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuthStore.getState()
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Interceptor para refresh token automático
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const { refreshToken } = useAuthStore.getState()
        const response = await axios.post('/api/v1/auth/refresh', {}, {
       headers: { Authorization: `Bearer ${refreshToken}` },
        })

        const { access_token } = response.data
        useAuthStore.getState().login(
          access_token,
          refreshToken!,
          useAuthStore.getState().user!
        )

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        useAuthStore.getState().logout()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Auth endpoints
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  
  register: (email: string, password: string, nome: string) =>
    api.post('/auth/register', { email, password, nome }),
  
  me: () => api.get('/auth/me'),
  
  logout: () => api.post('/auth/logout'),
}

// Dashboard endpoints
export const dashboardApi = {
  getMetrics: () => api.get('/dashboard/metrics'),
  
  getChartData: () => api.get('/dashboard/chart/gastos-mes'),
  
  getRecentTransactions: () => api.get('/dashboard/recent-transactions'),
  
  getGrupos: () => api.get('/dashboard/grupos'),
}

// Transactions endpoints
export const transactionsApi = {
  list: (params?: {
    page?: number
    per_page?: number
    grupo?: string
    marcacao?: string
    estabelecimento?: string
    data_inicio?: string
    data_fim?: string
  }) => api.get('/transactions', { params }),
  
  get: (id: number) => api.get(`/transactions/${id}`),
  
  update: (id: number, data: { grupo?: string; marcacao?: string; observacoes?: string }) =>
    api.put(`/transactions/${id}`, data),
  
  delete: (id: number) => api.delete(`/transactions/${id}`),
}

export default api
