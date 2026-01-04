import { NextRequest, NextResponse } from 'next/server'
import path from 'path'
import { exec } from 'child_process'
import { promisify } from 'util'
import { writeFileSync, unlinkSync } from 'fs'

const execAsync = promisify(exec)

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return NextResponse.json({ error: 'Nenhum arquivo foi enviado' }, { status: 400 })
    }
    
    // Validações básicas
    const allowedTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/pdf'
    ]
    
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(csv|xls|xlsx|pdf|ofx)$/i)) {
      return NextResponse.json({ 
        error: 'Tipo de arquivo não suportado. Use CSV, Excel, PDF ou OFX.' 
      }, { status: 400 })
    }
    
    // Validação de tamanho (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      return NextResponse.json({ 
        error: 'Arquivo muito grande. Tamanho máximo: 10MB' 
      }, { status: 400 })
    }
    
    // Salvar arquivo temporariamente para validação
    const tempDir = path.join(process.cwd(), '../uploads_temp')
    const tempFileName = `validate_${Date.now()}_${file.name}`
    const tempFilePath = path.join(tempDir, tempFileName)
    
    try {
      const fileBuffer = Buffer.from(await file.arrayBuffer())
      writeFileSync(tempFilePath, fileBuffer)
      
      // Detectar tipo de arquivo e banco usando Python
      const pythonScript = `
import sys
import os
sys.path.append('${path.join(process.cwd(), '..')}')

from app.utils.processors.preprocessors.detect_and_preprocess import detect_and_preprocess

try:
    # Validar arquivo
    arquivo_path = '${tempFilePath.replace(/\\/g, '\\\\')}'
    
    # Verificar se arquivo existe
    if not os.path.exists(arquivo_path):
        print('{"error": "Arquivo não encontrado"}')
        sys.exit(1)
    
    # Detectar tipo
    resultado = detect_and_preprocess(arquivo_path)
    
    if resultado['success']:
        print(f'{{"success": true, "bank": "{resultado.get("bank", "Unknown")}", "format": "{resultado.get("format", "Unknown")}", "preview_rows": {len(resultado.get("data", []))}}}')
    else:
        print(f'{{"error": "{resultado.get("error", "Erro na detecção")}"}}')
        
except Exception as e:
    print(f'{{"error": "Erro na validação: {str(e)}"}}')
    sys.exit(1)
`
      
      const pythonPath = path.join(process.cwd(), '../venv/bin/python')
      const { stdout, stderr } = await execAsync(`${pythonPath} -c "${pythonScript}"`)
      
      if (stderr) {
        console.error('Erro na validação Python:', stderr)
        return NextResponse.json({ 
          error: 'Erro na validação do arquivo' 
        }, { status: 500 })
      }
      
      const result = JSON.parse(stdout.trim())
      
      if (result.error) {
        return NextResponse.json({ error: result.error }, { status: 400 })
      }
      
      return NextResponse.json({
        valid: true,
        bank: result.bank,
        format: result.format,
        previewRows: result.preview_rows,
        fileName: file.name,
        fileSize: file.size,
        fileType: file.type
      })
      
    } finally {
      // Limpar arquivo temporário
      try {
        unlinkSync(tempFilePath)
      } catch (error) {
        console.warn('Erro ao remover arquivo temporário:', error)
      }
    }
    
  } catch (error) {
    console.error('Erro na validação:', error)
    return NextResponse.json({ 
      error: 'Erro interno na validação' 
    }, { status: 500 })
  }
}

export async function GET() {
  return NextResponse.json({ 
    message: 'Endpoint de validação de arquivos',
    allowedTypes: ['CSV', 'Excel', 'PDF', 'OFX'],
    maxSize: '10MB',
    supportedBanks: ['Itaú', 'BTG Pactual', 'Banco do Brasil', 'Mercado Pago']
  })
}