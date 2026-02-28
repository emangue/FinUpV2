'use client';

/**
 * F.03: Orçamento por categoria com barras de progresso coloridas
 * Sprint 6 - Plano Financeiro
 */
import { useState, useEffect } from 'react';
import { getOrcamento, type OrcamentoItem } from '../api';

function formatCurrency(v: number) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0,
  }).format(v);
}

function barColor(status: OrcamentoItem['status']) {
  switch (status) {
    case 'ok':
      return 'bg-emerald-500';
    case 'alerta':
      return 'bg-amber-500';
    case 'excedido':
      return 'bg-red-500';
    default:
      return 'bg-gray-300';
  }
}

interface OrcamentoCategoriasProps {
  ano: number;
  mes: number;
}

export function OrcamentoCategorias({ ano, mes }: OrcamentoCategoriasProps) {
  const [items, setItems] = useState<OrcamentoItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getOrcamento(ano, mes)
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, [ano, mes]);

  if (loading) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-sm animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/3 mb-4" />
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-16 bg-gray-100 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-sm">
        <h3 className="text-[17px] font-semibold text-black mb-3">Orçamento por categoria</h3>
        <p className="text-sm text-gray-500">
          Nenhum gasto nem meta definida para este mês. Defina metas em &quot;Gerenciar metas por grupo&quot;.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
      <div className="p-4 border-b border-gray-100">
        <h3 className="text-[17px] font-semibold text-black">
          Orçamento por categoria
        </h3>
        <p className="text-[13px] text-gray-500 mt-0.5">
          {['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][mes - 1]}/{ano}
        </p>
      </div>
      <div className="divide-y divide-gray-100">
        {items.map((item) => (
          <div key={item.grupo} className="p-4">
            <div className="flex justify-between items-baseline mb-1">
              <span className="font-medium text-black">{item.grupo}</span>
              <span className="text-[13px] text-gray-600">
                {formatCurrency(item.gasto)}
                {item.meta != null && (
                  <> / {formatCurrency(item.meta)}</>
                )}
              </span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${barColor(item.status)}`}
                style={{
                  width: item.percentual != null
                    ? `${Math.min(item.percentual, 100)}%`
                    : '0%',
                }}
              />
            </div>
            {item.percentual != null && (
              <p className="text-[12px] text-gray-500 mt-1">
                {item.percentual.toFixed(0)}% utilizado
                {item.status === 'excedido' && (
                  <span className="text-red-600 font-medium ml-1">· Acima da meta</span>
                )}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
