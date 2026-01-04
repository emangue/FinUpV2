import { NextResponse } from 'next/server'
import Database from 'better-sqlite3'
import path from 'path'

const dbPath = path.join(process.cwd(), '../financas_dev.db')

// GET - Listar todos os bancos e suas compatibilidades
export async function GET() {
  try {
    const db = new Database(dbPath, { readonly: true })
    
    const compatibility = db.prepare(`
      SELECT id, bank_name, file_format, status
      FROM bank_format_compatibility
      ORDER BY bank_name, file_format
    `).all()
    
    db.close()
    
    return NextResponse.json(compatibility)
  } catch (error) {
    console.error('Erro ao buscar compatibilidades:', error)
    return NextResponse.json({ error: 'Erro ao buscar compatibilidades' }, { status: 500 })
  }
}

// POST - Adicionar novo banco com seus formatos
export async function POST(request: Request) {
  try {
    const { bank_name, formats } = await request.json()
    
    if (!bank_name || !formats) {
      return NextResponse.json({ error: 'Nome do banco e formatos são obrigatórios' }, { status: 400 })
    }
    
    const db = new Database(dbPath)
    
    // Inserir cada formato
    const stmt = db.prepare(`
      INSERT INTO bank_format_compatibility (bank_name, file_format, status)
      VALUES (?, ?, ?)
    `)
    
    const insert = db.transaction(() => {
      for (const [format, status] of Object.entries(formats)) {
        stmt.run(bank_name, format, status)
      }
    })
    
    insert()
    db.close()
    
    return NextResponse.json({ success: true })
  } catch (error: any) {
    console.error('Erro ao adicionar banco:', error)
    if (error.message?.includes('UNIQUE')) {
      return NextResponse.json({ error: 'Banco já existe' }, { status: 409 })
    }
    return NextResponse.json({ error: 'Erro ao adicionar banco' }, { status: 500 })
  }
}

// PUT - Atualizar formatos de um banco existente
export async function PUT(request: Request) {
  try {
    const { bank_name, formats, old_bank_name } = await request.json()
    
    if (!bank_name || !formats) {
      return NextResponse.json({ error: 'Nome do banco e formatos são obrigatórios' }, { status: 400 })
    }
    
    const db = new Database(dbPath)
    
    const bankToUpdate = old_bank_name || bank_name
    
    // Atualizar cada formato
    const stmt = db.prepare(`
      UPDATE bank_format_compatibility
      SET status = ?, updated_at = CURRENT_TIMESTAMP
      WHERE bank_name = ? AND file_format = ?
    `)
    
    const update = db.transaction(() => {
      for (const [format, status] of Object.entries(formats)) {
        stmt.run(status, bankToUpdate, format)
      }
    })
    
    update()
    db.close()
    
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Erro ao atualizar banco:', error)
    return NextResponse.json({ error: 'Erro ao atualizar banco' }, { status: 500 })
  }
}
