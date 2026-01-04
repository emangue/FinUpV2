import { NextRequest, NextResponse } from 'next/server'
import Database from 'better-sqlite3'
import path from 'path'

/**
 * GET /api/upload/preview/[sessionId]
 * 
 * Retorna todos os registros de uma sessão de preview
 */
export async function GET(
  request: NextRequest,
  context: { params: Promise<{ sessionId: string }> }
) {
  try {
    const params = await context.params
    const { sessionId } = params

    const dbPath = path.join(process.cwd(), '../financas_dev.db')
    const db = new Database(dbPath)

    const registros = db.prepare(`
      SELECT 
        id,
        banco,
        cartao,
        nome_arquivo,
        mes_fatura,
        data,
        lancamento,
        valor,
        created_at
      FROM upload_preview
      WHERE session_id = ?
      ORDER BY data ASC
    `).all(sessionId)

    db.close()

    if (registros.length === 0) {
      return NextResponse.json({ 
        error: 'Sessão não encontrada ou expirada' 
      }, { status: 404 })
    }

    // Agregar metadados
    const primeiroRegistro = registros[0]
    const metadata = {
      banco: primeiroRegistro.banco,
      cartao: primeiroRegistro.cartao,
      nomeArquivo: primeiroRegistro.nome_arquivo,
      mesFatura: primeiroRegistro.mes_fatura,
      totalRegistros: registros.length,
      somaTotal: registros.reduce((acc, r) => acc + r.valor, 0)
    }

    return NextResponse.json({
      metadata,
      registros
    })

  } catch (error) {
    console.error('Erro ao buscar preview:', error)
    return NextResponse.json({ 
      error: 'Erro ao buscar dados do preview' 
    }, { status: 500 })
  }
}

/**
 * DELETE /api/upload/preview/[sessionId]
 * 
 * Remove dados de preview (cancelar importação)
 */
export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ sessionId: string }> }
) {
  try {
    const params = await context.params
    const { sessionId } = params

    const dbPath = path.join(process.cwd(), '../financas_dev.db')
    const db = new Database(dbPath)

    const result = db.prepare(`
      DELETE FROM upload_preview WHERE session_id = ?
    `).run(sessionId)

    db.close()

    return NextResponse.json({
      success: true,
      deletedCount: result.changes
    })

  } catch (error) {
    console.error('Erro ao deletar preview:', error)
    return NextResponse.json({ 
      error: 'Erro ao deletar preview' 
    }, { status: 500 })
  }
}
