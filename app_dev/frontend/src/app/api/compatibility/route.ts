import { NextResponse } from 'next/server'
import { openDatabase } from '@/lib/db-config'

export async function GET() {
  try {
    const db = openDatabase({ readonly: true })
    
    const compatibility = db.prepare(`
      SELECT bank_name, file_format, status
      FROM bank_format_compatibility
      ORDER BY bank_name, file_format
    `).all()
    
    console.log('📊 Compatibilidade carregada:', compatibility.length, 'registros')
    
    db.close()
    
    // Organizar por banco
    const byBank: Record<string, Record<string, string>> = {}
    
    for (const row of compatibility as any[]) {
      if (!byBank[row.bank_name]) {
        byBank[row.bank_name] = {}
      }
      byBank[row.bank_name][row.file_format] = row.status
    }
    
    console.log('✅ Retornando:', Object.keys(byBank).length, 'bancos')
    
    return NextResponse.json(byBank)
  } catch (error) {
    console.error('❌ Erro ao buscar compatibilidade:', error)
    return NextResponse.json({ error: 'Erro ao buscar compatibilidade' }, { status: 500 })
  }
}
