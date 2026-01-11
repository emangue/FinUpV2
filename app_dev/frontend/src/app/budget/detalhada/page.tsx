'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Calendar, DollarSign, Save, Copy, ArrowLeft, AlertCircle } from 'lucide-react';
import { API_CONFIG } from '@/core/config/api.config';
import Link from 'next/link';

interface BudgetItem {
  tipo_gasto: string;
  mes_referencia: string;
  valor_planejado: number;
}

interface MetaGeralItem {
  categoria_geral: string;
  valor_planejado: number;
}

// Mapeamento de TipoGasto para Categoria Geral
const categoriaMapping: Record<string, string[]> = {
  'Casa': ['Ajustável - Casa'],
  'Cartão de Crédito': [
    'Ajustável',
    'Fixo',
    'Ajustável - Delivery',
    'Ajustável - Saídas',
    'Ajustável - Supermercado',
    'Ajustável - Roupas',
    'Ajustável - Presentes',
    'Ajustável - Assinaturas',
    'Ajustável - Tech',
  ],
  'Doações': ['Ajustável - Doações'],
  'Saúde': ['Ajustável - Esportes'],
  'Viagens': ['Ajustável - Viagens'],
  'Outros': ['Ajustável - Carro', 'Ajustável - Uber'],
};

const meses = [
  { value: '01', label: 'Janeiro' },
  { value: '02', label: 'Fevereiro' },
  { value: '03', label: 'Março' },
  { value: '04', label: 'Abril' },
  { value: '05', label: 'Maio' },
  { value: '06', label: 'Junho' },
  { value: '07', label: 'Julho' },
  { value: '08', label: 'Agosto' },
  { value: '09', label: 'Setembro' },
  { value: '10', label: 'Outubro' },
  { value: '11', label: 'Novembro' },
  { value: '12', label: 'Dezembro' },
];

export default function BudgetDetalhadaPage() {
  const currentDate = new Date();
  const [selectedMonth, setSelectedMonth] = useState(String(currentDate.getMonth() + 1).padStart(2, '0'));
  const [selectedYear, setSelectedYear] = useState(String(currentDate.getFullYear()));
  const [budgetData, setBudgetData] = useState<Record<string, number>>({});
  const [metaGeral, setMetaGeral] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const mesReferencia = `${selectedYear}-${selectedMonth}`;

  // Carregar dados do orçamento detalhado e meta geral
  useEffect(() => {
    loadBudget();
    loadMetaGeral();
  }, [selectedMonth, selectedYear]);

  const loadBudget = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/api/v1/budget?mes_referencia=${mesReferencia}&user_id=1`
      );
      
      if (response.ok) {
        const result = await response.json();
        const data = result.budgets || [];
        const budgetMap: Record<string, number> = {};
        data.forEach((item: BudgetItem) => {
          budgetMap[item.tipo_gasto] = item.valor_planejado;
        });
        setBudgetData(budgetMap);
      } else {
        setBudgetData({});
      }
    } catch (error) {
      console.error('Erro ao carregar orçamento detalhado:', error);
      setMessage({ type: 'error', text: 'Erro ao carregar dados do orçamento detalhado' });
    } finally {
      setLoading(false);
    }
  };

  const loadMetaGeral = async () => {
    try {
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/api/v1/budget/geral?mes_referencia=${mesReferencia}&user_id=1`
      );
      
      if (response.ok) {
        const result = await response.json();
        const data = result.budgets || [];
        const metaMap: Record<string, number> = {};
        data.forEach((item: MetaGeralItem) => {
          metaMap[item.categoria_geral] = item.valor_planejado;
        });
        setMetaGeral(metaMap);
      }
    } catch (error) {
      console.error('Erro ao carregar meta geral:', error);
    }
  };

  const handleValueChange = (tipoGasto: string, value: string) => {
    const numValue = parseFloat(value) || 0;
    setBudgetData(prev => ({
      ...prev,
      [tipoGasto]: numValue,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const items = Object.entries(budgetData)
        .filter(([_, valor]) => valor > 0)
        .map(([tipo_gasto, valor_planejado]) => ({
          tipo_gasto,
          valor_planejado,
        }));

      const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/v1/budget/bulk-upsert?user_id=1`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mes_referencia: mesReferencia, budgets: items }),
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Orçamento detalhado salvo com sucesso!' });
        setTimeout(() => setMessage(null), 3000);
      } else {
        throw new Error('Erro ao salvar');
      }
    } catch (error) {
      console.error('Erro ao salvar orçamento:', error);
      setMessage({ type: 'error', text: 'Erro ao salvar orçamento' });
    } finally {
      setSaving(false);
    }
  };

  const handleCopyPreviousMonth = async () => {
    const currentMonth = parseInt(selectedMonth);
    const currentYear = parseInt(selectedYear);
    
    let prevMonth = currentMonth - 1;
    let prevYear = currentYear;
    
    if (prevMonth < 1) {
      prevMonth = 12;
      prevYear -= 1;
    }
    
    const prevMesReferencia = `${prevYear}-${String(prevMonth).padStart(2, '0')}`;
    
    try {
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/api/v1/budget?mes_referencia=${prevMesReferencia}&user_id=1`
      );
      
      if (response.ok) {
        const result = await response.json();
        const data = result.budgets || [];
        const budgetMap: Record<string, number> = {};
        data.forEach((item: BudgetItem) => {
          budgetMap[item.tipo_gasto] = item.valor_planejado;
        });
        setBudgetData(budgetMap);
        setMessage({ type: 'success', text: `Dados copiados de ${meses[prevMonth - 1].label} ${prevYear}` });
        setTimeout(() => setMessage(null), 3000);
      } else {
        setMessage({ type: 'error', text: 'Nenhum orçamento encontrado no mês anterior' });
      }
    } catch (error) {
      console.error('Erro ao copiar mês anterior:', error);
      setMessage({ type: 'error', text: 'Erro ao copiar dados do mês anterior' });
    }
  };

  const getTotalPorCategoria = (categoria: string): number => {
    const tiposGasto = categoriaMapping[categoria] || [];
    return tiposGasto.reduce((sum, tipo) => sum + (budgetData[tipo] || 0), 0);
  };

  const isOverBudget = (categoria: string): boolean => {
    const total = getTotalPorCategoria(categoria);
    const meta = metaGeral[categoria] || 0;
    return meta > 0 && total > meta;
  };

  return (
    <div className="flex-1 space-y-6 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/budget" className="text-sm text-muted-foreground hover:text-primary flex items-center gap-2 mb-2">
            <ArrowLeft className="h-4 w-4" />
            Voltar para Meta Geral
          </Link>
          <h2 className="text-3xl font-bold tracking-tight">Meta Detalhada por Tipo de Gasto</h2>
          <p className="text-muted-foreground mt-2">
            Detalhe o orçamento por categoria específica. Os totais não devem ultrapassar a meta geral.
          </p>
        </div>
      </div>

      {message && (
        <div
          className={`p-4 rounded-lg border ${
            message.type === 'success'
              ? 'bg-green-50 border-green-200 text-green-800'
              : 'bg-red-50 border-red-200 text-red-800'
          }`}
        >
          {message.text}
        </div>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Selecionar Período
              </CardTitle>
              <CardDescription className="mt-2">
                Escolha o mês e ano para gerenciar o orçamento detalhado
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopyPreviousMonth}
                disabled={loading || saving}
              >
                <Copy className="h-4 w-4 mr-2" />
                Copiar Mês Anterior
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <Label htmlFor="month">Mês</Label>
              <Select value={selectedMonth} onValueChange={setSelectedMonth}>
                <SelectTrigger id="month">
                  <SelectValue placeholder="Selecione o mês" />
                </SelectTrigger>
                <SelectContent>
                  {meses.map(mes => (
                    <SelectItem key={mes.value} value={mes.value}>
                      {mes.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex-1">
              <Label htmlFor="year">Ano</Label>
              <Select value={selectedYear} onValueChange={setSelectedYear}>
                <SelectTrigger id="year">
                  <SelectValue placeholder="Selecione o ano" />
                </SelectTrigger>
                <SelectContent>
                  {[2024, 2025, 2026, 2027].map(year => (
                    <SelectItem key={year} value={String(year)}>
                      {year}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Carregando...</div>
      ) : (
        <Accordion type="multiple" className="w-full space-y-4">
          {Object.entries(categoriaMapping).map(([categoria, tiposGasto]) => {
            const total = getTotalPorCategoria(categoria);
            const meta = metaGeral[categoria] || 0;
            const overBudget = isOverBudget(categoria);

            return (
              <AccordionItem key={categoria} value={categoria} className="border rounded-lg">
                <Card>
                  <AccordionTrigger className="px-6 py-4 hover:no-underline">
                    <div className="flex items-center justify-between w-full pr-4">
                      <div className="flex items-center gap-3">
                        <DollarSign className="h-5 w-5" />
                        <span className="font-semibold text-lg">{categoria}</span>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Total: </span>
                          <span className={`font-bold ${overBudget ? 'text-red-600' : ''}`}>
                            R$ {total.toFixed(2)}
                          </span>
                        </div>
                        {meta > 0 && (
                          <>
                            <div>
                              <span className="text-muted-foreground">Meta: </span>
                              <span className="font-bold">R$ {meta.toFixed(2)}</span>
                            </div>
                            {overBudget && (
                              <AlertCircle className="h-5 w-5 text-red-600" />
                            )}
                          </>
                        )}
                      </div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent>
                    <CardContent className="pt-0">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {tiposGasto.map(tipo => (
                          <div key={tipo} className="space-y-2">
                            <Label htmlFor={tipo}>{tipo}</Label>
                            <div className="flex items-center gap-2">
                              <span className="text-muted-foreground">R$</span>
                              <Input
                                id={tipo}
                                type="number"
                                step="0.01"
                                min="0"
                                value={budgetData[tipo] || ''}
                                onChange={(e) => handleValueChange(tipo, e.target.value)}
                                placeholder="0.00"
                                className="flex-1"
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                      {overBudget && (
                        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                          <div className="text-sm text-red-800">
                            <strong>Atenção:</strong> O total desta categoria (R$ {total.toFixed(2)}) ultrapassou a meta geral (R$ {meta.toFixed(2)}) em R$ {(total - meta).toFixed(2)}.
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </AccordionContent>
                </Card>
              </AccordionItem>
            );
          })}
        </Accordion>
      )}

      <div className="flex justify-end gap-4">
        <Button
          variant="outline"
          onClick={loadBudget}
          disabled={loading || saving}
        >
          Cancelar
        </Button>
        <Button
          onClick={handleSave}
          disabled={loading || saving}
        >
          <Save className="h-4 w-4 mr-2" />
          {saving ? 'Salvando...' : 'Salvar Orçamento Detalhado'}
        </Button>
      </div>
    </div>
  );
}
