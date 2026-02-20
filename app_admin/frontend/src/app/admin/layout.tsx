"use client"

import { RequireAdmin } from "@/components/RequireAdmin"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { useAuth } from "@/contexts/AuthContext"
import { Button } from "@/components/ui/button"
import {
  Users,
  LayoutGrid,
  Building2,
  Database,
  Tags,
  LogOut,
  ChevronLeft,
} from "lucide-react"

const navItems = [
  { href: "/admin", label: "Dashboard", icon: LayoutGrid },
  { href: "/admin/contas", label: "Contas", icon: Users },
  { href: "/admin/screens", label: "Telas", icon: LayoutGrid },
  { href: "/admin/bancos", label: "Bancos", icon: Building2 },
  { href: "/admin/backup", label: "Backup", icon: Database },
  { href: "/admin/categorias-genericas", label: "Categorias Genéricas", icon: Tags },
]

export default function AdminLayout({
  children,
}: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const { logout } = useAuth()

  const handleLogout = () => {
    logout()
    router.push("/login")
  }

  return (
    <RequireAdmin>
      <div className="min-h-screen bg-slate-50">
        <header className="sticky top-0 z-10 border-b bg-white shadow-sm">
          <div className="flex h-14 items-center justify-between px-4">
            <Link href="/admin" className="flex items-center gap-2 font-semibold">
              <ChevronLeft className="h-5 w-5" />
              FinUp Admin
            </Link>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              Sair
            </Button>
          </div>
        </header>

        <nav className="border-b bg-white">
          <div className="flex gap-1 overflow-x-auto px-4 py-2">
            {navItems.map(({ href, label, icon: Icon }) => {
              const isActive = pathname === href || (href !== "/admin" && pathname.startsWith(href))
              return (
                <Link
                  key={href}
                  href={href}
                  className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {label}
                </Link>
              )
            })}
          </div>
        </nav>

        <main className="p-4">{children}</main>
      </div>
    </RequireAdmin>
  )
}
