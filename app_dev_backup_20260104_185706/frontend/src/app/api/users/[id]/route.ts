import { apiClient } from '@/lib/api-client';
import { NextResponse } from 'next/server';

export async function GET(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params;
    const response = await apiClient.get(`/users/${params.id}`);
    return NextResponse.json(response.data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data?.detail || 'Erro ao buscar usuário' },
      { status: error.response?.status || 500 }
    );
  }
}

export async function PUT(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params;
    const body = await request.json();
    const response = await apiClient.put(`/users/${params.id}`, body);
    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error('Erro ao atualizar usuário:', error);
    return NextResponse.json(
      { error: error.response?.data?.detail || error.message || 'Erro ao atualizar usuário' },
      { status: error.response?.status || 500 }
    );
  }
}

export async function DELETE(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params;
    await apiClient.delete(`/users/${params.id}`);
    return new NextResponse(null, { status: 204 });
  } catch (error: any) {
    console.error('Erro ao deletar usuário:', error);
    return NextResponse.json(
      { error: error.response?.data?.detail || error.message || 'Erro ao deletar usuário' },
      { status: error.response?.status || 500 }
    );
  }
}
