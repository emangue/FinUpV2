import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/compatibility/')
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }
    
    const compatibility = await response.json()
    console.log('📊 Compatibilidade carregada:', compatibility.length, 'registros')
    
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
    
  } catch (error: any) {
    console.error('❌ Erro ao buscar compatibilidade:', error)
    return NextResponse.json({ error: 'Erro ao buscar compatibilidade' }, { status: 500 })
  }
}
