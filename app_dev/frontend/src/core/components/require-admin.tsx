'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'

interface RequireAdminProps {
  children: React.ReactNode
}

/**
 * 🔐 PROTEÇÃO DE ROTAS ADMIN
 * 
 * Componente que protege rotas administrativas.
 * Redireciona usuários não-admin para página 404 (eles nem sabem que a rota existe).
 * 
 * **Como usar:**
 * ```tsx
 * export default function AdminPage() {
 *   return (
 *     <RequireAdmin>
 *       <div>Conteúdo Admin</div>
 *     </RequireAdmin>
 *   )
 * }
 * ```
 * 
 * **Proteção em 3 camadas:**
 * 1. Backend: `require_admin` dependency (403 Forbidden)
 * 2. Frontend: Este componente (redirect para 404)
 * 3. Sidebar: Links admin escondidos para não-admins
 * 
 * **Comportamento:**
 * - Carregando: Mostra null (sem flash de conteúdo)
 * - Não autenticado: Redireciona para /404
 * - Autenticado mas não admin: Redireciona para /404
 * - Admin: Renderiza children normalmente
 */
export function RequireAdmin({ children }: RequireAdminProps) {
  const router = useRouter()
  const { user, loading } = useAuth()
  
  useEffect(() => {
    if (!loading && (!user || user.role !== 'admin')) {
      // Redireciona para 404 - usuário não sabe que rota existe
      router.push('/404')
    }
  }, [user, loading, router])
  
  // Não renderiza nada enquanto valida ou se não for admin
  if (loading || !user || user.role !== 'admin') {
    return null
  }
  
  // Renderiza conteúdo admin apenas se validado
  return <>{children}</>
}
