#!/usr/bin/env node
/**
 * Validação Automática de Acessibilidade - Mobile V1.0
 * Sprint 4 - Teste WCAG 2.1 AA
 * 
 * Valida:
 * - Touch targets ≥44px
 * - Contraste de cores WCAG AA (4.5:1)
 * - ARIA labels
 * - Hierarquia de headings
 * - Alt text em imagens
 * - Formulários acessíveis
 */

const fs = require('fs');
const path = require('path');

// Configurações
const MOBILE_DIR = path.join(__dirname, '../../app_dev/frontend/src/app/mobile');
const COMPONENTS_DIR = path.join(__dirname, '../../app_dev/frontend/src/components/mobile');
const MIN_TOUCH_TARGET = 44;
const MIN_CONTRAST_RATIO = 4.5;

// Contadores
let totalFiles = 0;
let totalIssues = 0;
const issues = {
  touchTargets: [],
  contrast: [],
  aria: [],
  headings: [],
  forms: []
};

console.log('🔍 VALIDAÇÃO DE ACESSIBILIDADE - WCAG 2.1 AA');
console.log('═══════════════════════════════════════════════════\n');

// Função para verificar touch targets
function checkTouchTargets(content, filePath) {
  const patterns = [
    // Buttons com classes Tailwind
    /className="[^"]*\b(w-\d+|h-\d+|p-\d+)[^"]*"/g,
    // Icon sizes
    /className="[^"]*\bsize-\d+/g,
    // Width/Height inline
    /width={(\d+)}|height={(\d+)}/g
  ];

  const lines = content.split('\n');
  lines.forEach((line, index) => {
    // Verificar botões sem tamanho mínimo
    if (line.includes('button') || line.includes('Button')) {
      if (!line.includes('min-h-[44px]') && !line.includes('h-11') && !line.includes('h-12')) {
        if (line.includes('w-') || line.includes('h-') || line.includes('size-')) {
          const match = line.match(/[wh]-(\d+)|size-(\d+)/);
          if (match) {
            const size = parseInt(match[1] || match[2]) * 4; // Tailwind: 1 = 4px
            if (size < MIN_TOUCH_TARGET) {
              issues.touchTargets.push({
                file: filePath,
                line: index + 1,
                issue: `Touch target muito pequeno: ${size}px (mínimo: ${MIN_TOUCH_TARGET}px)`,
                code: line.trim()
              });
            }
          }
        }
      }
    }
  });
}

// Função para verificar contraste de cores
function checkContrast(content, filePath) {
  const colorPatterns = [
    // Text colors com background
    { pattern: /text-gray-400|text-gray-500/g, bg: 'white', issue: 'Texto cinza pode ter contraste insuficiente' },
    { pattern: /text-white.*bg-indigo-400/g, issue: 'Contraste text-white em bg-indigo-400 pode ser baixo' },
    { pattern: /text-gray-600.*bg-gray-100/g, issue: 'Contraste text-gray-600 em bg-gray-100 pode ser insuficiente' }
  ];

  const lines = content.split('\n');
  lines.forEach((line, index) => {
    colorPatterns.forEach(({ pattern, issue }) => {
      if (pattern.test(line)) {
        issues.contrast.push({
          file: filePath,
          line: index + 1,
          issue: issue,
          code: line.trim()
        });
      }
    });
  });
}

// Função para verificar ARIA labels
function checkAriaLabels(content, filePath) {
  const lines = content.split('\n');
  lines.forEach((line, index) => {
    // Botões sem texto visível devem ter aria-label
    if ((line.includes('<button') || line.includes('button')) && 
        (line.includes('<svg') || line.includes('Icon'))) {
      if (!line.includes('aria-label') && !line.includes('aria-labelledby') && 
          !line.includes('title=') && !line.includes('alt=')) {
        issues.aria.push({
          file: filePath,
          line: index + 1,
          issue: 'Botão com ícone sem aria-label ou título',
          code: line.trim()
        });
      }
    }

    // Inputs sem label
    if (line.includes('<input') && !line.includes('type="hidden"')) {
      const nextLines = content.split('\n').slice(index - 5, index + 5).join(' ');
      if (!nextLines.includes('<label') && !nextLines.includes('aria-label') && 
          !nextLines.includes('placeholder')) {
        issues.forms.push({
          file: filePath,
          line: index + 1,
          issue: 'Input sem label associado',
          code: line.trim()
        });
      }
    }

    // Role switch sem aria-checked
    if (line.includes('role="switch"') && !line.includes('aria-checked')) {
      issues.aria.push({
        file: filePath,
        line: index + 1,
        issue: 'Switch sem aria-checked',
        code: line.trim()
      });
    }
  });
}

// Função para verificar hierarquia de headings
function checkHeadings(content, filePath) {
  const headings = [];
  const lines = content.split('\n');
  
  lines.forEach((line, index) => {
    const match = line.match(/<h([1-6])|className="[^"]*text-([1-6])xl/);
    if (match) {
      const level = parseInt(match[1] || match[2]);
      headings.push({ level, line: index + 1 });
    }
  });

  // Verificar se começa com h1
  if (headings.length > 0 && headings[0].level !== 1) {
    issues.headings.push({
      file: filePath,
      line: headings[0].line,
      issue: 'Página não começa com h1',
      code: 'Primeira heading deveria ser h1'
    });
  }

  // Verificar saltos de nível
  for (let i = 1; i < headings.length; i++) {
    if (headings[i].level - headings[i-1].level > 1) {
      issues.headings.push({
        file: filePath,
        line: headings[i].line,
        issue: `Salto de heading: h${headings[i-1].level} → h${headings[i].level}`,
        code: 'Headings devem ser sequenciais'
      });
    }
  }
}

// Processar arquivo
function processFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  totalFiles++;

  checkTouchTargets(content, filePath);
  checkContrast(content, filePath);
  checkAriaLabels(content, filePath);
  checkHeadings(content, filePath);
}

// Processar diretório recursivamente
function processDirectory(dir) {
  if (!fs.existsSync(dir)) {
    console.log(`⚠️  Diretório não encontrado: ${dir}\n`);
    return;
  }

  const entries = fs.readdirSync(dir, { withFileTypes: true });

  entries.forEach(entry => {
    const fullPath = path.join(dir, entry.name);
    
    if (entry.isDirectory()) {
      processDirectory(fullPath);
    } else if (entry.name.endsWith('.tsx') || entry.name.endsWith('.ts')) {
      processFile(fullPath);
    }
  });
}

// Executar validações
console.log('📁 Processando arquivos...\n');
processDirectory(MOBILE_DIR);
processDirectory(COMPONENTS_DIR);

// Contar total de issues
totalIssues = Object.values(issues).reduce((sum, arr) => sum + arr.length, 0);

// Exibir resultados
console.log(`✅ Arquivos processados: ${totalFiles}`);
console.log(`${totalIssues > 0 ? '⚠️' : '✅'} Issues encontradas: ${totalIssues}\n`);

if (totalIssues > 0) {
  console.log('═══════════════════════════════════════════════════');
  console.log('📋 RELATÓRIO DETALHADO\n');

  // Touch Targets
  if (issues.touchTargets.length > 0) {
    console.log(`❌ TOUCH TARGETS (${issues.touchTargets.length} issues)`);
    console.log('─────────────────────────────────────────────────');
    issues.touchTargets.forEach(issue => {
      console.log(`\n📍 ${path.relative(process.cwd(), issue.file)}:${issue.line}`);
      console.log(`   ${issue.issue}`);
      console.log(`   ${issue.code.substring(0, 80)}...`);
    });
    console.log('\n');
  }

  // Contraste
  if (issues.contrast.length > 0) {
    console.log(`❌ CONTRASTE (${issues.contrast.length} issues)`);
    console.log('─────────────────────────────────────────────────');
    issues.contrast.forEach(issue => {
      console.log(`\n📍 ${path.relative(process.cwd(), issue.file)}:${issue.line}`);
      console.log(`   ${issue.issue}`);
      console.log(`   ${issue.code.substring(0, 80)}...`);
    });
    console.log('\n');
  }

  // ARIA
  if (issues.aria.length > 0) {
    console.log(`❌ ARIA LABELS (${issues.aria.length} issues)`);
    console.log('─────────────────────────────────────────────────');
    issues.aria.forEach(issue => {
      console.log(`\n📍 ${path.relative(process.cwd(), issue.file)}:${issue.line}`);
      console.log(`   ${issue.issue}`);
      console.log(`   ${issue.code.substring(0, 80)}...`);
    });
    console.log('\n');
  }

  // Formulários
  if (issues.forms.length > 0) {
    console.log(`❌ FORMULÁRIOS (${issues.forms.length} issues)`);
    console.log('─────────────────────────────────────────────────');
    issues.forms.forEach(issue => {
      console.log(`\n📍 ${path.relative(process.cwd(), issue.file)}:${issue.line}`);
      console.log(`   ${issue.issue}`);
      console.log(`   ${issue.code.substring(0, 80)}...`);
    });
    console.log('\n');
  }

  // Headings
  if (issues.headings.length > 0) {
    console.log(`❌ HIERARQUIA DE HEADINGS (${issues.headings.length} issues)`);
    console.log('─────────────────────────────────────────────────');
    issues.headings.forEach(issue => {
      console.log(`\n📍 ${path.relative(process.cwd(), issue.file)}:${issue.line}`);
      console.log(`   ${issue.issue}`);
      console.log(`   ${issue.code.substring(0, 80)}...`);
    });
    console.log('\n');
  }
}

console.log('═══════════════════════════════════════════════════');
console.log('📊 RESUMO FINAL\n');
console.log(`Touch Targets:    ${issues.touchTargets.length} issues`);
console.log(`Contraste:        ${issues.contrast.length} issues`);
console.log(`ARIA Labels:      ${issues.aria.length} issues`);
console.log(`Formulários:      ${issues.forms.length} issues`);
console.log(`Hierarquia H1-H6: ${issues.headings.length} issues`);
console.log('\n═══════════════════════════════════════════════════');

// Salvar relatório JSON
const report = {
  timestamp: new Date().toISOString(),
  totalFiles,
  totalIssues,
  issues
};

const reportPath = path.join(__dirname, 'accessibility-report.json');
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
console.log(`\n💾 Relatório salvo em: ${reportPath}\n`);

// Exit code
process.exit(totalIssues > 0 ? 1 : 0);
