import IconButton from '../atoms/IconButton';

interface PreviewHeaderProps {
  onCancel: () => void;
}

export default function PreviewHeader({ onCancel }: PreviewHeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-4 sticky top-0 z-40">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Preview de Importação</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Revise os dados antes de confirmar a importação
          </p>
        </div>
        <IconButton icon="close" onClick={onCancel} ariaLabel="Cancelar importação" />
      </div>
    </header>
  );
}
