'use client';

/**
 * Upload Mobile - Página de Upload (Protótipo V2)
 * 
 * Design do protótipo com:
 * - Seleção de instituição financeira
 * - Seleção de cartão (para faturas)
 * - Período da fatura
 * - Formato do arquivo
 * - Upload de arquivo
 * 
 * TODO: Conectar com APIs reais
 */

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { TabType, FileFormat } from '@/features/upload/types';
import { banks, creditCards, months, years, fileFormats } from '@/features/upload/mocks/mockUploadData';
import { 
  BankSelector, 
  CardSelector, 
  MonthYearPicker, 
  FormatSelector, 
  FileInput, 
  TabBar 
} from '@/features/upload/components';

export default function UploadPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabType>('fatura');
  const [selectedBank, setSelectedBank] = useState('');
  const [selectedCard, setSelectedCard] = useState('');
  const [selectedYear, setSelectedYear] = useState(2026);
  const [selectedMonth, setSelectedMonth] = useState('Fevereiro');
  const [selectedFormat, setSelectedFormat] = useState<FileFormat>('csv');
  const [fileName, setFileName] = useState('Nenhum...');

  const handleFileChange = (file: File | null) => {
    if (file) {
      setFileName(file.name);
    }
  };

  const handleAddCard = () => {
    alert('Funcionalidade de adicionar cartão será implementada em breve');
  };

  const handleSubmit = () => {
    if (!selectedBank) {
      alert('Por favor, selecione uma instituição financeira');
      return;
    }
    if (activeTab === 'fatura' && !selectedCard) {
      alert('Por favor, selecione um cartão de crédito');
      return;
    }
    if (fileName === 'Nenhum...') {
      alert('Por favor, selecione um arquivo');
      return;
    }
    
    // TODO: Conectar com API real
    alert('Arquivo sendo processado...');
  };

  return (
    <div className="bg-gray-50 min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md mx-auto">
        
        {/* Header */}
        <header className="bg-white rounded-t-3xl px-6 py-4 flex items-center justify-between border-b border-gray-100">
          <button 
            onClick={() => router.back()}
            className="text-gray-700 hover:text-gray-900 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path>
            </svg>
          </button>
          <h1 className="text-lg font-bold text-gray-800">Importar Arquivo</h1>
          <div className="w-6"></div>
        </header>
        
        {/* Subtitle */}
        <div className="bg-white px-6 py-3 border-b border-gray-100">
          <p className="text-xs text-gray-400 text-center">Faça o upload de faturas de cartão ou extratos bancários</p>
        </div>
        
        {/* Main Content */}
        <div className="bg-white px-6 py-6">
          
          {/* Tabs */}
        <TabBar 
          activeTab={activeTab}
          onChange={setActiveTab}
        />
          {/* Instituição Financeira */}
        <BankSelector 
          banks={banks}
          value={selectedBank}
          onChange={setSelectedBank}
          required
        />
          {/* Cartão de Crédito (apenas para Fatura) */}
          {activeTab === 'fatura' && (
            <>
              <CardSelector 
                cards={creditCards}
                value={selectedCard}
                onChange={setSelectedCard}
                onAddNew={handleAddCard}
                required
              />
          
              {/* Período da Fatura (apenas para Fatura) */}
              <MonthYearPicker 
                months={months}
                years={years}
                selectedMonth={selectedMonth}
                selectedYear={selectedYear}
                onMonthChange={setSelectedMonth}
                onYearChange={setSelectedYear}
                required
              />
            </>
          )}
          
          {/* Formato do arquivo */}
          <FormatSelector 
            formats={fileFormats}
            value={selectedFormat}
            onChange={setSelectedFormat}
          />
          
          {/* Arquivo */}
          <FileInput 
            fileName={fileName}
            onChange={handleFileChange}
          />
          
          {/* Botão Importar */}
          <div className="pt-4 pb-6">
            <button 
              onClick={handleSubmit}
              className="w-full py-4 bg-gray-900 hover:bg-gray-800 text-white text-sm font-bold rounded-xl transition-colors shadow-lg"
            >
              Importar Arquivo
            </button>
          </div>
          
        </div>
      </div>
    </div>
  );
}
