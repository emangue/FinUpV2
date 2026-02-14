'use client';

import { useState, useEffect } from 'react';
import { fetchWithAuth } from '@/core/utils/api-client';
import { API_CONFIG } from '@/core/config/api.config';
import { Plus, FolderPlus, Trash2, AlertTriangle, ChevronDown, ChevronRight } from 'lucide-react';
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
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface GrupoComSubgrupos {
  grupo: string;
  subgrupos: string[];
  total_subgrupos: number;
}

interface GrupoFormData {
  grupo: string;
  subgrupo: string;
  tipo_gasto: string;
  categoria_geral: string;
}

interface SubgrupoFormData {
  subgrupo: string;
}

export default function GestaoMarcacoes() {
  const MARCACOES_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/marcacoes`;
  const GRUPOS_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/grupos`;
  
  const [grupos, setGrupos] = useState<GrupoComSubgrupos[]>([]);
  const [expandedGrupos, setExpandedGrupos] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Modal de criar grupo + subgrupo
  const [grupoModalOpen, setGrupoModalOpen] = useState(false);
  const [grupoFormData, setGrupoFormData] = useState<GrupoFormData>({
    grupo: '',
    subgrupo: '',
    tipo_gasto: 'Ajustável',
    categoria_geral: 'Despesa',
  });
  
  // Modal de adicionar subgrupo
  const [subgrupoModalOpen, setSubgrupoModalOpen] = useState(false);
  const [selectedGrupo, setSelectedGrupo] = useState<string>('');
  const [subgrupoFormData, setSubgrupoFormData] = useState<SubgrupoFormData>({
    subgrupo: '',
  });
  
  // Modal de confirmação de exclusão
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ grupo: string; subgrupo: string } | null>(null);

  useEffect(() => {
    loadGruposComSubgrupos();
  }, []);

  const loadGruposComSubgrupos = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetchWithAuth(`${MARCACOES_URL}/grupos-com-subgrupos`);
      if (!response.ok) throw new Error('Erro ao carregar grupos');
      const data = await response.json();
      setGrupos(data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  const toggleGrupoExpansion = (grupo: string) => {
    const newExpanded = new Set(expandedGrupos);
    if (newExpanded.has(grupo)) {
      newExpanded.delete(grupo);
    } else {
      newExpanded.add(grupo);
    }
    setExpandedGrupos(newExpanded);
  };

  const handleCreateGrupo = async () => {
    try {
      setError(null);
      setSuccess(null);

      const response = await fetchWithAuth(`${MARCACOES_URL}/grupos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(grupoFormData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao criar grupo');
      }

      const result = await response.json();
      setSuccess(result.message || 'Grupo criado com sucesso!');
      setGrupoModalOpen(false);
      setGrupoFormData({
        grupo: '',
        subgrupo: '',
        tipo_gasto: 'Ajustável',
        categoria_geral: 'Despesa',
      });
      loadGruposComSubgrupos();

      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    }
  };

  const handleAddSubgrupo = async () => {
    try {
      setError(null);
      setSuccess(null);

      const encodedGrupo = encodeURIComponent(selectedGrupo);
      const response = await fetchWithAuth(
        `${MARCACOES_URL}/grupos/${encodedGrupo}/subgrupos`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(subgrupoFormData),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao adicionar subgrupo');
      }

      const result = await response.json();
      setSuccess(result.message || 'Subgrupo adicionado com sucesso!');
      setSubgrupoModalOpen(false);
      setSubgrupoFormData({ subgrupo: '' });
      loadGruposComSubgrupos();

      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    }
  };

  const handleDeleteSubgrupo = async () => {
    if (!deleteTarget) return;

    try {
      setError(null);
      setSuccess(null);

      const encodedGrupo = encodeURIComponent(deleteTarget.grupo);
      const encodedSubgrupo = encodeURIComponent(deleteTarget.subgrupo);
      
      const response = await fetchWithAuth(
        `${MARCACOES_URL}/grupos/${encodedGrupo}/subgrupos/${encodedSubgrupo}`,
        {
          method: 'DELETE',
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao excluir subgrupo');
      }

      const result = await response.json();
      setSuccess(result.message || 'Subgrupo excluído com sucesso!');
      setDeleteDialogOpen(false);
      setDeleteTarget(null);
      loadGruposComSubgrupos();

      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
      setDeleteDialogOpen(false);
      setDeleteTarget(null);
    }
  };

  const openAddSubgrupoModal = (grupo: string) => {
    setSelectedGrupo(grupo);
    setSubgrupoFormData({ subgrupo: '' });
    setSubgrupoModalOpen(true);
  };

  const openDeleteDialog = (grupo: string, subgrupo: string) => {
    setDeleteTarget({ grupo, subgrupo });
    setDeleteDialogOpen(true);
  };

  return (
    <DashboardLayout>
      <div className="container mx-auto py-8 px-4">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Gestão de Marcações</h1>
            <p className="text-muted-foreground">
              Gerencie grupos e subgrupos para classificação de transações
            </p>
          </div>
          <Button onClick={() => setGrupoModalOpen(true)}>
            <FolderPlus className="mr-2 h-4 w-4" />
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
        ) : grupos.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">Nenhum grupo cadastrado</p>
              <Button
                variant="outline"
                className="mt-4"
                onClick={() => setGrupoModalOpen(true)}
              >
                Criar Primeiro Grupo
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {grupos.map((grupo) => (
              <Card key={grupo.grupo}>
                <CardHeader className="cursor-pointer hover:bg-accent/50 transition-colors"
                  onClick={() => toggleGrupoExpansion(grupo.grupo)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {expandedGrupos.has(grupo.grupo) ? (
                        <ChevronDown className="h-5 w-5 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="h-5 w-5 text-muted-foreground" />
                      )}
                      <div>
                        <CardTitle className="text-lg">{grupo.grupo}</CardTitle>
                        <CardDescription>
                          {grupo.total_subgrupos} subgrupo{grupo.total_subgrupos !== 1 ? 's' : ''}
                        </CardDescription>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        openAddSubgrupoModal(grupo.grupo);
                      }}
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Subgrupo
                    </Button>
                  </div>
                </CardHeader>

                {expandedGrupos.has(grupo.grupo) && (
                  <CardContent>
                    <div className="space-y-2">
                      {grupo.subgrupos.map((subgrupo) => (
                        <div
                          key={subgrupo}
                          className="flex items-center justify-between p-3 border rounded-md hover:bg-accent/30 transition-colors"
                        >
                          <span className="text-sm">{subgrupo}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openDeleteDialog(grupo.grupo, subgrupo)}
                          >
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        )}

        {/* Modal de Criar Grupo + Subgrupo */}
        <Dialog open={grupoModalOpen} onOpenChange={setGrupoModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Novo Grupo</DialogTitle>
              <DialogDescription>
                Crie um grupo e seu primeiro subgrupo. O grupo será criado em base_grupos_config
                e o subgrupo em base_marcacoes.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="grupo">Nome do Grupo *</Label>
                <Input
                  id="grupo"
                  value={grupoFormData.grupo}
                  onChange={(e) =>
                    setGrupoFormData({ ...grupoFormData, grupo: e.target.value })
                  }
                  placeholder="Ex: Alimentação, Transporte..."
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="subgrupo">Primeiro Subgrupo *</Label>
                <Input
                  id="subgrupo"
                  value={grupoFormData.subgrupo}
                  onChange={(e) =>
                    setGrupoFormData({ ...grupoFormData, subgrupo: e.target.value })
                  }
                  placeholder="Ex: Supermercado, Combustível..."
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="tipo_gasto">Tipo de Gasto *</Label>
                <Select
                  value={grupoFormData.tipo_gasto}
                  onValueChange={(value) =>
                    setGrupoFormData({ ...grupoFormData, tipo_gasto: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Fixo">Fixo</SelectItem>
                    <SelectItem value="Ajustável">Ajustável</SelectItem>
                    <SelectItem value="Eventual">Eventual</SelectItem>
                    <SelectItem value="Investimentos">Investimentos</SelectItem>
                    <SelectItem value="Transferência">Transferência</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="categoria_geral">Categoria Geral *</Label>
                <Select
                  value={grupoFormData.categoria_geral}
                  onValueChange={(value) =>
                    setGrupoFormData({ ...grupoFormData, categoria_geral: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Despesa">Despesa</SelectItem>
                    <SelectItem value="Receita">Receita</SelectItem>
                    <SelectItem value="Investimentos">Investimentos</SelectItem>
                    <SelectItem value="Transferência Entre Contas">
                      Transferência Entre Contas
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setGrupoModalOpen(false);
                  setGrupoFormData({
                    grupo: '',
                    subgrupo: '',
                    tipo_gasto: 'Ajustável',
                    categoria_geral: 'Despesa',
                  });
                }}
              >
                Cancelar
              </Button>
              <Button onClick={handleCreateGrupo}>Criar</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Modal de Adicionar Subgrupo */}
        <Dialog open={subgrupoModalOpen} onOpenChange={setSubgrupoModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Adicionar Subgrupo</DialogTitle>
              <DialogDescription>
                Adicione um subgrupo ao grupo &quot;{selectedGrupo}&quot;.
                <br />
                O subgrupo herdará o tipo de gasto e categoria do grupo automaticamente.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="new_subgrupo">Nome do Subgrupo *</Label>
                <Input
                  id="new_subgrupo"
                  value={subgrupoFormData.subgrupo}
                  onChange={(e) =>
                    setSubgrupoFormData({ subgrupo: e.target.value })
                  }
                  placeholder="Ex: Delivery, Jantar Fora..."
                />
              </div>
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setSubgrupoModalOpen(false);
                  setSubgrupoFormData({ subgrupo: '' });
                }}
              >
                Cancelar
              </Button>
              <Button onClick={handleAddSubgrupo}>Adicionar</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Dialog de Confirmação de Exclusão */}
        <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Confirmar Exclusão</AlertDialogTitle>
              <AlertDialogDescription>
                Tem certeza que deseja excluir o subgrupo &quot;{deleteTarget?.subgrupo}&quot;
                do grupo &quot;{deleteTarget?.grupo}&quot;?
                <br />
                <br />
                <strong>Atenção:</strong> Não será possível excluir se houver transações
                associadas a este subgrupo.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancelar</AlertDialogCancel>
              <AlertDialogAction
                onClick={handleDeleteSubgrupo}
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
