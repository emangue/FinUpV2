'use client'

import { usePathname, useRouter } from 'next/navigation'
import { Home, Receipt, Target, User } from 'lucide-react'

export function BottomNav() {
  const pathname = usePathname()
  const router = useRouter()

  const navItems = [
    {
      label: 'Início',
      icon: Home,
      path: '/dashboard/mobile',
      active: pathname === '/dashboard/mobile'
    },
    {
      label: 'Transações',
      icon: Receipt,
      path: '/transactions',
      active: pathname === '/transactions'
    },
    {
      label: 'Metas',
      icon: Target,
      path: '/budget',
      active: pathname === '/budget'
    },
    {
      label: 'Perfil',
      icon: User,
      path: '/settings/profile',
      active: pathname === '/settings/profile'
    }
  ]

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-lg">
      <div className="flex items-center justify-around h-16 px-2">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <button
              key={item.path}
              onClick={() => router.push(item.path)}
              className={`flex flex-col items-center justify-center flex-1 h-full gap-1 transition-colors ${
                item.active
                  ? 'text-primary'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className={`h-5 w-5 ${item.active ? 'stroke-[2.5]' : ''}`} />
              <span className={`text-xs ${item.active ? 'font-semibold' : 'font-medium'}`}>
                {item.label}
              </span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}
