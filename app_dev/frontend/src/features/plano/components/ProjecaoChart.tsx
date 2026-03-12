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
import { getProjecao, type ProjecaoResponse } from '../api';
import { useCashflowAnual } from '../hooks/use-cashflow-anual';

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
  const [baseData, setBaseData] = useState<ProjecaoResponse | null>(null);
  // P3: React Query — se TabelaReciboAnual e ProjecaoChart montarem juntos com o
  // mesmo `ano`, apenas 1 request HTTP é disparado (deduplicação por queryKey).
  const { data: cashflow } = useCashflowAnual(ano);
  // G1: sliderValue = estado visual imediato; debouncedPct = dispara fetch após parar
  const [sliderValue, setSliderValue] = useState(0);
  const [debouncedPct, setDebouncedPct] = useState(0);
  const [loadingBase, setLoadingBase] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Overlay: parâmetros fixos (validados pelo usuário)
  const OVERLAY = { top: 5, left: 65, right: 60, bottom: 35 };
  const OVERLAY_STORAGE_KEY = 'projecao-overlay-width-pct';
  const OVERLAY_RIGHT_EXTEND_KEY = 'projecao-overlay-right-extend';
  const defaultWidths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((m) => (m / 12) * 100);
  const [overlayWidthPct, setOverlayWidthPct] = useState<number[]>(defaultWidths);
  const [overlayRightExtend, setOverlayRightExtend] = useState(0);

  useEffect(() => {
    try {
      const s = localStorage.getItem(OVERLAY_STORAGE_KEY);
      if (s) {
        const parsed = JSON.parse(s) as number[];
        if (Array.isArray(parsed) && parsed.length === 12) setOverlayWidthPct(parsed);
      }
      const ext = localStorage.getItem(OVERLAY_RIGHT_EXTEND_KEY);
      if (ext != null) setOverlayRightExtend(Math.max(0, Number(ext) || 0));
    } catch {}
  }, []);

  // G1: debounce — sliderValue muda imediatamente (UI suave), debouncedPct dispara fetch após 400ms
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedPct(sliderValue), 400);
    return () => clearTimeout(timer);
  }, [sliderValue]);

  // G3 Effect 1: dados base (projeção) — cashflow vem do React Query acima (useCashflowAnual)
  useEffect(() => {
    setLoadingBase(true);
    setError(null);
    getProjecao(ano, 12, 0, true)
      .then((base) => {
        setBaseData(base);
      })
      .catch((e) => setError(e?.message || 'Erro'))
      .finally(() => setLoadingBase(false));
  }, [ano]);

  if (loadingBase && !baseData) {
    return (
      <div className="rounded-2xl bg-white border border-gray-100 p-4 h-64 flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-2 border-indigo-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (error && !baseData) {
    return (
      <div className="rounded-2xl bg-white border border-gray-100 p-4">
        <p className="text-sm text-red-600">{error}</p>
      </div>
    );
  }

  // Plano = base (0%). Plano com redução = data (quando debouncedPct > 0).
  const patrimonio = baseData?.patrimonio_inicial ?? 0;
  const seriePlano = baseData?.serie ?? [];
  const mesesCf = cashflow?.meses ?? [];

  // Série Real: patrimônio + soma acumulada de investimentos_realizados (transações CategoriaGeral=Investimentos).
  let acumInvest = patrimonio;
  const serieReal = seriePlano.map((s, i) => {
    const m = mesesCf[i];
    if (!m?.use_realizado) return null;
    const inv = m.investimentos_realizados ?? 0;
    acumInvest += inv;
    return acumInvest;
  });

  const lastRealIdx = serieReal.findLastIndex((v) => v != null);
  const realAteMes = lastRealIdx >= 0 ? serieReal[lastRealIdx] : null;

  // Curva laranja = curva verde + savings cumulativos nos meses futuros.
  // NUNCA usando o backend com debouncedPct: aquele usa fórmulas estruturalmente
  // diferentes (renda-gastos-invest vs patrimônio+investimentos), o que introduz
  // desvios não relacionados à economia de gastos.
  const serieRealMaisEconomia: (number | undefined)[] = (() => {
    if (debouncedPct <= 0) return [];
    // Base: curva verde (realMaisPlano) ou azul (seriePlano) se não houver dados realizados
    const hasReal = realAteMes != null && lastRealIdx >= 0;
    const ytdPl = hasReal ? (seriePlano[lastRealIdx]?.acumulado ?? null) : null;
    const base = hasReal && ytdPl != null
      ? seriePlano.map((s, i) =>
          i <= lastRealIdx && serieReal[i] != null
            ? (serieReal[i] as number)
            : (realAteMes as number) + ((s.acumulado ?? 0) - ytdPl)
        )
      : seriePlano.map((s) => s.acumulado ?? 0);
    // Adicionar savings cumulativos SOMENTE a partir do primeiro mês não realizado
    const startSavingsIdx = hasReal ? lastRealIdx + 1 : 0;
    let cumSavings = 0;
    return base.map((baseValue, i) => {
      if (i >= startSavingsIdx) {
        cumSavings += (mesesCf[i]?.gastos_recorrentes ?? 0) * (debouncedPct / 100);
      }
      return (baseValue as number) + cumSavings;
    });
  })();

  const mesRealLabel = lastRealIdx >= 0 ? seriePlano[lastRealIdx]?.mes_referencia?.replace('-', '/').slice(-7) : null;
  const ytdPlano = lastRealIdx >= 0 ? seriePlano[lastRealIdx]?.acumulado ?? null : null;
  const fyPlano = seriePlano[seriePlano.length - 1]?.acumulado ?? 0;
  const fyRealMaisPlano =
    realAteMes != null && lastRealIdx >= 0 && ytdPlano != null
      ? realAteMes + (fyPlano - ytdPlano)
      : null;

  // Breakdowns de economia (usados no rodapé explicativo)
  const fyRealMaisEconomiaFinal = debouncedPct > 0 && serieRealMaisEconomia.length > 0
    ? (serieRealMaisEconomia[serieRealMaisEconomia.length - 1] ?? 0)
    : 0;
  const mesesFuturos = seriePlano.length - (lastRealIdx + 1); // meses ainda não realizados

  // Ganho calculado diretamente dos gastos_recorrentes futuros do cashflow:
  // ganho = soma de (gastos_recorrentes_mes × pct%) para cada mês não realizado.
  // Isso é preciso — não compara curvas com fórmulas diferentes (azul vs laranja).
  const ganhoEconomia = debouncedPct > 0
    ? mesesCf
        .slice(lastRealIdx + 1)
        .reduce((sum, m) => sum + (m.gastos_recorrentes ?? 0) * (debouncedPct / 100), 0)
    : 0;
  const ganhoPorMes = mesesFuturos > 0 ? ganhoEconomia / mesesFuturos : 0;

  // Curva verde FY Real+Plano: sólida nos realizados, tracejada na projeção futura
  const realMaisPlanoSolido = lastRealIdx >= 0 ? serieReal.map((v, i) => (i <= lastRealIdx ? v : null)) : [];
  const realMaisPlanoTracejado =
    realAteMes != null && lastRealIdx >= 0 && ytdPlano != null
      ? seriePlano.map((s, i) =>
          i < lastRealIdx ? null : realAteMes + ((s.acumulado ?? 0) - ytdPlano)
        )
      : [];

  // Série única Real+Plano (para fallback de renderização)
  const realMaisPlano =
    realAteMes != null && lastRealIdx >= 0 && ytdPlano != null
      ? seriePlano.map((s, i) =>
          i <= lastRealIdx && serieReal[i] != null
            ? serieReal[i]
            : realAteMes + ((s.acumulado ?? 0) - ytdPlano)
        )
      : [];

  const chartData = seriePlano.map((s, i) => ({
    name: s.mes_referencia.replace('-', '/').slice(-7),
    plano: s.acumulado,
    real: serieReal[i],
    realMaisPlano: lastRealIdx >= 0 && realMaisPlano.length > 0 ? realMaisPlano[i] : undefined,
    realMaisPlanoSolido: lastRealIdx >= 0 ? realMaisPlanoSolido[i] ?? undefined : undefined,
    realMaisPlanoTracejado: lastRealIdx >= 0 ? realMaisPlanoTracejado[i] ?? undefined : undefined,
    realMaisEconomia: debouncedPct > 0 ? serieRealMaisEconomia[i] : undefined,
  }));

  return (
    <div className="rounded-2xl bg-white border border-gray-100 overflow-hidden">
      <div className="p-4 border-b border-gray-100">
        <h3 className="font-semibold text-black mb-1">Projeção de poupança</h3>
        <p className="text-xs text-gray-500 mb-2">
          Poupança acumulada no ano (sem patrimônio inicial). Subir = guardando mais; descer = gastando mais que a renda.
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
            value={sliderValue}
            onChange={(e) => setSliderValue(Number(e.target.value))}
            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
          />
          <span className="text-sm font-medium text-indigo-600 w-12">{sliderValue}%</span>
        </div>
      </div>
      <div className="p-4 h-64 relative">
        {chartData.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-8">Sem dados de projeção</p>
        ) : (
          <>
            {lastRealIdx >= 0 && (
              <div
                className="absolute pointer-events-none flex"
                style={{
                  top: `calc(1rem + ${OVERLAY.top}px)`,
                  left: `calc(1rem + ${OVERLAY.left}px)`,
                  right: `calc(1rem + ${Math.max(0, OVERLAY.right - overlayRightExtend)}px)`,
                  bottom: `calc(1rem + ${OVERLAY.bottom}px)`,
                }}
              >
                <div
                  className="bg-gray-200/60 rounded-l"
                  style={{ width: `${overlayWidthPct[lastRealIdx] ?? 25}%` }}
                />
              </div>
            )}
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} stroke="#9ca3af" />
              <YAxis tickFormatter={(v) => fmtK(v)} tick={{ fontSize: 10 }} stroke="#9ca3af" domain={['auto', 'auto']} />
              <Tooltip
                formatter={(value: number) => [fmt(value), '']}
                labelFormatter={(label) => `Mês ${label}`}
              />
              <Line
                type="monotone"
                dataKey="plano"
                stroke="#6366f1"
                strokeWidth={2}
                dot={{ r: 2 }}
              />
              {lastRealIdx >= 0 && realAteMes != null && ytdPlano != null && realMaisPlano.some((v) => v != null) && (
                <Line
                  type="monotone"
                  dataKey="realMaisPlano"
                  name="Real+Plano"
                  stroke="#22c55e"
                  strokeWidth={2.5}
                  dot={{ r: 2 }}
                  connectNulls={true}
                  isAnimationActive={false}
                />
              )}
              {debouncedPct > 0 && (
                <Line
                  type="monotone"
                  dataKey="realMaisEconomia"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  dot={{ r: 2 }}
                  strokeDasharray="4 2"
                />
              )}
            </LineChart>
          </ResponsiveContainer>
          </>
        )}
      </div>
      {chartData.length > 0 && (
        <div className="px-4 pb-4 pt-1 space-y-0.5">
          {realAteMes != null && mesRealLabel && ytdPlano != null ? (
            <>
              <p className="text-xs text-gray-600">
                YTD Real: {fmtK(realAteMes)} / YTD Plano: {fmtK(ytdPlano)}
              </p>
              <p className="text-xs text-gray-600">
                FY Real+Plano: {fmtK(fyRealMaisPlano ?? 0)} / FY Plano: {fmtK(fyPlano)}
              </p>
              {debouncedPct > 0 && serieRealMaisEconomia.length > 0 && (
                <>
                  <p className="text-xs text-gray-600">
                    FY Real + Plano {debouncedPct}% economia: {fmtK(fyRealMaisEconomiaFinal)}
                  </p>
                  {mesesFuturos > 0 && (
                    <p className="text-xs text-emerald-600 font-medium">
                      → +{fmtK(ganhoEconomia)} no ano (+{fmtK(ganhoPorMes)}/mês em {mesesFuturos} {mesesFuturos === 1 ? 'mês' : 'meses'} restantes)
                    </p>
                  )}
                </>
              )}
            </>
          ) : (
            <p className="text-xs text-gray-600">
              {debouncedPct > 0 && serieRealMaisEconomia.length > 0 ? (
                <>Base: {fmtK(fyPlano)} · Com {debouncedPct}% economia: {fmtK(fyRealMaisEconomiaFinal)}</>
              ) : (
                <>Fim do ano: {fmtK(fyPlano)}</>
              )}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
