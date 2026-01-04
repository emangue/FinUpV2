'use client';

import React from 'react';
import { Bar, BarChart, CartesianGrid, LabelList, XAxis } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart';

interface CategoryData {
  categoria: string;
  valor: number;
  percentual: number;
}

interface CategoryExpensesProps {
  data?: CategoryData[];
  loading?: boolean;
  error?: string | null;
}

const chartConfig = {
  percentual: {
    label: "Percentual",
    color: "#f97316", // orange-500
  },
} satisfies ChartConfig;

const CategoryExpenses: React.FC<CategoryExpensesProps> = ({
  data = [],
  loading = false,
  error = null
}) => {
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
      const data = payload[0]?.payload;
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-medium">{`${label}`}</p>
          <p className="text-orange-600">
            Valor: {formatCurrency(data?.valor || 0)}
          </p>
          <p className="text-gray-600">
            {data?.percentual?.toFixed(1)}% da receita
          </p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>% Por Categoria de Gasto em Relação à Receita</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center">
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
          <CardTitle>% Por Categoria de Gasto em Relação à Receita</CardTitle>
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
        <CardTitle className="text-base">% Por Categoria de Gasto em Relação à Receita</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart
            accessibilityLayer
            data={data}
            margin={{
              top: 20,
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="categoria"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => value.slice(0, 8) + (value.length > 8 ? '...' : '')}
            />
            <ChartTooltip
              cursor={false}
              content={<CustomTooltip />}
            />
            <Bar dataKey="percentual" fill="var(--color-percentual)" radius={8}>
              <LabelList
                position="top"
                offset={12}
                className="fill-foreground"
                fontSize={12}
                formatter={(value: number) => `${value.toFixed(1)}%`}
              />
            </Bar>
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};

export default CategoryExpenses;