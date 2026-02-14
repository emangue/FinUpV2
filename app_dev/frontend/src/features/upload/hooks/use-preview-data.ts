/**
 * usePreviewData Hook
 * Gerencia carregamento de dados de preview de uma sessão
 */

import { useState, useEffect } from 'react';
import { PreviewData } from '../types';
import { fetchPreviewData } from '../services/upload-api';

export function usePreviewData(sessionId: string | null) {
  const [data, setData] = useState<PreviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setLoading(false);
      return;
    }
    const id = sessionId;

    async function loadPreviewData() {
      try {
        setLoading(true);
        setError(null);
        const previewData = await fetchPreviewData(id);
        setData(previewData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
        console.error('Erro ao carregar preview:', err);
      } finally {
        setLoading(false);
      }
    }

    loadPreviewData();
  }, [sessionId]);

  return { data, loading, error };
}
