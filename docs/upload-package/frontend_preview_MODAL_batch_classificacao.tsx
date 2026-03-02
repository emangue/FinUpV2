'use client';

/**
 * BatchClassifyModal - Classificação em lote por estabelecimento
 * Sprint 4 F.10: Agrupa transações não classificadas por estabelecimento_base,
 * dropdown de grupo/subgrupo, sugestões da API, "Salvar tudo"
 */
import { useState, useEffect } from 'react';
import { Transaction } from '../types';
import { GRUPOS, SUBGRUPOS, formatCurrency } from '../lib/constants';
import { fetchWithAuth } from '@/core/utils/api-client';
import { API_CONFIG } from '@/core/config/api.config';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface EstabelecimentoGroup {
  estabelecimento: string;
  previewIds: string[];
  totalValue: number;
  count: number;
  grupo: string;
  subgrupo: string;
}

interface BatchClassifyModalProps {
  isOpen: boolean;
  onClose: () => void;
  transactions: Transaction[];
  sessionId: string;
  onSaved: (updates: Map<string, { grupo: string; subgrupo: string }>) => void;
}

function flattenUnclassified(transactions: Transaction[]): { id: string; description: string; value: number }[] {
  const result: { id: string; description: string; value: number }[] = [];
  for (const tx of transactions) {
    const isUnclassified = !tx.grupo || !tx.subgrupo;
    if (!isUnclassified) continue;

    if (tx.items && tx.items.length > 0) {
      for (const item of tx.items) {
        if (!item.grupo || !item.subgrupo) {
          result.push({ id: item.id, description: item.description, value: item.value });
        }
      }
    } else {
      result.push({ id: tx.id, description: tx.description, value: tx.value });
    }
  }
  return result;
}

function groupByEstabelecimento(
  flat: { id: string; description: string; value: number }[]
): EstabelecimentoGroup[] {
  const map = new Map<string, { previewIds: string[]; totalValue: number }>();
  for (const item of flat) {
    const key = item.description.trim() || '(sem nome)';
    if (!map.has(key)) {
      map.set(key, { previewIds: [], totalValue: 0 });
    }
    const g = map.get(key)!;
    g.previewIds.push(item.id);
    g.totalValue += item.value;
  }
  return Array.from(map.entries()).map(([estabelecimento, { previewIds, totalValue }]) => ({
    estabelecimento,
    previewIds,
    totalValue,
    count: previewIds.length,
    grupo: '',
    subgrupo: '',
  }));
}

export default function BatchClassifyModal({
  isOpen,
  onClose,
  transactions,
  sessionId,
  onSaved,
}: BatchClassifyModalProps) {
  const [groups, setGroups] = useState<EstabelecimentoGroup[]>([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isOpen || !transactions.length) return;
    const flat = flattenUnclassified(transactions);
    const grouped = groupByEstabelecimento(flat);
    setGroups(grouped);
    setError('');
  }, [isOpen, transactions]);

  // Carregar sugestões da API e preencher grupos
  useEffect(() => {
    if (!isOpen || groups.length === 0) return;

    const loadSugestoes = async () => {
      try {
        const res = await fetchWithAuth(
          `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/estabelecimentos/sugestoes?limit=200`
        );
        if (!res.ok) return;
        const data = await res.json();
        const sugestoes = (data.sugestoes || []) as { estabelecimento: string; grupo: string }[];

        const normalizarEstab = (s: string) =>
          s.replace(/\s*\(\d+\/\d+\)\s*$/i, '').trim().toLowerCase();

        const sugestoesMap = new Map<string, string>();
        for (const s of sugestoes) {
          const key = normalizarEstab((s.estabelecimento || '').trim());
          if (key && !sugestoesMap.has(key)) {
            sugestoesMap.set(key, s.grupo || '');
          }
        }

        setGroups((prev) =>
          prev.map((g) => {
            const key = normalizarEstab(g.estabelecimento);
            const grupoSugerido = sugestoesMap.get(key);
            if (!grupoSugerido) return g;
            const subgrupos = SUBGRUPOS[grupoSugerido];
            const subgrupoSugerido = subgrupos?.[0] || '';
            return { ...g, grupo: grupoSugerido, subgrupo: subgrupoSugerido };
          })
        );
      } catch {
        // Ignorar erro de sugestões
      }
    };

    loadSugestoes();
  }, [isOpen, groups.length]);

  const updateGroup = (index: number, campo: 'grupo' | 'subgrupo', valor: string) => {
    setGroups((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], [campo]: valor };
      if (campo === 'grupo') next[index].subgrupo = '';
      return next;
    });
  };

  const handleSalvarTudo = async () => {
    const incompletos = groups.filter((g) => !g.grupo || !g.subgrupo);
    if (incompletos.length > 0) {
      setError(`Complete grupo e subgrupo para: ${incompletos.map((g) => g.estabelecimento).join(', ')}`);
      return;
    }
    setError('');
    setSaving(true);

    const baseUrl = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/preview/${sessionId}`;
    try {
      const updates = new Map<string, { grupo: string; subgrupo: string }>();
      for (const g of groups) {
        const val = { grupo: g.grupo, subgrupo: g.subgrupo };
        for (const id of g.previewIds) {
          updates.set(id, val);
        }
        await Promise.all(
          g.previewIds.map((id) =>
            fetchWithAuth(
              `${baseUrl}/${id}?grupo=${encodeURIComponent(g.grupo)}&subgrupo=${encodeURIComponent(g.subgrupo)}`,
              { method: 'PATCH' }
            )
          )
        );
      }
      onSaved(updates);
      onClose();
    } catch (err) {
      setError('Erro ao salvar. Tente novamente.');
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md max-h-[85vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Classificar em lote</DialogTitle>
          <DialogDescription>
            Agrupe por estabelecimento e defina grupo/subgrupo. Sugestões são preenchidas automaticamente.
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto space-y-4 py-2">
          {groups.map((g, i) => (
            <div
              key={g.estabelecimento}
              className="p-3 rounded-lg border border-gray-200 bg-gray-50/50"
            >
              <div className="flex justify-between items-start mb-2">
                <p className="font-medium text-gray-900 text-sm truncate flex-1 mr-2">
                  {g.estabelecimento}
                </p>
                <span className="text-xs text-gray-500 shrink-0">
                  {g.count}× {formatCurrency(g.totalValue)}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-gray-500">Grupo</label>
                  <select
                    value={g.grupo}
                    onChange={(e) => updateGroup(i, 'grupo', e.target.value)}
                    className="w-full text-sm border rounded-lg px-2 py-1.5 mt-0.5"
                  >
                    <option value="">Selecione</option>
                    {GRUPOS.map((gr) => (
                      <option key={gr} value={gr}>{gr}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Subgrupo</label>
                  <select
                    value={g.subgrupo}
                    onChange={(e) => updateGroup(i, 'subgrupo', e.target.value)}
                    disabled={!g.grupo}
                    className="w-full text-sm border rounded-lg px-2 py-1.5 mt-0.5 disabled:bg-gray-100"
                  >
                    <option value="">Selecione</option>
                    {g.grupo &&
                      SUBGRUPOS[g.grupo]?.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                  </select>
                </div>
              </div>
            </div>
          ))}
        </div>

        {error && (
          <p className="text-sm text-red-600">{error}</p>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={saving}>
            Cancelar
          </Button>
          <Button onClick={handleSalvarTudo} disabled={saving}>
            {saving ? 'Salvando...' : 'Salvar tudo'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
