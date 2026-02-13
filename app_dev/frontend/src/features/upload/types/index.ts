export type TabType = 'extrato' | 'fatura';

export type FileFormat = 'csv' | 'excel' | 'pdf' | 'pdf-password' | 'ofx';

export interface Bank {
  id: string;
  name: string;
}

export interface CreditCard {
  id: string;
  bankId: string;
  lastDigits: string;
  name: string;
}

export interface UploadFormData {
  type: TabType;
  bank: string;
  card?: string;
  year?: number;
  month?: string;
  format: FileFormat;
  file?: File;
}

// Re-export preview types
export * from './preview.types';
