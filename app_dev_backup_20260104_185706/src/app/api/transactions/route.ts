import { NextRequest, NextResponse } from 'next/server'
import Database from 'better-sqlite3'
import path from 'path'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const type = searchParams.get('type') || 'all' // all, receitas, despesas
    const page = parseInt(searchParams.get('page') || '1')
    const limit = parseInt(searchParams.get('limit') || '10')
    const offset = (page - 1) * limit

    // Filtros avançados
    const estabelecimento = searchParams.get('estabelecimento')
    const grupo = searchParams.get('grupo')
    const subgrupo = searchParams.get('subgrupo')
    const tipoGasto = searchParams.get('tipoGasto')
    const banco = searchParams.get('banco')
    const mesInicio = searchParams.get('mesInicio')
    const mesFim = searchParams.get('mesFim')

    const dbPath = path.join(process.cwd(), 'financas_dev.db')
    const db = new Database(dbPath)

    const whereClauses = ['IgnorarDashboard = 0']
    const params: any[] = []
    
    if (type === 'receitas') {
      whereClauses.push("TipoTransacao = ?")
      params.push('Receitas')
    } else if (type === 'despesas') {
      whereClauses.push("(TipoTransacao = ? OR TipoTransacao = ?)")
      params.push('Despesas', 'Cartão de Crédito')
    }

    if (estabelecimento) {
      whereClauses.push('Estabelecimento LIKE ?')
      params.push(`%${estabelecimento}%`)
    }

    if (grupo && grupo.trim()) {
      whereClauses.push('GRUPO = ?')
      params.push(grupo.trim())
    }

    if (subgrupo) {
      whereClauses.push('SUBGRUPO LIKE ?')
      params.push(`%${subgrupo}%`)
    }

    if (tipoGasto && tipoGasto.trim()) {
      whereClauses.push('TipoGasto = ?')
      params.push(tipoGasto.trim())
    }

    if (banco && banco.trim()) {
      whereClauses.push('banco_origem = ?')
      params.push(banco.trim())
    }

    if (mesInicio) {
      whereClauses.push('MesFatura >= ?')
      params.push(mesInicio)
    }

    if (mesFim) {
      whereClauses.push('MesFatura <= ?')
      params.push(mesFim)
    }

    const whereClause = 'WHERE ' + whereClauses.join(' AND ')

    // Buscar total de registros
    const countQuery = `SELECT COUNT(*) as total FROM journal_entries ${whereClause}`
    const countResult = db.prepare(countQuery).get(...params) as { total: number }
    const total = countResult.total

    // Buscar transações
    const query = `
      SELECT 
        IdTransacao,
        Data,
        Estabelecimento,
        ValorPositivo,
        TipoTransacao,
        GRUPO,
        SUBGRUPO,
        TipoGasto,
        origem_classificacao,
        MesFatura,
        banco_origem,
        NomeCartao
      FROM journal_entries
      ${whereClause}
      ORDER BY Data DESC
      LIMIT ? OFFSET ?
    `

    const transactions = db.prepare(query).all(...params, limit, offset)

    db.close()

    return NextResponse.json({
      transactions,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit)
      }
    })
  } catch (error) {
    console.error('Erro ao buscar transações:', error)
    return NextResponse.json({ 
      error: 'Erro interno do servidor' 
    }, { status: 500 })
  }
}