interface SectionHeaderProps {
  title: string;
}

export function SectionHeader({ title }: SectionHeaderProps) {
  return (
    <h2 className="text-base font-semibold text-gray-900 mb-3">
      {title}
    </h2>
  );
}
