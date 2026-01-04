import { NextResponse } from 'next/server'

// GET - Listar todos os bancos e suas compatibilidades
export async function GET() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/compatibility/')
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }
    
    const data = await response.json()
    
    // A página espera um array simples de BankCompatibility[]
    // O backend já retorna no formato correto
    return NextResponse.json(data)
    
  } catch (error: any) {
    console.error('Erro ao buscar compatibilidades:', error)
    return NextResponse.json({ error: 'Erro ao buscar compatibilidades' }, { status: 500 })
  }
}

// POST - Adicionar novo banco com seus formatos  
export async function POST(request: Request) {
  try {
    const body = await request.json()
    
    // TODO: Implementar no backend FastAPI
    return NextResponse.json({ error: 'Endpoint não implementado no backend' }, { status: 501 })
    
  } catch (error: any) {
    console.error('Erro ao adicionar banco:', error)
    return NextResponse.json({ error: 'Erro ao adicionar banco' }, { status: 500 })
  }
}

// PUT - Atualizar formatos de um banco existente
export async function PUT(request: Request) {
  try {
    const body = await request.json()
    
    // TODO: Implementar no backend FastAPI
    return NextResponse.json({ error: 'Endpoint não implementado no backend' }, { status: 501 })
    
  } catch (error: any) {
    console.error('Erro ao atualizar banco:', error)
    return NextResponse.json({ error: 'Erro ao atualizar banco' }, { status: 500 })
  }
}
