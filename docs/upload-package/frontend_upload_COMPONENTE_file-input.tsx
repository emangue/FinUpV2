/**
 * FileInput - Input de Upload de Arquivo
 * Componente reutilizável com drag & drop e seleção de arquivo
 */

interface FileInputProps {
  fileName: string;
  onChange: (file: File | null) => void;
  accept?: string;
}

export function FileInput({ fileName, onChange, accept = '.csv,.xls,.xlsx,.pdf,.ofx' }: FileInputProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    onChange(file || null);
  };

  return (
    <div className="mb-6">
      <label className="flex flex-col items-center gap-3 px-6 py-8 border-2 border-dashed border-gray-300 rounded-2xl cursor-pointer hover:border-gray-900 hover:bg-gray-50 transition-all bg-gray-50/50">
        <div className="rounded-full bg-gray-900 p-4">
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
          </svg>
        </div>
        <span className="text-base font-bold text-gray-900">Toque para escolher o arquivo</span>
        <span className="text-xs text-gray-500">CSV, Excel, PDF ou OFX</span>
        <input 
          type="file" 
          className="hidden" 
          onChange={handleChange}
          accept={accept}
        />
      </label>
      <p className="text-sm text-gray-500 mt-2 text-center">{fileName}</p>
    </div>
  );
}
