import { Bank, CreditCard } from '../types';

export const banks: Bank[] = [
  { id: 'nubank', name: 'Nubank' },
  { id: 'inter', name: 'Inter' },
  { id: 'itau', name: 'Itaú' },
  { id: 'bradesco', name: 'Bradesco' },
  { id: 'santander', name: 'Santander' },
  { id: 'bb', name: 'Banco do Brasil' },
  { id: 'caixa', name: 'Caixa Econômica' },
  { id: 'btg', name: 'BTG Pactual' },
  { id: 'c6', name: 'C6 Bank' },
  { id: 'picpay', name: 'PicPay' },
];

export const creditCards: CreditCard[] = [
  { id: '1', bankId: 'nubank', lastDigits: '1234', name: 'Nubank **** 1234' },
  { id: '2', bankId: 'inter', lastDigits: '5678', name: 'Inter **** 5678' },
  { id: '3', bankId: 'itau', lastDigits: '9012', name: 'Itaú **** 9012' },
  { id: '4', bankId: 'bradesco', lastDigits: '3456', name: 'Bradesco **** 3456' },
  { id: '5', bankId: 'c6', lastDigits: '7890', name: 'C6 Bank **** 7890' },
];

export const months = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];

export const years = [2023, 2024, 2025, 2026, 2027];

export const fileFormats = [
  { value: 'csv' as const, label: 'CSV' },
  { value: 'excel' as const, label: 'Planilha Excel (XLS/XLSX)' },
  { value: 'pdf' as const, label: 'PDF' },
  { value: 'pdf-password' as const, label: 'PDF com senha' },
  { value: 'ofx' as const, label: 'OFX' },
];
