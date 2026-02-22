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
import { fetchCompatibility } from '@/features/upload/services/upload-api';
import type { BankCompatibilityMap } from '@/features/upload/services/upload-api';
import type { FormatAvailability } from '@/features/upload/components/format-selector';
import { useAuth } from '@/contexts/AuthContext';
import { API_ENDPOINTS } from '@/core/config/api.config';

export default function UploadPage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading, login } = useAuth();
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    const setupAuth = async () => {
      if (isAuthenticated) {
        setAuthReady(true);
        return;
      }
      try {
        await login('admin@financas.com', 'cahriZqonby8');
      } catch {
        // Falha silenciosa - usuário pode fazer login manual
      } finally {
        setAuthReady(true);
      }
    };
    if (!authLoading) setupAuth();
  }, [isAuthenticated, authLoading, login]);
  
  // Hooks para dados reais
  const { banks, loading: loadingBanks } = useBanks();
  const { cards, loading: loadingCards } = useCreditCards();
  const { upload, uploading, progress } = useUpload();

  // Compatibilidade de formatos por banco (desabilita TBD)
  const [compatibility, setCompatibility] = useState<BankCompatibilityMap>({});
  useEffect(() => {
    fetchCompatibility().then(setCompatibility).catch(() => setCompatibility({}));
  }, []);
  
  // Form state
  const [activeTab, setActiveTab] = useState<TabType>('fatura');
  const [selectedBank, setSelectedBank] = useState('');
  const [selectedCard, setSelectedCard] = useState('');
  const [selectedYear, setSelectedYear] = useState(2026);
  const [selectedMonth, setSelectedMonth] = useState('Fevereiro');
  const [selectedFormat, setSelectedFormat] = useState<FileFormat>('csv');
  const [fileName, setFileName] = useState('Nenhum...');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [password, setPassword] = useState('');  // Senha do PDF protegido

  const handleFileChange = (file: File | null) => {
    if (file) {
      setFileName(file.name);
      setSelectedFile(file);
      // Auto-detectar formato pela extensão do arquivo
      const ext = file.name.split('.').pop()?.toLowerCase();
      if (ext === 'xlsx' || ext === 'xls' || ext === 'xlsm') {
        setSelectedFormat('excel');
      } else if (ext === 'csv' || ext === 'txt') {
        setSelectedFormat('csv');
      } else if (ext === 'pdf') {
        setSelectedFormat('pdf');
      } else if (ext === 'ofx') {
        setSelectedFormat('ofx');
      }
    }
  };

  // Quando banco muda, se formato atual for TBD, resetar para primeiro disponível
  const formatAvailability: FormatAvailability = selectedBank && compatibility[selectedBank]
    ? {
        csv: compatibility[selectedBank].csv_status,
        excel: compatibility[selectedBank].excel_status,
        pdf: compatibility[selectedBank].pdf_status,
        'pdf-password': compatibility[selectedBank].pdf_status,
        ofx: compatibility[selectedBank].ofx_status,
      }
    : {};

  useEffect(() => {
    if (!selectedBank || !compatibility[selectedBank]) return;
    const b = compatibility[selectedBank];
    const getStatus = (f: FileFormat) => (f === 'pdf-password' ? b.pdf_status : b[`${f}_status` as keyof typeof b]);
    if (getStatus(selectedFormat) === 'TBD') {
      const first = (['csv', 'excel', 'pdf', 'pdf-password', 'ofx'] as const).find((f) => getStatus(f) !== 'TBD');
      if (first) setSelectedFormat(first);
    }
  }, [selectedBank, compatibility, selectedFormat]);

  const handleAddCard = () => {
    alert('Funcionalidade de adicionar cartão será implementada em breve');
  };

  const handleSubmit = async () => {
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
    if (selectedFormat === 'pdf-password' && !password.trim()) {
      alert('Por favor, informe a senha do PDF protegido');
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
        formato: selectedFormat,
        senha: selectedFormat === 'pdf-password' ? password : undefined,  // ✅ Senha apenas para pdf-password
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
            formatAvailability={Object.keys(formatAvailability).length > 0 ? formatAvailability : undefined}
            bankNotSelected={!selectedBank}
          />

          {/* Senha do PDF (apenas quando formato pdf-password estiver selecionado) */}
          {selectedFormat === 'pdf-password' && (
            <div className="mb-6">
              <label className="block text-sm font-bold text-gray-900 mb-2">
                Senha do PDF <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Digite a senha do arquivo PDF"
                autoComplete="current-password"
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm text-gray-700 focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900"
              />
              <p className="text-xs text-gray-400 mt-1">
                Necessária para PDFs do Itaú ou BTG Pactual protegidos por senha
              </p>
            </div>
          )}
          
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

