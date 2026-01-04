import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // TODO: Implementar consulta ao banco de dados real
    // Por enquanto, retornamos dados simulados
    
    const uploads = [
      {
        id: 1,
        fileName: 'fatura_itau_202512.pdf',
        bank: 'Banco Itaú',
        creditCard: 'Mastercard 4321',
        uploadDate: '2025-01-03T10:30:00Z',
        fileSize: 245760, // bytes
        status: 'processed',
        transactionsCount: 45,
        type: 'fatura'
      },
      {
        id: 2,
        fileName: 'extrato_bradesco_202512.xlsx',
        bank: 'Banco Bradesco',
        creditCard: null,
        uploadDate: '2025-01-02T15:45:00Z',
        fileSize: 128512,
        status: 'processed',
        transactionsCount: 23,
        type: 'extrato'
      },
      {
        id: 3,
        fileName: 'fatura_santander_202511.pdf',
        bank: 'Banco Santander',
        creditCard: 'Visa 1234',
        uploadDate: '2025-01-01T09:15:00Z',
        fileSize: 189440,
        status: 'error',
        transactionsCount: 0,
        type: 'fatura',
        error: 'Arquivo corrompido'
      }
    ]

    return NextResponse.json(uploads)
    
  } catch (error) {
    console.error('Erro ao buscar histórico de uploads:', error)
    return NextResponse.json({ 
      error: 'Erro interno do servidor' 
    }, { status: 500 })
  }
}