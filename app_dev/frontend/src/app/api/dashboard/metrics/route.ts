import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const year = searchParams.get('year') || '2025';
    const month = searchParams.get('month') || 'all';
    
    const backendUrl = `http://localhost:8000/api/v1/dashboard/metrics?year=${year}&month=${month}`;
    
    const response = await fetch(backendUrl);
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }
    
    const data = await response.json();
    
    // Transformar para o formato esperado pelo frontend
    return NextResponse.json({
      totalDespesas: data.total_despesas,
      totalReceitas: data.total_receitas,
      saldoAtual: data.saldo,
      totalTransacoes: data.total_transacoes
    });
    
  } catch (error: any) {
    console.error('Error in metrics API:', error);
    return NextResponse.json(
      { error: error.message || 'Erro ao buscar métricas' },
      { status: 500 }
    );
  }
}