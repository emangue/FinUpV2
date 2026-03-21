'use client';

/**
 * Tabela Recibo Anual — Mês | Renda | Gastos | Aporte | Saldo
 * Status visual: ok, parcial, futuro, negativo
 * Resumo do ano no rodapé
 * "Ver cálculo" mostra dados exatos do cálculo
 */
import { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, Calculator, X, Plus } from 'lucide-react';
import { getCashflowDetalheMes, postExpectativa } from '../api';
import { useCashflowAnual } from '../hooks/use-cashflow-anual';

/** Formato completo (modal, tooltips) */
function fmt(v: number | null | undefined): string {
  if (v == null) return '—';
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(v);
}

/** Formato compacto para tabela (25k, 53,8k) — sem R$ para caber na tela */
function fmtCompact(v: number | null | undefined): string {
  if (v == null) return '—';
  const abs = Math.abs(v);
  if (abs >= 1_000_000) return `${(v / 1_000_000).toFixed(1).replace('.', ',')}M`;
  if (abs >= 1_000) return `${(v / 1_000).toFixed(1).replace('.', ',')}k`;
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(v);
}

function StatusIcon({ status }: { status: string }) {
  if (status === 'ok') return <span className="text-green-600">✓</span>;
  if (status === 'negativo') return <span className="text-red-600">✗</span>;
  if (status === 'parcial') return <span className="text-amber-600">◐</span>;
  return <span className="text-gray-400">○</span>;
}

const MESES_NOME: Record<number, string> = {
  1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
  7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez',
};

export function TabelaReciboAnual({ ano }: { ano: number }) {
  // P3: React Query — deduplicação automática se TabelaReciboAnual e ProjecaoChart
  // montarem simultaneamente com o mesmo `ano` (ambos chamam useCashflowAnual(ano)
  // → 1 único request HTTP em vez de 2).
  const { data, isLoading: loading, error: queryError, refetch } = useCashflowAnual(ano);
  const error = queryError?.message ?? null;

  const [expanded, setExpanded] = useState(false);
  const [detalheMes, setDetalheMes] = useState<{ ano: number; mes: number } | null>(null);
  const [detalheData, setDetalheData] = useState<Awaited<ReturnType<typeof getCashflowDetalheMes>> | null>(null);
  const [detalheLoading, setDetalheLoading] = useState(false);
  const [showAddExtra, setShowAddExtra] = useState(false);
  const [extraDesc, setExtraDesc] = useState('');
  const [extraValor, setExtraValor] = useState('');
  const [extraSaving, setExtraSaving] = useState(false);

  if (loading) {
    return (
      <div className="rounded-2xl bg-white border border-gray-100 p-4">
        <div className="animate-pulse h-8 bg-gray-100 rounded mb-2" />
        <div className="animate-pulse h-32 bg-gray-50 rounded" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-2xl bg-white border border-gray-100 p-4">
        <p className="text-sm text-red-600">{error || 'Sem dados'}</p>
      </div>
    );
  }

  const meses = data.meses;
  const totalRenda = meses.reduce((s, m) => s + (m.renda_usada ?? m.renda_esperada ?? 0), 0);
  const totalGastos = meses.reduce((s, m) => {
    const g = m.total_gastos ?? m.gastos_usados ?? m.gastos_realizados ?? m.gastos_recorrentes;
    return s + (g || 0);
  }, 0);
  // aporte_usado = renda - gastos (inclui extraordinários em ambos os lados)
  const totalAporte = meses.reduce((s, m) => s + (m.aporte_usado ?? 0), 0);
  const mesesNegativos = meses.filter((m) => (m.aporte_usado ?? 0) < 0).length;

  const handleVerCalculo = (y: number, mm: number) => {
    setDetalheMes({ ano: y, mes: mm });
    setDetalheData(null);
    setShowAddExtra(false);
    setExtraDesc('');
    setExtraValor('');
    setDetalheLoading(true);
    getCashflowDetalheMes(y, mm)
      .then(setDetalheData)
      .catch(() => setDetalheData(null))
      .finally(() => setDetalheLoading(false));
  };

  const handleAddGastoExtra = async () => {
    if (!detalheMes) return;
    const valor = parseFloat(extraValor.replace(',', '.'));
    if (!extraDesc.trim() || isNaN(valor) || valor <= 0) return;
    setExtraSaving(true);
    try {
      await postExpectativa({
        descricao: extraDesc.trim(),
        valor,
        mes_referencia: `${detalheMes.ano}-${String(detalheMes.mes).padStart(2, '0')}`,
        tipo_lancamento: 'debito',
        tipo_expectativa: 'sazonal_plano',
      });
      setExtraDesc('');
      setExtraValor('');
      setShowAddExtra(false);
      refetch();  // P3: invalida e recarrega via React Query (em vez de getCashflow manual)
    } finally {
      setExtraSaving(false);
    }
  };

  return (
    <div className="rounded-2xl bg-white border border-gray-100 overflow-hidden">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50"
      >
        <span className="font-semibold text-black">Cashflow anual {ano}</span>
        {expanded ? (
          <ChevronUp className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        )}
      </button>

      {expanded && (
        <div className="border-t border-gray-100 overflow-x-auto">
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="bg-gray-50 text-gray-600">
                <th className="text-left py-1 px-2 font-semibold text-gray-700">Mês</th>
                <th className="text-right py-1 px-2 font-semibold text-gray-700">Renda</th>
                <th className="text-right py-1 px-2 font-semibold text-gray-700">Gastos</th>
                <th className="text-right py-1 px-2 font-semibold text-gray-700">Aporte</th>
                <th className="w-6" />
                <th className="w-14" />
              </tr>
            </thead>
            <tbody>
              {meses.map((m) => {
                const [y, mm] = m.mes_referencia.split('-').map(Number);
                const mesNome = MESES_NOME[mm] || String(mm);
                const gastos = m.total_gastos ?? m.gastos_usados ?? m.gastos_realizados ?? m.gastos_recorrentes;
                return (
                  <tr key={m.mes_referencia} className="border-t border-gray-100">
                    <td className="py-1 px-2 text-gray-600">{mesNome}/{y}</td>
                    <td className="py-1 px-2 text-right text-gray-600">{fmtCompact(m.renda_usada ?? m.renda_esperada)}</td>
                    <td className="py-1 px-2 text-right text-gray-600">{fmtCompact(gastos)}</td>
                    <td className={`py-1 px-2 text-right font-medium ${(m.aporte_usado ?? 0) < 0 ? 'text-red-600' : 'text-gray-900'}`}>
                      {fmtCompact(m.aporte_usado)}
                    </td>
                    <td className="py-1 px-1">
                      <StatusIcon status={m.status_mes} />
                    </td>
                    <td className="py-1 px-1">
                      <button
                        type="button"
                        onClick={() => handleVerCalculo(y, mm)}
                        className="p-1 rounded hover:bg-gray-100 text-gray-500 hover:text-indigo-600"
                        title="Ver como o número foi calculado"
                        aria-label="Ver cálculo"
                      >
                        <Calculator className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
            <tfoot>
              <tr className="bg-gray-50 font-semibold border-t-2 border-gray-200">
                <td className="py-1 px-2 text-gray-900">Resumo {ano}</td>
                <td className="py-1 px-2 text-right text-gray-900">{fmtCompact(totalRenda)}</td>
                <td className="py-1 px-2 text-right text-gray-900">{fmtCompact(totalGastos)}</td>
                <td className={`py-1 px-2 text-right font-medium ${totalAporte < 0 ? 'text-red-600' : 'text-gray-900'}`}>
                  {fmtCompact(totalAporte)}
                </td>
                <td />
                <td />
              </tr>
            </tfoot>
          </table>
          {mesesNegativos > 0 && (
            <p className="text-xs text-amber-600 px-4 py-2">
              {mesesNegativos} {mesesNegativos === 1 ? 'mês' : 'meses'} com saldo negativo
            </p>
          )}
        </div>
      )}

      {/* Modal: Cálculo exato do mês */}
      {detalheMes && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setDetalheMes(null)}>
          <div
            className="bg-white rounded-2xl shadow-xl max-w-lg w-full max-h-[85vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="font-semibold text-black">
                Cálculo exato — {MESES_NOME[detalheMes.mes]}/{detalheMes.ano}
              </h3>
              <button type="button" onClick={() => setDetalheMes(null)} className="p-2 hover:bg-gray-100 rounded-full">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 text-sm space-y-4">
              {detalheLoading ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin h-8 w-8 border-2 border-indigo-600 border-t-transparent rounded-full" />
                </div>
              ) : detalheData ? (
                <>
                  <div className="bg-gray-50 rounded-lg p-3 font-mono text-xs break-all">
                    {detalheData.formula}
                  </div>
                  <div>
                    <p className="font-medium text-gray-700">Filtro MesFatura:</p>
                    <p className="text-gray-600">{detalheData.mes_fatura_filtro}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-blue-50 rounded p-2">
                      <p className="text-xs text-blue-600">Total realizado</p>
                      <p className="font-semibold">{fmt(detalheData.total_realizado)}</p>
                    </div>
                    <div className="bg-amber-50 rounded p-2">
                      <p className="text-xs text-amber-600">Total planejado</p>
                      <p className="font-semibold">{fmt(detalheData.total_planejado)}</p>
                    </div>
                  </div>
                  <p className="text-gray-600">
                    Fonte usada: <strong>{detalheData.fonte_usada}</strong> → Valor exibido: {fmt(detalheData.valor_exibido_no_cashflow)}
                  </p>
                  <p className="text-gray-600">
                    {detalheData.qtd_transacoes} transações somadas
                  </p>
                  {detalheData.soma_por_grupo.length > 0 && (
                    <div>
                      <p className="font-medium text-gray-700 mb-1">Realizado por grupo:</p>
                      <ul className="space-y-0.5 text-gray-600">
                        {detalheData.soma_por_grupo.map((g) => (
                          <li key={g.grupo}>{g.grupo}: {fmt(g.total)}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {detalheData.planejado_por_grupo.length > 0 && (
                    <div>
                      <p className="font-medium text-gray-700 mb-1">Planejado por grupo:</p>
                      <ul className="space-y-0.5 text-gray-600">
                        {detalheData.planejado_por_grupo.map((g) => (
                          <li key={g.grupo}>{g.grupo}: {fmt(g.total)}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {/* Adicionar gasto extraordinário */}
                  <div className="border-t border-gray-100 pt-4">
                    {!showAddExtra ? (
                      <button
                        type="button"
                        onClick={() => setShowAddExtra(true)}
                        className="flex items-center gap-2 text-indigo-600 hover:text-indigo-700 text-sm font-medium"
                      >
                        <Plus className="w-4 h-4" />
                        Adicionar gasto extraordinário
                      </button>
                    ) : (
                      <div className="space-y-2">
                        <p className="text-xs text-gray-600">
                          Coisas que você lembra no meio do caminho (ex: IPVA, presente, conserto)
                        </p>
                        <input
                          type="text"
                          placeholder="Descrição (ex: IPVA)"
                          value={extraDesc}
                          onChange={(e) => setExtraDesc(e.target.value)}
                          className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2"
                        />
                        <input
                          type="text"
                          placeholder="Valor (ex: 1500 ou 1500,50)"
                          value={extraValor}
                          onChange={(e) => setExtraValor(e.target.value)}
                          className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2"
                        />
                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={handleAddGastoExtra}
                            disabled={extraSaving || !extraDesc.trim() || !extraValor}
                            className="px-3 py-1.5 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                          >
                            {extraSaving ? 'Salvando…' : 'Adicionar'}
                          </button>
                          <button
                            type="button"
                            onClick={() => { setShowAddExtra(false); setExtraDesc(''); setExtraValor(''); }}
                            className="px-3 py-1.5 text-gray-600 text-sm hover:bg-gray-100 rounded-lg"
                          >
                            Cancelar
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-gray-700 mb-1">Transações ({detalheData.transacoes.length}):</p>
                    <div className="max-h-48 overflow-y-auto border rounded text-xs">
                      <table className="w-full">
                        <thead className="bg-gray-50 sticky top-0">
                          <tr>
                            <th className="text-left p-1.5">Estabelecimento</th>
                            <th className="text-right p-1.5">Valor</th>
                            <th className="text-left p-1.5">Grupo</th>
                            <th className="text-left p-1.5">Data</th>
                          </tr>
                        </thead>
                        <tbody>
                          {detalheData.transacoes.map((t) => (
                            <tr key={t.id} className="border-t">
                              <td className="p-1.5 truncate max-w-[120px]" title={t.estabelecimento}>{t.estabelecimento}</td>
                              <td className="p-1.5 text-right">{fmt(t.valor_abs_usado)}</td>
                              <td className="p-1.5">{t.grupo}</td>
                              <td className="p-1.5">{t.data || '—'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              ) : (
                <p className="text-red-600">Erro ao carregar detalhes</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
