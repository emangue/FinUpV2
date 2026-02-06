import { Badge } from '@/components/atoms/Badge';
import { ProgressBar } from '@/components/atoms/ProgressBar';
import type { Category } from '@/types/wallet';

interface CategoryRowProps {
  category: Category;
}

export function CategoryRow({ category }: CategoryRowProps) {
  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(val);
  };

  return (
    <div className="py-4">
      {/* Header: Badge + Label + Count + Valor Total */}
      <div className="flex items-center gap-3 mb-3">
        <Badge color={category.color} size={10} />
        <div className="flex-1">
          <span className="text-sm font-semibold text-gray-900">
            {category.label}
          </span>
          <span className="text-xs text-gray-500 ml-2">
            {category.count} {category.count === 1 ? 'ativo' : 'ativos'}
          </span>
        </div>
        <span className="text-sm font-bold text-gray-900">
          {formatCurrency(category.value)}
        </span>
      </div>

      {/* Progress Bar com percentual dentro */}
      <ProgressBar 
        percentage={category.percentage} 
        color={category.color}
        height={36}
        percentageLabel={category.percentage}
      />
    </div>
  );
}
