'use client';

/**
 * F.07: 4 banners S29 (nudges contextuais) com localStorage "não mostrar de novo"
 * Prioridade: 1) sem upload, 2) sem plano (S29), 3) sem investimento, 4) upload > 30 dias
 */

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { X, Upload, Wallet, RefreshCw, Target } from 'lucide-react';
import { fetchWithAuth } from '@/core/utils/api-client';

const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
const NUDGE_PREFIX = 'nudge_dismissed_';
// P1: tipos de nudge — usados para verificar se todos foram dispensados
const NUDGE_TYPES = ['sem_upload', 'sem_plano', 'sem_investimento', 'upload_30_dias'] as const;

interface Progress {
  primeiro_upload: boolean;
  plano_criado: boolean;
  investimento_adicionado: boolean;
  ultimo_upload_em: string | null;
}

function diasAtras(dateStr: string): number {
  const d = new Date(dateStr);
  const hoje = new Date();
  const diff = hoje.getTime() - d.getTime();
  return Math.floor(diff / (1000 * 60 * 60 * 24));
}

function mesAnteriorLabel(): string {
  const d = new Date();
  d.setMonth(d.getMonth() - 1);
  const meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
  return `${meses[d.getMonth()]} ${d.getFullYear()}`;
}

export function NudgeBanners() {
  const [progress, setProgress] = useState<Progress | null>(null);
  const [visible, setVisible] = useState<string | null>(null);

  useEffect(() => {
    // P1: se todos os nudges já foram dispensados, não buscar a API
    // P1: se onboarding completo (todos os passos feitos), não há nudges a mostrar
    if (typeof window !== 'undefined') {
      if (localStorage.getItem('onboarding_completo') === 'true') return;
      const todosDispensados = NUDGE_TYPES.every(
        (tipo) => localStorage.getItem(`${NUDGE_PREFIX}${tipo}`) === 'true'
      );
      if (todosDispensados) return;
    }

    fetchWithAuth(`${apiUrl}/api/v1/onboarding/progress`)
      .then((r) => (r.ok ? r.json() : null))
      .then(setProgress)
      .catch(() => setProgress(null));
  }, []);

  useEffect(() => {
    if (!progress) return;

    const isDismissed = (tipo: string) =>
      typeof window !== 'undefined' && localStorage.getItem(`${NUDGE_PREFIX}${tipo}`) === 'true';

    // Prioridade 1: Sem upload
    if (!progress.primeiro_upload && !isDismissed('sem_upload')) {
      setVisible('sem_upload');
      return;
    }
    // Prioridade 2: Upload feito, sem plano (S29)
    if (progress.primeiro_upload && !progress.plano_criado && !isDismissed('sem_plano')) {
      setVisible('sem_plano');
      return;
    }
    // Prioridade 3: Plano criado, sem investimento
    if (progress.plano_criado && !progress.investimento_adicionado && !isDismissed('sem_investimento')) {
      setVisible('sem_investimento');
      return;
    }
    // Prioridade 4: Último upload há > 30 dias
    if (progress.ultimo_upload_em) {
      const dias = diasAtras(progress.ultimo_upload_em);
      if (dias > 30 && !isDismissed('upload_30_dias')) {
        setVisible('upload_30_dias');
        return;
      }
    }
    setVisible(null);
  }, [progress]);

  const handleClose = (tipo: string) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(`${NUDGE_PREFIX}${tipo}`, 'true');
    }
    setVisible(null);
  };

  if (!visible) return null;

  if (visible === 'sem_upload') {
    return (
      <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 mb-4 flex items-start justify-between gap-3">
        <div className="flex-1">
          <p className="text-sm font-medium text-blue-900">
            Suba seu extrato e veja para onde vai seu dinheiro
          </p>
          <Link href="/mobile/upload" className="inline-block mt-2">
            <Button size="sm" variant="outline" className="border-blue-300 text-blue-800">
              <Upload className="w-4 h-4 mr-1" />
              Fazer upload
            </Button>
          </Link>
        </div>
        <button
          onClick={() => handleClose('sem_upload')}
          className="p-1 text-blue-600 hover:text-blue-800"
          aria-label="Fechar"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    );
  }

  if (visible === 'sem_plano') {
    return (
      <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-4 mb-4 flex items-start justify-between gap-3">
        <div className="flex-1">
          <p className="text-sm font-medium text-indigo-900">
            Ótimo início! Crie seu Plano para ter um orçamento real
          </p>
          <Link href="/mobile/plano" className="inline-block mt-2">
            <Button size="sm" variant="outline" className="border-indigo-300 text-indigo-800">
              <Target className="w-4 h-4 mr-1" />
              Criar plano
            </Button>
          </Link>
        </div>
        <button
          onClick={() => handleClose('sem_plano')}
          className="p-1 text-indigo-600 hover:text-indigo-800"
          aria-label="Fechar"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    );
  }

  if (visible === 'sem_investimento') {
    return (
      <div className="rounded-xl border border-green-200 bg-green-50 p-4 mb-4 flex items-start justify-between gap-3">
        <div className="flex-1">
          <p className="text-sm font-medium text-green-900">
            Complete seu patrimônio! Adicione seus investimentos
          </p>
          <Link href="/mobile/carteira" className="inline-block mt-2">
            <Button size="sm" variant="outline" className="border-green-300 text-green-800">
              <Wallet className="w-4 h-4 mr-1" />
              Adicionar
            </Button>
          </Link>
        </div>
        <button
          onClick={() => handleClose('sem_investimento')}
          className="p-1 text-green-600 hover:text-green-800"
          aria-label="Fechar"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    );
  }

  if (visible === 'upload_30_dias') {
    return (
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 mb-4 flex items-start justify-between gap-3">
        <div className="flex-1">
          <p className="text-sm font-medium text-amber-900">
            Hora de atualizar! Suba o extrato de {mesAnteriorLabel()}
          </p>
          <Link href="/mobile/upload" className="inline-block mt-2">
            <Button size="sm" variant="outline" className="border-amber-300 text-amber-800">
              <RefreshCw className="w-4 h-4 mr-1" />
              Atualizar
            </Button>
          </Link>
        </div>
        <button
          onClick={() => handleClose('upload_30_dias')}
          className="p-1 text-amber-600 hover:text-amber-800"
          aria-label="Fechar"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return null;
}
