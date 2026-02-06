/**
 * useCreditCards Hook
 * Gerencia carregamento de cartões de crédito do usuário
 */

import { useState, useEffect } from 'react';
import { CreditCard } from '../types';
import { fetchCreditCards } from '../services/upload-api';

export function useCreditCards() {
  const [cards, setCards] = useState<CreditCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadCards() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchCreditCards();
        setCards(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
        console.error('Erro ao carregar cartões:', err);
      } finally {
        setLoading(false);
      }
    }

    loadCards();
  }, []);

  return { cards, loading, error };
}
