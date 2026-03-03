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
import { toast } from 'sonner';
import { logger } from '@/lib/logger';
import { TabType, FileFormat } from '@/features/upload/types';
import { months, years, fileFormats } from '@/features/upload/mocks/mockUploadData';
import { 
  BankSelector, 
  CardSelector, 
  MonthYearPicker, 
  FormatSelector, 
  FileInput, 
  TabBar,
  FileDetectionCard,
} from '@/features/upload/components';
import { useBanks, useCreditCards, useUpload } from '@/features/upload/hooks';
import { fetchCompatibility, createCard, PasswordRequiredError, detectFile, importPlanilhaFile, type DetectionResult } from '@/features/upload/services/upload-api';
import type { BankCompatibilityMap } from '@/features/upload/services/upload-api';
import type { FormatAvailability } from '@/features/upload/components/format-selector';
import { useAuth } from '@/contexts/AuthContext';
import { usePendingUpload } from '@/contexts/PendingUploadContext';
import { API_ENDPOINTS } from '@/core/config/api.config';
import { Settings } from 'lucide-react';

export default function UploadPage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading, login } = useAuth();
  const { consumePendingFile } = usePendingUpload();
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
  const { cards, loading: loadingCards, refetch: refetchCards } = useCreditCards();
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

  // Filtrar cartões pelo banco selecionado (card.bankId = card.banco no backend)
  // Busca bidirecional: "Banco Itaú" deve casar com seleção "Itaú" (e vice-versa)
  const filteredCards = selectedBank
    ? cards.filter(c => {
        const cardBank = c.bankId.toLowerCase();
        const selBank = selectedBank.toLowerCase();
        return cardBank === selBank || cardBank.includes(selBank) || selBank.includes(cardBank);
      })
    : cards;
  const [selectedYear, setSelectedYear] = useState(2026);
  const [selectedMonth, setSelectedMonth] = useState('Fevereiro');
  const [selectedFormat, setSelectedFormat] = useState<FileFormat>('csv');
  const [fileName, setFileName] = useState('Nenhum...');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [password, setPassword] = useState('');  // Senha do PDF protegido
  const [detection, setDetection] = useState<DetectionResult | null>(null);
  const [detecting, setDetecting] = useState(false);
  const [importingPlanilha, setImportingPlanilha] = useState(false);

  // Estado do dialog: adicionar cartão
  const [showAddCard, setShowAddCard] = useState(false);
  const [newCardName, setNewCardName] = useState('');
  const [newCardFinal, setNewCardFinal] = useState('');
  const [addingCard, setAddingCard] = useState(false);

  // Estado do prompt: arquivo protegido por senha
  const [showPasswordPrompt, setShowPasswordPrompt] = useState(false);
  const [passwordPromptMsg, setPasswordPromptMsg] = useState('');
  const [retryPassword, setRetryPassword] = useState('');

  // Resetar cartão selecionado quando o banco mudar
  useEffect(() => {
    setSelectedCard('');
  }, [selectedBank]);

  // Arquivo vindo do FAB da bottom nav (tocou Upload → escolheu arquivo → navegou)
  useEffect(() => {
    if (!authReady) return;
    const pending = consumePendingFile();
    if (pending) {
      handleFileChange(pending);
    }
  }, [authReady]);

  const handleFileChange = async (file: File | null) => {
    setDetection(null);
    if (file) {
      setFileName(file.name);
      setSelectedFile(file);
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
      setDetecting(true);
      try {
        const res = await detectFile(file);
        setDetection(res);
        if (res.banco !== 'generico' && banks.length > 0) {
          const bancoNorm = res.banco.toLowerCase().replace(/ú/u, 'u');
          const match = banks.find((b) => {
            const name = (b.id || b.name || '').toLowerCase().replace(/ú/u, 'u');
            return name.includes(bancoNorm) || bancoNorm.includes(name);
          });
          if (match) setSelectedBank(match.name);
        }
        // Fallback: quando backend retorna generico, inferir do filename (ex: fatura-itau.csv)
        if (res.banco === 'generico' && banks.length > 0) {
          const fn = file.name.toLowerCase().replace(/ú/u, 'u');
          const match = banks.find((b) => {
            const name = (b.id || b.name || '').toLowerCase().replace(/ú/u, 'u');
            return fn.includes(name);
          });
          if (match) setSelectedBank(match.name);
        }
        if (res.periodo_inicio && activeTab === 'fatura') {
          const [y, m] = res.periodo_inicio.split('-');
          if (y && m) {
            setSelectedYear(parseInt(y, 10));
            setSelectedMonth(months[parseInt(m, 10) - 1] || selectedMonth);
          }
        }
      } catch (err) {
        setDetection(null);
        console.warn('[Upload] Detecção falhou:', err);
        toast.error('Não foi possível detectar o arquivo. Selecione banco e período manualmente.');
      } finally {
        setDetecting(false);
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

  const handleBankChange = (bank: string) => {
    setSelectedBank(bank);
    setSelectedCard('');  // Resetar cartão ao trocar banco
  };

  const handleAddCard = () => {
    setNewCardName('');
    setNewCardFinal('');
    setShowAddCard(true);
  };

  const handleSaveNewCard = async () => {
    if (!newCardName.trim()) {
      toast.error('Por favor, informe o nome do cartão');
      return;
    }
    if (newCardFinal.length !== 4 || !/^\d{4}$/.test(newCardFinal)) {
      toast.error('O final do cartão deve ter exatamente 4 dígitos');
      return;
    }
    if (!selectedBank) {
      toast.error('Selecione uma instituição financeira antes de adicionar o cartão');
      return;
    }
    try {
      setAddingCard(true);
      const newCard = await createCard({
        nome_cartao: newCardName.trim(),
        final_cartao: newCardFinal,
        banco: selectedBank,
      });
      await refetchCards();
      setSelectedCard(newCard.id);
      setShowAddCard(false);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Erro ao adicionar cartão');
    } finally {
      setAddingCard(false);
    }
  };

  const handleSubmit = async () => {
    // Validações
    if (!selectedBank) {
      alert('Por favor, selecione uma instituição financeira');
      return;
    }
    if (activeTab === 'fatura' && !selectedCard) {
      toast.error('Por favor, selecione um cartão de crédito');
      return;
    }
    if (!selectedFile) {
      toast.error('Por favor, selecione um arquivo');
      return;
    }
    if (selectedFormat === 'pdf-password' && !password.trim()) {
      toast.error('Por favor, informe a senha do PDF protegido');
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
      logger.log('✅ [MOBILE-UPLOAD] Upload bem-sucedido! SessionId:', result.sessionId);
      router.push(`/mobile/preview/${result.sessionId}`);
      
    } catch (error) {
      if (error instanceof PasswordRequiredError) {
        setPasswordPromptMsg(
          error.wrongPassword
            ? 'Senha incorreta. Por favor, verifique e tente novamente.'
            : 'Este arquivo é protegido por senha. Informe a senha para continuar.'
        );
        setRetryPassword('');
        setShowPasswordPrompt(true);
        return;
      }
      console.error('❌ [MOBILE-UPLOAD] Erro no upload:', error);
      alert('Erro ao fazer upload. Por favor, tente novamente.');
    }
  };

  const handleImportPlanilha = async () => {
    if (!selectedFile) return;
    try {
      setImportingPlanilha(true);
      const result = await importPlanilhaFile(selectedFile);
      toast.success(`${result.totalRegistros} transações importadas`);
      router.push(`/mobile/preview/${result.sessionId}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Erro ao importar planilha');
    } finally {
      setImportingPlanilha(false);
    }
  };

  const handleRetryWithPassword = async () => {
    if (!retryPassword.trim()) {
      alert('Por favor, informe a senha');
      return;
    }
    // Atualizar o campo de senha e o formato para pdf-password (ou manter excel)
    // Em seguida resubmeter
    const isExcel = selectedFormat === 'excel';
    if (!isExcel) setSelectedFormat('pdf-password');
    setPassword(retryPassword);
    setShowPasswordPrompt(false);

    // Submeter diretamente com a nova senha
    try {
      let cartaoNome: string | undefined;
      let cartaoFinal: string | undefined;
      if (activeTab === 'fatura' && selectedCard) {
        const cartao = cards.find(c => c.id.toString() === selectedCard);
        if (cartao) { cartaoNome = cartao.name; cartaoFinal = cartao.lastDigits; }
      }
      const result = await upload({
        file: selectedFile!,
        banco: selectedBank,
        tipo: activeTab,
        cartaoId: activeTab === 'fatura' ? selectedCard : undefined,
        cartaoNome,
        cartaoFinal,
        mes: activeTab === 'fatura' ? selectedMonth : undefined,
        ano: activeTab === 'fatura' ? selectedYear : undefined,
        formato: isExcel ? 'excel' : 'pdf-password',
        senha: retryPassword,
      });
      logger.log('✅ [MOBILE-UPLOAD] Upload com senha bem-sucedido! SessionId:', result.sessionId);
      router.push(`/mobile/preview/${result.sessionId}`);
    } catch (error) {
      if (error instanceof PasswordRequiredError) {
        setPasswordPromptMsg('Senha incorreta. Por favor, verifique e tente novamente.');
        setRetryPassword('');
        setShowPasswordPrompt(true);
        return;
      }
      console.error('❌ [MOBILE-UPLOAD] Erro no retry:', error);
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

      {/* Dialog: Arquivo protegido por senha */}
      {showPasswordPrompt && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-xl">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">🔒</span>
              <h2 className="text-base font-bold text-gray-900">Arquivo Protegido</h2>
            </div>
            <p className="text-sm text-gray-500 mb-4">{passwordPromptMsg}</p>

            <div className="mb-6">
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                Senha <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                value={retryPassword}
                onChange={(e) => setRetryPassword(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleRetryWithPassword()}
                placeholder="Digite a senha do arquivo"
                autoFocus
                autoComplete="current-password"
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm text-gray-700 focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900"
              />
              <p className="text-xs text-gray-400 mt-1">
                Para BTG: geralmente é o CPF sem pontos e traço
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowPasswordPrompt(false)}
                className="flex-1 py-3 border border-gray-300 rounded-xl text-sm font-semibold text-gray-700 hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleRetryWithPassword}
                disabled={uploading}
                className="flex-1 py-3 bg-gray-900 rounded-xl text-sm font-bold text-white hover:bg-gray-800 disabled:opacity-50"
              >
                {uploading ? 'Enviando...' : 'Confirmar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Dialog: Adicionar Novo Cartão */}
      {showAddCard && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-xl">
            <h2 className="text-base font-bold text-gray-900 mb-1">Novo Cartão</h2>
            {selectedBank && (
              <p className="text-xs text-gray-400 mb-4">{selectedBank}</p>
            )}

            <div className="mb-4">
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                Nome do Cartão <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={newCardName}
                onChange={(e) => setNewCardName(e.target.value)}
                placeholder="Ex: Itaú Mastercard Black"
                autoFocus
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm text-gray-700 focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900"
              />
            </div>

            <div className="mb-6">
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                Final do Cartão <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                inputMode="numeric"
                maxLength={4}
                value={newCardFinal}
                onChange={(e) => setNewCardFinal(e.target.value.replace(/\D/g, '').slice(0, 4))}
                placeholder="4 dígitos"
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm text-gray-700 focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900 tracking-widest"
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowAddCard(false)}
                disabled={addingCard}
                className="flex-1 py-3 border border-gray-300 rounded-xl text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleSaveNewCard}
                disabled={addingCard}
                className="flex-1 py-3 bg-gray-900 rounded-xl text-sm font-bold text-white hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {addingCard ? 'Salvando...' : 'Adicionar'}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="w-full max-w-md mx-auto">
        
        {/* Header */}
        <header className="bg-white rounded-t-3xl px-6 py-4 flex items-center justify-between border-b border-gray-100">
          <button 
            onClick={() => router.push('/mobile/dashboard')}
            className="text-gray-700 hover:text-gray-900 transition-colors"
            aria-label="Voltar"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path>
            </svg>
          </button>
          <h1 className="text-lg font-bold text-gray-800">Importar Arquivo</h1>
          <button
            onClick={() => router.push('/mobile/profile')}
            className="p-2 rounded-full text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
            aria-label="Perfil e configurações"
          >
            <Settings className="w-5 h-5" />
          </button>
        </header>
        
        {/* Subtitle */}
        <div className="bg-white px-6 py-3 border-b border-gray-100 flex flex-col items-center gap-1">
          <p className="text-xs text-gray-400 text-center">Faça o upload de faturas de cartão ou extratos bancários</p>
          <button
            onClick={() => router.push('/mobile/upload/batch')}
            className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
          >
            Importar vários arquivos →
          </button>
        </div>
        
        {/* Main Content */}
        <div className="bg-white px-6 py-6 rounded-b-3xl">
          
          {/* Tabs */}
          <TabBar 
            activeTab={activeTab}
            onChange={setActiveTab}
          />

          {/* Arquivo — PRIMEIRO: usuário escolhe arquivo antes de preencher o resto */}
          <FileInput 
            fileName={fileName}
            onChange={handleFileChange}
          />
          {detecting && (
            <div className="mb-4 text-sm text-gray-500 flex items-center gap-2">
              <span className="animate-pulse">Detectando banco e período...</span>
            </div>
          )}
          {detection && !detecting && (
            <div className="mb-6">
              <FileDetectionCard
                detection={detection}
                onProceed={() => setDetection(null)}
                onCancel={() => {
                  setSelectedFile(null);
                  setFileName('Nenhum...');
                  setDetection(null);
                }}
                loading={uploading || importingPlanilha}
                onImportPlanilha={detection?.banco === 'generico' && detection?.tipo === 'planilha' ? handleImportPlanilha : undefined}
              />
            </div>
          )}
          
          {/* Instituição Financeira */}
          {loadingBanks ? (
            <div className="mb-6 text-center text-gray-500">Carregando bancos...</div>
          ) : (
            <BankSelector 
              banks={banks}
              value={selectedBank}
              onChange={handleBankChange}
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
                  cards={filteredCards}
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

