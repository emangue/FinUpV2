'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { TabType, FileFormat } from '@/types';
import { banks, creditCards, months, years, fileFormats } from '@/lib/constants';

export default function UploadPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabType>('fatura');
  const [selectedBank, setSelectedBank] = useState('');
  const [selectedCard, setSelectedCard] = useState('');
  const [selectedYear, setSelectedYear] = useState(2026);
  const [selectedMonth, setSelectedMonth] = useState('Fevereiro');
  const [selectedFormat, setSelectedFormat] = useState<FileFormat>('csv');
  const [fileName, setFileName] = useState('Nenhum...');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
    }
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
        <div className="bg-white px-6 py-6 content-animate">
          
          {/* Tabs */}
          <div className="flex gap-3 mb-6">
            <button 
              onClick={() => setActiveTab('extrato')}
              className={`flex-1 px-6 py-3 rounded-xl text-sm font-semibold transition-all ${
                activeTab === 'extrato'
                  ? 'bg-gray-900 text-white shadow-lg'
                  : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
              }`}
            >
              Extrato bancário
            </button>
            <button 
              onClick={() => setActiveTab('fatura')}
              className={`flex-1 px-6 py-3 rounded-xl text-sm font-semibold transition-all ${
                activeTab === 'fatura'
                  ? 'bg-gray-900 text-white shadow-lg'
                  : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
              }`}
            >
              Fatura Cartão
            </button>
          </div>
          
          {/* Instituição Financeira */}
          <div className="mb-6">
            <label className="block text-sm font-bold text-gray-900 mb-2">
              Instituição Financeira <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <select 
                value={selectedBank}
                onChange={(e) => setSelectedBank(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-gray-700 appearance-none cursor-pointer hover:border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              >
                <option value="">Selecione o banco</option>
                {banks.map((bank) => (
                  <option key={bank.id} value={bank.id}>{bank.name}</option>
                ))}
              </select>
              <svg className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </div>
          </div>
          
          {/* Cartão de Crédito (apenas para Fatura) */}
          {activeTab === 'fatura' && (
            <div className="mb-6">
              <label className="block text-sm font-bold text-gray-900 mb-2">
                Cartão de Crédito <span className="text-red-500">*</span>
              </label>
              <div className="flex gap-3">
                <div className="relative flex-1">
                  <select 
                    value={selectedCard}
                    onChange={(e) => setSelectedCard(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl text-gray-700 appearance-none cursor-pointer hover:border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  >
                    <option value="">Selecione o cartão</option>
                    {creditCards.map((card) => (
                      <option key={card.id} value={card.id}>{card.name}</option>
                    ))}
                  </select>
                  <svg className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                  </svg>
                </div>
                <button className="w-12 h-12 flex items-center justify-center bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors">
                  <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path>
                  </svg>
                </button>
              </div>
            </div>
          )}
          
          {/* Período da Fatura (apenas para Fatura) */}
          {activeTab === 'fatura' && (
            <div className="mb-6">
              <label className="block text-sm font-bold text-gray-900 mb-2">
                Período da Fatura <span className="text-red-500">*</span>
              </label>
              <div className="flex gap-3">
                <div className="relative w-32">
                  <select 
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(Number(e.target.value))}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl text-gray-700 font-medium appearance-none cursor-pointer hover:border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  >
                    {years.map((year) => (
                      <option key={year} value={year}>{year}</option>
                    ))}
                  </select>
                  <svg className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                  </svg>
                </div>
                <div className="relative flex-1">
                  <select 
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl text-gray-700 font-medium appearance-none cursor-pointer hover:border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  >
                    {months.map((month) => (
                      <option key={month} value={month}>{month}</option>
                    ))}
                  </select>
                  <svg className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                  </svg>
                </div>
              </div>
            </div>
          )}
          
          {/* Formato do arquivo */}
          <div className="mb-6">
            <label className="block text-sm font-bold text-gray-900 mb-3">
              Formato do arquivo para importação
            </label>
            <div className="space-y-3">
              {fileFormats.map((format) => (
                <div key={format.value} className="flex items-center">
                  <input 
                    type="radio" 
                    id={`format-${format.value}`}
                    name="format" 
                    value={format.value}
                    checked={selectedFormat === format.value}
                    onChange={(e) => setSelectedFormat(e.target.value as FileFormat)}
                    className="hidden peer"
                  />
                  <label 
                    htmlFor={`format-${format.value}`}
                    className="relative flex items-center cursor-pointer group"
                  >
                    <span className={`w-[18px] h-[18px] border-2 rounded-full mr-3 flex items-center justify-center transition-colors ${
                      selectedFormat === format.value
                        ? 'border-gray-900'
                        : 'border-gray-300 group-hover:border-gray-400'
                    }`}>
                      {selectedFormat === format.value && (
                        <span className="w-2 h-2 bg-gray-900 rounded-full"></span>
                      )}
                    </span>
                    <span className="text-sm text-gray-700">
                      <span className="font-semibold">{format.label}</span>
                      <span className="text-gray-400 ml-2">(selecione um banco)</span>
                    </span>
                  </label>
                </div>
              ))}
            </div>
          </div>
          
          {/* Arquivo */}
          <div className="mb-6">
            <label className="block text-sm font-bold text-gray-900 mb-3">
              Arquivo
            </label>
            <label className="flex items-center gap-3 px-6 py-4 border-2 border-dashed border-gray-200 rounded-xl cursor-pointer hover:border-gray-300 hover:bg-gray-50 transition-all">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
              <span className="text-sm font-semibold text-gray-700">Escolher Arquivo</span>
              <input 
                type="file" 
                className="hidden" 
                onChange={handleFileChange}
                accept=".csv,.xls,.xlsx,.pdf,.ofx"
              />
            </label>
            <p className="text-sm text-gray-400 mt-2">{fileName}</p>
          </div>
          
          {/* Botão Importar */}
          <div className="pt-4 pb-20">
            <button 
              onClick={handleSubmit}
              className="w-full py-4 bg-gray-900 hover:bg-gray-800 text-white text-sm font-bold rounded-xl transition-colors shadow-lg"
            >
              Importar Arquivo
            </button>
          </div>
          
        </div>
        
        {/* Bottom Navigation */}
        <nav className="bg-white rounded-b-3xl px-6 py-4 flex items-center justify-around border-t border-gray-100">
          <button className="flex flex-col items-center gap-1 text-gray-400 hover:text-gray-900 transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
            </svg>
            <span className="text-[10px] font-medium">Home</span>
          </button>
          <button className="flex flex-col items-center gap-1 text-gray-400 hover:text-gray-900 transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path>
            </svg>
            <span className="text-[10px] font-medium">Card</span>
          </button>
          <button className="flex flex-col items-center gap-1 text-gray-900">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
            <span className="text-[10px] font-bold">Upload</span>
          </button>
        </nav>
      </div>
    </div>
  );
}
