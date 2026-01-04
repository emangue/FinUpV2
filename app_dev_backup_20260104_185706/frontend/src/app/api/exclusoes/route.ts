import { apiClient } from '@/lib/api-client';
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const apenasAtivos = searchParams.get('apenas_ativos') !== 'false';
    const banco = searchParams.get('banco');
    
    const response = await apiClient.get('/exclusoes/', {
      params: { apenas_ativos: apenasAtivos, banco }
    });
    
    return NextResponse.json(response.data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data?.detail || 'Erro ao buscar exclusões' },
      { status: error.response?.status || 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const response = await apiClient.post('/exclusoes/', body);
    
    return NextResponse.json(response.data, { status: 201 });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data?.detail || 'Erro ao criar exclusão' },
      { status: error.response?.status || 500 }
    );
  }
}
