import { NextRequest, NextResponse } from 'next/server'
import Database from 'better-sqlite3'
import path from 'path'
import { uploadSessions } from '../session/route'

interface ConfirmTransaction {
  idTransacao: string
  data: string
  estabelecimento: string
  valor: number
  valorPositivo: number
  tipoTransacao: string
  grupo: string
  subgrupo: string
  tipoGasto: string
  mesFatura: string
  banco_origem: string
  nomeCartao?: string
  categoriaGeral: string
  ignorarDashboard: boolean
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { sessionId, transactions, confirmAll = false } = body
    
    if (!sessionId) {
      return NextResponse.json({ error: 'Session ID é obrigatório' }, { status: 400 })
    }
    
    // Buscar sessão
    const session = uploadSessions.get(sessionId)
    
    if (!session) {
      return NextResponse.json({ error: 'Sessão não encontrada' }, { status: 404 })
    }
    
    if (session.status !== 'ready') {
      return NextResponse.json({ 
        error: 'Sessão não está pronta para confirmação' 
      }, { status: 400 })
    }
    
    // Conectar com banco de dados
    const dbPath = path.join(process.cwd(), '../financas_dev.db')
    const db = new Database(dbPath)
    
    try {
      // Iniciar transação
      db.exec('BEGIN TRANSACTION')
      
      // Preparar statement de inserção - seguindo exatamente o esquema da tabela
      const insertStmt = db.prepare(`
        INSERT INTO journal_entries (
          user_id, Data, Estabelecimento, Valor, ValorPositivo,
          TipoTransacao, TipoGasto, GRUPO, SUBGRUPO, IdTransacao,
          IdParcela, MesFatura, Ano, arquivo_origem, banco_origem,
          tipodocumento, origem_classificacao, IgnorarDashboard,
          NomeCartao, CategoriaGeral, created_at
        ) VALUES (
          ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
        )
      `)
      
      let insertedCount = 0
      let duplicateCount = 0
      let errorCount = 0
      
      // Processar transações
      const transactionsToProcess = confirmAll ? session.previewData : transactions
      
      for (const transaction of transactionsToProcess || []) {
        try {
          // Verificar duplicata por IdTransacao
          const existing = db.prepare(
            'SELECT COUNT(*) as count FROM journal_entries WHERE IdTransacao = ?'
          ).get(transaction.idTransacao)
          
          if (existing.count > 0) {
            duplicateCount++
            continue
          }
          
          // Extrair ano da data
          const [dia, mes, ano] = transaction.data.split('/')
          const anoInt = parseInt(ano)
          
          // Inserir transação - seguindo ordem exata do schema
          insertStmt.run(
            1, // user_id - TODO: pegar do contexto de autenticação
            transaction.data,
            transaction.estabelecimento,
            transaction.valor,
            transaction.valorPositivo,
            transaction.tipoTransacao,
            transaction.tipoGasto || null,
            transaction.grupo || null,
            transaction.subgrupo || null,
            transaction.idTransacao,
            transaction.idParcela || null,
            transaction.mesFatura || null,
            anoInt,
            `Upload - ${session.fileName}`,
            transaction.banco_origem,
            transaction.tipodocumento || 'Upload',
            transaction.origem_classificacao || 'Upload Automático',
            transaction.ignorarDashboard ? 1 : 0,
            transaction.nomeCartao || null,
            transaction.categoriaGeral || 'Despesa'
          )
          
          insertedCount++
          
        } catch (error) {
          console.error('Erro ao inserir transação:', transaction.idTransacao, error)
          errorCount++
        }
      }
      
      // Confirmar transação
      db.exec('COMMIT')
      
      // ✨ NOVO: Atualizar bases de padrões e parcelas após upload bem-sucedido
      if (insertedCount > 0) {
        try {
          console.log(`🔄 Atualizando bases após inserção de ${insertedCount} transações...`)
          
          const pythonScript = `
import sys
import os
sys.path.append("${process.cwd()}")
sys.path.append("${process.cwd()}/app")

# Importa o sistema de construção de bases
from app.utils.base_builders import atualizar_bases_apos_upload

# Atualiza as bases (user_id=1 por padrão)
resultado = atualizar_bases_apos_upload(user_id=1)

import json
print(json.dumps(resultado))
`
          
          const { spawn } = require('child_process')
          
          // Executa script Python para atualizar bases
          const updateBases = spawn('python', ['-c', pythonScript], {
            cwd: process.cwd(),
            stdio: ['pipe', 'pipe', 'pipe']
          })
          
          updateBases.stdout.on('data', (data) => {
            console.log('📊 Base update:', data.toString())
          })
          
          updateBases.stderr.on('data', (data) => {
            console.error('⚠️ Base update warning:', data.toString())
          })
          
          updateBases.on('close', (code) => {
            if (code === 0) {
              console.log('✅ Bases atualizadas com sucesso')
            } else {
              console.error(`❌ Erro ao atualizar bases (exit code: ${code})`)
            }
          })
          
        } catch (error) {
          console.error('🚨 Erro ao executar atualização de bases:', error)
          // Não falha o upload por causa disso, apenas loga o erro
        }
      }
      
      // Atualizar status da sessão
      session.status = 'confirmed'
      uploadSessions.set(sessionId, session)
      
      return NextResponse.json({
        success: true,
        summary: {
          inserted: insertedCount,
          duplicates: duplicateCount,
          errors: errorCount,
          total: transactionsToProcess?.length || 0
        },
        sessionId
      })
      
    } catch (error) {
      // Rollback em caso de erro
      db.exec('ROLLBACK')
      throw error
    } finally {
      db.close()
    }
    
  } catch (error) {
    console.error('Erro ao confirmar transações:', error)
    return NextResponse.json({ 
      error: 'Erro interno do servidor' 
    }, { status: 500 })
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const sessionId = searchParams.get('sessionId')
    
    if (!sessionId) {
      return NextResponse.json({ error: 'Session ID é obrigatório' }, { status: 400 })
    }
    
    // Remover sessão
    const deleted = uploadSessions.delete(sessionId)
    
    if (!deleted) {
      return NextResponse.json({ error: 'Sessão não encontrada' }, { status: 404 })
    }
    
    return NextResponse.json({
      success: true,
      message: 'Sessão cancelada com sucesso'
    })
    
  } catch (error) {
    console.error('Erro ao cancelar sessão:', error)
    return NextResponse.json({ 
      error: 'Erro interno do servidor' 
    }, { status: 500 })
  }
}