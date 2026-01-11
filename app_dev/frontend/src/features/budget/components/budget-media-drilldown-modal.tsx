'use client';

import React, { useState, useEffect } from 'react';
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
import { ArrowRight, ExternalLink } from 'lucide-react';
import { API_CONFIG } from '@/core/config/api.config';

interface MesDetalhamento {
  mes_referencia: string;
  mes_nome: string;
  valor_total: number;
  quantidade_transacoes: number;
}

interface DetalhamentoMedia {
  tipo_gasto: string;
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

export function BudgetMediaDrilldownModal({
  open,
  onOpenChange,
  tipoGasto,
  mesReferencia,
}: BudgetMediaDrilldownModalProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [detalhamento, setDetalhamento] = useState<DetalhamentoMedia | null>(null);

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
        tipo_gasto: tipoGasto,
        mes_referencia: mesReferencia,
      });

      const response = await fetch(
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
    // Navegar para página de transações com filtros aplicados
    const params = new URLSearchParams({
      tipoGasto: tipoGasto || '',
      mes_referencia: mesRef,
    });
    
    router.push(`/transactions?${params.toString()}`);
    onOpenChange(false); // Fechar modal
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Detalhamento da Média - {tipoGasto}</DialogTitle>
          <DialogDescription>
            Veja o detalhamento dos últimos 3 meses que compõem a média calculada
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
                      <TableHead>Mês</TableHead>
                      <TableHead className="text-right">Valor Total</TableHead>
                      <TableHead className="text-right">Transações</TableHead>
                      <TableHead className="text-right">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {detalhamento.meses_considerados.map((mes) => (
                      <TableRow key={mes.mes_referencia}>
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
                    ))}
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
  );
}
