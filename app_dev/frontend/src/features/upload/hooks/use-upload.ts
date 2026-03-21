/**
 * useUpload Hook
 * Gerencia upload de arquivo e navegação
 */

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { uploadFile, PasswordRequiredError } from '../services/upload-api';

export function useUpload() {
  const router = useRouter();
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const upload = async (formData: {
    file: File;
    banco: string;
    tipo: 'extrato' | 'fatura';
    cartaoId?: string;
    cartaoNome?: string;
    cartaoFinal?: string;
    mes?: string;
    ano?: number;
    formato: string;
    senha?: string;  // Senha do PDF protegido (opcional)
  }) => {
    try {
      setUploading(true);
      setProgress(0);
      setError(null);

      // Simular progresso (TODO: implementar progresso real com XMLHttpRequest)
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const result = await uploadFile(formData);

      clearInterval(progressInterval);
      setProgress(100);

      // ✅ Retornar resultado sem fazer redirect automático
      // Deixar o componente decidir para onde redirecionar
      return result;
    } catch (err) {
      if (err instanceof PasswordRequiredError) {
        // Erro esperado: arquivo protegido por senha. Repassa para o componente tratar.
        // Não logar como erro para não disparar o overlay do Next.js dev.
        throw err;
      }
      setError(err instanceof Error ? err.message : 'Erro ao fazer upload');
      console.error('Erro no upload:', err);
      throw err;
    } finally {
      setUploading(false);
    }
  };

  return { upload, uploading, progress, error };
}
