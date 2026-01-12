import axios from 'axios';
import { API_CONFIG, API_ENDPOINTS } from '@/core/config/api.config';

/**
 * API Client para comunicação com backend
 * 
 * ⚠️ IMPORTANTE: 
 * - Usa configuração centralizada de @/core/config/api.config
 * - Para mudar URL do backend, modifique APENAS api.config.ts
 * - Não modificar baseURL diretamente aqui
 * - Usa httpOnly cookies para autenticação (não localStorage)
 */
export const apiClient = axios.create({
  baseURL: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // ⚠️ CRÍTICO: Envia cookies httpOnly automaticamente
});

/**
 * Request interceptor
 * 
 * ⚠️ NÃO adicionar Authorization header manualmente!
 * Cookies httpOnly são enviados automaticamente via withCredentials: true
 */
apiClient.interceptors.request.use(
  (config) => {
    // Cookies são enviados automaticamente pelo browser
    // Não precisa manipular tokens manualmente
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor to handle common errors
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized - redirect to login
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      // Cookies são limpos automaticamente pelo servidor no logout
      // Apenas redirecionar para login
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// ==========================================
// AUTH API - Funções de autenticação
// ==========================================

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface UserResponse {
  id: number;
  email: string;
  nome: string;
  role: string;
  ativo: number;
  created_at?: string;
  updated_at?: string;
}

/**
 * API de Autenticação
 * 
 * ⚠️ IMPORTANTE:
 * - Usa httpOnly cookies (seguro contra XSS)
 * - Backend FastAPI seta cookies automaticamente
 * - Frontend não precisa gerenciar tokens manualmente
 */
export const authAPI = {
  /**
   * Login - Autentica usuário e recebe cookies httpOnly
   * 
   * @param email - Email do usuário
   * @param password - Senha
   * @returns Tokens (também vêm em cookies httpOnly)
   */
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await axios.post<LoginResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      { email, password },
      { 
        withCredentials: true, // ⚠️ CRÍTICO: Recebe e salva cookies
        headers: { 'Content-Type': 'application/json' }
      }
    );
    return response.data;
  },

  /**
   * Logout - Revoga tokens e limpa cookies
   */
  async logout(): Promise<void> {
    await apiClient.post('/auth/logout');
  },

  /**
   * Me - Retorna dados do usuário autenticado
   * 
   * Usa cookie httpOnly automaticamente enviado pelo browser
   */
  async me(): Promise<UserResponse> {
    const response = await apiClient.get<UserResponse>('/auth/me');
    return response.data;
  },

  /**
   * Refresh - Renova access token usando refresh token
   */
  async refresh(): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/refresh');
    return response.data;
  },
};
