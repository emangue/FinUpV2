/**
 * FormatSelector - Seletor de Formato de Arquivo
 * Componente reutilizável para seleção de formato (radio buttons)
 */

import { FileFormat } from '../types';

interface FormatOption {
  value: FileFormat;
  label: string;
}

interface FormatSelectorProps {
  formats: FormatOption[];
  value: FileFormat;
  onChange: (format: FileFormat) => void;
}

export function FormatSelector({ formats, value, onChange }: FormatSelectorProps) {
  return (
    <div className="mb-6">
      <label className="block text-sm font-bold text-gray-900 mb-3">
        Formato do arquivo para importação
      </label>
      <div className="space-y-3">
        {formats.map((format) => (
          <div key={format.value} className="flex items-center">
            <input 
              type="radio" 
              id={`format-${format.value}`}
              name="format" 
              value={format.value}
              checked={value === format.value}
              onChange={(e) => onChange(e.target.value as FileFormat)}
              className="hidden peer"
            />
            <label 
              htmlFor={`format-${format.value}`}
              className="relative flex items-center cursor-pointer group"
            >
              <span className={`w-[18px] h-[18px] border-2 rounded-full mr-3 flex items-center justify-center transition-colors ${
                value === format.value
                  ? 'border-gray-900'
                  : 'border-gray-300 group-hover:border-gray-400'
              }`}>
                {value === format.value && (
                  <span className="w-2 h-2 bg-gray-900 rounded-full"></span>
                )}
              </span>
              <span className="text-sm text-gray-700">
                <span className="font-semibold">{format.label}</span>
                <span className="text-gray-400 ml-2">(selecione um banco)</span>
              </span>
            </label>
          </div>
        ))}
      </div>
    </div>
  );
}
