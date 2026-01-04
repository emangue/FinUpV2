import { NextRequest, NextResponse } from 'next/server'

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await context.params
    const body = await request.json()
    
    const response = await fetch(`http://localhost:8000/api/v1/marcacoes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      return NextResponse.json(data, { status: response.status })
    }
    
    console.log('✅ Marcação atualizada:', id)
    return NextResponse.json(data)
    
  } catch (error: any) {
    console.error('❌ Erro ao atualizar marcação:', error)
    return NextResponse.json({ error: 'Erro ao atualizar marcação' }, { status: 500 })
  }
}

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await context.params
    
    const response = await fetch(`http://localhost:8000/api/v1/marcacoes/${id}`, {
      method: 'DELETE'
    })
    
    if (!response.ok && response.status !== 204) {
      const data = await response.json()
      return NextResponse.json(data, { status: response.status })
    }
    
    console.log('✅ Marcação deletada:', id)
    return NextResponse.json({ success: true }, { status: 204 })
    
  } catch (error: any) {
    console.error('❌ Erro ao deletar marcação:', error)
    return NextResponse.json({ error: 'Erro ao deletar marcação' }, { status: 500 })
  }
}
