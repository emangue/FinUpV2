import { NextRequest, NextResponse } from 'next/server'
import Database from 'better-sqlite3'
import path from 'path'

interface ClassificationRule {
  id: number
  pattern: string
  grupo: string
  subgrupo: string
  tipoGasto: string
  priority: number
}

interface DuplicateCheck {
  idTransacao: string
  similarity: number
  existing: any
  isExactDuplicate: boolean
  isDuplicate: boolean
}

export async function POST(request: NextRequest) {
  try {
    const { transactions, sessionId } = await request.json()
    
    if (!transactions || !Array.isArray(transactions)) {
      return NextResponse.json({ error: 'Lista de transações é obrigatória' }, { status: 400 })
    }
    
    const dbPath = path.join(process.cwd(), '../financas_dev.db')
    const db = new Database(dbPath)
    
    try {
      // 1. Carregar regras de classificação
      const classificationRules = loadClassificationRules(db)
      
      // 2. Processar cada transação
      const processedTransactions = []
      const duplicateChecks = []
      
      for (const transaction of transactions) {
        // Classificação IA
        const classified = await classifyTransaction(transaction, classificationRules)
        
        // Verificação de duplicatas
        const duplicateCheck = await checkDuplicates(db, classified)
        
        processedTransactions.push(classified)
        duplicateChecks.push(duplicateCheck)
      }
      
      return NextResponse.json({
        transactions: processedTransactions,
        duplicates: duplicateChecks,
        summary: {
          total: transactions.length,
          classified: processedTransactions.filter(t => t.classified).length,
          duplicates: duplicateChecks.filter(d => d.isDuplicate).length,
          exactDuplicates: duplicateChecks.filter(d => d.isExactDuplicate).length
        }
      })
      
    } finally {
      db.close()
    }
    
  } catch (error) {
    console.error('Erro na classificação IA:', error)
    return NextResponse.json({ 
      error: 'Erro interno do servidor' 
    }, { status: 500 })
  }
}

function loadClassificationRules(db: Database): ClassificationRule[] {
  try {
    // Carregar da tabela base_marcacoes se existir
    const rules = db.prepare(`
      SELECT 
        id,
        GRUPO,
        SUBGRUPO, 
        TipoGasto,
        1 as priority
      FROM base_marcacoes 
      ORDER BY id
    `).all()
    
    return rules.map(rule => ({
      id: rule.id,
      pattern: `${rule.GRUPO}|${rule.SUBGRUPO}`.toLowerCase(),
      grupo: rule.GRUPO,
      subgrupo: rule.SUBGRUPO,
      tipoGasto: rule.TipoGasto,
      priority: rule.priority
    }))
    
  } catch (error) {
    console.warn('Erro ao carregar regras de classificação, usando padrões:', error)
    
    // Regras padrão baseadas nos dados existentes
    return [
      { id: 1, pattern: 'uber|99|taxi', grupo: 'Transporte', subgrupo: 'Uber', tipoGasto: 'Ajustável - Uber', priority: 1 },
      { id: 2, pattern: 'ifood|rappi|delivery|uber eats', grupo: 'Alimentação', subgrupo: 'Pedidos para casa', tipoGasto: 'Ajustável - Delivery', priority: 1 },
      { id: 3, pattern: 'supermercado|atacadista|mercado|extra|carrefour', grupo: 'Alimentação', subgrupo: 'Supermercado', tipoGasto: 'Ajustável - Supermercado', priority: 1 },
      { id: 4, pattern: 'restaurante|bar|lanchonete|cafeteria', grupo: 'Alimentação', subgrupo: 'Saídas', tipoGasto: 'Ajustável - Saídas', priority: 1 },
      { id: 5, pattern: 'posto|shell|petrobras|gasolina|combustivel', grupo: 'Transporte', subgrupo: 'Combustível', tipoGasto: 'Ajustável - Carro', priority: 1 },
      { id: 6, pattern: 'netflix|spotify|amazon prime|disney', grupo: 'Casa', subgrupo: 'Assinaturas', tipoGasto: 'Ajustável - Assinaturas', priority: 1 },
      { id: 7, pattern: 'mercado pago|pix|transferencia', grupo: 'Transferências', subgrupo: 'PIX', tipoGasto: 'Transferência', priority: 1 },
      { id: 8, pattern: 'azul|gol|latam|viagem|iberia', grupo: 'Transporte', subgrupo: 'Viagens', tipoGasto: 'Ajustável - Viagens', priority: 1 },
      { id: 9, pattern: 'amazon|mercado livre|magalu|americanas', grupo: 'Casa', subgrupo: 'Compras Online', tipoGasto: 'Ajustável', priority: 1 },
      { id: 10, pattern: 'farmacia|drogaria|remedios', grupo: 'Saúde', subgrupo: 'Farmácia', tipoGasto: 'Ajustável', priority: 1 }
    ]
  }
}

async function classifyTransaction(transaction: any, rules: ClassificationRule[]): Promise<any> {
  const estabelecimento = transaction.estabelecimento.toLowerCase()
  let classified = false
  
  // Tentar classificar com regras
  for (const rule of rules) {
    const patterns = rule.pattern.split('|')
    
    for (const pattern of patterns) {
      if (estabelecimento.includes(pattern.toLowerCase())) {
        transaction.grupo = rule.grupo
        transaction.subgrupo = rule.subgrupo
        transaction.tipoGasto = rule.tipoGasto
        transaction.origem_classificacao = 'Automática - Base Padrões'
        classified = true
        break
      }
    }
    
    if (classified) break
  }
  
  // Classificação baseada em valor se não achou padrão
  if (!classified) {
    if (transaction.valorPositivo > 0) {
      // Classificação por faixas de valor
      if (transaction.valorPositivo > 500) {
        transaction.grupo = 'Casa'
        transaction.subgrupo = 'Gastos Altos'
        transaction.tipoGasto = 'Ajustável'
      } else if (transaction.valorPositivo < 20) {
        transaction.grupo = 'Pequenos Gastos'
        transaction.subgrupo = 'Diversos'
        transaction.tipoGasto = 'Ajustável'
      } else {
        transaction.grupo = ''
        transaction.subgrupo = ''
        transaction.tipoGasto = ''
      }
      transaction.origem_classificacao = 'Não Classificada'
      classified = true
    }
  }
  
  // Determinar categoria geral baseada no valor e tipo
  if (transaction.valor > 0) {
    transaction.categoriaGeral = 'Receita'
  } else if (transaction.tipoTransacao === 'Receitas') {
    transaction.categoriaGeral = 'Receita'
  } else if (transaction.grupo === 'Investimentos') {
    transaction.categoriaGeral = 'Investimentos'
  } else {
    transaction.categoriaGeral = 'Despesa'
  }
  
  transaction.classified = classified
  return transaction
}

async function checkDuplicates(db: Database, transaction: any): Promise<DuplicateCheck> {
  try {
    // 1. Verificação exata por IdTransacao
    const exactMatch = db.prepare(`
      SELECT * FROM journal_entries 
      WHERE IdTransacao = ?
    `).get(transaction.idTransacao)
    
    if (exactMatch) {
      return {
        idTransacao: transaction.idTransacao,
        similarity: 1.0,
        existing: exactMatch,
        isExactDuplicate: true,
        isDuplicate: true
      }
    }
    
    // 2. Verificação por similaridade
    const [dia, mes, ano] = transaction.data.split('/')
    const startDate = `${dia}/${mes}/${ano}`
    
    // Buscar transações similares (mesmo valor e data próxima)
    const similarTransactions = db.prepare(`
      SELECT *, 
        ABS(ValorPositivo - ?) as valor_diff,
        ABS(julianday(?) - julianday(Data)) as data_diff
      FROM journal_entries 
      WHERE ABS(ValorPositivo - ?) <= 0.01
        AND ABS(julianday(?) - julianday(Data)) <= 7
        AND banco_origem = ?
      ORDER BY valor_diff ASC, data_diff ASC
      LIMIT 5
    `).all(
      transaction.valorPositivo, 
      startDate, 
      transaction.valorPositivo,
      startDate,
      transaction.banco_origem
    )
    
    // Calcular similaridade do estabelecimento
    let bestMatch = null
    let bestSimilarity = 0
    
    for (const similar of similarTransactions) {
      const similarity = calculateStringSimilarity(
        transaction.estabelecimento.toLowerCase(),
        similar.Estabelecimento.toLowerCase()
      )
      
      if (similarity > bestSimilarity) {
        bestSimilarity = similarity
        bestMatch = similar
      }
    }
    
    // Considerar duplicata se similaridade > 85%
    const isDuplicate = bestSimilarity > 0.85
    
    return {
      idTransacao: transaction.idTransacao,
      similarity: bestSimilarity,
      existing: bestMatch,
      isExactDuplicate: false,
      isDuplicate
    }
    
  } catch (error) {
    console.error('Erro na verificação de duplicatas:', error)
    return {
      idTransacao: transaction.idTransacao,
      similarity: 0,
      existing: null,
      isExactDuplicate: false,
      isDuplicate: false
    }
  }
}

function calculateStringSimilarity(str1: string, str2: string): number {
  const len1 = str1.length
  const len2 = str2.length
  
  if (len1 === 0 && len2 === 0) return 1
  if (len1 === 0 || len2 === 0) return 0
  
  // Algoritmo de distância de Levenshtein simplificado
  const matrix = Array(len1 + 1).fill(null).map(() => Array(len2 + 1).fill(null))
  
  for (let i = 0; i <= len1; i++) matrix[i][0] = i
  for (let j = 0; j <= len2; j++) matrix[0][j] = j
  
  for (let i = 1; i <= len1; i++) {
    for (let j = 1; j <= len2; j++) {
      if (str1[i - 1] === str2[j - 1]) {
        matrix[i][j] = matrix[i - 1][j - 1]
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j - 1] + 1
        )
      }
    }
  }
  
  const distance = matrix[len1][len2]
  const maxLen = Math.max(len1, len2)
  
  return 1 - (distance / maxLen)
}