import { NextRequest, NextResponse } from 'next/server'
import Database from 'better-sqlite3'
import path from 'path'

const dbPath = path.join(process.cwd(), '../financas_dev.db')

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await context.params
    const { GRUPO, SUBGRUPO, TipoGasto } = await request.json()
    
    if (!GRUPO || !SUBGRUPO || !TipoGasto) {
      return NextResponse.json(
        { error: 'GRUPO, SUBGRUPO e TipoGasto são obrigatórios' },
        { status: 400 }
      )
    }
    
    const db = new Database(dbPath)
    
    const result = db.prepare(`
      UPDATE base_marcacoes 
      SET GRUPO = ?, SUBGRUPO = ?, TipoGasto = ?
      WHERE id = ?
    `).run(GRUPO, SUBGRUPO, TipoGasto, id)
    
    db.close()
    
    if (result.changes === 0) {
      return NextResponse.json({ error: 'Marcação não encontrada' }, { status: 404 })
    }
    
    console.log('✅ Marcação atualizada:', id)
    
    return NextResponse.json({ 
      id,
      GRUPO,
      SUBGRUPO,
      TipoGasto
    })
  } catch (error) {
    console.error('❌ Erro ao atualizar marcação:', error)
    return NextResponse.json({ error: 'Erro ao atualizar marcação' }, { status: 500 })
  }
}

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await context.params
    
    const db = new Database(dbPath)
    
    const result = db.prepare(`
      DELETE FROM base_marcacoes WHERE id = ?
    `).run(id)
    
    db.close()
    
    if (result.changes === 0) {
      return NextResponse.json({ error: 'Marcação não encontrada' }, { status: 404 })
    }
    
    console.log('✅ Marcação deletada:', id)
    
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('❌ Erro ao deletar marcação:', error)
    return NextResponse.json({ error: 'Erro ao deletar marcação' }, { status: 500 })
  }
}
