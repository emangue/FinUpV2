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
import { Calendar, Save, Copy, ArrowLeft, DollarSign } from 'lucide-react';
import { API_CONFIG } from '@/core/config/api.config';
import Link from 'next/link';

interface BudgetItem {
  tipo_gasto: string;
  mes_referencia: string;
  valor_planejado: number;
}

interface MediaHistorica {
  [tipo_gasto: string]: number;
}

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

// TipoGastos serão carregados dinamicamente da journal_entries
// Apenas os tipos que pertencem a CategoriaGeral = 'Despesa'

// Função para formatar moeda brasileira
const formatarMoeda = (valor: number): string => {
  return valor.toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

export default function BudgetSimplesPage() {
  const currentDate = new Date();
  const [selectedMonth, setSelectedMonth] = useState(String(currentDate.getMonth() + 1).padStart(2, '0'));
  const [selectedYear, setSelectedYear] = useState(String(currentDate.getFullYear()));
  const [budgetData, setBudgetData] = useState<Record<string, number>>({});
  const [mediaHistorica, setMediaHistorica] = useState<MediaHistorica>({});
  const [tiposGastoDisponiveis, setTiposGastoDisponiveis] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const mesReferencia = `${selectedYear}-${selectedMonth}`;

  const loadTiposGastoComMedia = async () => {
    try {
      const mesReferencia = `${selectedYear}-${selectedMonth}`;
      
      // Buscar tipos de gasto COM médias já calculadas do backend
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/api/v1/transactions/tipos-gasto-com-media?mes_referencia=${mesReferencia}&user_id=1`
      );

      if (!response.ok) {
        console.error('Erro ao buscar tipos de gasto:', response.status);
        setTiposGastoDisponiveis([]);
        setMediaHistorica({});
        return;
      }

      const data = await response.json();
      
      // Extrair tipos e médias
      const tipos: string[] = [];
      const medias: MediaHistorica = {};
      
      data.tipos_gasto.forEach((item: any) => {
        tipos.push(item.tipo_gasto);
        medias[item.tipo_gasto] = item.media_3_meses;
      });
      
      console.log('Tipos de gasto carregados:', tipos.length);
      console.log('Médias calculadas:', Object.keys(medias).length);
      
      setTiposGastoDisponiveis(tipos);
      setMediaHistorica(medias);
    } catch (error) {
      console.error('Erro ao carregar tipos de gasto:', error);
      setTiposGastoDisponiveis([]);
      setMediaHistorica({});
    }
  };

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
      console.error('Erro ao carregar orçamento:', error);
      setMessage({ type: 'error', text: 'Erro ao carregar dados do orçamento' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTiposGastoComMedia();
    loadBudget();
  }, [selectedMonth, selectedYear]);

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
        setMessage({ type: 'success', text: 'Orçamento salvo com sucesso!' });
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
    
    const prevMonthStr = String(prevMonth).padStart(2, '0');
    const prevMesReferencia = `${prevYear}-${prevMonthStr}`;
    
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
        setMessage({ type: 'success', text: `Valores copiados de ${meses[prevMonth - 1].label}/${prevYear}` });
        setTimeout(() => setMessage(null), 3000);
      }
    } catch (error) {
      console.error('Erro ao copiar mês anterior:', error);
      setMessage({ type: 'error', text: 'Erro ao copiar mês anterior' });
    }
  };

  const totalGeral = Object.values(budgetData).reduce((sum, val) => sum + (val || 0), 0);

  return (
    <div className="flex-1 space-y-6 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/budget" className="text-sm text-muted-foreground hover:text-primary flex items-center gap-2 mb-2">
            <ArrowLeft className="h-4 w-4" />
            Voltar para Meta Geral
          </Link>
          <h2 className="text-3xl font-bold tracking-tight">Meta por Tipo de Gasto</h2>
          <p className="text-muted-foreground mt-2">
            Defina metas individuais por tipo de gasto do sistema
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
                Escolha o mês e ano para gerenciar o orçamento
              </CardDescription>
            </div>
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
                  {[2024, 2025, 2026].map(ano => (
                    <SelectItem key={ano} value={String(ano)}>
                      {ano}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex-1">
              <Label>Total Geral</Label>
              <div className="flex items-center gap-2 h-10 px-3 py-2 border rounded-md bg-gray-50">
                <DollarSign className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-bold">
                  R$ {formatarMoeda(totalGeral)}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Carregando...</div>
      ) : tiposGastoDisponiveis.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground mb-4">Nenhum tipo de gasto encontrado para este período.</p>
          <p className="text-sm text-muted-foreground">Clique em "Carregar" para buscar os dados.</p>
        </div>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Tipos de Gasto</CardTitle>
            <CardDescription>
              Defina o valor planejado para cada tipo de gasto
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {tiposGastoDisponiveis.map(tipo => {
                const media = mediaHistorica[tipo];
                return (
                  <div key={tipo} className="space-y-2">
                    <div className="flex items-baseline justify-between">
                      <Label htmlFor={tipo} className="font-medium">
                        {tipo}
                      </Label>
                      {media && media > 0 && (
                        <span className="text-xs text-muted-foreground italic">
                          média: R$ {formatarMoeda(media)}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">R$</span>
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
                );
              })}
            </div>
          </CardContent>
        </Card>
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
          {saving ? 'Salvando...' : 'Salvar Orçamento'}
        </Button>
      </div>

      <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          💡 <strong>Dica:</strong> Para uma visão hierárquica e customizável, use a{' '}
          <Link href="/budget/detalhada" className="underline font-semibold">
            Meta Detalhada por Categorias
          </Link>
        </p>
      </div>
    </div>
  );
}
