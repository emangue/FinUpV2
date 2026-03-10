'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { FileText, ChevronRight, Trash2, Calendar } from 'lucide-react';
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { months } from '@/features/upload/mocks/mockUploadData';

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
  const [rollbackPreview, setRollbackPreview] = useState<{ transacoes_count: number; parcelas_count: number; tem_vinculos_investimento: boolean } | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [periodDialogOpen, setPeriodDialogOpen] = useState(false);
  const [uploadToPeriod, setUploadToPeriod] = useState<UploadHistoryItem | null>(null);
  const [periodAno, setPeriodAno] = useState<number>(new Date().getFullYear());
  const [periodMes, setPeriodMes] = useState<number>(new Date().getMonth() + 1);
  const [updatingPeriod, setUpdatingPeriod] = useState(false);

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

  const handleDeleteClick = async (upload: UploadHistoryItem) => {
    setUploadToDelete(upload);
    setRollbackPreview(null);
    setDeleteDialogOpen(true);
    try {
      const res = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/history/${upload.id}/rollback-preview`
      );
      if (res.ok) {
        const data = await res.json();
        setRollbackPreview({
          transacoes_count: data.transacoes_count,
          parcelas_count: data.parcelas_count,
          tem_vinculos_investimento: data.tem_vinculos_investimento,
        });
      }
    } catch {
      setRollbackPreview({ transacoes_count: upload.transacoes_importadas, parcelas_count: 0, tem_vinculos_investimento: false });
    }
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
      setRollbackPreview(null);
      loadUploads();
    } catch (err) {
      console.error('Erro ao excluir upload:', err);
      alert(err instanceof Error ? err.message : 'Erro ao excluir upload');
    } finally {
      setDeleting(false);
    }
  };

  const handlePeriodClick = (upload: UploadHistoryItem) => {
    setUploadToPeriod(upload);
    if (upload.mes_fatura) {
      let ano: number, mes: number;
      if (upload.mes_fatura.includes('-')) {
        const [y, m] = upload.mes_fatura.split('-');
        ano = parseInt(y || '2025', 10);
        mes = parseInt(m || '1', 10);
      } else if (upload.mes_fatura.length >= 6) {
        ano = parseInt(upload.mes_fatura.slice(0, 4), 10);
        mes = parseInt(upload.mes_fatura.slice(4, 6), 10);
      } else {
        const now = new Date();
        ano = now.getFullYear();
        mes = now.getMonth() + 1;
      }
      setPeriodAno(ano);
      setPeriodMes(mes);
    } else {
      const now = new Date();
      setPeriodAno(now.getFullYear());
      setPeriodMes(now.getMonth() + 1);
    }
    setPeriodDialogOpen(true);
  };

  const handleConfirmPeriod = async () => {
    if (!uploadToPeriod) return;
    try {
      setUpdatingPeriod(true);
      const url = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/history/${uploadToPeriod.id}/periodo?ano=${periodAno}&mes=${periodMes}`;
      const response = await fetchWithAuth(url, { method: 'PATCH' });
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        const msg = err?.detail?.error || (typeof err?.detail === 'string' ? err.detail : null) || 'Erro ao ajustar período';
        throw new Error(msg);
      }
      setPeriodDialogOpen(false);
      setUploadToPeriod(null);
      loadUploads();
      alert(`Período ajustado para ${months[periodMes - 1]} ${periodAno}`);
    } catch (err) {
      console.error('Erro ao ajustar período:', err);
      alert(err instanceof Error ? err.message : 'Erro ao ajustar período');
    } finally {
      setUpdatingPeriod(false);
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
                  onClick={() => handlePeriodClick(upload)}
                  disabled={updatingPeriod}
                  className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
                  title="Ajustar ano e mês do período"
                  aria-label="Ajustar período"
                >
                  <Calendar className="w-4 h-4" />
                </button>
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

      <Dialog open={periodDialogOpen} onOpenChange={setPeriodDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Ajustar período</DialogTitle>
            <DialogDescription>
              Altere o ano e mês de todas as transações deste upload.
              {uploadToPeriod && (
                <span className="block mt-2 font-medium text-foreground">
                  {uploadToPeriod.nome_arquivo} • {uploadToPeriod.transacoes_importadas} transações
                </span>
              )}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Mês</label>
                <Select value={String(periodMes)} onValueChange={(v) => setPeriodMes(parseInt(v, 10))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {months.map((nome, i) => (
                      <SelectItem key={i} value={String(i + 1)}>{nome}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Ano</label>
                <Select value={String(periodAno)} onValueChange={(v) => setPeriodAno(parseInt(v, 10))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030].map((y) => (
                      <SelectItem key={y} value={String(y)}>{y}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setPeriodDialogOpen(false)}
              disabled={updatingPeriod}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={handleConfirmPeriod}
              disabled={updatingPeriod}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              {updatingPeriod ? 'Ajustando...' : 'Aplicar'}
            </button>
          </div>
        </DialogContent>
      </Dialog>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir upload</AlertDialogTitle>
            <AlertDialogDescription>
              Deseja excluir todas as {rollbackPreview?.transacoes_count ?? uploadToDelete?.transacoes_importadas ?? 0} transações deste upload?
              {rollbackPreview && rollbackPreview.parcelas_count > 0 && (
                <> e {rollbackPreview.parcelas_count} parcela(s) vinculada(s)</>
              )}
              ?
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
              {rollbackPreview?.tem_vinculos_investimento && (
                <>
                  <br />
                  <span className="text-amber-600 font-medium">⚠️ Este upload tem vínculos com investimentos.</span>
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
