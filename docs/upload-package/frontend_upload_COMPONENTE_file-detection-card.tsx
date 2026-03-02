'use client';

/**
 * Sprint 3: FileDetectionCard
 * Exibe banco/tipo/período detectados + alerta de duplicata
 */
import { AlertTriangle, FileText, Building2, Calendar } from 'lucide-react';
import type { DetectionResult } from '../services/upload-api';
import { Button } from '@/components/ui/button';

interface FileDetectionCardProps {
  detection: DetectionResult;
  onProceed: () => void;
  onCancel: () => void;
  loading?: boolean;
  /** Sprint 5: quando banco=generico e tipo=planilha, chama este callback em vez de onProceed */
  onImportPlanilha?: () => void;
}

const BANCO_LABELS: Record<string, string> = {
  nubank: 'Nubank',
  itau: 'Itaú',
  btg: 'BTG Pactual',
  bb: 'Banco do Brasil',
  mercadopago: 'Mercado Pago',
  generico: 'Planilha genérica',
};

const TIPO_LABELS: Record<string, string> = {
  extrato: 'Extrato',
  fatura: 'Fatura',
  planilha: 'Planilha',
};

function formatPeriodo(inicio: string | null, fim: string | null): string {
  if (!inicio && !fim) return '—';
  if (inicio && fim && inicio !== fim) return `${inicio} a ${fim}`;
  return inicio || fim || '—';
}

export function FileDetectionCard({
  detection,
  onProceed,
  onCancel,
  loading = false,
  onImportPlanilha,
}: FileDetectionCardProps) {
  const duplicata = detection.duplicata_detectada;
  const bancoLabel = BANCO_LABELS[detection.banco] || detection.banco;
  const tipoLabel = TIPO_LABELS[detection.tipo] || detection.tipo;
  const isPlanilha = detection.banco === 'generico' && detection.tipo === 'planilha';

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="rounded-full bg-indigo-100 p-2">
          <FileText className="h-5 w-5 text-indigo-600" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-900 truncate">
            {detection.filename || 'Arquivo'}
          </p>
          <div className="mt-2 space-y-1 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <Building2 className="h-4 w-4 text-gray-400" />
              <span>{bancoLabel}</span>
              <span className="text-gray-400">•</span>
              <span>{tipoLabel}</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <span>{formatPeriodo(detection.periodo_inicio, detection.periodo_fim)}</span>
            </div>
          </div>

          {duplicata && (
            <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3">
              <div className="flex items-start gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-amber-900 text-sm">
                    Possível duplicata
                  </p>
                  <p className="text-xs text-amber-800 mt-0.5">
                    Já existe um upload similar ({duplicata.total_transacoes} transações).
                    Carregar de qualquer forma pode criar duplicatas.
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="mt-4 flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onCancel}
              disabled={loading}
            >
              Cancelar
            </Button>
            {isPlanilha && onImportPlanilha ? (
              <Button
                size="sm"
                onClick={onImportPlanilha}
                disabled={loading}
              >
                {loading ? 'Importando...' : 'Importar planilha'}
              </Button>
            ) : (
              <Button
                size="sm"
                onClick={onProceed}
                disabled={loading}
              >
                {loading ? 'Processando...' : duplicata ? 'Carregar de qualquer forma' : 'Continuar'}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
