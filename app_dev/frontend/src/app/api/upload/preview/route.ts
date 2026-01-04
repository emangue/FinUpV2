import { NextRequest, NextResponse } from 'next/server'
import Database from 'better-sqlite3'
import path from 'path'
import fs from 'fs'

/**
 * POST /api/upload/preview
 * 
 * Processa arquivo para preview antes da importação definitiva
 * Gera base temporária com: banco, cartão, arquivo, data, lançamento, valor, mesFatura
 */
export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    const banco = formData.get('banco') as string
    const cartao = formData.get('cartao') as string
    const mesFatura = formData.get('mesFatura') as string // Formato: "2026-01"
    const tipoDocumento = formData.get('tipoDocumento') as string // "fatura" ou "extrato"
    const formato = formData.get('formato') as string // "csv", "xls", etc

    if (!file || !banco || !mesFatura) {
      return NextResponse.json({ 
        error: 'Arquivo, banco e mês fatura são obrigatórios' 
      }, { status: 400 })
    }

    // Salvar arquivo temporariamente
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)
    const tempDir = path.join(process.cwd(), '../uploads_temp')
    
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true })
    }

    const tempFilePath = path.join(tempDir, `preview_${Date.now()}_${file.name}`)
    fs.writeFileSync(tempFilePath, buffer)

    // Processar arquivo baseado no banco + tipo + formato
    const processador = getProcessador(banco, tipoDocumento, formato)
    
    if (!processador) {
      fs.unlinkSync(tempFilePath) // Limpar arquivo temp
      return NextResponse.json({ 
        error: `Processador não encontrado para: ${banco} - ${tipoDocumento} - ${formato}` 
      }, { status: 400 })
    }

    // Processar e obter dados
    const dadosProcessados = await processador(tempFilePath, {
      banco,
      cartao: cartao || 'N/A',
      nomeArquivo: file.name,
      mesFatura
    })

    // Salvar na base temporária
    const dbPath = path.join(process.cwd(), '../financas_dev.db')
    const db = new Database(dbPath)

    // Criar tabela temporária se não existir
    db.exec(`
      CREATE TABLE IF NOT EXISTS upload_preview (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        banco TEXT NOT NULL,
        cartao TEXT,
        nome_arquivo TEXT NOT NULL,
        mes_fatura TEXT NOT NULL,
        data TEXT NOT NULL,
        lancamento TEXT NOT NULL,
        valor REAL NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `)

    // Gerar session_id único para esta importação
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    // Inserir dados processados
    const stmt = db.prepare(`
      INSERT INTO upload_preview 
      (session_id, banco, cartao, nome_arquivo, mes_fatura, data, lancamento, valor)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `)

    for (const row of dadosProcessados) {
      stmt.run(
        sessionId,
        banco,
        cartao || 'N/A',
        file.name,
        mesFatura,
        row.data,
        row.lancamento,
        row.valor
      )
    }

    db.close()

    // Limpar arquivo temporário
    fs.unlinkSync(tempFilePath)

    return NextResponse.json({
      success: true,
      sessionId,
      totalRegistros: dadosProcessados.length,
      preview: dadosProcessados.slice(0, 5) // Primeiros 5 registros
    })

  } catch (error) {
    console.error('Erro ao processar preview:', error)
    return NextResponse.json({ 
      error: error instanceof Error ? error.message : 'Erro ao processar arquivo' 
    }, { status: 500 })
  }
}

/**
 * Retorna o processador adequado baseado em banco + tipo + formato
 */
function getProcessador(banco: string, tipo: string, formato: string) {
  const key = `${banco.toLowerCase()}_${tipo.toLowerCase()}_${formato.toLowerCase()}`
  
  const processadores: Record<string, any> = {
    'itau_fatura_csv': processarFaturaItauCSV,
    'btg_extrato_xls': null, // TODO: implementar
    'mercadopago_extrato_csv': null, // TODO: implementar
  }

  return processadores[key] || null
}

/**
 * Processador específico para Fatura Itaú CSV
 */
async function processarFaturaItauCSV(
  filePath: string, 
  metadata: { banco: string; cartao: string; nomeArquivo: string; mesFatura: string }
) {
  const fs = require('fs')
  const csvContent = fs.readFileSync(filePath, 'utf-8')
  
  const linhas = csvContent.split('\n').filter(l => l.trim())
  
  // Detectar linha de cabeçalho
  let startIndex = 0
  for (let i = 0; i < Math.min(5, linhas.length); i++) {
    const linha = linhas[i].toLowerCase()
    if (linha.includes('data') && (linha.includes('lançamento') || linha.includes('estabelecimento'))) {
      startIndex = i + 1
      break
    }
  }

  const dados = []
  
  for (let i = startIndex; i < linhas.length; i++) {
    const linha = linhas[i].trim()
    if (!linha) continue

    // Parse CSV simples (separado por vírgula ou ponto-e-vírgula)
    const separador = linha.includes(';') ? ';' : ','
    const colunas = linha.split(separador).map(c => c.trim().replace(/^"|"$/g, ''))

    if (colunas.length < 3) continue

    const [data, lancamento, valorStr] = colunas

    // Validar data (formato dd/mm/yyyy ou dd/mm/yy)
    if (!data || !/^\d{2}\/\d{2}\/\d{2,4}$/.test(data)) continue

    // Converter valor (formato brasileiro: 1.234,56)
    const valorLimpo = valorStr
      .replace(/[^\d,.-]/g, '')
      .replace(/\./g, '')
      .replace(',', '.')
    
    const valor = parseFloat(valorLimpo) || 0

    dados.push({
      data,
      lancamento: lancamento || 'N/A',
      valor
    })
  }

  return dados
}
