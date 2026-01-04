import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const year = searchParams.get('year') || '2025';
    const month = searchParams.get('month') || 'all';

    
    const backendUrl = `http://localhost:8000/api/v1/dashboard/chart/receitas-despesas`;
    
    const response = await fetch(backendUrl);
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }
    
    const data = await response.json();
    
    // Retornar no formato esperado pelo frontend
    return NextResponse.json(data);
    
  } catch (error: any) {
    console.error('Error in chart-data API:', error);
    return NextResponse.json(
      { error: error.message || 'Erro ao buscar dados do gráfico' },
      { status: 500 }
    );
  }
}