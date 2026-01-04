import { NextResponse } from 'next/server'

// GET - Listar todas as categorias (marcações)
export async function GET() {
  try {
    // Redireciona para endpoint de marcações que já existe no backend
    const response = await fetch('http://localhost:8000/api/v1/marcacoes/')
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
    
  } catch (error: any) {
    console.error('Erro ao buscar categorias:', error)
    return NextResponse.json({ error: 'Erro ao buscar categorias' }, { status: 500 })
  }
}

// POST - Criar nova categoria (marcação)
export async function POST(request: Request) {
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
    
    return NextResponse.json(data, { status: 201 })
    
  } catch (error: any) {
    console.error('Erro ao criar categoria:', error)
    return NextResponse.json({ error: 'Erro ao criar categoria' }, { status: 500 })
  }
}
