'use client';

import React, { useMemo } from 'react';
import { Bar, BarChart, CartesianGrid, XAxis } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart';

interface ChartDataItem {
  mes: string;
  receitas: number;
  despesas: number;
}

interface ChartAreaInteractiveProps {
  data?: ChartDataItem[];
  loading?: boolean;
  error?: string | null;
  selectedMonth?: string; // 'all' ou '1'-'12'
}

const chartConfig = {
  receitas: {
    label: "Receitas",
    color: "#10b981", // green-500
  },
  despesas: {
    label: "Despesas",
    color: "#ef4444", // red-500
  },
} satisfies ChartConfig;

const ChartAreaInteractive: React.FC<ChartAreaInteractiveProps> = ({
  data = [],
  loading = false,
  error = null,
  selectedMonth = 'all'
}) => {
  // Mapear nomes de meses para índices (1-12)
  const monthNameToIndex: { [key: string]: number } = {
    'Jan': 1, 'Fev': 2, 'Mar': 3, 'Abr': 4, 'Mai': 5, 'Jun': 6,
    'Jul': 7, 'Ago': 8, 'Set': 9, 'Out': 10, 'Nov': 11, 'Dez': 12
  };

  // Mostrar todos os 12 meses com scroll horizontal
  const visibleData = useMemo(() => {
    if (!data || data.length === 0) return [];
    
    // Retornar todos os dados disponíveis (12 meses)
    return data;
  }, [data]);
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-medium">{`Mês: ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.dataKey === 'receitas' ? 'Receitas' : 'Despesas'}: {formatCurrency(entry.value || 0)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Receitas vs Despesas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Carregando dados...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Receitas vs Despesas</CardTitle>
        </CardHeader>
        <CardContent>
          <Badge variant="destructive" className="w-full justify-center py-4">
            Erro ao carregar dados: {error}
          </Badge>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Receitas vs Despesas</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <div style={{ minWidth: '200px' }}>
            <ChartContainer config={chartConfig}>
              <BarChart accessibilityLayer data={visibleData}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="mes"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => value.slice(0, 3)}
            />
            <ChartTooltip
              cursor={false}
              content={<CustomTooltip />}
            />
                <Bar dataKey="receitas" fill="var(--color-receitas)" radius={4} />
                <Bar dataKey="despesas" fill="var(--color-despesas)" radius={4} />
              </BarChart>
            </ChartContainer>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ChartAreaInteractive;