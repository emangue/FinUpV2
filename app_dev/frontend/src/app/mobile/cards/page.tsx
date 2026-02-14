'use client';

/**
 * Cards Mobile - Gerenciamento de Cartões
 * Data: 14/02/2026
 * Tela mobile para gerenciar cartões de crédito
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { MobileHeader } from '@/components/mobile/mobile-header';
import { fetchWithAuth } from '@/core/utils/api-client';
import { API_CONFIG } from '@/core/config/api.config';
import { CreditCard, Plus, Edit, Trash2 } from 'lucide-react';
import { useRequireAuth } from '@/core/hooks/use-require-auth';

interface Card {
  id: number;
  nome_cartao: string;
  final_cartao: string;
  banco: string;
  ativo: number;
}

interface Bank {
  id: number;
  bank_name: string;
}

export default function CardsMobilePage() {
  const router = useRouter();
  const isAuth = useRequireAuth();
  const [cards, setCards] = useState<Card[]>([]);
  const [banks, setBanks] = useState<Bank[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCard, setEditingCard] = useState<Card | null>(null);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  
  // Form state
  const [cardName, setCardName] = useState('');
  const [lastDigits, setLastDigits] = useState('');
  const [selectedBank, setSelectedBank] = useState('');

  useEffect(() => {
    if (isAuth) {
      loadData();
    }
  }, [isAuth]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Carregar cartões
      const cardsResponse = await fetchWithAuth(`${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/cards/`);
      if (cardsResponse.ok) {
        const cardsData = await cardsResponse.json();
        setCards(cardsData.cards || []);
      }

      // Carregar bancos
      const banksResponse = await fetchWithAuth(`${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/compatibility/`);
      if (banksResponse.ok) {
        const banksData = await banksResponse.json();
        setBanks(banksData.banks || []);
      }
    } catch (err) {
      console.error('Erro ao carregar dados:', err);
      setError('Erro ao carregar cartões');
    } finally {
      setLoading(false);
    }
  };

  const handleAddCard = () => {
    setEditingCard(null);
    setCardName('');
    setLastDigits('');
    setSelectedBank('');
    setError('');
    setShowModal(true);
  };

  const handleEditCard = (card: Card) => {
    setEditingCard(card);
    setCardName(card.nome_cartao);
    setLastDigits(card.final_cartao);
    setSelectedBank(card.banco);
    setError('');
    setShowModal(true);
  };

  const handleSaveCard = async () => {
    // Validações
    if (!cardName.trim()) {
      setError('Nome do cartão é obrigatório');
      return;
    }

    if (!lastDigits.trim() || lastDigits.length !== 4) {
      setError('Final do cartão deve ter 4 dígitos');
      return;
    }

    if (!selectedBank.trim()) {
      setError('Selecione um banco');
      return;
    }

    try {
      const url = editingCard
        ? `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/cards/${editingCard.id}`
        : `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/cards/`;
      
      const method = editingCard ? 'PUT' : 'POST';
      
      const response = await fetchWithAuth(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome_cartao: cardName.trim(),
          final_cartao: lastDigits.trim(),
          banco: selectedBank.trim()
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao salvar cartão');
      }

      setShowModal(false);
      setSuccessMessage(editingCard ? 'Cartão atualizado!' : 'Cartão adicionado!');
      setTimeout(() => setSuccessMessage(''), 3000);
      loadData();
    } catch (err: any) {
      setError(err.message || 'Erro ao salvar cartão');
    }
  };

  const handleDeleteCard = async (cardId: number) => {
    if (!confirm('Deseja realmente deletar este cartão?')) return;

    try {
      const response = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/cards/${cardId}`,
        { method: 'DELETE' }
      );

      if (!response.ok) {
        throw new Error('Erro ao deletar cartão');
      }

      setSuccessMessage('Cartão deletado com sucesso!');
      setTimeout(() => setSuccessMessage(''), 3000);
      loadData();
    } catch (err) {
      setError('Erro ao deletar cartão');
      setTimeout(() => setError(''), 3000);
    }
  };

  if (!isAuth) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MobileHeader title="Cartões" leftAction="back" onBack={() => router.push('/mobile/profile')} />
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
        <MobileHeader title="Cartões" leftAction="back" onBack={() => router.push('/mobile/profile')} />
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Carregando cartões...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="Meus Cartões" leftAction="back" onBack={() => router.push('/mobile/profile')} />
      
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

        {/* Add Card Button */}
        <button
          onClick={handleAddCard}
          className="w-full bg-indigo-600 text-white rounded-2xl p-4 flex items-center justify-center space-x-2 font-semibold hover:bg-indigo-700 transition-colors shadow-sm"
        >
          <Plus className="w-5 h-5" />
          <span>Adicionar Cartão</span>
        </button>

        {/* Cards List */}
        {cards.length === 0 ? (
          <div className="bg-white rounded-2xl p-8 text-center shadow-sm">
            <CreditCard className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Nenhum cartão cadastrado
            </h3>
            <p className="text-sm text-gray-500">
              Adicione seus cartões para facilitar a importação de faturas
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {cards.map((card) => (
              <div key={card.id} className="bg-white rounded-2xl p-4 shadow-sm">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3 flex-1">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                      <CreditCard className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{card.nome_cartao}</h3>
                      <p className="text-sm text-gray-500">{card.banco}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        •••• {card.final_cartao}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEditCard(card)}
                      className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                    >
                      <Edit className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDeleteCard(card.id)}
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
          <div className="bg-white rounded-t-3xl w-full max-w-md animate-slide-up">
            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  {editingCard ? 'Editar' : 'Adicionar'} Cartão
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
                  Nome do Cartão
                </label>
                <input
                  type="text"
                  value={cardName}
                  onChange={(e) => setCardName(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="Ex: Mastercard Black"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Últimos 4 dígitos
                </label>
                <input
                  type="text"
                  value={lastDigits}
                  onChange={(e) => setLastDigits(e.target.value.replace(/\D/g, '').slice(0, 4))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="1234"
                  maxLength={4}
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
                  <option value="">Selecione o banco</option>
                  {[...new Set(banks.map(b => b.bank_name))].map((bank) => (
                    <option key={bank} value={bank}>
                      {bank}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex gap-2 pt-4">
                <button
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleSaveCard}
                  className="flex-1 px-4 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700"
                >
                  {editingCard ? 'Salvar' : 'Adicionar'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
