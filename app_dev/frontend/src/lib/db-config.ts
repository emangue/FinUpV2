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
 * Path ABSOLUTO do banco de dados
 * ⚠️ CRÍTICO: Este é o MESMO banco usado pelo backend FastAPI
 * NUNCA mudar este path sem coordenar com backend/app/config.py
 * 
 * ÚNICO BANCO USADO POR TODA A APLICAÇÃO:
 * - Backend FastAPI: /app_dev/backend/database/financas_dev.db
 * - Frontend Next.js: /app_dev/backend/database/financas_dev.db
 */
const DB_ABSOLUTE_PATH = '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend/database/financas_dev.db'

/**
 * Retorna o caminho absoluto do banco de dados
 * Inclui validação de existência
 */
export function getDbPath(): string {
  const absolutePath = DB_ABSOLUTE_PATH
  
  if (!fs.existsSync(absolutePath)) {
    throw new Error(
      `❌ BANCO NÃO ENCONTRADO\n` +
      `Path esperado: ${absolutePath}\n` +
      `⚠️ Verifique se o backend está rodando e criou o banco\n` +
      `Este é o ÚNICO banco usado por backend e frontend`
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
    relativo: DB_RELATIVE_PATH, (ÚNICO para toda aplicação):', {
    absoluto: dbPath,
    exists: fs.existsSync(dbPath),
    compartilhadoCom: 'Backend FastAPI em /app_dev/backend/database/financas_dev.db'
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
  const absolutePath = DB_ABSOLUTE_PATH
  const exists = fs.existsSync(absolutePath)
  
  return {
    absoluto: absolutePath,
    exists,
    tamanho: exists ? fs.statSync(absolutePath).size : 0,
    compartilhado: 'Backend + Frontend usam o MESMO arquivo'