import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const year = searchParams.get('year') || '2025';
    const month = searchParams.get('month') || 'all';
    
    const backendUrl = `http://localhost:8000/api/v1/dashboard/categories?year=${year}&month=${month}`;
    
    const response = await fetch(backendUrl);
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }
    
    const data = await response.json();
    
    // Transformar para o formato esperado pelo frontend
    const formattedData = data.map((item: any) => ({
      tipo_gasto: item.TipoGasto,
      total: item.total,
      percentual: item.percentual,
      quantidade: item.quantidade
    }));
    
    return NextResponse.json(formattedData);
    
  } catch (error: any) {
    console.error('Error in categories API:', error);
    return NextResponse.json(
      { error: error.message || 'Erro ao buscar categorias' },
      { status: 500 }
    );
  }
}