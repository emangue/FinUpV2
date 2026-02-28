'use client';

/**
 * DropZoneMulti - Sprint 4
 * Zona de drop para múltiplos arquivos com detecção paralela
 */
import { useCallback, useState } from 'react';
import { CloudUpload, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { detectFile, type DetectionResult } from '../services/upload-api';

export type FileDetectionState = {
  file: File;
  status: 'detectando' | 'ok' | 'erro';
  result: DetectionResult | null;
  error?: string;
};

interface DropZoneMultiProps {
  onFilesDetected?: (states: FileDetectionState[]) => void;
  maxFiles?: number;
  accept?: string;
  className?: string;
}

const ACCEPT_DEFAULT = '.csv,.xls,.xlsx,.pdf,.ofx';

export function DropZoneMulti({
  onFilesDetected,
  maxFiles = 10,
  accept = ACCEPT_DEFAULT,
  className,
}: DropZoneMultiProps) {
  const [files, setFiles] = useState<FileDetectionState[]>([]);
  const [isDragActive, setIsDragActive] = useState(false);

  const runDetection = useCallback(
    async (acceptedFiles: File[]) => {
      const limited = acceptedFiles.slice(0, maxFiles);
      const initial: FileDetectionState[] = limited.map((f) => ({
        file: f,
        status: 'detectando',
        result: null,
      }));
      setFiles(initial);

      const results = await Promise.allSettled(
        limited.map((f) => detectFile(f))
      );

      const updated: FileDetectionState[] = results.map((r, i) => {
        if (r.status === 'fulfilled') {
          return {
            ...initial[i],
            status: 'ok' as const,
            result: r.value,
          };
        }
        return {
          ...initial[i],
          status: 'erro' as const,
          result: null,
          error: r.reason?.message || 'Erro ao detectar',
        };
      });
      setFiles(updated);
      onFilesDetected?.(updated);
    },
    [maxFiles, onFilesDetected]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragActive(false);
      const dropped = Array.from(e.dataTransfer.files).filter((f) => f.size > 0);
      if (dropped.length) runDetection(dropped);
    },
    [runDetection]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
  }, []);

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selected = e.target.files ? Array.from(e.target.files) : [];
      e.target.value = '';
      if (selected.length) runDetection(selected);
    },
    [runDetection]
  );

  const removeFile = useCallback((index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }, []);

  return (
    <div className={cn('space-y-4', className)}>
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={cn(
          'border-2 border-dashed rounded-2xl p-8 text-center transition-colors cursor-pointer',
          isDragActive ? 'border-primary bg-primary/5' : 'border-gray-300 hover:border-gray-400 bg-gray-50/50'
        )}
        onClick={() => document.getElementById('dropzone-multi-input')?.click()}
      >
        <input
          id="dropzone-multi-input"
          type="file"
          multiple
          accept={accept}
          onChange={handleFileInput}
          className="hidden"
        />
        <CloudUpload className="mx-auto mb-2 text-gray-400" size={40} />
        <p className="font-medium text-gray-900">
          {isDragActive ? 'Solte os arquivos aqui' : 'Arraste arquivos ou clique para selecionar'}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Até {maxFiles} arquivos — CSV, Excel, PDF ou OFX
        </p>
      </div>

      {files.length > 0 && (
        <div className="space-y-3">
          {files.map((state, i) => (
            <FileDetectionCardMulti
              key={`${state.file.name}-${i}`}
              state={state}
              onRemove={() => removeFile(i)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function FileDetectionCardMulti({
  state,
  onRemove,
}: {
  state: FileDetectionState;
  onRemove: () => void;
}) {
  const { file, status, result, error } = state;

  if (status === 'detectando') {
    return (
      <div className="flex items-center gap-3 p-4 rounded-xl border border-gray-200 bg-white">
        <Loader2 className="animate-spin text-indigo-500 shrink-0" size={20} />
        <span className="text-sm font-medium text-gray-700 truncate flex-1">{file.name}</span>
      </div>
    );
  }

  if (status === 'erro') {
    return (
      <div className="flex items-center gap-3 p-4 rounded-xl border border-red-200 bg-red-50">
        <XCircle className="text-red-500 shrink-0" size={20} />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
          <p className="text-xs text-red-600">{error}</p>
        </div>
        <button
          onClick={onRemove}
          className="text-xs text-gray-500 hover:text-gray-700 underline"
        >
          Remover
        </button>
      </div>
    );
  }

  const bancoLabel = (result?.banco && (
    { nubank: 'Nubank', itau: 'Itaú', btg: 'BTG', bb: 'BB', mercadopago: 'Mercado Pago', generico: 'Planilha' }[result.banco]
  )) || result?.banco || '—';
  const tipoLabel = (result?.tipo && (
    { extrato: 'Extrato', fatura: 'Fatura', planilha: 'Planilha' }[result.tipo]
  )) || result?.tipo || '—';

  return (
    <div className="flex items-start gap-3 p-4 rounded-xl border border-gray-200 bg-white">
      <div className="rounded-full bg-green-100 p-2 shrink-0">
        <CheckCircle className="h-5 w-5 text-green-600" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-900 truncate">{file.name}</p>
        <p className="text-xs text-gray-600 mt-0.5">
          {bancoLabel} • {tipoLabel}
          {result?.periodo_inicio && ` • ${result.periodo_inicio}`}
        </p>
        {result?.duplicata_detectada && (
          <p className="text-xs text-amber-600 mt-1">⚠️ Possível duplicata</p>
        )}
      </div>
      <button
        onClick={onRemove}
        className="text-xs text-gray-500 hover:text-gray-700 underline shrink-0"
      >
        Remover
      </button>
    </div>
  );
}
