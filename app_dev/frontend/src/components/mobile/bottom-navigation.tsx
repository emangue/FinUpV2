// src/components/mobile/bottom-navigation.tsx
// UX Fundação S19 — Início | Transações | Upload (FAB) | Plano | Carteira
// Perfil fica no ícone engrenagem no header (S19.04)

'use client';

import { usePathname, useRouter } from 'next/navigation';
import { Home, List, Upload, Target, Wallet } from 'lucide-react';
import { cn } from '@/lib/utils';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Início', icon: Home, path: '/mobile/dashboard' },
  { id: 'transactions', label: 'Transações', icon: List, path: '/mobile/transactions' },
  { id: 'upload', label: 'Upload', icon: Upload, path: '/mobile/upload', fab: true },
  { id: 'budget', label: 'Plano', icon: Target, path: '/mobile/budget' },
  { id: 'carteira', label: 'Carteira', icon: Wallet, path: '/mobile/carteira' },
];

export function BottomNavigation() {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 pb-[env(safe-area-inset-bottom)]">
      <div className="flex items-end justify-around px-2 h-20">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname.startsWith(item.path);

          if (item.fab) {
            return (
              <div key={item.id} className="flex flex-col items-center flex-1 -mt-5 mb-1">
                <button
                  onClick={() => router.push(item.path)}
                  className="w-14 h-14 rounded-full bg-primary text-primary-foreground flex items-center justify-center shadow-lg transition-transform duration-150 active:scale-95"
                  aria-label={item.label}
                >
                  <Icon className="w-6 h-6" />
                </button>
                <span className="text-xs mt-1 font-medium text-primary">{item.label}</span>
              </div>
            );
          }

          return (
            <button
              key={item.id}
              onClick={() => router.push(item.path)}
              className={cn(
                'flex flex-col items-center justify-center flex-1 py-2 px-3 gap-1 min-h-[44px] transition-colors duration-150',
                isActive ? 'text-primary' : 'text-muted-foreground'
              )}
              aria-label={item.label}
            >
              <Icon className={cn('w-5 h-5', isActive && 'fill-primary')} />
              <span className="text-xs">{item.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
