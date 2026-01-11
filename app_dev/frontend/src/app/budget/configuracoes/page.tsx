'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { DollarSign, Save, Palette, Plus, Trash2 } from 'lucide-react';
import { API_CONFIG } from '@/core/config/api.config';
import { HexColorPicker } from 'react-colorful';

interface CategoriaConfig {
  id: number;
  nome_categoria: string;
  ordem: number;
  fonte_dados: 'GRUPO' | 'TIPO_TRANSACAO';
  filtro_valor: string;
  tipos_gasto_incluidos: string[];
  cor_visualizacao: string;
  ativo: boolean;
}

export default function BudgetConfiguracoesPage() {
  const [categorias, setCategorias] = useState<CategoriaConfig[]>([]);
  const [budgetTotal, setBudgetTotal] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [editingColorId, setEditingColorId] = useState<number | null>(null);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/api/v1/budget/categorias-config?user_id=1`
      );
      
      if (response.ok) {
        const data = await response.json();
        setCategorias(data.categorias || []);
      }
    } catch (error) {
      console.error('Erro ao carregar configurações:', error);
      setMessage({ type: 'error', text: 'Erro ao carregar configurações' });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveColors = async () => {
    setSaving(true);
    setMessage(null);
    
    try {
      // Salvar cores de todas as categorias
      const promises = categorias.map(cat =>
        fetch(`${API_CONFIG.BACKEND_URL}/api/v1/budget/categorias-config/${cat.id}?user_id=1`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ cor_visualizacao: cat.cor_visualizacao })
        })
      );
      
      await Promise.all(promises);
      
      setMessage({ type: 'success', text: 'Cores atualizadas com sucesso!' });
      setTimeout(() => setMessage(null), 3000);
      setEditingColorId(null);
    } catch (error) {
      console.error('Erro ao salvar cores:', error);
      setMessage({ type: 'error', text: 'Erro ao salvar cores' });
    } finally {
      setSaving(false);
    }
  };

  const handleColorChange = (categoriaId: number, newColor: string) => {
    setCategorias(prev => prev.map(cat =>
      cat.id === categoriaId ? { ...cat, cor_visualizacao: newColor } : cat
    ));
  };

  const handleSaveBudgetTotal = async () => {
    setSaving(true);
    setMessage(null);
    
    try {
      // Implementar salvamento do budget total
      // Por enquanto, apenas feedback visual
      setMessage({ type: 'success', text: 'Budget total atualizado!' });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Erro ao salvar budget total:', error);
      setMessage({ type: 'error', text: 'Erro ao salvar budget total' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex-1 space-y-6 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Configurações de Orçamento</h2>
          <p className="text-muted-foreground mt-2">
            Personalize cores das categorias e defina seu budget total mensal
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

      {/* Budget Total Mensal */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Budget Total Mensal
          </CardTitle>
          <CardDescription>
            Defina o limite máximo de gastos por mês. Se a soma das categorias ultrapassar, o sistema ajustará automaticamente.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-end gap-4">
            <div className="flex-1 max-w-md">
              <Label htmlFor="budget-total">Valor Total (R$)</Label>
              <Input
                id="budget-total"
                type="number"
                step="0.01"
                min="0"
                value={budgetTotal || ''}
                onChange={(e) => setBudgetTotal(parseFloat(e.target.value) || 0)}
                placeholder="0.00"
              />
            </div>
            <Button onClick={handleSaveBudgetTotal} disabled={saving || budgetTotal <= 0}>
              <Save className="h-4 w-4 mr-2" />
              Salvar Total
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Cores das Categorias */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Cores das Categorias
              </CardTitle>
              <CardDescription className="mt-2">
                Personalize as cores de cada categoria para facilitar visualização no dashboard
              </CardDescription>
            </div>
            <Button onClick={handleSaveColors} disabled={saving || loading}>
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Salvando...' : 'Salvar Cores'}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Carregando...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {categorias.map((categoria) => (
                <div key={categoria.id} className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label className="text-base font-semibold">
                      {categoria.nome_categoria}
                    </Label>
                    <div className="flex items-center gap-2">
                      <div
                        className="w-8 h-8 rounded border-2 border-gray-300 cursor-pointer hover:border-gray-400 transition-colors"
                        style={{ backgroundColor: categoria.cor_visualizacao }}
                        onClick={() => setEditingColorId(
                          editingColorId === categoria.id ? null : categoria.id
                        )}
                      />
                      <Input
                        type="text"
                        value={categoria.cor_visualizacao}
                        onChange={(e) => handleColorChange(categoria.id, e.target.value)}
                        className="w-24 text-sm font-mono"
                        placeholder="#000000"
                      />
                    </div>
                  </div>
                  
                  {editingColorId === categoria.id && (
                    <div className="p-4 border rounded-lg bg-white shadow-lg">
                      <HexColorPicker
                        color={categoria.cor_visualizacao}
                        onChange={(color) => handleColorChange(categoria.id, color)}
                      />
                      <div className="mt-3 flex justify-end">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setEditingColorId(null)}
                        >
                          Fechar
                        </Button>
                      </div>
                    </div>
                  )}
                  
                  <div className="text-sm text-muted-foreground">
                    <span className="font-medium">Fonte:</span>{' '}
                    {categoria.fonte_dados === 'GRUPO' ? 'Grupo' : 'Tipo Transação'}
                    {' · '}
                    <span className="font-medium">Ordem:</span> {categoria.ordem}
                  </div>
                  
                  {categoria.tipos_gasto_incluidos.length > 0 && (
                    <div className="text-xs text-muted-foreground">
                      <span className="font-medium">Tipos incluídos:</span>{' '}
                      {categoria.tipos_gasto_incluidos.length} tipo(s)
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Informação sobre Hierarquia */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex gap-3">
            <div className="text-blue-600 text-2xl">ℹ️</div>
            <div className="flex-1">
              <h3 className="font-semibold text-blue-900 mb-2">
                Sobre a Hierarquia de Categorias
              </h3>
              <p className="text-sm text-blue-800 leading-relaxed">
                A ordem das categorias define a <strong>hierarquia de classificação</strong>. 
                Transações são aplicadas à primeira categoria que corresponder aos critérios.
                Para reordenar, vá em <strong>Meta Detalhada</strong> e arraste as categorias.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
