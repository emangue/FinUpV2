'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Transaction, TabFilter, ClassificationData, FileInfo, ClassificationSource } from '../types';

/**
 * Reagrupa transações por description|grupo|subgrupo.
 * Quando uma transação é editada com nova marcação, ela sai do grupo original
 * e aparece em uma nova caixa com sua nova classificação.
 */
function regroupTransactions(transactions: Transaction[]): Transaction[] {
  const flat: Transaction[] = [];
  for (const tx of transactions) {
    if (tx.items && tx.items.length > 0) {
      flat.push(...tx.items);
    } else {
      flat.push(tx);
    }
  }

  const groupedMap = new Map<string, Transaction[]>();
  flat.forEach((tx) => {
    const key = `${tx.description}|${tx.grupo || ''}|${tx.subgrupo || ''}`;
    if (!groupedMap.has(key)) groupedMap.set(key, []);
    groupedMap.get(key)!.push(tx);
  });

  return Array.from(groupedMap.entries())
    .map(([, items]) => {
      if (items.length === 1) {
        return items[0];
      }
      const totalValue = items.reduce((sum, item) => sum + item.value, 0);
      const firstItem = items[0];
      const groupKey = `${firstItem.description}|${firstItem.grupo || ''}|${firstItem.subgrupo || ''}`;
      return {
        ...firstItem,
        id: `group-${groupKey}`,
        date: '',
        description: firstItem.description,
        value: totalValue,
        grupo: firstItem.grupo || '',
        subgrupo: firstItem.subgrupo || '',
        source: firstItem.source,
        isDuplicate: false,
        occurrences: items.length,
        items,
      };
    })
    .sort((a, b) => b.value - a.value);
}
import { calculateStats, generateTabs, setGruposSubgrupos, GRUPOS } from '../lib/constants';
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

export default function PreviewLayout({ sessionId, initialFileInfo, initialTransactions }: PreviewLayoutProps) {
  const router = useRouter();
  const [transactions, setTransactions] = useState<Transaction[]>(initialTransactions);
  const [activeTab, setActiveTab] = useState<TabFilter>('all');
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [gruposLoaded, setGruposLoaded] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [, setGroupsRefreshKey] = useState(0);

  const fetchGruposSubgrupos = async () => {
    try {
      const response = await fetchWithAuth(`${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/categories/grupos-subgrupos`);
      
      if (response.ok) {
        const data = await response.json();
        setGruposSubgrupos(data);
        setGruposLoaded(true);
      } else {
        console.error('❌ Erro ao buscar grupos/subgrupos:', response.status);
      }
    } catch (err) {
      console.error('❌ Erro ao buscar grupos/subgrupos:', err);
    }
  };

  const handleGroupAdded = async () => {
    await fetchGruposSubgrupos();
    setGroupsRefreshKey((k) => k + 1);
  };

  // Buscar grupos e subgrupos da API na montagem do componente
  useEffect(() => {
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

  const handleSaveClassification = async (data: ClassificationData) => {
    if (!selectedTransaction || !data.grupo || !data.subgrupo) return;

    const previewId = selectedTransaction.id;
    const baseUrl = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/preview/${sessionId}`;
    try {
      await fetchWithAuth(
        `${baseUrl}/${previewId}?grupo=${encodeURIComponent(data.grupo)}&subgrupo=${encodeURIComponent(data.subgrupo)}`,
        { method: 'PATCH' }
      );
    } catch (err) {
      console.error('Erro ao salvar classificação:', err);
      alert('Erro ao salvar. Tente novamente.');
      return;
    }

    setTransactions((prev) => {
      const updated = prev.map((tx) => {
        if (tx.items) {
          return {
            ...tx,
            items: tx.items.map((item) =>
              item.id === selectedTransaction.id
                ? { ...item, grupo: data.grupo, subgrupo: data.subgrupo, source: 'manual' as ClassificationSource }
                : item
            ),
          };
        }
        return tx.id === selectedTransaction.id
          ? { ...tx, grupo: data.grupo, subgrupo: data.subgrupo, source: 'manual' as ClassificationSource }
          : tx;
      });
      // Reagrupar: transação editada com nova marcação sai do grupo e aparece em nova caixa
      return regroupTransactions(updated as Transaction[]);
    });

    setIsModalOpen(false);
    setSelectedTransaction(null);
  };

  const handleBatchUpdate = async (transactionId: string, grupo: string, subgrupo: string) => {
    if (!grupo || !subgrupo) return;

    const tx = transactions.find((t) => t.id === transactionId);
    if (!tx) return;

    // IDs para persistir no backend (preview_transacoes)
    const previewIds: string[] = tx.items && tx.items.length > 0
      ? tx.items.map((item) => item.id)
      : [transactionId];

    // Persistir no backend para que o confirm leia os dados atualizados
    const baseUrl = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/preview/${sessionId}`;
    try {
      await Promise.all(
        previewIds.map((id) =>
          fetchWithAuth(`${baseUrl}/${id}?grupo=${encodeURIComponent(grupo)}&subgrupo=${encodeURIComponent(subgrupo)}`, {
            method: 'PATCH',
          })
        )
      );
    } catch (err) {
      console.error('Erro ao salvar classificação no preview:', err);
      alert('Erro ao salvar. Tente novamente.');
      return;
    }

    setTransactions((prev) =>
      prev.map((t) => {
        if (t.id !== transactionId) return t;
        const manual: ClassificationSource = 'manual';
        if (t.items && t.items.length > 0) {
          return {
            ...t,
            grupo,
            subgrupo,
            source: manual,
            items: t.items.map((item) => ({ ...item, grupo, subgrupo, source: manual })),
          };
        }
        return { ...t, grupo, subgrupo, source: manual };
      })
    );
  };

  const handleConfirmImport = async () => {
    if (hasUnclassified) return;
    
    setIsConfirming(true);
    
    try {
      const response = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/upload/confirm/${sessionId}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Upload confirmado:', data);
        
        // Navegar para dashboard
        router.push('/mobile/dashboard');
      } else {
        const error = await response.json();
        console.error('❌ Erro ao confirmar upload:', error);
        alert(`Erro ao confirmar importação: ${error.message || 'Erro desconhecido'}`);
      }
    } catch (error) {
      console.error('❌ Erro ao confirmar upload:', error);
      alert('Erro ao confirmar importação. Tente novamente.');
    } finally {
      setIsConfirming(false);
    }
  };

  const handleCancel = () => {
    if (confirm('Deseja cancelar a importação? Todas as alterações serão perdidas.')) {
      alert('Importação cancelada');
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white min-h-screen shadow-lg relative">
      <PreviewHeader onCancel={handleCancel} />

      <div className="pb-52">
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
            onGroupAdded={handleGroupAdded}
            existingGroups={GRUPOS}
          />
        </div>
      </div>

      {/* Bottom Action Bar */}
      <BottomActionBar 
        hasUnclassified={hasUnclassified} 
        onConfirm={handleConfirmImport}
        isLoading={isConfirming}
      />

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
