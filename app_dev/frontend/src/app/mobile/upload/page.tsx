'use client';

/**
 * Upload Mobile - Página de Upload (Protótipo V2 + APIs Reais)
 * 
 * Conectado com backend:
 * - useBanks → GET /api/v1/compatibility/banks
 * - useCreditCards → GET /api/v1/cards
 * - useUpload → POST /api/v1/upload
 * 
 * 🚨 PALIATIVO: Auto-login para dev (remover na produção)
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { TabType, FileFormat } from '@/features/upload/types';
import { months, years, fileFormats } from '@/features/upload/mocks/mockUploadData';
import { 
  BankSelector, 
  CardSelector, 
  MonthYearPicker, 
  FormatSelector, 
  FileInput, 
  TabBar 
} from '@/features/upload/components';
import { useBanks, useCreditCards, useUpload } from '@/features/upload/hooks';
import { setAuthToken, isAuthenticated } from '@/core/utils/api-client';
import { API_ENDPOINTS } from '@/core/config/api.config';

export default function UploadPage() {
  const router = useRouter();
  const [authReady, setAuthReady] = useState(false);
  
  // 🚨 PALIATIVO - Auto-login para desenvolvimento
  useEffect(() => {
    const setupAuth = async () => {
      if (isAuthenticated()) {
        setAuthReady(true);
        return;
      }

      try {
        const response = await fetch(API_ENDPOINTS.AUTH.LOGIN, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: 'admin@financas.com',
            password: 'cahriZqonby8'
          })
        });

        if (response.ok) {
          const data = await response.json();
          console.group('✅ [MOBILE-UPLOAD] Auto-login bem-sucedido')
          console.log('👤 Usuário:', data.user)
          console.log('🔑 Token recebido (primeiros 30 chars):', data.access_token.substring(0, 30) + '...')
          console.groupEnd()
          setAuthToken(data.access_token);
        } else {
          console.error('❌ [MOBILE-UPLOAD] Falha no auto-login:', response.status, response.statusText)
        }
      } catch (err) {
        console.error('[mobile-upload] Erro no auto-login:', err);
      } finally {
        setAuthReady(true);
      }
    };

    setupAuth();
  }, []);
  
  // Hooks para dados reais
  const { banks, loading: loadingBanks } = useBanks();
  const { cards, loading: loadingCards } = useCreditCards();
  const { upload, uploading, progress } = useUpload();
  
  // Form state
  const [activeTab, setActiveTab] = useState<TabType>('fatura');
  const [selectedBank, setSelectedBank] = useState('');
  const [selectedCard, setSelectedCard] = useState('');
  const [selectedYear, setSelectedYear] = useState(2026);
  const [selectedMonth, setSelectedMonth] = useState('Fevereiro');
  const [selectedFormat, setSelectedFormat] = useState<FileFormat>('csv');
  const [fileName, setFileName] = useState('Nenhum...');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = (file: File | null) => {
    if (file) {
      setFileName(file.name);
      setSelectedFile(file);
    }
  };

  const handleAddCard = () => {
    alert('Funcionalidade de adicionar cartão será implementada em breve');
  };

  const handleSubmit = async () => {
    console.group('🚀 [MOBILE-UPLOAD] handleSubmit iniciado')
    console.log('📋 Formulário:', { 
      banco: selectedBank, 
      tipo: activeTab, 
      formato: selectedFormat,
      cartao: selectedCard, 
      mes: selectedMonth, 
      ano: selectedYear 
    })
    console.log('📎 Arquivo:', selectedFile ? { 
      name: selectedFile.name, 
      size: selectedFile.size, 
      type: selectedFile.type 
    } : 'NENHUM')
    console.log('🔑 Autenticado?', isAuthenticated())
    console.groupEnd()
    
    // Validações
    if (!selectedBank) {
      alert('Por favor, selecione uma instituição financeira');
      return;
    }
    if (activeTab === 'fatura' && !selectedCard) {
      alert('Por favor, selecione um cartão de crédito');
      return;
    }
    if (!selectedFile) {
      alert('Por favor, selecione um arquivo');
      return;
    }
    
    try {
      // Buscar dados completos do cartão selecionado
      let cartaoNome: string | undefined;
      let cartaoFinal: string | undefined;
      
      if (activeTab === 'fatura' && selectedCard) {
        const cartao = cards.find(c => c.id.toString() === selectedCard);
        if (cartao) {
          cartaoNome = cartao.name;
          cartaoFinal = cartao.lastDigits;
        }
      }
      
      const result = await upload({
        file: selectedFile,
        banco: selectedBank,
        tipo: activeTab,
        cartaoId: activeTab === 'fatura' ? selectedCard : undefined,
        cartaoNome,  // ✅ Enviar nome do cartão
        cartaoFinal,  // ✅ Enviar final do cartão
        mes: activeTab === 'fatura' ? selectedMonth : undefined,
        ano: activeTab === 'fatura' ? selectedYear : undefined,
        formato: selectedFormat
      });
      
      // ✅ Redirecionar para preview MOBILE com sessionId
      console.log('✅ [MOBILE-UPLOAD] Upload bem-sucedido! SessionId:', result.sessionId);
      router.push(`/mobile/preview/${result.sessionId}`);
      
    } catch (error) {
      console.error('❌ [MOBILE-UPLOAD] Erro no upload:', error);
      alert('Erro ao fazer upload. Por favor, tente novamente.');
    }
  };

  // 🚨 Loading screen enquanto autentica
  if (!authReady) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-emerald-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Configurando autenticação...</p>
        </div>
      </div>
    );
  }

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
        <div className="bg-white px-6 py-6 rounded-b-3xl">
          
          {/* Tabs */}
          <TabBar 
            activeTab={activeTab}
            onChange={setActiveTab}
          />
          
          {/* Instituição Financeira */}
          {loadingBanks ? (
            <div className="mb-6 text-center text-gray-500">Carregando bancos...</div>
          ) : (
            <BankSelector 
              banks={banks}
              value={selectedBank}
              onChange={setSelectedBank}
              required
            />
          )}
          
          {/* Cartão de Crédito (apenas para Fatura) */}
          {activeTab === 'fatura' && (
            <>
              {loadingCards ? (
                <div className="mb-6 text-center text-gray-500">Carregando cartões...</div>
              ) : (
                <CardSelector 
                  cards={cards}
                  value={selectedCard}
                  onChange={setSelectedCard}
                  onAddNew={handleAddCard}
                  required
                />
              )}
          
              {/* Período da Fatura */}
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
          
          {/* Progress Bar */}
          {uploading && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Fazendo upload...</span>
                <span className="text-sm font-bold text-gray-900">{progress}%</span>
              </div>
              <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gray-900 transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Botão Importar */}
          <div className="pt-4 pb-6">
            <button 
              onClick={handleSubmit}
              disabled={uploading || loadingBanks || (activeTab === 'fatura' && loadingCards)}
              className="w-full py-4 bg-gray-900 hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed text-white text-sm font-bold rounded-xl transition-colors shadow-lg"
            >
              {uploading ? 'Enviando...' : 'Importar Arquivo'}
            </button>
          </div>
          
        </div>
      </div>
    </div>
  );
}

