import { NextRequest, NextResponse } from 'next/server'
import Database from 'better-sqlite3'
import path from 'path'
import crypto from 'crypto'

// Interface para sessão de upload
interface UploadSession {
  id: string
  userId: number
  fileName: string
  fileData: Buffer
  bankType: string
  fileFormat: string
  status: 'processing' | 'ready' | 'confirmed' | 'error'
  previewData?: any[]
  createdAt: string
  expiresAt: string
}

// Armazenamento temporário de sessões (em produção, usar Redis ou banco)
const uploadSessions = new Map<string, UploadSession>()

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    
    const file = formData.get('file') as File
    const bank = formData.get('bank') as string
    const fileFormat = formData.get('fileFormat') as string
    
    if (!file) {
      return NextResponse.json({ error: 'Arquivo é obrigatório' }, { status: 400 })
    }

    // Validar tipo de arquivo
    const validExtensions = ['.pdf', '.xls', '.xlsx', '.ofx', '.csv']
    const fileName = file.name.toLowerCase()
    const isValidFile = validExtensions.some(ext => fileName.endsWith(ext))
    
    if (!isValidFile) {
      return NextResponse.json({ 
        error: 'Tipo de arquivo não suportado. Use: PDF, XLS, XLSX, OFX ou CSV' 
      }, { status: 400 })
    }

    // Gerar ID único para a sessão
    const sessionId = crypto.randomUUID()
    
    // Converter arquivo para Buffer
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)
    
    // Criar sessão
    const session: UploadSession = {
      id: sessionId,
      userId: 1, // TODO: Pegar do contexto de autenticação
      fileName: file.name,
      fileData: buffer,
      bankType: bank,
      fileFormat: fileFormat,
      status: 'processing',
      createdAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24h
    }
    
    // Salvar sessão
    uploadSessions.set(sessionId, session)
    
    return NextResponse.json({
      sessionId,
      status: 'created',
      fileName: file.name,
      size: file.size,
      bankType: bank,
      fileFormat: fileFormat
    })
    
  } catch (error) {
    console.error('Erro ao criar sessão de upload:', error)
    return NextResponse.json({ 
      error: 'Erro interno do servidor' 
    }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const sessionId = searchParams.get('sessionId')
    
    if (!sessionId) {
      return NextResponse.json({ error: 'Session ID é obrigatório' }, { status: 400 })
    }
    
    const session = uploadSessions.get(sessionId)
    
    if (!session) {
      return NextResponse.json({ error: 'Sessão não encontrada' }, { status: 404 })
    }
    
    // Verificar se a sessão expirou
    if (new Date() > new Date(session.expiresAt)) {
      uploadSessions.delete(sessionId)
      return NextResponse.json({ error: 'Sessão expirada' }, { status: 410 })
    }
    
    // Retornar dados da sessão (sem o arquivo)
    const { fileData, ...sessionData } = session
    
    return NextResponse.json(sessionData)
    
  } catch (error) {
    console.error('Erro ao buscar sessão:', error)
    return NextResponse.json({ 
      error: 'Erro interno do servidor' 
    }, { status: 500 })
  }
}

// Função auxiliar para limpar sessões expiradas
export function cleanExpiredSessions() {
  const now = new Date()
  for (const [sessionId, session] of uploadSessions.entries()) {
    if (now > new Date(session.expiresAt)) {
      uploadSessions.delete(sessionId)
    }
  }
}

// Exportar para uso em outros endpoints
export { uploadSessions }