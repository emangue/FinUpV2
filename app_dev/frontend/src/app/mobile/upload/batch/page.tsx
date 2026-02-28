'use client';

/**
 * Upload em lote - Múltiplos arquivos
 * Sprint 4: DropZoneMulti + detecção paralela
 */
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { MobileHeader } from '@/components/mobile/mobile-header';
import { DropZoneMulti, type FileDetectionState } from '@/features/upload/components';
import { Button } from '@/components/ui/button';
import { useRequireAuth } from '@/core/hooks/use-require-auth';
import { fetchWithAuth } from '@/core/utils/api-client';
import { API_CONFIG } from '@/core/config/api.config';
import { toast } from 'sonner';

export default function UploadBatchPage() {
  const router = useRouter();
  const isAuth = useRequireAuth();
  const [files, setFiles] = useState<FileDetectionState[]>([]);
  const [uploading, setUploading] = useState(false);

  const handleFilesDetected = (states: FileDetectionState[]) => {
    setFiles(states);
  };

  const handleImportBatch = async () => {
    const okFiles = files.filter((f) => f.status === 'ok' && f.result);
    if (okFiles.length === 0) {
      toast.error('Nenhum arquivo válido para importar');
      return;
    }

    const bancos = [...new Set(okFiles.map((f) => f.result?.banco).filter(Boolean))];
    if (bancos.length > 1) {
      toast.error('Todos os arquivos devem ser do mesmo banco. Separe por banco.');
      return;
    }

    const banco = okFiles[0].result?.banco || 'generico';
    const tipo = okFiles[0].result?.tipo || 'extrato';

    const bancoParaApi: Record<string, string> = {
      itau: 'Itaú',
      btg: 'BTG Pactual',
      mercadopago: 'Mercado Pago',
      nubank: 'Nubank',
      bb: 'Banco do Brasil',
      generico: 'Planilha genérica',
    };
    const bancoForm = bancoParaApi[banco] || banco;

    setUploading(true);
    try {
      const formData = new FormData();
      okFiles.forEach((f) => formData.append('files', f.file));
      formData.append('banco', bancoForm);
      formData.append('tipoDocumento', tipo);

      const res = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/batch`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.detail?.error || err?.detail || 'Erro no upload');
      }

      const data = await res.json();
      toast.success(`${data.totalArquivos} arquivo(s) importado(s) — ${data.totalTransacoes} transações`);
      router.push(`/mobile/preview/${data.sessionId}`);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Erro ao importar');
    } finally {
      setUploading(false);
    }
  };

  if (!isAuth) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MobileHeader title="Importar em lote" leftAction="back" />
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      <MobileHeader title="Importar em lote" leftAction="back" />
      <div className="p-5">
        <DropZoneMulti onFilesDetected={handleFilesDetected} maxFiles={10} />

        {files.length > 0 && files.some((f) => f.status === 'ok') && (
          <div className="mt-6">
            <Button
              onClick={handleImportBatch}
              disabled={uploading}
              className="w-full"
            >
              {uploading ? 'Importando...' : `Importar ${files.filter((f) => f.status === 'ok').length} arquivo(s)`}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
