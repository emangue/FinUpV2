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

    let whereClause = '';
    if (month !== 'all') {
      // Se um mês específico for selecionado, mostrar últimos 6 meses incluindo esse
      const selectedMonth = `${year}${month.padStart(2, '0')}`;
      whereClause = `WHERE MesFatura <= '${selectedMonth}' AND MesFatura > '${(parseInt(year) - 1).toString()}${month.padStart(2, '0')}'`;
    } else {
      // Se "todos os meses", mostrar todos os meses do ano
      whereClause = `WHERE MesFatura LIKE '${year}%'`;
    }

    // Buscar dados dos últimos meses
    const chartData = db.prepare(`
      SELECT 
        MesFatura,
        TipoTransacao,
        SUM(ValorPositivo) as valor
      FROM journal_entries
      ${whereClause} 
        AND MesFatura IS NOT NULL
        AND IgnorarDashboard = 0
      GROUP BY MesFatura, TipoTransacao
      ORDER BY MesFatura
    `).all() as Array<{ MesFatura: string; TipoTransacao: string; valor: number }>;

    // Transformar dados para o formato do gráfico
    const chartMap = new Map<string, { receitas: number; despesas: number; mesFormatado: string }>();

    chartData.forEach(item => {
      const mes = item.MesFatura;
      if (!chartMap.has(mes)) {
        // Formatar mês (AAAAMM -> MMM/AAAA)
        const year = mes.substring(0, 4);
        const month = mes.substring(4, 6);
        const monthNames = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                           'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
        const mesFormatado = `${monthNames[parseInt(month) - 1]}/${year}`;
        
        chartMap.set(mes, { receitas: 0, despesas: 0, mesFormatado });
      }

      const data = chartMap.get(mes)!;
      if (item.TipoTransacao === 'Receitas') {
        data.receitas = item.valor;
      } else if (['Despesas', 'Cartão de Crédito'].includes(item.TipoTransacao)) {
        data.despesas += item.valor;
      }
    });

    // Converter para array e ordenar
    const chartArray = Array.from(chartMap.entries())
      .map(([mes, data]) => ({
        mes: data.mesFormatado,
        receitas: data.receitas,
        despesas: data.despesas
      }))
      .sort((a, b) => {
        // Extrair ano e mês para ordenação
        const [mesA, anoA] = a.mes.split('/');
        const [mesB, anoB] = b.mes.split('/');
        const monthNames = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                           'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
        
        const mesNumA = monthNames.indexOf(mesA) + 1;
        const mesNumB = monthNames.indexOf(mesB) + 1;
        
        if (anoA !== anoB) return anoA.localeCompare(anoB);
        return mesNumA - mesNumB;
      });

    db.close();

    return NextResponse.json(chartArray);
  } catch (error) {
    console.error('Error fetching chart data:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}