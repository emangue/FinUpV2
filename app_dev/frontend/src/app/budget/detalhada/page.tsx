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
import { Calendar, DollarSign, Save, Copy, ArrowLeft, GripVertical, Plus, Trash2, Edit } from 'lucide-react';
import { API_CONFIG } from '@/core/config/api.config';
import Link from 'next/link';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface BudgetItem {
  tipo_gasto: string;
  mes_referencia: string;
  valor_planejado: number;
}



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

// Componente sortable para accordion item
function SortableAccordionItem({ categoria, children }: { categoria: CategoriaConfig; children: React.ReactNode }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: categoria.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div ref={setNodeRef} style={style} className="touch-none">
      <AccordionItem value={categoria.id.toString()} className="border rounded-lg">
        <Card>
          <div className="flex items-center">
            <div
              {...attributes}
              {...listeners}
              className="px-2 py-4 cursor-grab active:cursor-grabbing hover:bg-gray-50 rounded-l-lg"
            >
              <GripVertical className="h-5 w-5 text-gray-400" />
            </div>
            <div className="flex-1">
              {children}
            </div>
          </div>
        </Card>
      </AccordionItem>
    </div>
  );
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

// Função para formatar moeda brasileira
const formatarMoeda = (valor: number): string => {
  return valor.toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

export default function BudgetDetalhadaPage() {
  const currentDate = new Date();
  const [selectedMonth, setSelectedMonth] = useState(String(currentDate.getMonth() + 1).padStart(2, '0'));
  const [selectedYear, setSelectedYear] = useState(String(currentDate.getFullYear()));
  const [budgetData, setBudgetData] = useState<Record<string, number>>({});
  const [categorias, setCategorias] = useState<CategoriaConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  // Estados para gerenciamento de categorias
  const [showAddCategoryModal, setShowAddCategoryModal] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [categoryToDelete, setCategoryToDelete] = useState<CategoriaConfig | null>(null);
  const [newCategory, setNewCategory] = useState({
    nome_categoria: '',
    fonte_dados: 'GRUPO' as 'GRUPO' | 'TIPO_TRANSACAO',
    filtro_valor: '',
    cor_visualizacao: '#94a3b8',
  });

  const mesReferencia = `${selectedYear}-${selectedMonth}`;

  // Sensors para drag & drop
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Carregar dados do orçamento detalhado e categorias
  useEffect(() => {
    loadBudget();
    loadCategorias();
  }, [selectedMonth, selectedYear]);

  const loadCategorias = async () => {
    try {
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/api/v1/budget/categorias-config?apenas_ativas=true`
      );
      
      if (response.ok) {
        const result = await response.json();
        console.log('Categorias carregadas:', result.categorias?.length, result.categorias);
        setCategorias(result.categorias || []);
      }
    } catch (error) {
      console.error('Erro ao carregar categorias:', error);
    }
  };

  const loadBudget = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/api/v1/budget?mes_referencia=${mesReferencia}`
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

      const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/v1/budget/bulk-upsert`, {
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
        `${API_CONFIG.BACKEND_URL}/api/v1/budget?mes_referencia=${prevMesReferencia}`
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

  const handleAddCategory = async () => {
    if (!newCategory.nome_categoria || !newCategory.filtro_valor) {
      setMessage({ type: 'error', text: 'Preencha todos os campos obrigatórios' });
      return;
    }

    try {
      const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/v1/budget/categorias-config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newCategory,
          ordem: categorias.length + 1,
        }),
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Categoria adicionada com sucesso!' });
        setShowAddCategoryModal(false);
        setNewCategory({
          nome_categoria: '',
          fonte_dados: 'GRUPO',
          filtro_valor: '',
          cor_visualizacao: '#94a3b8',
        });
        await loadCategorias();
        setTimeout(() => setMessage(null), 3000);
      } else {
        throw new Error('Erro ao adicionar categoria');
      }
    } catch (error) {
      console.error('Erro ao adicionar categoria:', error);
      setMessage({ type: 'error', text: 'Erro ao adicionar categoria' });
    }
  };

  const handleDeleteCategory = async () => {
    if (!categoryToDelete) return;

    try {
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/api/v1/budget/categorias-config/${categoryToDelete.id}`,
        { method: 'DELETE' }
      );

      if (response.ok) {
        setMessage({ type: 'success', text: 'Categoria deletada com sucesso!' });
        setShowDeleteDialog(false);
        setCategoryToDelete(null);
        await loadCategorias();
        setTimeout(() => setMessage(null), 3000);
      } else {
        throw new Error('Erro ao deletar categoria');
      }
    } catch (error) {
      console.error('Erro ao deletar categoria:', error);
      setMessage({ type: 'error', text: 'Erro ao deletar categoria' });
    }
  };

  const getTotalPorCategoria = (categoria: CategoriaConfig): number => {
    const tiposGasto = categoria.tipos_gasto_incluidos || [];
    return tiposGasto.reduce((sum, tipo) => sum + (budgetData[tipo] || 0), 0);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    
    if (!over || active.id === over.id) return;

    const oldIndex = categorias.findIndex(c => c.id === active.id);
    const newIndex = categorias.findIndex(c => c.id === over.id);

    const reordered = arrayMove(categorias, oldIndex, newIndex);
    setCategorias(reordered);

    // Enviar reordenação para o backend
    try {
      const reorders = reordered.map((cat, index) => ({
        id: cat.id,
        nova_ordem: index + 1,
      }));

      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/api/v1/budget/categorias-config/reordenar`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ reordenar: reorders }),
        }
      );

      if (!response.ok) {
        // Reverter em caso de erro
        const oldOrder = arrayMove(reordered, newIndex, oldIndex);
        setCategorias(oldOrder);
        setMessage({ type: 'error', text: 'Erro ao reordenar categorias' });
      }
    } catch (error) {
      console.error('Erro ao reordenar:', error);
      const oldOrder = arrayMove(reordered, newIndex, oldIndex);
      setCategorias(oldOrder);
      setMessage({ type: 'error', text: 'Erro ao reordenar categorias' });
    }
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
        <Button
          onClick={() => setShowAddCategoryModal(true)}
          className="flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Nova Categoria
        </Button>
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
            <div className="flex-1">
              <Label htmlFor="total">Total Geral</Label>
              <div className="flex items-center gap-2 h-10 px-3 py-2 border rounded-md bg-gray-50">
                <span className="text-sm font-semibold">R$</span>
                <span className="text-sm font-bold">
                  {formatarMoeda((categorias?.reduce((sum, cat) => sum + getTotalPorCategoria(cat), 0) || 0))}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Carregando...</div>
      ) : (
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={categorias.map(c => c.id)}
            strategy={verticalListSortingStrategy}
          >
            <Accordion type="multiple" className="w-full space-y-4">
              {categorias.map((categoria) => {
                const total = getTotalPorCategoria(categoria);
                const tiposGasto = categoria.tipos_gasto_incluidos || [];

                return (
                  <SortableAccordionItem key={categoria.id} categoria={categoria}>
                    <div className="relative">
                      <AccordionTrigger className="px-6 py-4 hover:no-underline">
                        <div className="flex items-center justify-between w-full pr-12">
                          <div className="flex items-center gap-3">
                            <div
                              className="w-4 h-4 rounded"
                              style={{ backgroundColor: categoria.cor_visualizacao }}
                            />
                            <span className="font-semibold text-lg">{categoria.nome_categoria}</span>
                            <span className="text-xs text-muted-foreground">
                              ({categoria.fonte_dados === 'GRUPO' ? 'Grupo' : 'Tipo'}: {categoria.filtro_valor})
                            </span>
                          </div>
                          <div className="flex items-center gap-4 text-sm">
                            <div>
                              <span className="text-muted-foreground">Total: </span>
                              <span className="font-bold">
                                R$ {formatarMoeda(total)}
                              </span>
                            </div>
                          </div>
                        </div>
                      </AccordionTrigger>
                      <button
                        className="absolute right-12 top-1/2 -translate-y-1/2 h-8 w-8 rounded-md flex items-center justify-center text-red-600 hover:text-red-700 hover:bg-red-50 transition-colors z-10"
                        onClick={(e) => {
                          e.stopPropagation();
                          setCategoryToDelete(categoria);
                          setShowDeleteDialog(true);
                        }}
                        aria-label="Deletar categoria"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
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
                      </CardContent>
                    </AccordionContent>
                  </SortableAccordionItem>
                );
              })}
            </Accordion>
          </SortableContext>
        </DndContext>
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

      {/* Modal para adicionar nova categoria */}
      <Dialog open={showAddCategoryModal} onOpenChange={setShowAddCategoryModal}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Nova Categoria de Orçamento</DialogTitle>
            <DialogDescription>
              Adicione uma nova categoria para organizar seu orçamento detalhado
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="nome_categoria">Nome da Categoria *</Label>
              <Input
                id="nome_categoria"
                placeholder="Ex: Educação, Lazer, Investimentos"
                value={newCategory.nome_categoria}
                onChange={(e) => setNewCategory({ ...newCategory, nome_categoria: e.target.value })}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="fonte_dados">Fonte de Dados *</Label>
              <Select 
                value={newCategory.fonte_dados} 
                onValueChange={(value: 'GRUPO' | 'TIPO_TRANSACAO') => 
                  setNewCategory({ ...newCategory, fonte_dados: value })
                }
              >
                <SelectTrigger id="fonte_dados">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="GRUPO">Grupo (da transação)</SelectItem>
                  <SelectItem value="TIPO_TRANSACAO">Tipo de Transação</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="filtro_valor">
                {newCategory.fonte_dados === 'GRUPO' ? 'Nome do Grupo' : 'Tipo de Transação'} *
              </Label>
              <Input
                id="filtro_valor"
                placeholder={newCategory.fonte_dados === 'GRUPO' ? 'Ex: Educação' : 'Ex: PIX'}
                value={newCategory.filtro_valor}
                onChange={(e) => setNewCategory({ ...newCategory, filtro_valor: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="cor_visualizacao">Cor</Label>
              <div className="flex gap-2 items-center">
                <Input
                  id="cor_visualizacao"
                  type="color"
                  value={newCategory.cor_visualizacao}
                  onChange={(e) => setNewCategory({ ...newCategory, cor_visualizacao: e.target.value })}
                  className="w-20 h-10"
                />
                <Input
                  value={newCategory.cor_visualizacao}
                  onChange={(e) => setNewCategory({ ...newCategory, cor_visualizacao: e.target.value })}
                  placeholder="#94a3b8"
                  className="flex-1"
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddCategoryModal(false)}>
              Cancelar
            </Button>
            <Button onClick={handleAddCategory}>
              <Plus className="h-4 w-4 mr-2" />
              Adicionar Categoria
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog de confirmação para deletar */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Deletar Categoria</DialogTitle>
            <DialogDescription>
              Tem certeza que deseja deletar a categoria{' '}
              <strong className="text-foreground">{categoryToDelete?.nome_categoria}</strong>?
              <br />
              <br />
              Esta ação não pode ser desfeita. Todos os valores de orçamento associados
              a esta categoria serão mantidos no banco de dados, mas a categoria não
              aparecerá mais na lista.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2 sm:gap-0">
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancelar
            </Button>
            <Button
              onClick={handleDeleteCategory}
              className="bg-red-600 hover:bg-red-700"
            >
              Deletar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
