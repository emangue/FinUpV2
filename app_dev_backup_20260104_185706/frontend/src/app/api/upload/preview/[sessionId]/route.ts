import { NextRequest, NextResponse } from 'next/server'
import { openDatabase } from '@/lib/db-config'

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

    console.log('🔍 GET Preview - Session ID:', sessionId)
    
    const db = openDatabase()

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
    
    console.log('📊 GET Preview - Registros encontrados:', registros.length)

    db.close()

    if (registros.length === 0) {
      console.log('⚠️ GET Preview - Nenhum registro encontrado para session:', sessionId)
      return NextResponse.json({ 
        errorCode: 'PREV_001',
        error: '[PREV_001] Sessão não encontrada ou expirada',
        details: { sessionId }
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
    console.error('❌ Erro ao buscar preview:', error)
    return NextResponse.json({ 
      errorCode: 'PREV_002',
      error: 'Erro ao acessar banco de dados',
      details: { message: error instanceof Error ? error.message : 'Unknown error' }
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

    const db = openDatabase()

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
