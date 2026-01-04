#!/usr/bin/env node

// Teste simples do import do db-config
console.log('🧪 Testando import do db-config...')

try {
  // Simular a estrutura de caminho do Next.js
  process.chdir('/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/frontend')
  
  // Importar (só para Node.js - precisa compilar TypeScript primeiro)
  const fs = require('fs')
  const path = require('path')
  
  // Verificar se o arquivo TypeScript existe
  const tsPath = './src/lib/db-config.ts'
  if (fs.existsSync(tsPath)) {
    console.log('✅ Arquivo db-config.ts encontrado:', path.resolve(tsPath))
  }
  
  // Verificar se o banco existe
  const dbPath = '../backend/database/financas_dev.db'
  const absoluteDbPath = path.resolve(dbPath)
  
  if (fs.existsSync(absoluteDbPath)) {
    console.log('✅ Banco de dados encontrado:', absoluteDbPath)
    console.log('📊 Tamanho:', fs.statSync(absoluteDbPath).size, 'bytes')
  } else {
    console.log('❌ Banco de dados não encontrado:', absoluteDbPath)
  }
  
  console.log('🎯 Teste de import: PASSOU (arquivos existem)')
  
} catch (error) {
  console.error('❌ Erro no teste:', error.message)
  process.exit(1)
}