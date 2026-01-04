import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const sessionId = params.sessionId

    // Chama o backend para processar e classificar
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/api/v1/upload/process-classify/${sessionId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // Passar autenticação se necessário
        ...(request.headers.get('cookie') ? { 'Cookie': request.headers.get('cookie')! } : {})
      }
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Erro ao processar' }))
      return NextResponse.json(
        { error: errorData.error || 'Erro ao classificar transações' },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Erro em process-classify route:', error)
    return NextResponse.json(
      { error: 'Erro ao processar classificação' },
      { status: 500 }
    )
  }
}
