'use client';

/**
 * Etapa 4 — Recibo do Ano + Plano de Aposentadoria
 * Traz toda a complexidade da tela PersonalizarPlanoLayout:
 * - Patrimônio (dashboard ou perfil)
 * - Idade atual / aposentadoria
 * - Meta financeira (patrimônio necessário)
 * - Aporte, retorno, inflação
 * - Gráfico de projeção (nominal vs real)
 * - Tabelas: Recibo anual, expectativas
 */

import * as React from 'react';
import { useDashboardMetrics } from '@/features/dashboard/hooks/use-dashboard';
import { planProfiles } from '@/features/plano-aposentadoria/lib/plan-profiles';
import type { PlanoProfile } from '@/features/plano-aposentadoria/types';
import { getPerfil, getProjecaoLonga } from '../api';
import type { ExpectativaItem } from '../api';
import { TabelaReciboAnual } from './TabelaReciboAnual';
import { ProjecaoChart } from './ProjecaoChart';
import { mobileTypography } from '@/config/mobile-typography';

const RECORRENCIA_INTERVAL: Record<string, number> = {
  unico: 0,
  bimestral: 2,
  trimestral: 3,
  semestral: 6,
  anual: 12,
};

/** Expande expectativas (sazonais ou extras) por mês do ano. Parcelado: valor/parcelas nos meses consecutivos. Não parcelado: valor no mês conforme recorrência, aplicando evolução por ocorrência. */
function expandirPorMes(
  planAno: number,
  items: ExpectativaItem[],
  sinal: 1 | -1
): number[] {
  const porMes = new Array(12).fill(0);
  for (const e of items) {
    const [refAno, refMes] = e.mes_referencia.split('-').map(Number);
    const parcelas = e.parcelas ?? 1;
    const recorrencia = (e.recorrencia ?? 'unico') as string;

    if (parcelas > 1) {
      // Parcelado: valor/parcelas em N meses consecutivos — sem evolução por parcela
      const valorParcela = e.valor / parcelas;
      let ano = refAno;
      let mes = refMes;
      for (let i = 0; i < parcelas; i++) {
        if (ano === planAno && mes >= 1 && mes <= 12) {
          porMes[mes - 1] += sinal * valorParcela;
        }
        mes += 1;
        if (mes > 12) {
          mes = 1;
          ano += 1;
        }
      }
    } else {
      // Não parcelado: valor no mês conforme recorrência, com evolução por ocorrência
      const interval = RECORRENCIA_INTERVAL[recorrencia] ?? 0;
      let ano = refAno;
      let mes = refMes;
      let count = 0;
      while (count <= 24) {
        if (ano === planAno && mes >= 1 && mes <= 12) {
          // count = número da ocorrência (0 = primeira, 1 = segunda, ...); evolução a partir da 2ª
          let val = e.valor;
          if (e.evoluir && e.evolucaoValor && count > 0) {
            if (e.evolucaoTipo === 'percentual') {
              val = e.valor * Math.pow(1 + e.evolucaoValor / 100, count);
            } else {
              val = e.valor + e.evolucaoValor * count;
            }
          }
          porMes[mes - 1] += sinal * val;
        }
        if (interval === 0) break;
        mes += interval;
        while (mes > 12) {
          mes -= 12;
          ano += 1;
        }
        count += 1;
      }
    }
  }
  return porMes;
}

function fC(v: number): string {
  if (v >= 1e6) return 'R$ ' + (v / 1e6).toFixed(1).replace('.', ',') + 'M';
  if (v >= 1e3) return 'R$ ' + Math.round(v / 1e3).toLocaleString('pt-BR') + ' mil';
  return 'R$ ' + Math.round(v).toLocaleString('pt-BR');
}
function fF(v: number): string {
  return 'R$ ' + Math.round(v).toLocaleString('pt-BR');
}

// ─── Componente de resumo de parâmetros ─────────────────────────────────────
const MESES_ABREV = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];

function ParametrosSummary({
  state,
  totalGastosRecorrentes,
  extraRendas,
  sazonais,
  fC: fmtC,
}: {
  state: PlanoAposentadoriaState;
  totalGastosRecorrentes: number;
  extraRendas: ExpectativaItem[];
  sazonais: ExpectativaItem[];
  fC: (v: number) => string;
}) {
  const [open, setOpen] = React.useState(false);
  const crescRenda = state.crescimentoRenda ?? 0;
  const crescGastos = state.crescimentoGastos ?? 0;
  const extrasAnual = extraRendas.reduce((s, e) => s + e.valor, 0);
  const sazonaisAnual = sazonais.reduce((s, e) => s + e.valor, 0);
  return (
    <div className="bg-white rounded-2xl border border-gray-200">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between p-5 text-left"
      >
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-gray-400">Parâmetros da projeção</p>
          <p className="text-sm text-gray-600 mt-0.5">
            Renda {fmtC(state.rendaMensal ?? 0)}/mês
            {crescRenda > 0 && <span className="text-indigo-600"> · +{crescRenda.toFixed(1)}% a.a. renda</span>}
            {crescGastos > 0 && <span className="text-orange-500"> · +{crescGastos.toFixed(1)}% a.a. gastos</span>}
          </p>
        </div>
        <span className="text-gray-400 ml-3">{open ? '▲' : '▼'}</span>
      </button>
      {open && (
        <div className="px-5 pb-5 space-y-4 border-t border-gray-100">
          {/* Renda */}
          <div className="pt-3">
            <p className="text-[10px] font-bold uppercase text-gray-400 mb-2">Renda</p>
            <div className="space-y-1.5">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Recorrente</span>
                <span className="font-medium">{fmtC(state.rendaMensal ?? 0)}/mês</span>
              </div>
              {crescRenda > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Crescimento renda</span>
                  <span className="text-[11px] font-medium text-indigo-600">
                    +{crescRenda.toFixed(1)}% a.a. a partir de {MESES_ABREV[(state.reajusteMes ?? 1) - 1]}/{state.reajusteAno}
                  </span>
                </div>
              )}
              {extraRendas.length > 0 && (
                <div className="mt-1 pt-1 border-t border-gray-100 space-y-1">
                  {extraRendas.map((e) => (
                    <div key={e.id} className="flex justify-between text-sm">
                      <span className="text-gray-500">
                        {e.descricao || '(sem descrição)'}
                        {e.evoluir && e.evolucaoValor ? (
                          <span className="ml-1 text-[10px] text-indigo-500">
                            +{e.evolucaoTipo === 'percentual'
                              ? `${e.evolucaoValor}%/ano`
                              : `R$${Math.round(e.evolucaoValor/1000)}k/ano`}
                          </span>
                        ) : null}
                      </span>
                      <span className="font-medium text-emerald-700">{fmtC(e.valor)}</span>
                    </div>
                  ))}
                  <div className="flex justify-between text-xs pt-1 text-gray-400">
                    <span>Total extraordinárias/ano</span>
                    <span className="font-semibold text-emerald-600">{fmtC(extrasAnual)}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
          {/* Gastos */}
          <div>
            <p className="text-[10px] font-bold uppercase text-gray-400 mb-2">Gastos</p>
            <div className="space-y-1.5">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Recorrentes</span>
                <span className="font-medium">{fmtC(totalGastosRecorrentes)}/mês</span>
              </div>
              {crescGastos > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Inflação gastos</span>
                  <span className="text-[11px] font-medium text-orange-500">+{crescGastos.toFixed(1)}% a.a. todo janeiro</span>
                </div>
              )}
              {sazonais.length > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Sazonais/ano</span>
                  <span className="font-medium text-red-600">{fmtC(sazonaisAnual)}</span>
                </div>
              )}
            </div>
          </div>
          {/* Projeção */}
          <div>
            <p className="text-[10px] font-bold uppercase text-gray-400 mb-2">Projeção</p>
            <div className="space-y-1.5">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Aporte inicial/mês</span>
                <span className="font-medium">{fmtC(state.aporte)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Retorno esperado</span>
                <span className="font-medium">{state.retorno.toFixed(1)}% a.a. nominal</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Inflação</span>
                <span className="font-medium">{state.inflacao.toFixed(1)}% a.a.</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Horizonte</span>
                <span className="font-medium">{state.age} → {state.retire} anos ({state.retire - state.age} anos)</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Patrimônio atual</span>
                <span className="font-medium">{fmtC(state.patrimonio)}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export interface PlanoAposentadoriaState {
  age: number;
  retire: number;
  patrimonio: number;
  rendaMensal: number;
  aporte: number;
  retorno: number;
  inflacao: number;
  /** Evolução da renda (% a.a.) — renda e aporte crescem ao longo do tempo */
  crescimentoRenda: number;
  /** Mês em que o reajuste ocorre todo ano (1-12). Padrão: mês atual. */
  reajusteMes?: number;
  /** Ano do primeiro reajuste. */
  reajusteAno?: number;
  /** Inflação dos gastos recorrentes (% a.a.), aplicada todo janeiro */
  crescimentoGastos?: number;
  activeProfile: PlanoProfile;
}

export interface PlanoAposentadoriaStepContentProps {
  ano: number;
  state: PlanoAposentadoriaState;
  onStateChange: (updater: (s: PlanoAposentadoriaState) => PlanoAposentadoriaState) => void;
  extraRendas: ExpectativaItem[];
  /** Gastos recorrentes (Etapa 2) — para cálculo de disponível */
  totalGastosRecorrentes?: number;
  /** Gastos sazonais (Etapa 3) — expandidos por mês (parcelado vs recorrência) */
  sazonais: ExpectativaItem[];
  /** Inflação anual dos gastos (% a.a.), aplicada todo janeiro na projeção */
  crescimentoGastos?: number;
}

export function PlanoAposentadoriaStepContent({
  ano,
  state,
  onStateChange,
  extraRendas,
  totalGastosRecorrentes = 0,
  sazonais = [],
  crescimentoGastos = 0,
}: PlanoAposentadoriaStepContentProps) {
  const hoje = new Date();
  const { metrics } = useDashboardMetrics(hoje.getFullYear(), hoje.getMonth() + 1);
  const patrimonioLiquido = metrics?.patrimonio_liquido_mes ?? 0;

  const [projecaoLonga, setProjecaoLonga] = React.useState<{
    patrimonio_final_real: number;
    patrimonio_final_nominal: number;
    meses: number;
  } | null>(null);
  const [loaded, setLoaded] = React.useState(false);
  const lastSetAporteRef = React.useRef<number | null>(null);

  const temPlanData =
    totalGastosRecorrentes > 0 || sazonais.length > 0 || extraRendas.length > 0;

  React.useEffect(() => {
    if (loaded) return;
    setLoaded(true);
    getPerfil()
      .then((p) => {
        onStateChange((s) => {
          // Aporte: usar perfil só quando não há dados do plano (Etapas 2–3); senão, pré-selecionamos maxAporte
          const aporteFromPerfil = (p.aporte_planejado ?? 0) > 0 ? p.aporte_planejado! : s.aporte;
          const aporteFinal = temPlanData ? s.aporte : aporteFromPerfil;
          return {
            ...s,
            age: p.idade_atual ?? s.age,
            retire: p.idade_aposentadoria ?? s.retire,
            patrimonio: (p.patrimonio_atual ?? 0) > 0 ? p.patrimonio_atual! : s.patrimonio,
            rendaMensal: (p.renda_mensal_liquida ?? 0) > 0 ? p.renda_mensal_liquida! : s.rendaMensal,
            aporte: aporteFinal,
            retorno: p.taxa_retorno_anual != null ? p.taxa_retorno_anual * 100 : s.retorno,
            inflacao: s.inflacao,
          };
        });
        if (patrimonioLiquido <= 0 && (p.patrimonio_atual ?? 0) > 0) {
          onStateChange((s) => ({ ...s, patrimonio: p.patrimonio_atual! }));
        }
      })
      .catch(() => {});
  }, [loaded, temPlanData]);

  React.useEffect(() => {
    if (patrimonioLiquido > 0) {
      onStateChange((s) => (s.patrimonio <= 0 ? { ...s, patrimonio: patrimonioLiquido } : s));
    }
  }, [patrimonioLiquido]);

  React.useEffect(() => {
    getProjecaoLonga(state.inflacao)
      .then((r) =>
        setProjecaoLonga({
          patrimonio_final_real: r.patrimonio_final_real,
          patrimonio_final_nominal: r.patrimonio_final_nominal,
          meses: r.meses,
        })
      )
      .catch(() => setProjecaoLonga(null));
  }, [state.inflacao]);

  const years = Math.max(1, state.retire - state.age);
  const months = years * 12;
  const retornoReal =
    ((1 + state.retorno / 100) / (1 + state.inflacao / 100) - 1) * 100;
  const patrimonioNecessario = (state.rendaMensal * 12) / 0.04;

  // Sazonais e extras por mês (parcelado: valor/parcelas nos meses corretos; não parcelado: valor no mês conforme recorrência)
  const sazonaisPorMes = React.useMemo(
    () => expandirPorMes(ano, sazonais, -1),
    [ano, sazonais]
  );
  const extrasPorMes = React.useMemo(
    () => expandirPorMes(ano, extraRendas, 1),
    [ano, extraRendas]
  );

  // Disponível por mês = renda - gastos - sazonais_no_mes + extras_no_mes
  const disponivelPorMes = React.useMemo(() => {
    return Array.from({ length: 12 }, (_, i) =>
      Math.max(
        0,
        state.rendaMensal -
          totalGastosRecorrentes +
          sazonaisPorMes[i] +
          extrasPorMes[i]
      )
    );
  }, [
    state.rendaMensal,
    totalGastosRecorrentes,
    sazonaisPorMes,
    extrasPorMes,
  ]);

  // Máximo aporte = menor disponível entre os meses (garante que todo mês cobre)
  const maxAporte = React.useMemo(() => {
    const temDados =
      totalGastosRecorrentes > 0 || sazonais.length > 0 || extraRendas.length > 0;
    if (!temDados) return 50000; // Sem dados do plano: slider livre até 50k
    const minDisp = Math.min(...disponivelPorMes);
    return Math.max(100, Math.round(minDisp / 100) * 100);
  }, [
    totalGastosRecorrentes,
    sazonais.length,
    extraRendas.length,
    disponivelPorMes,
    state.aporte,
  ]);

  // Pré-selecionar aporte = maxAporte quando há dados; limitar se exceder; atualizar quando maxAporte aumentar (ex.: após renda carregar)
  React.useEffect(() => {
    if (!temPlanData) return;
    const shouldSet =
      state.aporte === 0 ||
      state.aporte > maxAporte ||
      state.aporte === lastSetAporteRef.current;
    if (shouldSet) {
      lastSetAporteRef.current = maxAporte;
      onStateChange((s) => ({ ...s, aporte: maxAporte }));
    } else if (state.aporte !== lastSetAporteRef.current) {
      lastSetAporteRef.current = null; // usuário alterou manualmente
    }
  }, [temPlanData, maxAporte, state.aporte]);

  const aporteEfetivo = temPlanData ? Math.min(state.aporte, maxAporte) : state.aporte;
  const aporteUsado = aporteEfetivo > 0 ? aporteEfetivo : state.aporte;

  // Aporte por mês da projeção:
  //   Com dados do plano: aporte(t) = renda(t) - gastos(t) + extras(t) - sazonais(t)
  //   Sem dados:          aporte(t) = aporteUsado fixo (slider manual)
  const anoBase = hoje.getFullYear();
  const mesBase = hoje.getMonth() + 1;
  const crescimentoRenda = state.crescimentoRenda ?? 0;
  const reajusteMes = state.reajusteMes ?? mesBase;
  const reajusteAno = state.reajusteAno ?? anoBase;
  const rendaBase = state.rendaMensal > 0 ? state.rendaMensal : 0;
  const aportePorMesProjecao = React.useMemo(() => {
    const out: number[] = [];
    const fatorRenda = 1 + crescimentoRenda / 100;
    const fatorGastos = 1 + crescimentoGastos / 100;
    for (let m = 0; m < months; m++) {
      const anoOffset = Math.floor((mesBase - 1 + m) / 12);
      const ano_m = anoBase + anoOffset;
      const mes_m = ((mesBase - 1 + m) % 12) + 1;
      const saz = expandirPorMes(ano_m, sazonais, -1);
      const ext = expandirPorMes(ano_m, extraRendas, 1);
      const netExtra = (ext[mes_m - 1] ?? 0) + (saz[mes_m - 1] ?? 0);
      let aporteNoMes: number;
      if (temPlanData && rendaBase > 0) {
        // renda cresce anualmente a partir de reajusteMes/reajusteAno
        const reajusteCount =
          ano_m < reajusteAno || (ano_m === reajusteAno && mes_m < reajusteMes)
            ? 0
            : (ano_m - reajusteAno) + (mes_m >= reajusteMes ? 1 : 0);
        const rendaNoMes = rendaBase * Math.pow(fatorRenda, reajusteCount);
        // gastos crescem todo janeiro (anos completos desde anoBase)
        const gastosNoMes = totalGastosRecorrentes * Math.pow(fatorGastos, anoOffset);
        aporteNoMes = rendaNoMes - gastosNoMes + netExtra;
      } else {
        // Sem dados do plano: aporte fixo do slider
        aporteNoMes = aporteUsado + netExtra;
      }
      out.push(Math.max(0, aporteNoMes));
    }
    return out;
  }, [months, anoBase, mesBase, rendaBase, totalGastosRecorrentes, crescimentoRenda, crescimentoGastos, reajusteMes, reajusteAno, sazonais, extraRendas, temPlanData, aporteUsado]);

  const projection = React.useMemo(() => {
    const monthlyRateNom = Math.pow(1 + state.retorno / 100, 1 / 12) - 1;
    let pNom = state.patrimonio;
    for (let m = 0; m < months; m++) {
      const aporteMes = aportePorMesProjecao[m] ?? aporteUsado;
      pNom = (pNom + aporteMes) * (1 + monthlyRateNom);
    }
    const totalAportes =
      state.patrimonio + aportePorMesProjecao.reduce((s, a) => s + a, 0);
    const rendimentosNom = pNom - totalAportes;

    const monthlyRateReal = Math.pow(1 + retornoReal / 100, 1 / 12) - 1;
    let pReal = state.patrimonio;
    for (let m = 0; m < months; m++) {
      const aporteMes = aportePorMesProjecao[m] ?? aporteUsado;
      pReal = (pReal + aporteMes) * (1 + monthlyRateReal);
    }
    const rendaPassivaNom = (pNom * 0.04) / 12;
    const rendaPassivaReal = (pReal * 0.04) / 12;
    const perdaInflacao = pNom - pReal;
    const multiplier = pReal / Math.max(totalAportes, 1);
    return {
      pNom,
      pReal,
      totalAportes,
      rendimentosNom,
      rendaPassivaNom,
      rendaPassivaReal,
      perdaInflacao,
      multiplier,
    };
  }, [
    state.patrimonio,
    aporteUsado,
    aportePorMesProjecao,
    state.retorno,
    retornoReal,
    months,
  ]);

  const curvePaths = React.useMemo(() => {
    const maxVal = Math.max(projection.pNom * 1.05, 1);
    const startY = 115;
    const endY = 8;
    const startX = 10;
    const endX = 310;

    const y1 = startY - (projection.pNom / maxVal) * (startY - endY);
    const cp1x = startX + (endX - startX) * 0.35;
    const cp1y = startY - ((projection.pNom * 0.15) / maxVal) * (startY - endY);
    const cp2x = startX + (endX - startX) * 0.7;
    const cp2y = startY - ((projection.pNom * 0.55) / maxVal) * (startY - endY);
    const nomPath = `M ${startX} ${startY} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${endX} ${y1}`;
    const nomArea = `${nomPath} L ${endX} 125 L ${startX} 125 Z`;

    const yReal = startY - (projection.pReal / maxVal) * (startY - endY);
    const cpR1y = startY - ((projection.pReal * 0.15) / maxVal) * (startY - endY);
    const cpR2y = startY - ((projection.pReal * 0.55) / maxVal) * (startY - endY);
    const realPath = `M ${startX} ${startY} C ${cp1x} ${cpR1y}, ${cp2x} ${cpR2y}, ${endX} ${yReal}`;
    const realArea = `${realPath} L ${endX} 125 L ${startX} 125 Z`;

    return { nomPath, nomArea, realPath, realArea };
  }, [projection]);

  const sentiment = React.useMemo(() => {
    if (projection.rendaPassivaReal >= state.rendaMensal) {
      return {
        emoji: '😊',
        text: 'Seu plano está excelente! Meta batida em valores reais.',
        bg: 'bg-emerald-50',
        textColor: 'text-emerald-700',
      };
    }
    if (projection.rendaPassivaReal >= state.rendaMensal * 0.7) {
      return {
        emoji: '😐',
        text: 'Quase lá! Considere aumentar aportes ou prazo.',
        bg: 'bg-amber-50',
        textColor: 'text-amber-700',
      };
    }
    return {
      emoji: '😟',
      text: 'Aportes insuficientes considerando a inflação.',
      bg: 'bg-red-50',
      textColor: 'text-red-700',
    };
  }, [projection.rendaPassivaReal, state.rendaMensal]);

  const setProfile = (profile: PlanoProfile) => {
    const d = planProfiles[profile];
    onStateChange((s) => ({
      ...s,
      retorno: d.retorno,
      inflacao: d.inflacao,
      activeProfile: profile,
    }));
  };

  const minAporte = 100;

  return (
    <div className="space-y-4">
      <p className={mobileTypography.frequency.tailwind}>
        Recibo do ano e projeção até aposentadoria.
      </p>

      {/* Idade */}
      <div className="bg-white rounded-2xl border border-gray-200 p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-xs text-gray-500">Sua idade atual</p>
            <span className="text-2xl font-bold text-gray-900">{state.age}</span>
            <span className="text-sm text-gray-400 ml-1">anos</span>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500">Aposentadoria</p>
            <span className="text-2xl font-bold text-emerald-600">{state.retire}</span>
            <span className="text-sm text-gray-400 ml-1">anos</span>
          </div>
        </div>
        <div className="mb-3">
          <label className="text-[10px] text-gray-400 uppercase tracking-wide mb-1 block">
            Idade atual
          </label>
          <input
            type="range"
            min={18}
            max={70}
            value={state.age}
            className="w-full h-2 bg-gray-200 rounded-lg accent-indigo-600"
            onChange={(e) =>
              onStateChange((s) => ({ ...s, age: parseInt(e.target.value) }))
            }
          />
        </div>
        <div>
          <label className="text-[10px] text-gray-400 uppercase tracking-wide mb-1 block">
            Idade de aposentadoria
          </label>
          <input
            type="range"
            min={40}
            max={80}
            value={state.retire}
            className="w-full h-2 bg-gray-200 rounded-lg accent-indigo-600"
            onChange={(e) =>
              onStateChange((s) => ({ ...s, retire: parseInt(e.target.value) }))
            }
          />
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Faltam <strong>{Math.max(0, state.retire - state.age)}</strong> anos
        </p>
      </div>

      {/* Meta Financeira — Patrimônio + Renda */}
      <div className="bg-white rounded-2xl border border-gray-200 p-5">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">
          Meta Financeira
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-[10px] text-gray-400 uppercase block mb-1">
              Patrimônio atual
            </label>
            <input
              type="number"
              min={0}
              step={1000}
              value={state.patrimonio || ''}
              onChange={(e) =>
                onStateChange((s) => ({
                  ...s,
                  patrimonio: parseFloat(e.target.value) || 0,
                }))
              }
              className="w-full text-lg font-bold border-b-2 border-gray-200 pb-1 focus:border-gray-900 outline-none"
            />
            <p className="text-[9px] text-gray-400 mt-1">💡 Auto dos investimentos</p>
          </div>
          <div>
            <label className="text-[10px] text-gray-400 uppercase block mb-1">
              Renda desejada/mês
            </label>
            <input
              type="number"
              min={0}
              step={100}
              value={state.rendaMensal || ''}
              onChange={(e) =>
                onStateChange((s) => ({
                  ...s,
                  rendaMensal: parseFloat(e.target.value) || 0,
                }))
              }
              className="w-full text-lg font-bold border-b-2 border-emerald-200 pb-1 focus:border-emerald-500 outline-none text-emerald-700"
            />
            <p className="text-[9px] text-gray-400 mt-1">Na aposentadoria</p>
          </div>
        </div>
        <div className="mt-3 py-2 px-3 bg-amber-50 rounded-lg border border-amber-100">
          <div className="flex justify-between items-center">
            <span className="text-[10px] text-amber-700">
              Patrimônio necessário (regra 4%)
            </span>
            <span className="text-xs font-bold text-amber-900">
              {fF(patrimonioNecessario)}
            </span>
          </div>
        </div>
      </div>

      {/* Aporte Mensal */}
      <div className="bg-white rounded-2xl border border-gray-200 p-5">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">
          Aporte Mensal
        </h3>
        <div className="flex items-center justify-center gap-2 mb-3">
          <span className="text-gray-400">R$</span>
          <span className="text-3xl font-bold text-gray-900">
            {state.aporte.toLocaleString('pt-BR')}
          </span>
          <span className="text-gray-400 text-sm">/mês</span>
        </div>
        <input
          type="range"
          min={minAporte}
          max={maxAporte}
          step={100}
          value={Math.min(Math.max(state.aporte, minAporte), maxAporte)}
          className="w-full h-2 bg-gray-200 rounded-lg accent-indigo-600"
          onChange={(e) =>
            onStateChange((s) => ({ ...s, aporte: parseInt(e.target.value) }))
          }
        />
        <div className="flex gap-2 mt-2 justify-center">
          <button
            type="button"
            onClick={() =>
              onStateChange((s) => ({
                ...s,
                aporte: Math.max(minAporte, s.aporte - 100),
              }))
            }
            disabled={state.aporte <= minAporte}
            className="py-1.5 px-3 rounded-lg border border-gray-200 bg-white text-gray-700 font-semibold text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            −100
          </button>
          <button
            type="button"
            onClick={() =>
              onStateChange((s) => ({
                ...s,
                aporte: Math.min(maxAporte, s.aporte + 100),
              }))
            }
            disabled={state.aporte >= maxAporte}
            className="py-1.5 px-3 rounded-lg border border-gray-200 bg-white text-gray-700 font-semibold text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            +100
          </button>
        </div>
      </div>

      {/* Retorno & Inflação */}
      <div className="bg-white rounded-2xl border border-gray-200 p-5">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">
          Retorno & Inflação
        </h3>
        <div className="grid grid-cols-2 gap-2 mb-3">
          <div>
            <label className="text-[10px] text-gray-400 block mb-1">Retorno nominal (a.a.)</label>
            <input
              type="range"
              min={4}
              max={20}
              step={0.5}
              value={state.retorno}
              className="w-full h-2 bg-gray-200 rounded-lg accent-indigo-600"
              onChange={(e) =>
                onStateChange((s) => ({
                  ...s,
                  retorno: parseFloat(e.target.value),
                }))
              }
            />
            <span className="text-sm font-bold">{state.retorno}%</span>
          </div>
          <div>
            <label className="text-[10px] text-gray-400 block mb-1">Inflação (IPCA)</label>
            <input
              type="range"
              min={2}
              max={10}
              step={0.5}
              value={state.inflacao}
              className="w-full h-2 bg-gray-200 rounded-lg accent-indigo-600"
              onChange={(e) =>
                onStateChange((s) => ({
                  ...s,
                  inflacao: parseFloat(e.target.value),
                }))
              }
            />
            <span className="text-sm font-bold text-orange-600">
              {state.inflacao.toFixed(1).replace('.', ',')}%
            </span>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-2">
          {(['conservador', 'moderado', 'arrojado'] as PlanoProfile[]).map((p) => {
            const d = planProfiles[p];
            const realP =
              ((1 + d.retorno / 100) / (1 + d.inflacao / 100) - 1) * 100;
            const isActive = state.activeProfile === p;
            return (
              <button
                key={p}
                type="button"
                onClick={() => setProfile(p)}
                className={`py-2 px-2 rounded-xl border text-center text-xs ${
                  isActive
                    ? 'border-gray-900 bg-gray-900 text-white'
                    : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                <span className="font-bold block">{d.retorno}%</span>
                <span className="text-[9px] opacity-80">
                  {p.charAt(0).toUpperCase() + p.slice(1)}
                </span>
                <span className="text-[8px] block opacity-70">
                  Real: {realP.toFixed(0)}%
                </span>
              </button>
            );
          })}
        </div>
        <div className="mt-3 py-2 px-3 bg-blue-50 rounded-lg border border-blue-100">
          <span className="text-[10px] text-blue-700">Retorno real: </span>
          <span className="text-xs font-bold text-blue-900">
            {retornoReal.toFixed(1).replace('.', ',')}% a.a.
          </span>
        </div>
      </div>

      {/* Resumo de parâmetros da projeção — colapsável */}
      <ParametrosSummary
        state={state}
        totalGastosRecorrentes={totalGastosRecorrentes}
        extraRendas={extraRendas}
        sazonais={sazonais}
        fC={fC}
      />

      {/* Projeção — Gráfico + Cards */}
      <div className="bg-white rounded-2xl border border-gray-200 p-5">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">
          Projeção até aposentadoria
        </h3>
        <div className="flex items-center justify-between mb-3">
          <div className="flex flex-col items-center">
            <div className="w-3 h-3 rounded-full bg-gray-900" />
            <span className="text-[10px] text-gray-500">Hoje</span>
            <span className="text-[10px] font-semibold">{state.age} anos</span>
          </div>
          <div className="flex-1 h-0.5 bg-gradient-to-r from-gray-900 to-emerald-500 mx-2" />
          <div className="flex flex-col items-center">
            <div className="w-3 h-3 rounded-full bg-emerald-500" />
            <span className="text-[10px] text-gray-500">Aposentadoria</span>
            <span className="text-[10px] font-semibold text-emerald-600">
              aos {state.retire}
            </span>
          </div>
        </div>

        {/* Gráfico de curva — patrimônio nominal vs real */}
        <div className="relative mb-4" style={{ height: 140 }}>
          <svg
            viewBox="0 0 320 130"
            className="w-full h-full"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="areaGradNom" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity={0.12} />
                <stop offset="100%" stopColor="#10b981" stopOpacity={0.02} />
              </linearGradient>
              <linearGradient id="areaGradReal" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f97316" stopOpacity={0.08} />
                <stop offset="100%" stopColor="#f97316" stopOpacity={0.01} />
              </linearGradient>
            </defs>
            <path d={curvePaths.nomArea} fill="url(#areaGradNom)" />
            <path d={curvePaths.realArea} fill="url(#areaGradReal)" />
            <path
              d={curvePaths.nomPath}
              stroke="#111827"
              strokeWidth="2"
              fill="none"
            />
            <path
              d={curvePaths.realPath}
              stroke="#f97316"
              strokeWidth="2"
              strokeDasharray="4 4"
              fill="none"
            />
            <circle cx={10} cy={110} r={5} fill="white" stroke="#111827" strokeWidth={2} />
            <circle cx={10} cy={110} r={2} fill="#111827" />
          </svg>
          <div className="absolute left-[1%] bottom-[5%]">
            <div className="bg-gray-900 text-white text-[10px] font-semibold px-2 py-0.5 rounded-md shadow whitespace-nowrap">
              {fC(state.patrimonio)}
            </div>
          </div>
          <div className="absolute right-[1%] top-[0%]">
            <div className="bg-emerald-500 text-white text-[10px] font-semibold px-2 py-0.5 rounded-md shadow whitespace-nowrap">
              {fC(projection.pNom)}
            </div>
            <div className="text-[9px] text-gray-400 text-right mt-0.5">
              Meta {new Date().getFullYear() + years}
            </div>
          </div>
          <div className="absolute right-[1%] top-[35%]">
            <div className="bg-orange-400 text-white text-[10px] font-semibold px-2 py-0.5 rounded-md shadow whitespace-nowrap">
              {fC(projection.pReal)}
            </div>
            <div className="text-[9px] text-orange-400 text-right mt-0.5">
              Valor real
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4 mb-4 justify-center">
          <div className="flex items-center gap-1.5">
            <div className="w-5 h-0.5 bg-gray-900 rounded-full" />
            <span className="text-[10px] text-gray-500">Nominal</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-5 h-0.5 border-t-2 border-dashed border-orange-400" />
            <span className="text-[10px] text-gray-500">Real (- IPCA)</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 my-4">
          <div className="bg-emerald-50 rounded-xl p-3 text-center">
            <p className="text-[10px] text-emerald-700 font-medium uppercase">
              Patrimônio Nominal
            </p>
            <p className="text-lg font-bold text-emerald-700">
              {fC(projection.pNom)}
            </p>
          </div>
          <div className="bg-orange-50 rounded-xl p-3 text-center">
            <p className="text-[10px] text-orange-700 font-medium uppercase">
              Valor Real (hoje)
            </p>
            <p className="text-lg font-bold text-orange-700">
              {fC(projection.pReal)}
            </p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-blue-50 rounded-xl p-3 text-center">
            <p className="text-[10px] text-blue-700 font-medium uppercase">
              Renda Passiva
            </p>
            <p className="text-sm font-bold text-blue-700">
              ~{fC(projection.rendaPassivaReal)}/mês
            </p>
          </div>
          <div className="bg-gray-50 rounded-xl p-3 text-center">
            <p className="text-[10px] text-gray-500 font-medium uppercase">
              Total aportado
            </p>
            <p className="text-sm font-bold text-gray-900">
              {fF(projection.totalAportes)}
            </p>
          </div>
        </div>
        {(totalGastosRecorrentes > 0 || sazonais.length > 0 || extraRendas.length > 0) && (
          <p className="text-[10px] text-gray-500 mb-3 text-center">
            Cálculo: renda − gastos recorrentes − sazonais (por mês, parcelado/recorrência) + extras (por mês).
            {crescimentoRenda > 0 ? (
              <> Aporte cresce {(crescimentoRenda).toFixed(1).replace('.', ',')}% a.a. (base: {fC(aporteUsado)}/mês).</>
            ) : (
              <> Aporte efetivo: {fC(aporteUsado)}/mês.</>
            )}
          </p>
        )}
        <div
          className={`flex items-center justify-center gap-2 py-3 rounded-xl ${sentiment.bg}`}
        >
          <span className="text-2xl">{sentiment.emoji}</span>
          <span className={`text-sm font-medium ${sentiment.textColor}`}>
            {sentiment.text}
          </span>
        </div>
      </div>

      {/* Tabela Recibo Anual */}
      <TabelaReciboAnual ano={ano} />

      {/* Gráfico Projeção 12 meses */}
      <ProjecaoChart ano={ano} />

      {/* Projeção longa (backend) */}
      {projecaoLonga && (
        <div className="rounded-xl bg-indigo-50 border border-indigo-100 p-4">
          <p className="text-sm font-medium text-indigo-900">
            Projeção até aposentadoria: {fC(projecaoLonga.patrimonio_final_real)} (
            {projecaoLonga.meses} meses)
          </p>
          <p className="text-xs text-indigo-600 mt-1">
            Nominal: {fC(projecaoLonga.patrimonio_final_nominal)}
          </p>
        </div>
      )}
    </div>
  );
}
