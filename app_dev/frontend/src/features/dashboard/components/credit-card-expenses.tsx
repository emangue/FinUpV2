'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CreditCard } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { API_CONFIG } from '@/core/config/api.config';

interface CreditCardData {
  cartao: string;
  total: number;
  percentual: number;
  num_transacoes: number;
}

interface CreditCardExpensesProps {
  year?: string;
  month?: string;
}

const formatarMoeda = (valor: number): string => {
  return valor.toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

const CreditCardExpenses: React.FC<CreditCardExpensesProps> = ({ 
  year = '2025', 
  month = 'all' 
}) => {
  const router = useRouter();
  const [data, setData] = useState<CreditCardData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, [year, month]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams({ year });
      if (month !== 'all') {
        params.append('month', month);
      }

      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/api/v1/dashboard/credit-cards?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error('Erro ao buscar dados dos cartões');
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      console.error('Erro ao buscar dados dos cartões:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  const getCardIcon = (cardName: string): string => {
    const name = cardName.toLowerCase();
    if (name.includes('mastercard')) return '🔴';
    if (name.includes('visa')) return '🔵';
    if (name.includes('elo')) return '🟡';
    if (name.includes('amex') || name.includes('american')) return '🟢';
    return '💳';
  };

  const handleCardClick = (cardName: string) => {
    // Construir query params para filtrar transações
    const params = new URLSearchParams({
      cartao: cardName,
    });
    
    // Se month específico, adicionar filtro de mês
    if (month !== 'all') {
      const mesRef = `${year}${month.padStart(2, '0')}`;
      params.append('mes_referencia', mesRef);
    }
    
    // Redirecionar para página de transações
    router.push(`/transactions?${params.toString()}`);
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <CreditCard className="h-4 w-4" />
            Gastos com Cartões de Crédito
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[200px] flex items-center justify-center">
            <p className="text-sm text-muted-foreground">Carregando...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <CreditCard className="h-4 w-4" />
            Gastos com Cartões de Crédito
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[200px] flex items-center justify-center">
            <p className="text-sm text-red-500">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <CreditCard className="h-4 w-4" />
            Gastos com Cartões de Crédito
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[200px] flex items-center justify-center">
            <div className="text-center text-gray-500">
              <CreditCard className="h-12 w-12 mx-auto mb-4 opacity-30" />
              <p className="text-sm">Nenhum gasto com cartão encontrado</p>
              <p className="text-xs mt-1">Período: {month === 'all' ? 'Ano todo' : `Mês ${month}`}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <CreditCard className="h-4 w-4" />
          Gastos com Cartões de Crédito
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.map((card, index) => (
            <div 
              key={index} 
              className="space-y-2 cursor-pointer hover:bg-muted/50 p-2 rounded-lg transition-colors"
              onClick={() => handleCardClick(card.cartao)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{getCardIcon(card.cartao)}</span>
                  <span className="font-medium text-sm">{card.cartao}</span>
                </div>
                <div className="text-right">
                  <span className="text-sm font-semibold">
                    {card.percentual.toFixed(1)}%
                  </span>
                  <span className="text-xs text-muted-foreground ml-2">
                    R$ {formatarMoeda(card.total)}
                  </span>
                </div>
              </div>
              <Progress 
                value={card.percentual} 
                className="h-2"
              />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default CreditCardExpenses;
