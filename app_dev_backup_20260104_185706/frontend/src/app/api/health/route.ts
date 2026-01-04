import { NextResponse } from 'next/server'
import { checkDatabaseHealth, getDbInfo } from '@/lib/db-config'

/**
 * GET /api/health
 * 
 * Verifica saúde do sistema:
 * - Banco de dados acessível
 * - Path correto
 * - Tabelas críticas existem
 */
export async function GET() {
  const dbHealth = checkDatabaseHealth()
  const dbInfo = getDbInfo()
  
  const health = {
    status: dbHealth.ok ? 'healthy' : 'unhealthy',
    timestamp: new Date().toISOString(),
    database: {
      accessible: dbHealth.ok,
      path: dbHealth.path,
      info: dbInfo,
      error: dbHealth.error
    }
  }
  
  const statusCode = dbHealth.ok ? 200 : 500
  
  return NextResponse.json(health, { status: statusCode })
}
