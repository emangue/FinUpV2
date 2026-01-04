import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:8000';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  
  // Construir query string para o backend
  const params = new URLSearchParams();
  
  // Parâmetros de filtro (mesmos da listagem)
  if (searchParams.has('search')) {
    params.set('search', searchParams.get('search')!);
  }
  if (searchParams.has('tipo_transacao')) {
    params.set('tipo_transacao', searchParams.get('tipo_transacao')!);
  }
  if (searchParams.has('tipo_gasto')) {
    params.set('tipo_gasto', searchParams.get('tipo_gasto')!);
  }
  if (searchParams.has('grupo')) {
    params.set('grupo', searchParams.get('grupo')!);
  }
  if (searchParams.has('subgrupo')) {
    params.set('subgrupo', searchParams.get('subgrupo')!);
  }
  if (searchParams.has('estabelecimento')) {
    params.set('estabelecimento', searchParams.get('estabelecimento')!);
  }
  if (searchParams.has('year')) {
    params.set('year', searchParams.get('year')!);
  }
  if (searchParams.has('month')) {
    params.set('month', searchParams.get('month')!);
  }
  
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/transactions/filtered-total?${params.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching filtered total:', error);
    return NextResponse.json(
      { error: 'Failed to fetch filtered total' },
      { status: 500 }
    );
  }
}