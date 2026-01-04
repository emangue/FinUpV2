import { NextRequest, NextResponse } from 'next/server';
import Database from 'better-sqlite3';
import path from 'path';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const year = searchParams.get('year') || '2025';
    const month = searchParams.get('month') || 'all';

    const dbPath = path.join(process.cwd(), '../financas_dev.db');
    const db = new Database(dbPath);

    let whereClause = '';
    if (month !== 'all') {
      whereClause = `WHERE MesFatura = '${year}${month.padStart(2, '0')}'`;
    } else {
      whereClause = `WHERE MesFatura LIKE '${year}%'`;
    }

    // Total Despesas
    const totalDespesas = db.prepare(`
      SELECT COALESCE(SUM(ValorPositivo), 0) as total 
      FROM journal_entries 
      ${whereClause} AND TipoTransacao IN ('Despesas', 'Cartão de Crédito') AND IgnorarDashboard = 0
    `).get() as { total: number };

    // Total Receitas
    const totalReceitas = db.prepare(`
      SELECT COALESCE(SUM(ValorPositivo), 0) as total 
      FROM journal_entries 
      ${whereClause} AND TipoTransacao = 'Receitas' AND IgnorarDashboard = 0
    `).get() as { total: number };

    // Saldo Atual (Receitas - Despesas)
    const saldoAtual = totalReceitas.total - totalDespesas.total;

    // Total de Transações
    const totalTransacoes = db.prepare(`
      SELECT COUNT(*) as total 
      FROM journal_entries
      ${whereClause} AND IgnorarDashboard = 0
    `).get() as { total: number };

    db.close();

    return NextResponse.json({
      totalDespesas: totalDespesas.total,
      totalReceitas: totalReceitas.total,
      saldoAtual: saldoAtual,
      totalTransacoes: totalTransacoes.total
    });
  } catch (error) {
    console.error('Error fetching metrics:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}