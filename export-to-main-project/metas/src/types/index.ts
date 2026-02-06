export type GoalType = 'gasto' | 'investimento';

export interface Goal {
  id: string;
  name: string;
  type: GoalType;
  budget: number;
  spent: number;
  percentage: number;
  icon: string;
  color: string;
  category: string;
  alertAt80: boolean;
  alertAt100: boolean;
  active: boolean;
  description?: string;
  deadline?: string;
}

export interface Transaction {
  id: string;
  description: string;
  amount: number;
  date: string;
  category: string;
}

export interface Month {
  label: string;
  year: string;
  value: string;
}
