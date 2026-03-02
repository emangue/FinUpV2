/**
 * FormatSelector - Seletor de Formato de Arquivo
 * Componente reutilizável para seleção de formato (radio buttons)
 * Suporta formatAvailability para desabilitar formatos TBD (em breve)
 */

import { FileFormat } from '../types';
import type { FormatStatus } from '../services/upload-api';

interface FormatOption {
  value: FileFormat;
  label: string;
}

/** Mapa formato -> status (csv, excel, pdf, pdf-password usa pdf_status, ofx) */
export type FormatAvailability = Partial<Record<FileFormat, FormatStatus>>;

interface FormatSelectorProps {
  formats: FormatOption[];
  value: FileFormat;
  onChange: (format: FileFormat) => void;
  /** Status por formato: OK/WIP=clicável, TBD=desabilitado (em breve) */
  formatAvailability?: FormatAvailability;
  /** Quando true, mostra "(selecione um banco)" em vez de status */
  bankNotSelected?: boolean;
}

function getFormatStatus(
  format: FileFormat,
  availability?: FormatAvailability
): FormatStatus | undefined {
  if (!availability) return undefined;
  if (format === 'pdf-password') return availability.pdf ?? availability['pdf-password'];
  return availability[format];
}

function isFormatAvailable(status: FormatStatus | undefined, bankNotSelected: boolean): boolean {
  if (bankNotSelected) return false;
  if (status === undefined) return true;
  return status === 'OK' || status === 'WIP';
}

export function FormatSelector({
  formats,
  value,
  onChange,
  formatAvailability,
  bankNotSelected = false,
}: FormatSelectorProps) {
  return (
    <div className="mb-6">
      <label className="block text-sm font-bold text-gray-900 mb-3">
        Formato do arquivo para importação
      </label>
      <div className="space-y-3">
        {formats.map((format) => {
          const status = getFormatStatus(format.value, formatAvailability);
          const available = isFormatAvailable(status, bankNotSelected);
          return (
            <div key={format.value} className="flex items-center">
              <input
                type="radio"
                id={`format-${format.value}`}
                name="format"
                value={format.value}
                checked={value === format.value}
                onChange={(e) => available && onChange(e.target.value as FileFormat)}
                disabled={!available}
                className="hidden peer"
              />
              <label
                htmlFor={`format-${format.value}`}
                className={`relative flex items-center group ${
                  available ? 'cursor-pointer' : 'cursor-not-allowed opacity-60'
                }`}
              >
                <span
                  className={`w-[18px] h-[18px] border-2 rounded-full mr-3 flex items-center justify-center transition-colors ${
                    !available
                      ? 'border-gray-200 bg-gray-50'
                      : value === format.value
                        ? 'border-gray-900'
                        : 'border-gray-300 group-hover:border-gray-400'
                  }`}
                >
                  {value === format.value && available && (
                    <span className="w-2 h-2 bg-gray-900 rounded-full"></span>
                  )}
                </span>
                <span className="text-sm text-gray-700">
                  <span className="font-semibold">{format.label}</span>
                  <span className="text-gray-400 ml-2">
                    {bankNotSelected
                      ? '(selecione um banco)'
                      : status === 'TBD'
                        ? '(em breve)'
                        : status === 'WIP'
                          ? '(em desenvolvimento)'
                          : ''}
                  </span>
                </span>
              </label>
            </div>
          );
        })}
      </div>
    </div>
  );
}
