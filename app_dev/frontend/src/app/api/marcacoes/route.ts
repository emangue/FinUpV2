import { NextRequest, NextResponse } from 'next/server'
import Database from 'better-sqlite3'
import path from 'path'

const dbPath = path.join(process.cwd(), '../financas_dev.db')

export async function GET() {
  try {
    const db = new Database(dbPath, { readonly: true })
    
    const marcacoes = db.prepare(`
      SELECT id, GRUPO, SUBGRUPO, TipoGasto
      FROM base_marcacoes
      ORDER BY GRUPO, SUBGRUPO, TipoGasto
    `).all()
    
    db.close()
    
    console.log('📊 Marcações carregadas:', marcacoes.length, 'registros')
    
    return NextResponse.json(marcacoes)
  } catch (error) {
    console.error('❌ Erro ao buscar marcações:', error)
    return NextResponse.json({ error: 'Erro ao buscar marcações' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const { GRUPO, SUBGRUPO, TipoGasto } = await request.json()
    
    if (!GRUPO || !SUBGRUPO || !TipoGasto) {
      return NextResponse.json(
        { error: 'GRUPO, SUBGRUPO e TipoGasto são obrigatórios' },
        { status: 400 }
      )
    }
    
    const db = new Database(dbPath)
    
    // Verificar se já existe
    const existing = db.prepare(`
      SELECT id FROM base_marcacoes 
      WHERE GRUPO = ? AND SUBGRUPO = ? AND TipoGasto = ?
    `).get(GRUPO, SUBGRUPO, TipoGasto)
    
    if (existing) {
      db.close()
      return NextResponse.json(
        { error: 'Esta combinação já existe' },
        { status: 400 }
      )
    }
    
    const result = db.prepare(`
      INSERT INTO base_marcacoes (GRUPO, SUBGRUPO, TipoGasto)
      VALUES (?, ?, ?)
    `).run(GRUPO, SUBGRUPO, TipoGasto)
    
    db.close()
    
    console.log('✅ Nova marcação criada:', result.lastInsertRowid)
    
    return NextResponse.json({ 
      id: result.lastInsertRowid,
      GRUPO,
      SUBGRUPO,
      TipoGasto
    })
  } catch (error) {
    console.error('❌ Erro ao criar marcação:', error)
    return NextResponse.json({ error: 'Erro ao criar marcação' }, { status: 500 })
  }
}
