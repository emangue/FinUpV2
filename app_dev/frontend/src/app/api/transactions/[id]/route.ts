import { NextRequest, NextResponse } from 'next/server'
import Database from 'better-sqlite3'
import path from 'path'

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json()
    const { GRUPO, SUBGRUPO, IgnorarDashboard } = body
    
    const dbPath = path.join(process.cwd(), '../financas_dev.db')
    const db = new Database(dbPath)

    const updates: string[] = []
    const values: any[] = []

    if (GRUPO !== undefined) {
      updates.push('GRUPO = ?')
      values.push(GRUPO)
    }

    if (SUBGRUPO !== undefined) {
      updates.push('SUBGRUPO = ?')
      values.push(SUBGRUPO)
    }

    if (IgnorarDashboard !== undefined) {
      updates.push('IgnorarDashboard = ?')
      values.push(IgnorarDashboard)
    }

    if (updates.length === 0) {
      db.close()
      return NextResponse.json({ error: 'Nenhum campo para atualizar' }, { status: 400 })
    }

    values.push(params.id)

    const query = `UPDATE journal_entries SET ${updates.join(', ')} WHERE IdTransacao = ?`
    
    const result = db.prepare(query).run(...values)
    
    db.close()

    if (result.changes === 0) {
      return NextResponse.json({ error: 'Transação não encontrada' }, { status: 404 })
    }

    return NextResponse.json({ success: true, changes: result.changes })
  } catch (error) {
    console.error('Erro ao atualizar transação:', error)
    return NextResponse.json({ 
      error: 'Erro interno do servidor' 
    }, { status: 500 })
  }
}
