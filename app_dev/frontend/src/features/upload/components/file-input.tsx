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
      <label className="block text-sm font-bold text-gray-900 mb-3">
        Arquivo
      </label>
      <label className="flex items-center gap-3 px-6 py-4 border-2 border-dashed border-gray-200 rounded-xl cursor-pointer hover:border-gray-300 hover:bg-gray-50 transition-all">
        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
        </svg>
        <span className="text-sm font-semibold text-gray-700">Escolher Arquivo</span>
        <input 
          type="file" 
          className="hidden" 
          onChange={handleChange}
          accept={accept}
        />
      </label>
      <p className="text-sm text-gray-400 mt-2">{fileName}</p>
    </div>
  );
}
