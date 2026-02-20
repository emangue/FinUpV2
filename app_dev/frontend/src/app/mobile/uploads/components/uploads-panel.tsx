'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { FileText, ChevronRight, Trash2 } from 'lucide-react';
import { fetchWithAuth } from '@/core/utils/api-client';
import { API_CONFIG } from '@/core/config/api.config';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

interface UploadHistoryItem {
  id: number;
  session_id: string;
  banco: string;
  tipo_documento: string;
  nome_arquivo: string;
  nome_cartao?: string;
  mes_fatura?: string;
  status: string;
  total_registros: number;
  transacoes_importadas: number;
  transacoes_duplicadas: number;
  valor_somado?: number;
  classification_stats?: Record<string, number>;
  data_upload: string;
  data_confirmacao?: string;
}

interface UploadsPanelProps {
  limit?: number;
}

export function UploadsPanel({ limit = 10 }: UploadsPanelProps) {
  const router = useRouter();
  const [uploads, setUploads] = useState<UploadHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recreating, setRecreating] = useState<number | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [uploadToDelete, setUploadToDelete] = useState<UploadHistoryItem | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadUploads();
  }, [limit]);

  const loadUploads = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/history?limit=${limit}&offset=0&status=success`
      );
      if (!response.ok) throw new Error('Erro ao carregar histórico');
      const data = await response.json();
      setUploads(data.uploads || []);
    } catch (err) {
      console.error('Erro ao carregar uploads:', err);
      setError('Não foi possível carregar o histórico de uploads');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (upload: UploadHistoryItem) => {
    setUploadToDelete(upload);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!uploadToDelete) return;
    try {
      setDeleting(true);
      const response = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/history/${uploadToDelete.id}`,
        { method: 'DELETE' }
      );
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        const msg = err?.detail?.error || (typeof err?.detail === 'string' ? err.detail : null) || 'Erro ao excluir';
        throw new Error(msg);
      }
      setDeleteDialogOpen(false);
      setUploadToDelete(null);
      loadUploads();
    } catch (err) {
      console.error('Erro ao excluir upload:', err);
      alert(err instanceof Error ? err.message : 'Erro ao excluir upload');
    } finally {
      setDeleting(false);
    }
  };

  const handleRevisar = async (upload: UploadHistoryItem) => {
    if (upload.status !== 'success') return;
    try {
      setRecreating(upload.id);
      const response = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/recreate-preview/${upload.id}`,
        { method: 'POST' }
      );
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        const msg = err?.detail?.error || (typeof err?.detail === 'string' ? err.detail : null) || 'Erro ao criar preview';
        throw new Error(msg);
      }
      const { session_id } = await response.json();
      router.push(`/mobile/preview/${session_id}`);
    } catch (err) {
      console.error('Erro ao revisar upload:', err);
      alert(err instanceof Error ? err.message : 'Erro ao abrir preview');
    } finally {
      setRecreating(null);
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-sm">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
          Histórico de Uploads
        </h3>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-sm">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
          Histórico de Uploads
        </h3>
        <p className="text-sm text-red-600">{error}</p>
      </div>
    );
  }

  if (uploads.length === 0) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-sm">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
          Histórico de Uploads
        </h3>
        <p className="text-sm text-gray-500 py-4">Nenhum upload realizado ainda.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
      <div className="p-4 border-b border-gray-100">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          Histórico de Uploads
        </h3>
        <p className="text-xs text-gray-400 mt-0.5">Últimos {uploads.length} uploads realizados</p>
      </div>

      <div className="divide-y divide-gray-100">
        {uploads.map((upload) => (
          <div
            key={upload.id}
            className="p-4 hover:bg-gray-50/50 transition-colors"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <FileText className="w-4 h-4 text-indigo-500 shrink-0" />
                  <span className="font-medium text-gray-900 truncate">
                    {upload.nome_arquivo}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded-full text-green-600 bg-green-50">
                    Confirmado
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {upload.banco}
                  {upload.nome_cartao && ` • ${upload.nome_cartao}`}
                  {upload.mes_fatura && ` • ${upload.mes_fatura}`}
                </p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {formatDate(upload.data_upload)}
                </p>

                <div className="flex flex-wrap gap-3 mt-2 text-xs text-gray-600">
                  <span title="Total processado">
                    📊 {upload.total_registros} processadas
                  </span>
                  <span title="Salvas na base" className="text-green-600">
                    ✓ {upload.transacoes_importadas} salvas
                  </span>
                  {upload.valor_somado != null && (
                    <span title="Valor total das transações" className="font-medium">
                      💰 {upload.valor_somado < 0 ? '-' : ''}R$ {Math.abs(upload.valor_somado).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                  )}
                  {upload.transacoes_duplicadas > 0 && (
                    <span title="Duplicadas ignoradas" className="text-amber-600">
                      ⚠ {upload.transacoes_duplicadas} duplicadas
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => handleDeleteClick(upload)}
                  disabled={deleting}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                  title="Excluir todas as transações deste upload"
                  aria-label="Excluir upload"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleRevisar(upload)}
                  disabled={recreating !== null}
                  className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 disabled:opacity-50"
                >
                  {recreating === upload.id ? (
                    <>
                      <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-indigo-600" />
                      Abrindo...
                    </>
                  ) : (
                    <>
                      <ChevronRight className="w-4 h-4" />
                      Revisar
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir upload</AlertDialogTitle>
            <AlertDialogDescription>
              Deseja excluir todas as {uploadToDelete?.transacoes_importadas ?? 0} transações deste upload?
              <br />
              <br />
              <strong>{uploadToDelete?.nome_arquivo}</strong>
              {uploadToDelete?.banco && (
                <>
                  <br />
                  {uploadToDelete.banco}
                  {uploadToDelete.nome_cartao && ` • ${uploadToDelete.nome_cartao}`}
                </>
              )}
              <br />
              <br />
              Esta ação não pode ser desfeita.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={(e) => {
                e.preventDefault();
                handleConfirmDelete();
              }}
              disabled={deleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleting ? 'Excluindo...' : 'Sim, excluir'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
