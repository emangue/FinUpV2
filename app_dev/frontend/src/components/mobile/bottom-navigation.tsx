// src/components/mobile/bottom-navigation.tsx
// Mobile Experience V1.0 - BottomNavigation Component
// Data: 01/02/2026

'use client';

import { usePathname, useRouter } from 'next/navigation';
import { Home, List, Target, Wallet, User } from 'lucide-react';
import { cn } from '@/lib/utils';

export function BottomNavigation() {
  const pathname = usePathname();
  const router = useRouter();

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Home, path: '/mobile/dashboard' },
    { id: 'transactions', label: 'Transações', icon: List, path: '/mobile/transactions' },
    { id: 'budget', label: 'Metas', icon: Target, path: '/mobile/budget' },
    { id: 'carteira', label: 'Carteira', icon: Wallet, path: '/mobile/carteira' },
    { id: 'profile', label: 'Perfil', icon: User, path: '/mobile/profile' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50">
      <div className="flex items-center justify-around h-20 px-2">
        {tabs.map((tab, index) => {
          const Icon = tab.icon;
          const isActive = pathname.startsWith(tab.path);
          
          // FAB central (índice 2 = Metas)
          if (index === 2) {
            return (
              <div key={tab.id} className="flex flex-col items-center flex-1">
                {/* FAB */}
                <button
                  onClick={() => router.push(tab.path)}
                  className="
                    w-14 h-14 rounded-full bg-black text-white 
                    flex items-center justify-center 
                    shadow-lg -mt-6 
                    transition-transform duration-150 
                    active:scale-95
                  "
                  aria-label={tab.label}
                >
                  <Icon className="w-6 h-6" />
                </button>
                <span className="text-xs mt-1 text-gray-600">{tab.label}</span>
              </div>
            );
          }
          
          return (
            <button
              key={tab.id}
              onClick={() => router.push(tab.path)}
              className={cn(
                'flex flex-col items-center flex-1 py-2 transition-colors duration-150',
                isActive ? 'text-black' : 'text-gray-400'
              )}
              aria-label={tab.label}
            >
              <Icon className={cn('w-6 h-6', isActive && 'text-black')} />
              <span className="text-xs mt-1">{tab.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
