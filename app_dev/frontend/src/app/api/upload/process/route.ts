import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import fs from 'fs/promises'
import path from 'path'
import { uploadSessions } from '../session/route'

const execAsync = promisify(exec)

interface ProcessorResult {
  success: boolean
  transactions?: any[]
  error?: string
  metadata?: {
    bankDetected?: string
    fileFormat?: string
    totalTransactions?: number
  }
}

export async function POST(request: NextRequest) {
  try {
    const { sessionId } = await request.json()
    
    if (!sessionId) {
      return NextResponse.json({ error: 'Session ID é obrigatório' }, { status: 400 })
    }
    
    // Buscar sessão
    const session = uploadSessions.get(sessionId)
    
    if (!session) {
      return NextResponse.json({ error: 'Sessão não encontrada' }, { status: 404 })
    }
    
    if (session.status !== 'processing') {
      return NextResponse.json({ 
        error: 'Sessão não está em processamento' 
      }, { status: 400 })
    }
    
    // Criar arquivo temporário
    const tempDir = path.join(process.cwd(), '../uploads_temp')
    await fs.mkdir(tempDir, { recursive: true })
    
    const tempFilePath = path.join(tempDir, `${sessionId}_${session.fileName}`)
    await fs.writeFile(tempFilePath, session.fileData)
    
    try {
      // Executar processamento Python
      const result = await processFileWithPython(tempFilePath, session.bankType)
      
      if (result.success && result.transactions) {
        // Atualizar sessão com dados processados
        session.previewData = result.transactions
        session.status = 'ready'
        uploadSessions.set(sessionId, session)
        
        return NextResponse.json({
          success: true,
          sessionId,
          transactions: result.transactions,
          metadata: result.metadata
        })
      } else {
        session.status = 'error'
        uploadSessions.set(sessionId, session)
        
        return NextResponse.json({
          success: false,
          error: result.error || 'Erro no processamento do arquivo'
        }, { status: 400 })
      }
      
    } finally {
      // Limpar arquivo temporário
      try {
        await fs.unlink(tempFilePath)
      } catch (error) {
        console.warn('Erro ao limpar arquivo temporário:', error)
      }
    }
    
  } catch (error) {
    console.error('Erro no processamento:', error)
    return NextResponse.json({ 
      error: 'Erro interno do servidor' 
    }, { status: 500 })
  }
}

async function processFileWithPython(filePath: string, bankType: string): Promise<ProcessorResult> {
  try {
    const projectRoot = path.join(process.cwd(), '../../')
    const pythonEnv = path.join(projectRoot, 'venv/bin/python')
    
    // Script Python para processamento
    const processorScript = `
import sys
import json
import os
sys.path.append('${path.join(projectRoot, 'app')}')

from utils.processors.preprocessors import detect_and_preprocess
from blueprints.upload.processors.fatura_cartao import processar_fatura_cartao  
from blueprints.upload.processors.extrato_conta import processar_extrato_conta
from utils.hasher import generate_id_transacao
import pandas as pd

def process_file(file_path, bank_type):
    try:
        # Ler arquivo
        if file_path.lower().endswith('.csv'):
            df_raw = pd.read_csv(file_path, header=None)
        elif file_path.lower().endswith(('.xls', '.xlsx')):
            df_raw = pd.read_excel(file_path, header=None)
        else:
            # Para OFX ou outros, passar o path
            df_raw = file_path
        
        # Detectar e preprocessar
        resultado = detect_and_preprocess(df_raw, file_path)
        
        if not resultado or not resultado.get('df') is not None:
            return {"success": False, "error": "Arquivo não foi processado ou está vazio"}
        
        df_processed = resultado['df']
        banco_detectado = resultado['banco']
        tipodocumento = resultado['tipodocumento']
        
        if df_processed.empty:
            return {"success": False, "error": "DataFrame processado está vazio"}
        
        # Processar baseado no tipo de documento
        if tipodocumento == 'Fatura Cartão de Crédito' or 'cartão' in tipodocumento.lower():
            transacoes_list = processar_fatura_cartao(
                df_processed, 
                banco_detectado, 
                tipodocumento, 
                'Upload', 
                os.path.basename(file_path)
            )
        else:
            transacoes_list = processar_extrato_conta(
                df_processed, 
                banco_detectado, 
                tipodocumento, 
                'Upload', 
                os.path.basename(file_path)
            )
        
        # Transformar lista de transações para formato esperado
        transactions = []
        for transacao in transacoes_list:
            # Determinar CategoriaGeral baseado no tipo de transação
            categoria_geral = 'Despesa'  # Default
            if transacao['TipoTransacao'] == 'Receitas':
                categoria_geral = 'Receita'
            elif transacao['TipoTransacao'] in ['Cartão de Crédito', 'Despesas']:
                categoria_geral = 'Despesa'
                
            # Determinar origem de classificação
            origem_class = 'Não Classificada'
            if transacao.get('TipoGasto') and transacao['TipoGasto'] not in [None, '']:
                origem_class = 'Automática - Base Padrões'
            
            # Gerar nome do cartão baseado no banco
            nome_cartao = transacao.get('banco_origem', banco_detectado)
            if tipodocumento == 'Fatura Cartão de Crédito':
                nome_cartao = f"{banco_detectado}"
            else:
                nome_cartao = None
            
            transactions.append({
                "idTransacao": transacao['IdTransacao'],
                "data": transacao['Data'],
                "estabelecimento": transacao['Estabelecimento'],
                "valor": float(transacao['Valor']),
                "valorPositivo": float(transacao['ValorPositivo']),
                "tipoTransacao": transacao['TipoTransacao'],
                "grupo": transacao.get('GRUPO') or '',
                "subgrupo": transacao.get('SUBGRUPO') or '',
                "tipoGasto": transacao.get('TipoGasto') or '',
                "mesFatura": transacao.get('MesFatura', ''),
                "idParcela": transacao.get('IdParcela'),
                "ano": transacao.get('Ano'),
                "arquivo_origem": transacao.get('arquivo_origem', os.path.basename(file_path)),
                "banco_origem": banco_detectado,
                "tipodocumento": tipodocumento,
                "origem_classificacao": origem_class,
                "nomeCartao": nome_cartao,
                "categoriaGeral": categoria_geral,
                "ignorarDashboard": False
            })
        
        return {
            "success": True,
            "transactions": transactions,
            "metadata": {
                "bankDetected": banco_detectado,
                "fileFormat": tipodocumento,
                "totalTransactions": len(transactions),
                "preprocessed": resultado.get('preprocessado', False)
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    file_path = sys.argv[1]
    bank_type = sys.argv[2]
    result = process_file(file_path, bank_type)
    print(json.dumps(result))
`
    
    // Salvar script temporário
    const scriptPath = path.join(projectRoot, 'temp_processor.py')
    await fs.writeFile(scriptPath, processorScript)
    
    try {
      // Executar script Python
      const { stdout, stderr } = await execAsync(
        `cd "${projectRoot}" && "${pythonEnv}" temp_processor.py "${filePath}" "${bankType}"`,
        { timeout: 30000 }
      )
      
      if (stderr) {
        console.error('Python stderr:', stderr)
      }
      
      const result = JSON.parse(stdout) as ProcessorResult
      return result
      
    } finally {
      // Limpar script temporário
      try {
        await fs.unlink(scriptPath)
      } catch (error) {
        console.warn('Erro ao limpar script temporário:', error)
      }
    }
    
  } catch (error) {
    console.error('Erro ao executar processador Python:', error)
    return {
      success: false,
      error: `Erro no processamento: ${error.message}`
    }
  }
}