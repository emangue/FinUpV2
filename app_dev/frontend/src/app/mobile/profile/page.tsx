// src/app/mobile/profile/page.tsx
// Mobile Experience V1.0 - Profile Mobile
// Data: 01/02/2026
// Sprint 4 - Implementação Completa

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { MobileHeader } from '@/components/mobile/mobile-header';
import { fetchWithAuth } from '@/core/utils/api-client';
import { API_CONFIG } from '@/core/config/api.config';
import { User, Lock, LogOut, Bell, Moon, Globe, CreditCard, Ban, Upload } from 'lucide-react';
import { useRequireAuth } from '@/core/hooks/use-require-auth';

interface UserProfile {
  id: number;
  nome: string;
  email: string;
  role: string;
}

type EditMode = 'none' | 'profile' | 'password';

export default function ProfileMobilePage() {
  const router = useRouter();
  const isAuth = useRequireAuth(); // 🔐 Hook de proteção de rota
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState<EditMode>('none');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Profile edit form
  const [profileForm, setProfileForm] = useState({
    nome: '',
    email: ''
  });

  // Password change form
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  // Settings
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    // Só carrega dados se autenticado
    if (isAuth) {
      loadUserProfile();
    }
  }, [isAuth]);

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetchWithAuth(`${API_CONFIG.BACKEND_URL}/api/v1/auth/me`);
      
      if (!response.ok) {
        throw new Error('Erro ao carregar perfil');
      }

      const data = await response.json();
      setUser(data);
      setProfileForm({
        nome: data.nome,
        email: data.email
      });
    } catch (err) {
      console.error('Erro ao carregar perfil:', err);
      setError('Erro ao carregar dados do perfil');
    } finally {
      setLoading(false);
    }
  };

  // 🔐 Mostrar loading enquanto verifica autenticação
  if (!isAuth) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MobileHeader title="Perfil" leftAction="logo" />
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Verificando autenticação...</p>
          </div>
        </div>
      </div>
    );
  }

  const handleUpdateProfile = async () => {
    if (!profileForm.nome.trim()) {
      setError('Nome é obrigatório');
      return;
    }

    if (!profileForm.email.trim()) {
      setError('Email é obrigatório');
      return;
    }

    try {
      setSaving(true);
      setError('');
      setSuccessMessage('');

      const response = await fetchWithAuth(`${API_CONFIG.BACKEND_URL}/api/v1/auth/update-profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileForm)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao atualizar perfil');
      }

      const data = await response.json();
      setUser(data);
      setEditMode('none');
      setSuccessMessage('Perfil atualizado com sucesso!');
      
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      console.error('Erro ao atualizar perfil:', err);
      setError(err.message || 'Erro ao atualizar perfil');
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (!passwordForm.current_password) {
      setError('Senha atual é obrigatória');
      return;
    }

    if (!passwordForm.new_password || passwordForm.new_password.length < 6) {
      setError('Nova senha deve ter no mínimo 6 caracteres');
      return;
    }

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setError('As senhas não coincidem');
      return;
    }

    try {
      setSaving(true);
      setError('');
      setSuccessMessage('');

      const response = await fetchWithAuth(`${API_CONFIG.BACKEND_URL}/api/v1/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_password: passwordForm.current_password,
          new_password: passwordForm.new_password
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao alterar senha');
      }

      setEditMode('none');
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
      setSuccessMessage('Senha alterada com sucesso!');
      
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      console.error('Erro ao alterar senha:', err);
      setError(err.message || 'Erro ao alterar senha');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    router.push('/auth/login');
  };

  const cancelEdit = () => {
    setEditMode('none');
    setError('');
    if (user) {
      setProfileForm({
        nome: user.nome,
        email: user.email
      });
    }
    setPasswordForm({
      current_password: '',
      new_password: '',
      confirm_password: ''
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MobileHeader title="Perfil" leftAction="logo" />
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Carregando perfil...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="Perfil" leftAction="logo" />
      
      <div className="p-5 space-y-4">
        {/* Success Message */}
        {successMessage && (
          <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
            {successMessage}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* User Avatar & Info */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center space-x-4">
            <div className="w-20 h-20 rounded-full bg-indigo-100 flex items-center justify-center">
              <User className="w-10 h-10 text-indigo-600" />
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-bold text-gray-900">{user?.nome}</h2>
              <p className="text-sm text-gray-500">{user?.email}</p>
              <span className="inline-block mt-1 px-2 py-1 text-xs font-semibold rounded-full bg-indigo-100 text-indigo-800">
                {user?.role === 'admin' ? 'Administrador' : 'Usuário'}
              </span>
            </div>
          </div>
        </div>

        {/* Profile Edit Section */}
        {editMode === 'profile' ? (
          <div className="bg-white rounded-2xl p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Editar Perfil</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nome
              </label>
              <input
                type="text"
                value={profileForm.nome}
                onChange={(e) => setProfileForm({ ...profileForm, nome: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Seu nome completo"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                value={profileForm.email}
                onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="seu@email.com"
              />
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={cancelEdit}
                disabled={saving}
                className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleUpdateProfile}
                disabled={saving}
                className="flex-1 px-4 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50"
              >
                {saving ? 'Salvando...' : 'Salvar'}
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
            <button
              onClick={() => setEditMode('profile')}
              className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
                  <User className="w-5 h-5 text-indigo-600" />
                </div>
                <span className="font-medium text-gray-900">Editar Perfil</span>
              </div>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        )}

        {/* Password Change Section */}
        {editMode === 'password' ? (
          <div className="bg-white rounded-2xl p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Alterar Senha</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Senha Atual
              </label>
              <input
                type="password"
                value={passwordForm.current_password}
                onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="••••••"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nova Senha
              </label>
              <input
                type="password"
                value={passwordForm.new_password}
                onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="••••••"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirmar Nova Senha
              </label>
              <input
                type="password"
                value={passwordForm.confirm_password}
                onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="••••••"
              />
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={cancelEdit}
                disabled={saving}
                className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleChangePassword}
                disabled={saving}
                className="flex-1 px-4 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50"
              >
                {saving ? 'Salvando...' : 'Alterar Senha'}
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
            <button
              onClick={() => setEditMode('password')}
              className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
                  <Lock className="w-5 h-5 text-indigo-600" />
                </div>
                <span className="font-medium text-gray-900">Alterar Senha</span>
              </div>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        )}

        {/* Management Section */}
        <div className="bg-white rounded-2xl shadow-sm overflow-hidden divide-y">
          <div className="p-4">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
              Gerenciamento
            </h3>
          </div>

          <button
            onClick={() => router.push('/mobile/cards')}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
                <CreditCard className="w-5 h-5 text-purple-600" />
              </div>
              <span className="font-medium text-gray-900">Meus Cartões</span>
            </div>
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <button
            onClick={() => router.push('/mobile/exclusions')}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
                <Ban className="w-5 h-5 text-red-600" />
              </div>
              <span className="font-medium text-gray-900">Excluir / Ignorar</span>
            </div>
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <button
            onClick={() => router.push('/mobile/uploads')}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
                <Upload className="w-5 h-5 text-indigo-600" />
              </div>
              <span className="font-medium text-gray-900">Painel de Uploads</span>
            </div>
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        {/* Settings Section */}
        <div className="bg-white rounded-2xl shadow-sm overflow-hidden divide-y">
          <div className="p-4">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
              Configurações
            </h3>
          </div>

          <div className="flex items-center justify-between p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                <Bell className="w-5 h-5 text-green-600" />
              </div>
              <span className="font-medium text-gray-900">Notificações</span>
            </div>
            <button
              onClick={() => setNotifications(!notifications)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                notifications ? 'bg-indigo-600' : 'bg-gray-300'
              }`}
              role="switch"
              aria-checked={notifications}
              aria-label="Ativar notificações"
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  notifications ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center">
                <Moon className="w-5 h-5 text-white" />
              </div>
              <span className="font-medium text-gray-900">Modo Escuro</span>
            </div>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                darkMode ? 'bg-indigo-600' : 'bg-gray-300'
              }`}
              role="switch"
              aria-checked={darkMode}
              aria-label="Ativar modo escuro"
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  darkMode ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <button className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                <Globe className="w-5 h-5 text-blue-600" />
              </div>
              <span className="font-medium text-gray-900">Idioma</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Português</span>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </button>
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="w-full bg-red-50 text-red-600 rounded-2xl p-4 flex items-center justify-center space-x-2 font-semibold hover:bg-red-100 transition-colors shadow-sm"
        >
          <LogOut className="w-5 h-5" />
          <span>Sair da Conta</span>
        </button>

        {/* App Info */}
        <div className="text-center pt-4 pb-2">
          <p className="text-xs text-gray-400">FinUp Mobile v1.0</p>
          <p className="text-xs text-gray-400 mt-1">© 2026 - Todos os direitos reservados</p>
        </div>
      </div>
    </div>
  );
}
