'use client';

/**
 * ProjecaoChart — Poupança acumulada mês a mês
 * Três linhas: Real | Plano | Plano com redução (slider)
 * Legenda mínima (cores distintas)
 */
import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { getProjecao, getCashflow, type ProjecaoResponse } from '../api';

/** Formato em milhares (k). Se |v| < 100: "ok" */
function fmtK(v: number): string {
  if (Math.abs(v) < 100) return 'ok';
  const k = v / 1000;
  if (Math.abs(k) >= 1000) return `${(k / 1000).toFixed(1)}M`;
  return `${k >= 0 ? '' : '-'}${Math.abs(k).toFixed(1).replace('.', ',')}k`;
}

function fmt(v: number): string {
  if (v >= 1_000_000) return `R$ ${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `R$ ${Math.round(v / 1_000)} mil`;
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(v);
}

export function ProjecaoChart({ ano }: { ano: number }) {
  const [data, setData] = useState<ProjecaoResponse | null>(null);
  const [baseData, setBaseData] = useState<ProjecaoResponse | null>(null);
  const [cashflow, setCashflow] = useState<{ meses: Array<{ mes_referencia: string; renda_usada?: number; total_gastos?: number; aporte_usado?: number; use_realizado?: boolean }> } | null>(null);
  const [reducaoPct, setReducaoPct] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      getProjecao(ano, 12, reducaoPct),
      getCashflow(ano),
    ])
      .then(([proj, cf]) => {
        setData(proj);
        setCashflow(cf);
      })
      .catch((e) => setError(e?.message || 'Erro'))
      .finally(() => setLoading(false));
  }, [ano, reducaoPct]);

  useEffect(() => {
    if (reducaoPct > 0) {
      getProjecao(ano, 12, 0).then(setBaseData).catch(() => setBaseData(null));
    } else {
      setBaseData(null);
    }
  }, [ano, reducaoPct]);

  if (loading && !data) {
    return (
      <div className="rounded-2xl bg-white border border-gray-100 p-4 h-64 flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-2 border-indigo-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="rounded-2xl bg-white border border-gray-100 p-4">
        <p className="text-sm text-red-600">{error}</p>
      </div>
    );
  }

  const patrimonio = data?.patrimonio_inicial ?? 0;
  const seriePlano = data?.serie ?? [];
  const serieBase = baseData?.serie ?? [];
  const mesesCf = cashflow?.meses ?? [];

  // Série Real: patrimônio + cumsum(renda - gastos - aporte). Usa realizado quando use_realizado; senão saldo do plano.
  let acumReal = patrimonio;
  const serieReal = seriePlano.map((s, i) => {
    const m = mesesCf[i];
    let saldo: number;
    if (m?.use_realizado && m.renda_usada != null && m.total_gastos != null && m.aporte_usado != null) {
      saldo = m.renda_usada - m.total_gastos - m.aporte_usado;
    } else {
      saldo = s.saldo_mes;
    }
    acumReal += saldo;
    return m?.use_realizado ? acumReal : null;
  });

  const chartData = seriePlano.map((s, i) => ({
    name: s.mes_referencia.replace('-', '/').slice(-7),
    plano: s.acumulado,
    planoReducao: reducaoPct > 0 ? serieBase[i]?.acumulado : undefined,
    real: serieReal[i],
  }));

  return (
    <div className="rounded-2xl bg-white border border-gray-100 overflow-hidden">
      <div className="p-4 border-b border-gray-100">
        <h3 className="font-semibold text-black mb-1">Projeção de poupança</h3>
        <p className="text-xs text-gray-500 mb-2">
          Patrimônio acumulado mês a mês. Subir = guardando mais; descer = gastando mais que a renda.
        </p>
        <div className="flex items-center gap-3">
          <label className="text-[13px] text-gray-600 whitespace-nowrap">
            Reduzir gastos em:
          </label>
          <input
            type="range"
            min={0}
            max={50}
            step={5}
            value={reducaoPct}
            onChange={(e) => setReducaoPct(Number(e.target.value))}
            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
          />
          <span className="text-sm font-medium text-indigo-600 w-12">{reducaoPct}%</span>
        </div>
      </div>
      <div className="p-4 h-64">
        {chartData.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-8">Sem dados de projeção</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} stroke="#9ca3af" />
              <YAxis tickFormatter={(v) => fmtK(v)} tick={{ fontSize: 10 }} stroke="#9ca3af" />
              <Tooltip
                formatter={(value: number) => [fmt(value), '']}
                labelFormatter={(label) => `Mês ${label}`}
              />
              <Line
                type="monotone"
                dataKey="real"
                stroke="#22c55e"
                strokeWidth={2}
                dot={{ r: 2 }}
                connectNulls={false}
                strokeDasharray={undefined}
              />
              <Line
                type="monotone"
                dataKey="plano"
                stroke="#6366f1"
                strokeWidth={2}
                dot={{ r: 2 }}
              />
              {reducaoPct > 0 && (
                <Line
                  type="monotone"
                  dataKey="planoReducao"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  dot={{ r: 2 }}
                  strokeDasharray="4 2"
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
      {chartData.length > 0 && (
        <div className="px-4 pb-4 pt-1">
          <p className="text-xs text-gray-600">
            {reducaoPct > 0 && baseData?.serie?.length ? (
              <>
                Base: {fmtK(baseData.serie[baseData.serie.length - 1]?.acumulado ?? 0)} · Com {reducaoPct}% economia: {fmtK(chartData[chartData.length - 1]?.planoReducao ?? 0)}
              </>
            ) : (
              <>Fim do ano: {fmtK(chartData[chartData.length - 1]?.plano ?? 0)}</>
            )}
          </p>
        </div>
      )}
    </div>
  );
}
