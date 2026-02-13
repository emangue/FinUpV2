import Button from '../atoms/Button';

interface BottomActionBarProps {
  hasUnclassified: boolean;
  onConfirm: () => void;
}

export default function BottomActionBar({ hasUnclassified, onConfirm }: BottomActionBarProps) {
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 max-w-md mx-auto shadow-lg z-30">
      <Button
        onClick={onConfirm}
        variant={hasUnclassified ? 'disabled' : 'primary'}
        fullWidth
        className="py-3"
      >
        Confirmar Importação
      </Button>
      {hasUnclassified && (
        <p className="text-center text-xs text-gray-500 mt-2">
          Classifique todas as transações para confirmar
        </p>
      )}
    </div>
  );
}
