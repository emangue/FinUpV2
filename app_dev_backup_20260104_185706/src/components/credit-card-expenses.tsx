'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CreditCard } from 'lucide-react';

const CreditCardExpenses: React.FC = () => {
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
            <p className="text-sm">Em desenvolvimento</p>
            <p className="text-xs mt-1">Análise por cartão será implementada em breve</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default CreditCardExpenses;