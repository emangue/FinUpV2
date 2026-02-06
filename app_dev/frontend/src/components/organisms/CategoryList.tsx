import { SectionHeader } from '@/components/molecules/SectionHeader';
import { CategoryRow } from '@/components/molecules/CategoryRow';
import { Category } from '@/types/wallet';

interface CategoryListProps {
  title: string;
  categories: Category[];
}

export function CategoryList({ title, categories }: CategoryListProps) {
  return (
    <div className="space-y-4">
      {title && <SectionHeader title={title} />}
      <div className="bg-white rounded-2xl px-6 shadow-sm border border-gray-100 divide-y divide-gray-100">
        {categories.map((category) => (
          <CategoryRow
            key={category.id}
            category={category}
          />
        ))}
      </div>
    </div>
  );
}
