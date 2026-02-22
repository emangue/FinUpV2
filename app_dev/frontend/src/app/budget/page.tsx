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
import { Calendar, DollarSign, Save, Copy, FileText } from 'lucide-react';
import { API_CONFIG } from '@/core/config/api.config';
import Link from 'next/link';

interface BudgetItem {
  grupo: string;
  mes_referencia: string;
  valor_planejado: number;
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

export default function BudgetPage() {
  const currentDate = new Date();
  const [selectedMonth, setSelectedMonth] = useState(String(currentDate.getMonth() + 1).padStart(2, '0'));
  const [selectedYear, setSelectedYear] = useState(String(currentDate.getFullYear()));
  const [budgetData, setBudgetData] = useState<Record<string, number>>({});
  const [categoriasGerais, setCategoriasGerais] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const mesReferencia = `${selectedYear}-${selectedMonth}`;

  // Carregar grupos disponíveis
  useEffect(() => {
    loadGruposDisponiveis();
  }, []);

  // Carregar dados do orçamento quando mudar mês/ano
  useEffect(() => {
    if (categoriasGerais.length > 0) {
      loadBudget();
    }
  }, [selectedMonth, selectedYear]);

  const loadGruposDisponiveis = async () => {
    try {
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/api/v1/budget/planning/grupos-disponiveis`
      );
      
      if (response.ok) {
        const grupos = await response.json();
        console.log('Grupos carregados da API:', grupos.length, grupos);
        setCategoriasGerais(grupos);
        // Carregar budget logo após receber grupos
        if (grupos.length > 0) {
          await loadBudgetWithGroups(grupos);
        }
      }
    } catch (error) {
      console.error('Erro ao carregar grupos disponíveis:', error);
      // Fallback para lista mínima
      const fallbackGrupos = ['Casa', 'Viagens', 'Saúde', 'Alimentação', 'Outros'];
      setCategoriasGerais(fallbackGrupos);
      await loadBudgetWithGroups(fallbackGrupos);
    }
  };

  const loadBudgetWithGroups = async (grupos: string[]) => {
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/api/v1/budget/planning?mes_referencia=${mesReferencia}`
      );
      
      if (response.ok) {
        const result = await response.json();
        const data = result.budgets || [];
        const budgetMap: Record<string, number> = {};
        
        // Inicializar TODOS os grupos com 0
        grupos.forEach(grupo => {
          budgetMap[grupo] = 0;
        });
        
        // Sobrescrever com valores do banco
        data.forEach((item: BudgetItem) => {
          budgetMap[item.grupo] = item.valor_planejado;
        });
        
        console.log('Budget carregado:', Object.keys(budgetMap).length, 'grupos');
        setBudgetData(budgetMap);
      } else {
        // Se não houver dados, inicializar com zeros para todos os grupos
        const budgetMap: Record<string, number> = {};
        grupos.forEach(grupo => {
          budgetMap[grupo] = 0;
        });
        setBudgetData(budgetMap);
      }
    } catch (error) {
      console.error('Erro ao carregar orçamento:', error);
      setMessage({ type: 'error', text: 'Erro ao carregar dados do orçamento' });
    } finally {
      setLoading(false);
    }
  };

  const loadBudget = async () => {
    if (categoriasGerais.length === 0) return;
    await loadBudgetWithGroups(categoriasGerais);
  };

  const handleValueChange = (categoria: string, value: string) => {
    const numValue = parseFloat(value) || 0;
    setBudgetData(prev => ({
      ...prev,
      [categoria]: numValue,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const items = Object.entries(budgetData)
        .map(([grupo, valor_planejado]) => ({
          grupo,
          valor_planejado,
        }));

      const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/v1/budget/planning/bulk-upsert`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mes_referencia: mesReferencia, budgets: items }),
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Orçamento geral salvo com sucesso!' });
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
        `${API_CONFIG.BACKEND_URL}/api/v1/budget/planning?mes_referencia=${prevMesReferencia}`
      );
      
      if (response.ok) {
        const result = await response.json();
        const data = result.budgets || [];
        const budgetMap: Record<string, number> = {};
        data.forEach((item: BudgetItem) => {
          budgetMap[item.grupo] = item.valor_planejado;
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

  const totalPlanejado = Object.values(budgetData).reduce((sum, val) => sum + val, 0);

  return (
    <div className="flex-1 space-y-6 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Meta Geral de Orçamento</h2>
          <p className="text-muted-foreground mt-2">
            Defina metas gerais por categoria ampla
          </p>
        </div>
      </div>

      {/* Cards de Acesso Rápido */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="hover:border-primary transition-colors cursor-pointer" onClick={() => window.location.href = '/budget/simples'}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Meta por Tipo de Gasto
            </CardTitle>
            <CardDescription>
              Defina orçamento para tipos de gasto específicos (Fixo, Ajustável, etc)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full" asChild>
              <Link href="/budget/simples">Acessar Meta Simples →</Link>
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:border-primary transition-colors cursor-pointer" onClick={() => window.location.href = '/budget/detalhada'}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Meta por Categorias
            </CardTitle>
            <CardDescription>
              Organize por categorias customizáveis com hierarquia (Casa, Cartão, etc)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full" asChild>
              <Link href="/budget/detalhada">Acessar Meta Detalhada →</Link>
            </Button>
          </CardContent>
        </Card>
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
                Escolha o mês e ano para gerenciar o orçamento geral
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
              <Link href="/budget/detalhada">
                <Button variant="outline" size="sm">
                  <FileText className="h-4 w-4 mr-2" />
                  Ver Detalhamento
                </Button>
              </Link>
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

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Metas por Categoria Geral
          </CardTitle>
          <CardDescription>
            Total Planejado: <span className="font-bold text-lg">R$ {totalPlanejado.toFixed(2)}</span>
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Carregando...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {categoriasGerais.map(categoria => (
                <div key={categoria} className="space-y-2">
                  <Label htmlFor={categoria}>{categoria}</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">R$</span>
                    <Input
                      id={categoria}
                      type="number"
                      step="0.01"
                      min="0"
                      value={budgetData[categoria] || ''}
                      onChange={(e) => handleValueChange(categoria, e.target.value)}
                      placeholder="0.00"
                      className="flex-1"
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

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
          disabled={loading || saving || totalPlanejado === 0}
        >
          <Save className="h-4 w-4 mr-2" />
          {saving ? 'Salvando...' : 'Salvar Orçamento'}
        </Button>
      </div>
    </div>
  );
}
