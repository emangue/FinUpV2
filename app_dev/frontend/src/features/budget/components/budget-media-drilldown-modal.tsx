'use client';

import React, { useState, useEffect } from 'react';
import { fetchWithAuth } from '@/core/utils/api-client';  // ✅ FASE 3 - Autenticação obrigatória
import { useRouter } from 'next/navigation';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { ArrowRight, ChevronRight, ChevronDown, ListIcon } from 'lucide-react';
import { API_CONFIG } from '@/core/config/api.config';
import { Badge } from '@/components/ui/badge';

interface SubgrupoDetalhamento {
  subgrupo: string | null;
  valor_total: number;
  quantidade_transacoes: number;
}

interface MesDetalhamento {
  mes_referencia: string;
  mes_nome: string;
  valor_total: number;
  quantidade_transacoes: number;
  subgrupos?: SubgrupoDetalhamento[];
}

interface DetalhamentoMedia {
  grupo: string;
  mes_planejado: string;
  meses_considerados: MesDetalhamento[];
  media_calculada: number;
  total_geral: number;
}

interface BudgetMediaDrilldownModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  tipoGasto: string | null;
  mesReferencia: string | null;
}

const formatarMoeda = (valor: number): string => {
  return valor.toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

// Modal de todos os subgrupos
function TodosSubgruposModal({ 
  open, 
  onOpenChange, 
  mes, 
  subgrupos 
}: { 
  open: boolean; 
  onOpenChange: (open: boolean) => void; 
  mes: MesDetalhamento | null;
  subgrupos: SubgrupoDetalhamento[];
}) {
  if (!mes) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Todos os Subgrupos - {mes.mes_nome}</DialogTitle>
          <DialogDescription>
            Detalhamento completo de todos os subgrupos deste mês
          </DialogDescription>
        </DialogHeader>

        <div className="max-h-96 overflow-y-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Subgrupo</TableHead>
                <TableHead className="text-right">Valor</TableHead>
                <TableHead className="text-right">Transações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {subgrupos.map((sub, idx) => (
                <TableRow key={idx}>
                  <TableCell className="font-medium">
                    {sub.subgrupo || <span className="italic text-muted-foreground">Sem subgrupo</span>}
                  </TableCell>
                  <TableCell className="text-right font-semibold">
                    R$ {formatarMoeda(sub.valor_total)}
                  </TableCell>
                  <TableCell className="text-right">
                    {sub.quantidade_transacoes}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Fechar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export function BudgetMediaDrilldownModal({
  open,
  onOpenChange,
  tipoGasto,
  mesReferencia,
}: BudgetMediaDrilldownModalProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [detalhamento, setDetalhamento] = useState<DetalhamentoMedia | null>(null);
  const [expandedMeses, setExpandedMeses] = useState<Set<string>>(new Set());
  const [modalDemaisOpen, setModalDemaisOpen] = useState(false);
  const [mesModalDemais, setMesModalDemais] = useState<MesDetalhamento | null>(null);

  useEffect(() => {
    if (open && tipoGasto && mesReferencia) {
      loadDetalhamento();
    }
  }, [open, tipoGasto, mesReferencia]);

  const loadDetalhamento = async () => {
    if (!tipoGasto || !mesReferencia) return;

    setLoading(true);
    try {
      const params = new URLSearchParams({
        grupo: tipoGasto,
        mes_referencia: mesReferencia,
      });

      const response = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}/api/v1/budget/detalhamento-media?${params.toString()}`
      );

      if (response.ok) {
        const data = await response.json();
        setDetalhamento(data);
      } else {
        console.error('Erro ao carregar detalhamento');
      }
    } catch (error) {
      console.error('Erro ao carregar detalhamento:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVerTransacoesMes = (mesRef: string) => {
    const params = new URLSearchParams({
      grupo: tipoGasto || '',
      mes_referencia: mesRef,
    });
    
    router.push(`/transactions?${params.toString()}`);
    onOpenChange(false);
  };

  const toggleMesExpansion = (mesRef: string) => {
    const newExpanded = new Set(expandedMeses);
    if (newExpanded.has(mesRef)) {
      newExpanded.delete(mesRef);
    } else {
      newExpanded.add(mesRef);
    }
    setExpandedMeses(newExpanded);
  };

  const handleVerTodosSubgrupos = (mes: MesDetalhamento) => {
    setMesModalDemais(mes);
    setModalDemaisOpen(true);
  };

  const getTop3Demais = (subgrupos: SubgrupoDetalhamento[]) => {
    const top3 = subgrupos.slice(0, 3);
    const demais = subgrupos.slice(3);
    
    if (demais.length > 0) {
      const demaisAgregado: SubgrupoDetalhamento = {
        subgrupo: null, // Usar null como flag para "Demais"
        valor_total: demais.reduce((sum, s) => sum + s.valor_total, 0),
        quantidade_transacoes: demais.reduce((sum, s) => sum + s.quantidade_transacoes, 0)
      };
      return { top3, demaisAgregado, totalDemais: demais.length };
    }
    
    return { top3, demaisAgregado: null, totalDemais: 0 };
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Detalhamento da Média - {tipoGasto}</DialogTitle>
            <DialogDescription>
              Veja o detalhamento dos últimos 3 meses que compõem a média calculada para este grupo
            </DialogDescription>
          </DialogHeader>

          {loading ? (
            <div className="py-8 text-center text-muted-foreground">
              Carregando detalhamento...
            </div>
          ) : detalhamento ? (
            <div className="space-y-4">
              <Card>
                <CardContent className="pt-6">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-12"></TableHead>
                        <TableHead>Mês</TableHead>
                        <TableHead className="text-right">Valor Total</TableHead>
                        <TableHead className="text-right">Transações</TableHead>
                        <TableHead className="text-right">Ações</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {detalhamento.meses_considerados.map((mes) => {
                        const isExpanded = expandedMeses.has(mes.mes_referencia);
                        const temSubgrupos = mes.subgrupos && mes.subgrupos.length > 0;
                        const { top3, demaisAgregado, totalDemais } = temSubgrupos 
                          ? getTop3Demais(mes.subgrupos!) 
                          : { top3: [], demaisAgregado: null, totalDemais: 0 };

                        return (
                          <React.Fragment key={mes.mes_referencia}>
                            <TableRow>
                              <TableCell>
                                {temSubgrupos && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-6 w-6 p-0"
                                    onClick={() => toggleMesExpansion(mes.mes_referencia)}
                                  >
                                    {isExpanded ? (
                                      <ChevronDown className="h-4 w-4" />
                                    ) : (
                                      <ChevronRight className="h-4 w-4" />
                                    )}
                                  </Button>
                                )}
                              </TableCell>
                              <TableCell className="font-medium">{mes.mes_nome}</TableCell>
                              <TableCell className="text-right">
                                {mes.quantidade_transacoes > 0 ? (
                                  <span className="font-semibold">
                                    R$ {formatarMoeda(mes.valor_total)}
                                  </span>
                                ) : (
                                  <span className="text-muted-foreground italic">
                                    Sem transações
                                  </span>
                                )}
                              </TableCell>
                              <TableCell className="text-right">
                                {mes.quantidade_transacoes > 0 ? (
                                  <span>{mes.quantidade_transacoes}</span>
                                ) : (
                                  <span className="text-muted-foreground">-</span>
                                )}
                              </TableCell>
                              <TableCell className="text-right">
                                {mes.quantidade_transacoes > 0 && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleVerTransacoesMes(mes.mes_referencia)}
                                    className="gap-2"
                                  >
                                    Ver Transações
                                    <ArrowRight className="h-4 w-4" />
                                  </Button>
                                )}
                              </TableCell>
                            </TableRow>
                            
                            {/* Subgrupos expandidos */}
                            {isExpanded && temSubgrupos && (
                              <>
                                {top3.map((sub, idx) => (
                                  <TableRow key={`${mes.mes_referencia}-sub-${idx}`} className="bg-muted/50">
                                    <TableCell></TableCell>
                                    <TableCell className="pl-8 text-sm text-muted-foreground">
                                      {sub.subgrupo || <span className="italic">Sem subgrupo</span>}
                                    </TableCell>
                                    <TableCell className="text-right text-sm">
                                      R$ {formatarMoeda(sub.valor_total)}
                                    </TableCell>
                                    <TableCell className="text-right text-sm">
                                      {sub.quantidade_transacoes}
                                    </TableCell>
                                    <TableCell></TableCell>
                                  </TableRow>
                                ))}
                                
                                {/* Linha "Demais" */}
                                {demaisAgregado && (
                                  <TableRow className="bg-muted/30">
                                    <TableCell></TableCell>
                                    <TableCell className="pl-8">
                                      <Button
                                        variant="link"
                                        size="sm"
                                        className="h-auto p-0 text-sm font-medium"
                                        onClick={() => handleVerTodosSubgrupos(mes)}
                                      >
                                        <ListIcon className="mr-1 h-3 w-3" />
                                        Demais ({totalDemais})
                                      </Button>
                                    </TableCell>
                                    <TableCell className="text-right text-sm">
                                      R$ {formatarMoeda(demaisAgregado.valor_total)}
                                    </TableCell>
                                    <TableCell className="text-right text-sm">
                                      {demaisAgregado.quantidade_transacoes}
                                    </TableCell>
                                    <TableCell></TableCell>
                                  </TableRow>
                                )}
                              </>
                            )}
                          </React.Fragment>
                        );
                      })}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>

              <div className="grid grid-cols-2 gap-4 pt-2">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-sm text-muted-foreground">Total Geral</div>
                    <div className="text-2xl font-bold">
                      R$ {formatarMoeda(detalhamento.total_geral)}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Soma dos 3 meses
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="text-sm text-muted-foreground">Média Calculada</div>
                    <div className="text-2xl font-bold text-primary">
                      R$ {formatarMoeda(detalhamento.media_calculada)}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {detalhamento.meses_considerados.filter(m => m.quantidade_transacoes > 0).length}{' '}
                      {detalhamento.meses_considerados.filter(m => m.quantidade_transacoes > 0).length === 1 ? 'mês' : 'meses'} com dados
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          ) : (
            <div className="py-8 text-center text-muted-foreground">
              Nenhum dado disponível
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Fechar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de Todos os Subgrupos */}
      {mesModalDemais && (
        <TodosSubgruposModal
          open={modalDemaisOpen}
          onOpenChange={setModalDemaisOpen}
          mes={mesModalDemais}
          subgrupos={mesModalDemais.subgrupos || []}
        />
      )}
    </>
  );
}
