'use client';

import { useState, useEffect } from 'react';
import { fetchWithAuth } from '@/core/utils/api-client';
import { API_CONFIG } from '@/core/config/api.config';
import { Plus, Pencil, Trash2, AlertTriangle } from 'lucide-react';
import DashboardLayout from '@/components/dashboard-layout';
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface Grupo {
  id: number;
  nome_grupo: string;
  tipo_gasto_padrao: string;
  categoria_geral: string;
}

interface GrupoFormData {
  nome_grupo: string;
  tipo_gasto_padrao: string;
  categoria_geral: string;
}

export default function GestaoGrupos() {
  // URL base completa usando config centralizado
  const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/grupos`;
  
  const [grupos, setGrupos] = useState<Grupo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Opções disponíveis
  const [tiposGasto, setTiposGasto] = useState<string[]>([]);
  const [categorias, setCategorias] = useState<string[]>([]);
  
  // Modal de criar/editar
  const [modalOpen, setModalOpen] = useState(false);
  const [editingGrupo, setEditingGrupo] = useState<Grupo | null>(null);
  const [formData, setFormData] = useState<GrupoFormData>({
    nome_grupo: '',
    tipo_gasto_padrao: '',
    categoria_geral: '',
  });
  
  // Modal de confirmação de exclusão
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [grupoToDelete, setGrupoToDelete] = useState<Grupo | null>(null);

  useEffect(() => {
    loadGrupos();
    loadOpcoes();
  }, []);

  const loadGrupos = async () => {
    try {
      setLoading(true);
      const response = await fetchWithAuth(BASE_URL);
      if (!response.ok) throw new Error('Erro ao carregar grupos');
      const data = await response.json();
      setGrupos(data.grupos || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  const loadOpcoes = async () => {
    try {
      const response = await fetchWithAuth(`${BASE_URL}/opcoes`);
      if (!response.ok) throw new Error('Erro ao carregar opções');
      const data = await response.json();
      setTiposGasto(data.tipos_gasto || []);
      setCategorias(data.categorias || []);
    } catch (err) {
      console.error('Erro ao carregar opções:', err);
    }
  };

  const handleOpenModal = (grupo?: Grupo) => {
    if (grupo) {
      setEditingGrupo(grupo);
      setFormData({
        nome_grupo: grupo.nome_grupo,
        tipo_gasto_padrao: grupo.tipo_gasto_padrao,
        categoria_geral: grupo.categoria_geral,
      });
    } else {
      setEditingGrupo(null);
      setFormData({
        nome_grupo: '',
        tipo_gasto_padrao: '',
        categoria_geral: '',
      });
    }
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setEditingGrupo(null);
    setFormData({
      nome_grupo: '',
      tipo_gasto_padrao: '',
      categoria_geral: '',
    });
  };

  const handleSubmit = async () => {
    try {
      setError(null);
      setSuccess(null);

      const url = editingGrupo
        ? `${BASE_URL}/${editingGrupo.id}`
        : BASE_URL;

      const method = editingGrupo ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao salvar grupo');
      }

      setSuccess(
        editingGrupo
          ? 'Grupo atualizado com sucesso!'
          : 'Grupo criado com sucesso!'
      );
      handleCloseModal();
      loadGrupos();

      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    }
  };

  const handleDelete = async () => {
    if (!grupoToDelete) return;

    try {
      setError(null);
      setSuccess(null);

      const response = await fetch(`${apiUrl}/grupos/${grupoToDelete.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao excluir grupo');
      }

      setSuccess('Grupo excluído com sucesso!');
      setDeleteDialogOpen(false);
      setGrupoToDelete(null);
      loadGrupos();

      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
      setDeleteDialogOpen(false);
      setGrupoToDelete(null);
    }
  };

  const openDeleteDialog = (grupo: Grupo) => {
    setGrupoToDelete(grupo);
    setDeleteDialogOpen(true);
  };

  return (
    <DashboardLayout>
      <div className="container mx-auto py-8 px-4">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Gestão de Grupos</h1>
            <p className="text-muted-foreground">
              Configure grupos de despesas e receitas
            </p>
          </div>
          <Button onClick={() => handleOpenModal()}>
            <Plus className="mr-2 h-4 w-4" />
            Novo Grupo
          </Button>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6 bg-green-50 text-green-900 border-green-200">
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        {loading ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Carregando...</p>
          </div>
        ) : (
          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome do Grupo</TableHead>
                  <TableHead>Tipo de Gasto</TableHead>
                  <TableHead>Categoria Geral</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {grupos.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">
                      Nenhum grupo cadastrado
                    </TableCell>
                  </TableRow>
                ) : (
                  grupos.map((grupo) => (
                    <TableRow key={grupo.id}>
                      <TableCell className="font-medium">{grupo.nome_grupo}</TableCell>
                      <TableCell>{grupo.tipo_gasto_padrao}</TableCell>
                      <TableCell>
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            grupo.categoria_geral === 'Despesa'
                              ? 'bg-red-100 text-red-800'
                              : grupo.categoria_geral === 'Receita'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-blue-100 text-blue-800'
                          }`}
                        >
                          {grupo.categoria_geral}
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleOpenModal(grupo)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => openDeleteDialog(grupo)}
                        >
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        )}

        {/* Modal de Criar/Editar */}
        <Dialog open={modalOpen} onOpenChange={setModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingGrupo ? 'Editar Grupo' : 'Novo Grupo'}
              </DialogTitle>
              <DialogDescription>
                {editingGrupo
                  ? 'Altere os dados do grupo'
                  : 'Preencha os dados do novo grupo'}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="nome_grupo">Nome do Grupo</Label>
                <Input
                  id="nome_grupo"
                  value={formData.nome_grupo}
                  onChange={(e) =>
                    setFormData({ ...formData, nome_grupo: e.target.value })
                  }
                  placeholder="Ex: Alimentação, Transporte..."
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="tipo_gasto_padrao">Tipo de Gasto</Label>
                <Select
                  value={formData.tipo_gasto_padrao}
                  onValueChange={(value) =>
                    setFormData({ ...formData, tipo_gasto_padrao: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione..." />
                  </SelectTrigger>
                  <SelectContent>
                    {tiposGasto.map((tipo) => (
                      <SelectItem key={tipo} value={tipo}>
                        {tipo}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="categoria_geral">Categoria Geral</Label>
                <Select
                  value={formData.categoria_geral}
                  onValueChange={(value) =>
                    setFormData({ ...formData, categoria_geral: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione..." />
                  </SelectTrigger>
                  <SelectContent>
                    {categorias.map((categoria) => (
                      <SelectItem key={categoria} value={categoria}>
                        {categoria}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={handleCloseModal}>
                Cancelar
              </Button>
              <Button onClick={handleSubmit}>
                {editingGrupo ? 'Salvar' : 'Criar'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Dialog de Confirmação de Exclusão */}
        <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Confirmar Exclusão</AlertDialogTitle>
              <AlertDialogDescription>
                Tem certeza que deseja excluir o grupo &quot;{grupoToDelete?.nome_grupo}&quot;?
                <br />
                <br />
                <strong>Atenção:</strong> Não será possível excluir se houver transações associadas a este grupo.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancelar</AlertDialogCancel>
              <AlertDialogAction
                onClick={handleDelete}
                className="bg-red-600 hover:bg-red-700"
              >
                Excluir
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </DashboardLayout>
  );
}