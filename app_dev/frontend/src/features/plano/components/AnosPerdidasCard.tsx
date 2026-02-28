'use client';

/**
 * AnosPerdidasCard — Nudge quando gasto > renda
 * Exibe: "Com esse nível de gasto você está perdendo ~N anos de aposentadoria"
 */
import { useState, useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';
import { getImpactoLongoPrazo, type ImpactoLongoPrazoResponse } from '../api';

function formatCurrency(v: number) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0,
  }).format(v);
}

interface AnosPerdidasCardProps {
  ano: number;
  mes: number;
}

export function AnosPerdidasCard({ ano, mes }: AnosPerdidasCardProps) {
  const [impacto, setImpacto] = useState<ImpactoLongoPrazoResponse | null>(null);

  useEffect(() => {
    getImpactoLongoPrazo(ano, mes)
      .then(setImpacto)
      .catch(() => setImpacto(null));
  }, [ano, mes]);

  if (!impacto?.anos_perdidos || impacto.anos_perdidos <= 0) return null;

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4">
      <div className="flex gap-3">
        <div className="shrink-0 w-10 h-10 rounded-full bg-amber-200 flex items-center justify-center">
          <AlertTriangle className="w-5 h-5 text-amber-700" />
        </div>
        <div>
          <p className="text-[15px] font-semibold text-amber-900">
            Impacto no longo prazo
          </p>
          <p className="text-[13px] text-amber-800 mt-1">
            {impacto.mensagem}
          </p>
          {impacto.deficit_mensal != null && impacto.deficit_mensal > 0 && (
            <p className="text-[12px] text-amber-700 mt-2">
              Déficit mensal: {formatCurrency(impacto.deficit_mensal)}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
