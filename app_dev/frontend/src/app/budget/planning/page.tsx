"use client"

import { useState, useEffect } from "react"
import { 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  FileText,
  Filter
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

import { API_CONFIG } from "@/core/config/api.config"

interface BudgetPlanningItem {
  id: number;
  user_id: number;
  grupo: string;
  mes_referencia: string;
  valor_planejado: number;
  valor_medio_3_meses: number;
}

export default function BudgetPlanningPage() {
  const currentDate = new Date();
  
  // States - Planejamento
  const [planningData, setPlanningData] = useState<BudgetPlanningItem[]>([]);
  const [loadingPlanning, setLoadingPlanning] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState(String(currentDate.getMonth() + 1).padStart(2, '0'));
  const [selectedYear, setSelectedYear] = useState(String(currentDate.getFullYear()));
  const [grupoFilter, setGrupoFilter] = useState('');
  
  // Dialogs States
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [currentItem, setCurrentItem] = useState<Partial<BudgetPlanningItem>>({});
  
  // UI Feedback
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  // New Item State
  const [newItem, setNewItem] = useState({
    grupo: '',
    valor_planejado: ''
  });

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

  useEffect(() => {
    loadPlanningData();
  }, [selectedMonth, selectedYear]);

  const loadPlanningData = async () => {
    setLoadingPlanning(true);
    const mesReferencia = `${selectedYear}-${selectedMonth}`;
    try {
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/api/v1/budget?mes_referencia=${mesReferencia}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setPlanningData(data.budgets || []);
      } else {
        setPlanningData([]);
      }
    } catch (error) {
      console.error('Erro ao carregar planejamento:', error);
      setMessage({ type: 'error', text: 'Erro ao carregar dados de planejamento' });
    } finally {
      setLoadingPlanning(false);
    }
  };

  const formatarMoeda = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  };

  // --- Handlers - CRUD ---

  const handleAddItem = async () => {
    if (!newItem.grupo || !newItem.valor_planejado) return;

    setSaving(true);
    try {
      const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/v1/budget`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          grupo: newItem.grupo,
          mes_referencia: `${selectedYear}-${selectedMonth}`,
          valor_planejado: parseFloat(newItem.valor_planejado),
          valor_medio_3_meses: 0
        }),
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Item adicionado com sucesso' });
        setIsAddDialogOpen(false);
        setNewItem({ grupo: '', valor_planejado: '' });
        loadPlanningData();
        setTimeout(() => setMessage(null), 3000);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Falha ao adicionar');
      }
    } catch (error: any) {
      console.error('Erro ao adicionar item:', error);
      setMessage({ type: 'error', text: error.message || 'Erro ao adicionar item' });
    } finally {
      setSaving(false);
    }
  };

  const handleEditItem = async () => {
    if (!currentItem.id || !currentItem.grupo || currentItem.valor_planejado === undefined) return;

    setSaving(true);
    try {
      const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/v1/budget/${currentItem.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          grupo: currentItem.grupo,
          mes_referencia: currentItem.mes_referencia,
          valor_planejado: Number(currentItem.valor_planejado)
        }),
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Item atualizado com sucesso' });
        setIsEditDialogOpen(false);
        setCurrentItem({});
        loadPlanningData();
        setTimeout(() => setMessage(null), 3000);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Falha ao atualizar');
      }
    } catch (error: any) {
      console.error('Erro ao atualizar item:', error);
      setMessage({ type: 'error', text: error.message || 'Erro ao atualizar item' });
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteItem = async () => {
    if (!currentItem.id) return;

    setSaving(true);
    try {
      const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/v1/budget/${currentItem.id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Item removido com sucesso' });
        setIsDeleteDialogOpen(false);
        setCurrentItem({});
        loadPlanningData();
        setTimeout(() => setMessage(null), 3000);
      } else {
        throw new Error('Falha ao remover');
      }
    } catch (error) {
      console.error('Erro ao remover item:', error);
      setMessage({ type: 'error', text: 'Erro ao remover item' });
    } finally {
      setSaving(false);
    }
  };

  // Filtered Data
  const filteredPlanningData = planningData.filter(item => 
    grupoFilter ? item.grupo.toLowerCase().includes(grupoFilter.toLowerCase()) : true
  );

  return (
    <div className="flex-1 space-y-6 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Planejamento</h2>
          <p className="text-muted-foreground mt-2">
            Gerencie os valores de orçamento para cada grupo (Base: budget_planning)
          </p>
        </div>
        <Button onClick={() => setIsAddDialogOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nova Linha
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
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex gap-4 items-end">
                <div className="w-[180px]">
                    <Label className="mb-2 block text-xs font-medium text-gray-500">Mês</Label>
                    <Select value={selectedMonth} onValueChange={setSelectedMonth}>
                    <SelectTrigger>
                        <SelectValue placeholder="Mês" />
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
                <div className="w-[120px]">
                    <Label className="mb-2 block text-xs font-medium text-gray-500">Ano</Label>
                    <Select value={selectedYear} onValueChange={setSelectedYear}>
                    <SelectTrigger>
                        <SelectValue placeholder="Ano" />
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
            
            <div className="flex-1 max-w-sm">
                <Label className="mb-2 block text-xs font-medium text-gray-500">Buscar Grupo</Label>
                <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="Filtrar por grupo..."
                    className="pl-8"
                    value={grupoFilter}
                    onChange={(e) => setGrupoFilter(e.target.value)}
                />
                </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="border rounded-md">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Mês Ref.</TableHead>
                  <TableHead>Grupo</TableHead>
                  <TableHead>Valor Planejado</TableHead>
                  <TableHead>Média 3 Meses</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loadingPlanning ? (
                    <TableRow>
                        <TableCell colSpan={5} className="text-center h-24 text-muted-foreground">
                            Carregando dados...
                        </TableCell>
                    </TableRow>
                ) : filteredPlanningData.length === 0 ? (
                    <TableRow>
                        <TableCell colSpan={5} className="text-center h-24 text-muted-foreground">
                            Nenhum registro encontrado para {selectedMonth}/{selectedYear}.
                        </TableCell>
                    </TableRow>
                ) : (
                    filteredPlanningData.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.mes_referencia}</TableCell>
                    <TableCell className="font-medium">{item.grupo}</TableCell>
                    <TableCell>R$ {formatarMoeda(item.valor_planejado)}</TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                        {item.valor_medio_3_meses ? `R$ ${formatarMoeda(item.valor_medio_3_meses)}` : '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => {
                                setCurrentItem(item);
                                setIsEditDialogOpen(true);
                            }}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                            variant="ghost" 
                            size="sm" 
                            className="text-red-500 hover:text-red-600 hover:bg-red-50"
                            onClick={() => {
                                setCurrentItem(item);
                                setIsDeleteDialogOpen(true);
                            }}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )))}
              </TableBody>
            </Table>
          </div>
          <div className="mt-4 text-xs text-muted-foreground flex justify-between">
            <span>Total de registros: {filteredPlanningData.length}</span>
            <span>Soma Total: {formatarMoeda(filteredPlanningData.reduce((acc, item) => acc + item.valor_planejado, 0))}</span>
          </div>
        </CardContent>
      </Card>

      {/* Dialog: Adicionar Item */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nova Linha de Orçamento</DialogTitle>
            <DialogDescription>
              Adicionar valor manualmente à tabela budget_planning.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Mês de Referência</Label>
              <Input disabled value={`${selectedYear}-${selectedMonth}`} />
              <p className="text-[10px] text-muted-foreground">Definido pelo filtro da página</p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-grupo">Nome do Grupo</Label>
              <Input 
                id="new-grupo"
                placeholder="Ex: Farmácia, Mercado"
                value={newItem.grupo}
                onChange={(e) => setNewItem({...newItem, grupo: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-valor">Valor Planejado (R$)</Label>
              <Input 
                id="new-valor"
                type="number"
                step="0.01"
                placeholder="0.00"
                value={newItem.valor_planejado}
                onChange={(e) => setNewItem({...newItem, valor_planejado: e.target.value})}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>Cancelar</Button>
            <Button onClick={handleAddItem} disabled={saving}>Salvar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog: Editar Item */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar Orçamento</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Mês de Referência</Label>
              <Input disabled value={currentItem.mes_referencia} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-grupo">Nome do Grupo</Label>
              <Input 
                id="edit-grupo"
                value={currentItem.grupo || ''}
                onChange={(e) => setCurrentItem({...currentItem, grupo: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-valor">Valor Planejado (R$)</Label>
              <Input 
                id="edit-valor"
                type="number"
                step="0.01"
                value={currentItem.valor_planejado}
                onChange={(e) => setCurrentItem({...currentItem, valor_planejado: parseFloat(e.target.value)})}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>Cancelar</Button>
            <Button onClick={handleEditItem} disabled={saving}>Salvar Alterações</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog: Deletar Item */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmar Exclusão</DialogTitle>
            <DialogDescription>
              Tem certeza que deseja excluir o orçamento para o grupo <strong>{currentItem.grupo}</strong>?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>Cancelar</Button>
            <Button variant="destructive" onClick={handleDeleteItem} disabled={saving}>Excluir</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

    </div>
  );
}
