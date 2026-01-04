import { NextResponse } from 'next/server'
import Database from 'better-sqlite3'
import path from 'path'

const dbPath = path.join(process.cwd(), '../financas_dev.db')

// PUT - Atualizar categoria
export async function PUT(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params
    const { nome, tipo, ativo } = await request.json()
    
    const db = new Database(dbPath)
    
    const result = db.prepare(`
      UPDATE categories
      SET nome = COALESCE(?, nome),
          tipo = COALESCE(?, tipo),
          ativo = COALESCE(?, ativo),
          updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `).run(nome, tipo, ativo, id)
    
    db.close()
    
    if (result.changes === 0) {
      return NextResponse.json({ error: 'Categoria não encontrada' }, { status: 404 })
    }
    
    return NextResponse.json({ success: true, changes: result.changes })
  } catch (error) {
    console.error('Erro ao atualizar categoria:', error)
    return NextResponse.json({ error: 'Erro ao atualizar categoria' }, { status: 500 })
  }
}

// DELETE - Deletar categoria (soft delete - apenas inativa)
export async function DELETE(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params
    
    const db = new Database(dbPath)
    
    const result = db.prepare(`
      UPDATE categories
      SET ativo = 0,
          updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `).run(id)
    
    db.close()
    
    if (result.changes === 0) {
      return NextResponse.json({ error: 'Categoria não encontrada' }, { status: 404 })
    }
    
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Erro ao deletar categoria:', error)
    return NextResponse.json({ error: 'Erro ao deletar categoria' }, { status: 500 })
  }
}
