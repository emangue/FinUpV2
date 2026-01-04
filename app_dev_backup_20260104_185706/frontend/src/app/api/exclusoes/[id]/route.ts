import { apiClient } from '@/lib/api-client';
import { NextResponse } from 'next/server';

export async function PUT(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params;
    const body = await request.json();
    const response = await apiClient.put(`/exclusoes/${params.id}`, body);
    
    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error('Erro ao atualizar exclusão:', error);
    return NextResponse.json(
      { error: error.response?.data?.detail || error.message || 'Erro ao atualizar exclusão' },
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
    await apiClient.delete(`/exclusoes/${params.id}`);
    
    return new NextResponse(null, { status: 204 });
  } catch (error: any) {
    console.error('Erro ao deletar exclusão:', error);
    return NextResponse.json(
      { error: error.response?.data?.detail || error.message || 'Erro ao deletar exclusão' },
      { status: error.response?.status || 500 }
    );
  }
}
