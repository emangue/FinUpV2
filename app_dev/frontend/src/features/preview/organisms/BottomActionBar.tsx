import Button from '../atoms/Button';

interface BottomActionBarProps {
  hasUnclassified: boolean;
  onConfirm: () => void;
  isLoading?: boolean;
}

export default function BottomActionBar({ hasUnclassified, onConfirm, isLoading = false }: BottomActionBarProps) {
  return (
    <div className="fixed bottom-20 left-0 right-0 bg-white border-t border-gray-200 p-4 max-w-md mx-auto shadow-lg z-40">
      {/* Mensagem de status */}
      {!hasUnclassified && !isLoading && (
        <p className="text-center text-sm text-green-700 font-medium mb-3">
          ✓ Agora está ok para fazer o upload dos dados
        </p>
      )}
      {hasUnclassified && !isLoading && (
        <p className="text-center text-xs text-gray-500 mb-3">
          Classifique todas as transações para confirmar
        </p>
      )}
      {isLoading && (
        <p className="text-center text-xs text-gray-500 mb-3">
          Salvando transações no banco de dados...
        </p>
      )}

      <Button
        onClick={onConfirm}
        variant={hasUnclassified || isLoading ? 'disabled' : 'primary'}
        fullWidth
        className="py-3 font-semibold"
      >
        {isLoading ? 'Confirmando...' : 'Salvar e Importar Dados'}
      </Button>
    </div>
  );
}
