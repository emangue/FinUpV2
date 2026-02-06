import { ReactNode } from 'react';

interface StatCardProps {
  children: ReactNode;
  padding?: string; // Tailwind class
}

export function StatCard({ children, padding = 'p-6' }: StatCardProps) {
  return (
    <div className={`bg-white rounded-3xl shadow-sm ${padding}`}>
      {children}
    </div>
  );
}
