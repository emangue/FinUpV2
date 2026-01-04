import { NextRequest, NextResponse } from 'next/server'

export async function GET() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/marcacoes/')
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }
    
    const data = await response.json()
    console.log('📊 Marcações carregadas:', data.length, 'registros')
    
    return NextResponse.json(data)
    
  } catch (error: any) {
    console.error('❌ Erro ao buscar marcações:', error)
    return NextResponse.json({ error: 'Erro ao buscar marcações' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const response = await fetch('http://localhost:8000/api/v1/marcacoes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      return NextResponse.json(data, { status: response.status })
    }
    
    console.log('✅ Nova marcação criada:', data.id)
    return NextResponse.json(data, { status: 201 })
    
  } catch (error: any) {
    console.error('❌ Erro ao criar marcação:', error)
    return NextResponse.json({ error: 'Erro ao criar marcação' }, { status: 500 })
  }
}
