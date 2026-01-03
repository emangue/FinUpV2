import { LayoutDashboard, CreditCard, Upload, Settings } from 'lucide-react'
import { cn } from '../lib/utils'

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard', active: true },
  { icon: CreditCard, label: 'Transações', href: '/transacoes', active: false },
  { icon: Upload, label: 'Upload', href: '/upload', active: false },
  { icon: Settings, label: 'Admin', href: '/admin', active: false },
]

export default function Sidebar() {
  return (
    <aside className="w-72 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center justify-center border-b border-gray-200">
        <h1 className="text-2xl font-bold text-blue-600">FinUp DEV</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <a
              key={item.label}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                item.active
                  ? 'bg-blue-50 text-blue-600 font-medium'
                  : 'text-gray-600 hover:bg-gray-50'
              )}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </a>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          v4.0.0-dev • React + Flask API
        </p>
      </div>
    </aside>
  )
}
