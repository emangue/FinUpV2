'use client';

/**
 * ProjecaoChart — Poupança acumulada mês a mês
 * Slider: "Reduzir gastos em X%" (reducao_pct)
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
  LabelList,
} from 'recharts';
import { getProjecao, type ProjecaoResponse } from '../api';

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
  const [reducaoPct, setReducaoPct] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getProjecao(ano, 12, reducaoPct)
      .then(setData)
      .catch((e) => setError(e?.message || 'Erro'))
      .finally(() => setLoading(false));
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

  const chartData = (data?.serie ?? []).map((s) => ({
    name: s.mes_referencia.replace('-', '/').slice(-7), // "2026/03"
    acumulado: s.acumulado,
    saldo_mes: s.saldo_mes,
  }));

  return (
    <div className="rounded-2xl bg-white border border-gray-100 overflow-hidden">
      <div className="p-4 border-b border-gray-100">
        <h3 className="font-semibold text-black mb-1">Projeção de poupança</h3>
        <p className="text-xs text-gray-500 mb-2">
          Patrimônio acumulado mês a mês (patrimônio atual + saldo de cada mês). Subir = guardando mais; descer = gastando mais que a renda.
        </p>
        <div className="flex items-center gap-4 text-xs text-gray-600">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-indigo-600 rounded" />
            Patrimônio acumulado (R$ mil)
          </span>
        </div>
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
              <XAxis
                dataKey="name"
                tick={{ fontSize: 10 }}
                stroke="#9ca3af"
              />
              <YAxis
                tickFormatter={(v) => fmtK(v)}
                tick={{ fontSize: 10 }}
                stroke="#9ca3af"
              />
              <Tooltip
                formatter={(value: number) => [fmt(value), 'Patrimônio acumulado']}
                labelFormatter={(label) => `Mês ${label}`}
              />
              <Line
                type="monotone"
                dataKey="acumulado"
                stroke="#6366f1"
                strokeWidth={2}
                dot={{ r: 3 }}
                name="Patrimônio acumulado (R$ mil)"
              >
                <LabelList
                  dataKey="acumulado"
                  position="top"
                  formatter={(v: number) => fmtK(v)}
                  className="text-[10px] fill-indigo-600"
                />
              </Line>
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
