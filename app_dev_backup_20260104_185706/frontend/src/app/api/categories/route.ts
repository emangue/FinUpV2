import { NextResponse } from 'next/server'
import Database from 'better-sqlite3'
import path from 'path'

const dbPath = path.join(process.cwd(), '../financas_dev.db')

// GET - Listar todas as categorias
export async function GET() {
  try {
    const db = new Database(dbPath, { readonly: true })
    
    const categories = db.prepare(`
      SELECT id, nome, tipo, ativo
      FROM categories
      ORDER BY tipo, nome
    `).all()
    
    db.close()
    
    return NextResponse.json(categories)
  } catch (error) {
    console.error('Erro ao buscar categorias:', error)
    return NextResponse.json({ error: 'Erro ao buscar categorias' }, { status: 500 })
  }
}

// POST - Criar nova categoria
export async function POST(request: Request) {
  try {
    const { nome, tipo, ativo } = await request.json()
    
    if (!nome || !tipo) {
      return NextResponse.json({ error: 'Nome e tipo são obrigatórios' }, { status: 400 })
    }
    
    const db = new Database(dbPath)
    
    // Criar tabela se não existir
    db.prepare(`
      CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        tipo TEXT NOT NULL CHECK(tipo IN ('GRUPO', 'SUBGRUPO', 'TIPOGASTO')),
        ativo INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(nome, tipo)
      )
    `).run()
    
    const result = db.prepare(`
      INSERT INTO categories (nome, tipo, ativo)
      VALUES (?, ?, ?)
    `).run(nome, tipo, ativo ?? 1)
    
    db.close()
    
    return NextResponse.json({ success: true, id: result.lastInsertRowid })
  } catch (error: any) {
    console.error('Erro ao criar categoria:', error)
    if (error.message?.includes('UNIQUE')) {
      return NextResponse.json({ error: 'Categoria já existe' }, { status: 409 })
    }
    return NextResponse.json({ error: 'Erro ao criar categoria' }, { status: 500 })
  }
}
