'use client';

/**
 * Exclusions Mobile - Gerenciamento de Exclusões
 * Data: 14/02/2026
 * Tela mobile para gerenciar transações a excluir/ignorar
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { MobileHeader } from '@/components/mobile/mobile-header';
import { fetchWithAuth } from '@/core/utils/api-client';
import { API_CONFIG } from '@/core/config/api.config';
import { Ban, Plus, Edit, Trash2, Eye, EyeOff } from 'lucide-react';
import { useRequireAuth } from '@/core/hooks/use-require-auth';

interface Exclusion {
  id: number;
  nome_transacao: string;
  banco: string | null;
  tipo_documento: string | null;
  descricao: string | null;
  ativo: number;
  acao: string; // 'EXCLUIR' ou 'IGNORAR'
}

interface Bank {
  id: number;
  bank_name: string;
}

export default function ExclusionsMobilePage() {
  const router = useRouter();
  const isAuth = useRequireAuth();
  const [exclusions, setExclusions] = useState<Exclusion[]>([]);
  const [banks, setBanks] = useState<Bank[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingExclusion, setEditingExclusion] = useState<Exclusion | null>(null);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  
  // Form state
  const [transactionName, setTransactionName] = useState('');
  const [selectedBank, setSelectedBank] = useState('TODOS');
  const [applyToCard, setApplyToCard] = useState(true);
  const [applyToStatement, setApplyToStatement] = useState(true);
  const [action, setAction] = useState('EXCLUIR');
  const [description, setDescription] = useState('');

  useEffect(() => {
    if (isAuth) {
      loadData();
    }
  }, [isAuth]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Carregar exclusões
      const exclusionsResponse = await fetchWithAuth(`${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/exclusoes/`);
      if (exclusionsResponse.ok) {
        const exclusionsData = await exclusionsResponse.json();
        setExclusions(exclusionsData.exclusoes || []);
      }

      // Carregar bancos
      const banksResponse = await fetchWithAuth(`${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/compatibility/`);
      if (banksResponse.ok) {
        const banksData = await banksResponse.json();
        setBanks(banksData.banks || []);
      }
    } catch (err) {
      console.error('Erro ao carregar dados:', err);
      setError('Erro ao carregar regras');
    } finally {
      setLoading(false);
    }
  };

  const handleAddExclusion = () => {
    setEditingExclusion(null);
    setTransactionName('');
    setSelectedBank('TODOS');
    setApplyToCard(true);
    setApplyToStatement(true);
    setAction('EXCLUIR');
    setDescription('');
    setError('');
    setShowModal(true);
  };

  const handleEditExclusion = (exclusion: Exclusion) => {
    setEditingExclusion(exclusion);
    setTransactionName(exclusion.nome_transacao);
    setSelectedBank(exclusion.banco || 'TODOS');
    
    const tipo = exclusion.tipo_documento || 'ambos';
    setApplyToCard(tipo === 'cartao' || tipo === 'ambos');
    setApplyToStatement(tipo === 'extrato' || tipo === 'ambos');
    
    setAction(exclusion.acao || 'EXCLUIR');
    setDescription(exclusion.descricao || '');
    setError('');
    setShowModal(true);
  };

  const handleSaveExclusion = async () => {
    // Validações
    if (!transactionName.trim()) {
      setError('Nome da transação é obrigatório');
      return;
    }

    if (!applyToCard && !applyToStatement) {
      setError('Selecione pelo menos um tipo de documento');
      return;
    }

    // Determinar tipo_documento
    let tipoDocumento = 'ambos';
    if (applyToCard && !applyToStatement) {
      tipoDocumento = 'cartao';
    } else if (applyToStatement && !applyToCard) {
      tipoDocumento = 'extrato';
    }

    try {
      const url = editingExclusion
        ? `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/exclusoes/${editingExclusion.id}`
        : `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/exclusoes/`;
      
      const method = editingExclusion ? 'PUT' : 'POST';
      
      const response = await fetchWithAuth(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome_transacao: transactionName.trim(),
          banco: selectedBank === 'TODOS' ? null : selectedBank.trim(),
          tipo_documento: tipoDocumento,
          descricao: description.trim() || null,
          acao: action
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao salvar regra');
      }

      setShowModal(false);
      setSuccessMessage(editingExclusion ? 'Regra atualizada!' : 'Regra adicionada!');
      setTimeout(() => setSuccessMessage(''), 3000);
      loadData();
    } catch (err: any) {
      setError(err.message || 'Erro ao salvar regra');
    }
  };

  const handleDeleteExclusion = async (exclusionId: number) => {
    if (!confirm('Deseja realmente deletar esta regra?')) return;

    try {
      const response = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/exclusoes/${exclusionId}`,
        { method: 'DELETE' }
      );

      if (!response.ok) {
        throw new Error('Erro ao deletar regra');
      }

      setSuccessMessage('Regra deletada com sucesso!');
      setTimeout(() => setSuccessMessage(''), 3000);
      loadData();
    } catch (err) {
      setError('Erro ao deletar regra');
      setTimeout(() => setError(''), 3000);
    }
  };

  if (!isAuth) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MobileHeader title="Exclusões" leftAction="back" onBack={() => router.push('/mobile/profile')} />
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Verificando autenticação...</p>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MobileHeader title="Exclusões" leftAction="back" onBack={() => router.push('/mobile/profile')} />
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Carregando regras...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="Excluir / Ignorar" leftAction="back" onBack={() => router.push('/mobile/profile')} />
      
      <div className="p-5 space-y-4">
        {/* Success Message */}
        {successMessage && (
          <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
            {successMessage}
          </div>
        )}

        {/* Error Message */}
        {error && !showModal && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Add Button */}
        <button
          onClick={handleAddExclusion}
          className="w-full bg-indigo-600 text-white rounded-2xl p-4 flex items-center justify-center space-x-2 font-semibold hover:bg-indigo-700 transition-colors shadow-sm"
        >
          <Plus className="w-5 h-5" />
          <span>Nova Regra</span>
        </button>

        {/* Stats */}
        <div className="bg-white rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-around">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{exclusions.length}</p>
              <p className="text-xs text-gray-500">Total</p>
            </div>
            <div className="h-8 w-px bg-gray-200"></div>
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">
                {exclusions.filter(e => e.acao === 'EXCLUIR').length}
              </p>
              <p className="text-xs text-gray-500">Excluir</p>
            </div>
            <div className="h-8 w-px bg-gray-200"></div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {exclusions.filter(e => e.acao === 'IGNORAR').length}
              </p>
              <p className="text-xs text-gray-500">Ignorar</p>
            </div>
          </div>
        </div>

        {/* Exclusions List */}
        {exclusions.length === 0 ? (
          <div className="bg-white rounded-2xl p-8 text-center shadow-sm">
            <Ban className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Nenhuma regra cadastrada
            </h3>
            <p className="text-sm text-gray-500">
              Adicione regras para excluir ou ignorar transações específicas
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {exclusions.map((exclusion) => (
              <div key={exclusion.id} className="bg-white rounded-2xl p-4 shadow-sm">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-gray-900">
                        {exclusion.nome_transacao}
                      </h3>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        exclusion.acao === 'EXCLUIR' 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {exclusion.acao === 'EXCLUIR' ? (
                          <span className="flex items-center gap-1">
                            <EyeOff className="w-3 h-3" />
                            Excluir
                          </span>
                        ) : (
                          <span className="flex items-center gap-1">
                            <Eye className="w-3 h-3" />
                            Ignorar
                          </span>
                        )}
                      </span>
                    </div>
                    
                    <div className="space-y-1">
                      <p className="text-sm text-gray-600">
                        <span className="font-medium">Banco:</span>{' '}
                        {exclusion.banco || 'Todos'}
                      </p>
                      <p className="text-sm text-gray-600">
                        <span className="font-medium">Tipo:</span>{' '}
                        {exclusion.tipo_documento === 'cartao' ? 'Cartão' :
                         exclusion.tipo_documento === 'extrato' ? 'Extrato' :
                         'Ambos'}
                      </p>
                      {exclusion.descricao && (
                        <p className="text-xs text-gray-500 italic">
                          {exclusion.descricao}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex gap-2 ml-3">
                    <button
                      onClick={() => handleEditExclusion(exclusion)}
                      className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                    >
                      <Edit className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDeleteExclusion(exclusion.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-end justify-center z-50 p-4">
          <div className="bg-white rounded-t-3xl w-full max-w-md animate-slide-up max-h-[90vh] overflow-y-auto">
            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  {editingExclusion ? 'Editar' : 'Adicionar'} Regra
                </h2>
                <button
                  onClick={() => setShowModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nome da Transação *
                </label>
                <input
                  type="text"
                  value={transactionName}
                  onChange={(e) => setTransactionName(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="Ex: PAGAMENTO EFETUADO"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Banco
                </label>
                <select
                  value={selectedBank}
                  onChange={(e) => setSelectedBank(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="TODOS">Todos os bancos</option>
                  {[...new Set(banks.map(b => b.bank_name))].map((bank) => (
                    <option key={bank} value={bank}>
                      {bank}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Aplicar para *
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={applyToCard}
                      onChange={(e) => setApplyToCard(e.target.checked)}
                      className="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                    />
                    <span className="ml-3 text-sm text-gray-700">Cartão de Crédito</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={applyToStatement}
                      onChange={(e) => setApplyToStatement(e.target.checked)}
                      className="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                    />
                    <span className="ml-3 text-sm text-gray-700">Extrato Bancário</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ação *
                </label>
                <div className="space-y-2">
                  <label className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      value="EXCLUIR"
                      checked={action === 'EXCLUIR'}
                      onChange={(e) => setAction(e.target.value)}
                      className="w-4 h-4 text-red-600 focus:ring-red-500"
                    />
                    <div className="ml-3 flex-1">
                      <p className="text-sm font-medium text-gray-900">Excluir</p>
                      <p className="text-xs text-gray-500">Remove da importação (não aparece no preview)</p>
                    </div>
                  </label>
                  <label className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      value="IGNORAR"
                      checked={action === 'IGNORAR'}
                      onChange={(e) => setAction(e.target.value)}
                      className="w-4 h-4 text-yellow-600 focus:ring-yellow-500"
                    />
                    <div className="ml-3 flex-1">
                      <p className="text-sm font-medium text-gray-900">Ignorar</p>
                      <p className="text-xs text-gray-500">Importa mas não conta em dashboards</p>
                    </div>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Descrição (opcional)
                </label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="Ex: Pagamento da fatura anterior"
                />
              </div>

              <div className="flex gap-2 pt-4">
                <button
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleSaveExclusion}
                  className="flex-1 px-4 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700"
                >
                  {editingExclusion ? 'Salvar' : 'Adicionar'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
