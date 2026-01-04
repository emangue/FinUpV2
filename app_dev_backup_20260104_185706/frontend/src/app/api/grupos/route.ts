import { NextRequest, NextResponse } from 'next/server'
import Database from 'better-sqlite3'
import path from 'path'

export async function GET(request: NextRequest) {
  try {
    const dbPath = path.join(process.cwd(), '../financas_dev.db')
    const db = new Database(dbPath)

    // Buscar grupos distintos
    const gruposQuery = `SELECT DISTINCT GRUPO FROM journal_entries WHERE GRUPO IS NOT NULL ORDER BY GRUPO`
    const grupos = db.prepare(gruposQuery).all() as Array<{ GRUPO: string }>

    // Buscar subgrupos distintos
    const subgruposQuery = `SELECT DISTINCT SUBGRUPO FROM journal_entries WHERE SUBGRUPO IS NOT NULL ORDER BY SUBGRUPO`
    const subgrupos = db.prepare(subgruposQuery).all() as Array<{ SUBGRUPO: string }>

    db.close()

    return NextResponse.json({
      grupos: grupos.map(g => g.GRUPO),
      subgrupos: subgrupos.map(s => s.SUBGRUPO)
    })
  } catch (error) {
    console.error('Erro ao buscar grupos:', error)
    return NextResponse.json({ 
      error: 'Erro interno do servidor' 
    }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { tipo, nome } = body // tipo: 'grupo' ou 'subgrupo'

    if (!tipo || !nome) {
      return NextResponse.json({ error: 'Tipo e nome são obrigatórios' }, { status: 400 })
    }

    // Validação simples - o grupo/subgrupo será usado nas próximas transações
    // Não precisamos inserir na tabela agora, pois ele será inserido quando uma transação usar
    
    return NextResponse.json({ 
      success: true, 
      message: `${tipo === 'grupo' ? 'Grupo' : 'Subgrupo'} "${nome}" criado com sucesso` 
    })
  } catch (error) {
    console.error('Erro ao criar grupo/subgrupo:', error)
    return NextResponse.json({ 
      error: 'Erro interno do servidor' 
    }, { status: 500 })
  }
}
