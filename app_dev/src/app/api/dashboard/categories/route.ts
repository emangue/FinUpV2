import { NextRequest, NextResponse } from 'next/server';
import Database from 'better-sqlite3';
import path from 'path';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const year = searchParams.get('year') || '2025';
    const month = searchParams.get('month') || 'all';

    const dbPath = path.join(process.cwd(), 'financas_dev.db');
    const db = new Database(dbPath);

    // Tipos de gasto a excluir
    const tiposExcluir = [
      'Investimento - Ajustável',
      'Investimento - Fixo', 
      'Pagamento Fatura',
      'Receita - Outras',
      'Receita - Salário',
      'Salário',
      'Transferência'
    ];
    
    let whereClause = `WHERE TipoTransacao IN ('Despesas', 'Cartão de Crédito')
      AND IgnorarDashboard = 0
      AND TipoGasto NOT IN ('${tiposExcluir.join("', '")}')
      AND TipoGasto IS NOT NULL`;
    
    if (month !== 'all') {
      whereClause += ` AND MesFatura = '${year}${month.padStart(2, '0')}'`;
    } else {
      whereClause += ` AND MesFatura LIKE '${year}%'`;
    }

    // Buscar total de receitas para calcular percentuais
    const totalReceitas = db.prepare(`
      SELECT COALESCE(SUM(ValorPositivo), 1) as total 
      FROM journal_entries 
      WHERE TipoTransacao = 'Receitas'
      AND IgnorarDashboard = 0
      ${month !== 'all' ? `AND MesFatura = '${year}${month.padStart(2, '0')}'` : `AND MesFatura LIKE '${year}%'`}
    `).get() as { total: number };

    // Buscar gastos por TipoGasto
    const categoryData = db.prepare(`
      SELECT 
        TipoGasto as categoria,
        SUM(ValorPositivo) as valor,
        (SUM(ValorPositivo) / ${totalReceitas.total} * 100) as percentual
      FROM journal_entries
      ${whereClause}
      GROUP BY TipoGasto
      HAVING valor > 0
      ORDER BY valor DESC
      LIMIT 10
    `).all() as Array<{ categoria: string; valor: number; percentual: number }>;

    db.close();

    return NextResponse.json(categoryData);
  } catch (error) {
    console.error('Error fetching category data:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}