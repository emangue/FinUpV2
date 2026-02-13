'use client';

import { useState, useEffect } from 'react';
import { Transaction, TabFilter, ClassificationData, FileInfo } from '../types';
import { calculateStats, generateTabs, setGruposSubgrupos } from '../lib/constants';
import PreviewHeader from '../molecules/PreviewHeader';
import Alert from '../atoms/Alert';
import FileInfoCard from '../molecules/FileInfoCard';
import TabBar from '../molecules/TabBar';
import TransactionList from '../organisms/TransactionList';
import BottomActionBar from '../organisms/BottomActionBar';
import ClassificationModal from '../molecules/ClassificationModal';
import { API_CONFIG } from '@/core/config/api.config';
import { fetchWithAuth } from '@/core/utils/api-client';

interface PreviewLayoutProps {
  sessionId: string;
  initialFileInfo: FileInfo;
  initialTransactions: Transaction[];
}

export default function PreviewLayout({ initialFileInfo, initialTransactions }: PreviewLayoutProps) {
  const [transactions, setTransactions] = useState<Transaction[]>(initialTransactions);
  const [activeTab, setActiveTab] = useState<TabFilter>('all');
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [gruposLoaded, setGruposLoaded] = useState(false);

  // Buscar grupos e subgrupos da API na montagem do componente
  useEffect(() => {
    const fetchGruposSubgrupos = async () => {
      try {
        const response = await fetchWithAuth(`${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/categories/grupos-subgrupos`);
        
        if (response.ok) {
          const data = await response.json();
          console.log('🔍 DEBUG - Resposta da API grupos-subgrupos:', data);
          setGruposSubgrupos(data);
          setGruposLoaded(true);
        } else {
          console.error('❌ Erro ao buscar grupos/subgrupos:', response.status);
        }
      } catch (err) {
        console.error('❌ Erro ao buscar grupos/subgrupos:', err);
      }
    };

    fetchGruposSubgrupos();
  }, []);

  const stats = calculateStats(transactions);
  const tabs = generateTabs(stats);
  const hasUnclassified = stats.naoClassificadas > 0;

  // Mostrar loading enquanto carrega grupos
  if (!gruposLoaded) {
    return (
      <div className="max-w-md mx-auto bg-white min-h-screen shadow-lg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando categorias...</p>
        </div>
      </div>
    );
  }

  const handleEditTransaction = (transaction: Transaction) => {
    setSelectedTransaction(transaction);
    setIsModalOpen(true);
  };

  const handleSaveClassification = (data: ClassificationData) => {
    if (!selectedTransaction) return;

    setTransactions((prev) =>
      prev.map((tx) => {
        // Se for uma transação individual dentro de um grupo
        if (tx.items) {
          return {
            ...tx,
            items: tx.items.map((item) =>
              item.id === selectedTransaction.id
                ? { ...item, grupo: data.grupo, subgrupo: data.subgrupo, source: 'manual' }
                : item
            ),
          };
        }
        // Se for uma transação única
        return tx.id === selectedTransaction.id
          ? { ...tx, grupo: data.grupo, subgrupo: data.subgrupo, source: 'manual' }
          : tx;
      })
    );

    setIsModalOpen(false);
    setSelectedTransaction(null);
  };

  const handleBatchUpdate = (transactionId: string, grupo: string, subgrupo: string) => {
    if (!grupo || !subgrupo) return;

    setTransactions((prev) =>
      prev.map((tx) =>
        tx.id === transactionId
          ? { ...tx, grupo, subgrupo, source: 'manual' }
          : tx
      )
    );
  };

  const handleConfirmImport = () => {
    if (hasUnclassified) return;
    alert('✅ Importação confirmada com sucesso!');
    console.log('Transações para importar:', transactions);
  };

  const handleCancel = () => {
    if (confirm('Deseja cancelar a importação? Todas as alterações serão perdidas.')) {
      alert('Importação cancelada');
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white min-h-screen shadow-lg relative">
      <PreviewHeader onCancel={handleCancel} />

      <div className="pb-20">
        {/* Alert */}
        {hasUnclassified && (
          <div className="mx-4 mt-4">
            <Alert
              title={`${stats.naoClassificadas} transações sem classificação`}
              message={`Complete a classificação antes de confirmar a importação. ${stats.classificadas} de ${stats.total} transações já classificadas.`}
              variant="warning"
            />
          </div>
        )}

        {/* File Info */}
        <div className="mx-4 mt-4">
          <FileInfoCard fileInfo={initialFileInfo} />
        </div>

        {/* Transactions Section */}
        <div className="mt-6">
          <div className="px-4 mb-3">
            <h2 className="font-bold text-gray-900 text-lg">Lançamentos Detectados</h2>
            <p className="text-sm text-gray-600 mt-0.5">
              {stats.naoClassificadas} de {stats.total} lançamentos
            </p>
          </div>

          {/* Tabs */}
          <div className="px-4 mb-3">
            <TabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
          </div>

          {/* Transaction List */}
          <TransactionList
            transactions={transactions}
            activeTab={activeTab}
            onEdit={handleEditTransaction}
            onBatchUpdate={handleBatchUpdate}
          />
        </div>
      </div>

      {/* Bottom Action Bar */}
      <BottomActionBar hasUnclassified={hasUnclassified} onConfirm={handleConfirmImport} />

      {/* Classification Modal */}
      {selectedTransaction && (
        <ClassificationModal
          transaction={selectedTransaction}
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedTransaction(null);
          }}
          onSave={handleSaveClassification}
        />
      )}
    </div>
  );
}
