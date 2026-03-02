/**
 * useBanks Hook
 * Gerencia carregamento de instituições financeiras
 */

import { useState, useEffect } from 'react';
import { Bank } from '../types';
import { fetchBanks } from '../services/upload-api';

export function useBanks() {
  const [banks, setBanks] = useState<Bank[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadBanks() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchBanks();
        setBanks(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
        console.error('Erro ao carregar bancos:', err);
      } finally {
        setLoading(false);
      }
    }

    loadBanks();
  }, []);

  return { banks, loading, error };
}
