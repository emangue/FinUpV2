/**
 * Proxy Genérico de API - Next.js Route Handler
 * 
 * Este arquivo substitui TODAS as rotas individuais de API
 * Ele encaminha requisições para o backend FastAPI de forma transparente
 * 
 * Vantagens:
 * - 1 arquivo em vez de 20+
 * - Mudança de URL: apenas api.config.ts
 * - Mantém todos os headers e métodos HTTP
 * - Logging centralizado
 * - Error handling consistente
 * 
 * Uso no cliente:
 *   fetch('/api/transactions/list') → encaminha para http://localhost:8000/api/v1/transactions/list
 */

import { NextRequest, NextResponse } from 'next/server';
import { API_CONFIG } from '@/core/config/api.config';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ proxy: string[] }> }
) {
  const resolvedParams = await params;
  return handleProxy(request, resolvedParams.proxy, 'GET');
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ proxy: string[] }> }
) {
  const resolvedParams = await params;
  return handleProxy(request, resolvedParams.proxy, 'POST');
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ proxy: string[] }> }
) {
  const resolvedParams = await params;
  return handleProxy(request, resolvedParams.proxy, 'PUT');
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ proxy: string[] }> }
) {
  const resolvedParams = await params;
  return handleProxy(request, resolvedParams.proxy, 'PATCH');
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ proxy: string[] }> }
) {
  const resolvedParams = await params;
  return handleProxy(request, resolvedParams.proxy, 'DELETE');
}

async function handleProxy(
  request: NextRequest,
  pathSegments: string[],
  method: string
) {
  try {
    // Reconstruir path completo
    const path = pathSegments.join('/');
    
    // Construir URL do backend
    const backendUrl = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/${path}`;
    
    // Adicionar query params se houver
    const searchParams = request.nextUrl.searchParams.toString();
    const fullUrl = searchParams ? `${backendUrl}?${searchParams}` : backendUrl;
    
    // Whitelist de headers (segurança - evita spoofing)
    const ALLOWED_HEADERS = ['authorization', 'content-type', 'accept', 'accept-language', 'cache-control', 'pragma', 'cookie'];
    const headers = new Headers();
    const contentType = request.headers.get('content-type');
    ALLOWED_HEADERS.forEach((key) => {
      const value = request.headers.get(key);
      if (value && !(contentType?.includes('multipart/form-data') && key === 'content-type')) {
        headers.set(key, value);
      }
    });
    
    // 🔐 Token: Authorization header ou cookie auth_token (SSR)
    if (!headers.has('authorization')) {
      const tokenCookie = request.cookies.get('auth_token') || request.cookies.get('token');
      if (tokenCookie?.value) {
        headers.set('Authorization', `Bearer ${tokenCookie.value}`);
      }
    }
    
    // Preparar body se for POST/PUT/PATCH
    let body: any = undefined;
    if (['POST', 'PUT', 'PATCH'].includes(method)) {
      if (contentType?.includes('application/json')) {
        body = await request.json();
        body = JSON.stringify(body);
      } else if (contentType?.includes('multipart/form-data')) {
        // Para multipart/form-data, passar o FormData diretamente
        body = await request.formData();
      } else {
        body = await request.text();
      }
    }
    
    const response = await fetch(fullUrl, {
      method,
      headers,
      body,
      // @ts-ignore - FormData é válido aqui
      duplex: body instanceof ReadableStream ? 'half' : undefined,
    });
    
    // Ler resposta do backend
    const responseData = await response.text();
    
    // Criar resposta Next.js mantendo status e headers
    const nextResponse = new NextResponse(responseData, {
      status: response.status,
      statusText: response.statusText,
    });
    
    // Copiar headers relevantes
    response.headers.forEach((value, key) => {
      // Skip headers que não devem ser retornados
      if (!['content-encoding', 'transfer-encoding'].includes(key.toLowerCase())) {
        nextResponse.headers.set(key, value);
      }
    });
    
    return nextResponse;
    
  } catch (error) {
    const isProd = process.env.NODE_ENV === 'production';
    const message = isProd ? 'Erro interno. Tente novamente.' : (error instanceof Error ? error.message : 'Internal proxy error');
    return NextResponse.json({ detail: message, code: 'PROXY_ERROR' }, { status: 500 });
  }
}

// Configuração para permitir body em GET requests (Next.js)
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
