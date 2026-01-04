/**
 * 🗄️ CONFIGURAÇÃO CENTRALIZADA DO BANCO DE DADOS
 * 
 * ⚠️ ATENÇÃO: Este é o ÚNICO local onde o path do banco deve ser definido
 * 
 * SEMPRE importar deste arquivo em qualquer API route que precise acessar o banco:
 * 
 * ```typescript
 * import { getDbPath, openDatabase } from '@/lib/db-config'
 * 
 * const db = openDatabase()
 * // ... fazer queries ...
 * db.close()
 * ```
 * 
 * PADRÃO DE PATH:
 * - CWD = /app_dev/frontend (Next.js)
 * - Subir 2 níveis: ../../
 * - Caminho final: /app_dev/financas_dev.db
 */

import path from 'path'
import fs from 'fs'
import Database from 'better-sqlite3'

/**
 * Path relativo do banco de dados
 * SEMPRE usar este valor em todas as APIs
 * 
 * De /app_dev/frontend → ../financas_dev.db → /app_dev/financas_dev.db
 */
const DB_RELATIVE_PATH = '../financas_dev.db'

/**
 * Retorna o caminho absoluto do banco de dados
 * Inclui validação de existência
 */
export function getDbPath(): string {
  const cwd = process.cwd()
  const relativePath = path.join(cwd, DB_RELATIVE_PATH)
  const absolutePath = path.resolve(relativePath)
  
  if (!fs.existsSync(absolutePath)) {
    throw new Error(
      `❌ BANCO NÃO ENCONTRADO\n` +
      `Path esperado: ${absolutePath}\n` +
      `CWD: ${cwd}\n` +
      `Relativo: ${DB_RELATIVE_PATH}`
    )
  }
  
  return absolutePath
}

/**
 * Abre conexão com o banco de dados
 * Garante que o path está correto e o arquivo existe
 * 
 * @param options - Opções do better-sqlite3 (ex: { readonly: true })
 */
export function openDatabase(options?: Database.Options) {
  const dbPath = getDbPath()
  
  console.log('🗄️ Abrindo banco:', {
    cwd: process.cwd(),
    relativo: DB_RELATIVE_PATH,
    absoluto: dbPath,
    exists: fs.existsSync(dbPath)
  })
  
  return new Database(dbPath, options)
}

/**
 * Verifica se o banco existe e está acessível
 * Útil para health checks
 */
export function checkDatabaseHealth(): { ok: boolean; path: string; error?: string } {
  try {
    const dbPath = getDbPath()
    const db = new Database(dbPath, { readonly: true })
    
    // Teste simples de query
    db.prepare('SELECT 1').get()
    db.close()
    
    return { ok: true, path: dbPath }
  } catch (error) {
    return {
      ok: false,
      path: 'N/A',
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }
}

/**
 * Informações de debug sobre o banco
 */
export function getDbInfo() {
  const cwd = process.cwd()
  const relativePath = path.join(cwd, DB_RELATIVE_PATH)
  const absolutePath = path.resolve(relativePath)
  const exists = fs.existsSync(absolutePath)
  
  return {
    cwd,
    relativo: DB_RELATIVE_PATH,
    absoluto: absolutePath,
    exists,
    tamanho: exists ? fs.statSync(absolutePath).size : 0
  }
}
