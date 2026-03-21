'use client';

/**
 * Preview Mobile - Página de Pré-visualização (APIs Reais)
 * 
 * Conectado com backend:
 * - usePreviewData → GET /api/v1/upload/preview/{sessionId}
 */

import { use } from 'react';
import { useRouter } from 'next/navigation';
import { logger } from '@/lib/logger';
import { usePreviewData } from '@/features/upload/hooks';
import PreviewLayout from '@/features/preview/templates/PreviewLayout';

interface PreviewPageProps {
  params: Promise<{ sessionId: string }>;
}

export default function PreviewPage({ params }: PreviewPageProps) {
  const router = useRouter();
  const resolvedParams = use(params);
  const sessionId = resolvedParams.sessionId;
  
  const { data, loading, error } = usePreviewData(sessionId);

  if (loading) {
    return (
      <div className="max-w-md mx-auto bg-white min-h-screen shadow-lg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando preview...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-md mx-auto bg-white min-h-screen shadow-lg flex items-center justify-center p-6">
        <div className="text-center">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Erro ao carregar preview</h2>
          <p className="text-gray-600 mb-4">{error || 'Dados não encontrados'}</p>
          <button
            onClick={() => router.push('/mobile/upload')}
            className="px-6 py-3 bg-gray-900 text-white rounded-xl font-medium"
          >
            Voltar para Upload
          </button>
        </div>
      </div>
    );
  }

  // Mapeamento de origem_classificacao (API) para source (componentes)
  const mapSourceToEnum = (origem: string): 'base_parcelas' | 'base_padroes' | 'journal_entries' | 'regras_genericas' | 'manual' | 'not_classified' => {
    if (!origem) return 'not_classified';
    
    const map: Record<string, 'base_parcelas' | 'base_padroes' | 'journal_entries' | 'regras_genericas' | 'manual' | 'not_classified'> = {
      'Base Parcelas': 'base_parcelas',
      'Base Padrões': 'base_padroes',
      'Journal Entries': 'journal_entries',
      'Regras Genéricas': 'regras_genericas',
      'Manual': 'manual',
      'Não Classificado': 'not_classified',
    };
    
    return map[origem] || 'not_classified';
  };

  // DEBUG: Log dos dados recebidos do backend
  logger.log('🔍 DEBUG - Dados recebidos do backend:', data);
  logger.log('🔍 DEBUG - Primeiro registro:', data.dados?.[0]);

  // Converter dados da API para formato do componente (transações individuais)
  const individualTransactions = (data.dados || []).map((tx: any) => {
    const valor = parseFloat(tx.Valor || tx.valor || 0);
    
    return {
      id: tx.id.toString(),
      date: tx.Data || tx.data,
      description: tx.Lancamento || tx.lancamento,
      value: valor,
      type: (tx.CategoriaGeral || tx.categoria_geral) === 'Receita' ? 'receita' as const : 'despesa' as const,
      grupo: (tx.grupo ?? tx.GRUPO ?? '').toString().trim(),
      subgrupo: (tx.subgrupo ?? tx.SUBGRUPO ?? '').toString().trim(),
      source: mapSourceToEnum(tx.origem_classificacao),
      isDuplicate: tx.is_duplicate || false,
    };
  });

  // AGRUPAR transações por description + grupo + subgrupo + isDuplicate
  // Duplicatas formam grupos SEPARADOS das transações novas
  const groupedMap = new Map<string, typeof individualTransactions>();
  
  individualTransactions.forEach(tx => {
    // Chave única: description + grupo + subgrupo + isDuplicate (separa duplicatas de novas)
    const key = `${tx.description}|${tx.grupo || ''}|${tx.subgrupo || ''}|${tx.isDuplicate ? '1' : '0'}`;
    if (!groupedMap.has(key)) {
      groupedMap.set(key, []);
    }
    groupedMap.get(key)!.push(tx);
  });

  // Converter grupos para formato com occurrences e items
  const transactions = Array.from(groupedMap.entries())
    .map(([key, items]) => {
      if (items.length === 1) {
        // Transação única - retornar como está
        return items[0];
      } else {
        // Grupo de transações - criar estrutura agrupada
        const totalValue = items.reduce((sum, item) => sum + item.value, 0);
        const firstItem = items[0];
        
        return {
          id: `group-${key}`,
          date: '', // Grupos não têm data específica
          description: firstItem.description,
          value: totalValue,
          type: firstItem.type,
          grupo: firstItem.grupo || '',
          subgrupo: firstItem.subgrupo || '',
          source: firstItem.source,
          // isDuplicate verdadeiro apenas se TODOS os itens do grupo são duplicatas
          isDuplicate: items.every(i => i.isDuplicate === true),
          occurrences: items.length,
          items: items, // Itens individuais dentro do grupo
        };
      }
    })
    // Ordenar por valor decrescente (maior gasto primeiro)
    .sort((a, b) => b.value - a.value);

  logger.log('🔍 DEBUG - Transações agrupadas:', transactions);
  logger.log('🔍 DEBUG - Total de grupos/transações:', transactions.length);

  // Calcular soma total (usando transações individuais)
  const somaTotal = individualTransactions.reduce((sum, tx) => sum + tx.value, 0);

  const fileInfo = {
    banco: data.banco || 'Banco desconhecido',
    cartao: data.nome_cartao || 'N/A',
    arquivo: data.nome_arquivo || 'arquivo.csv',
    mesFatura: data.mes_fatura || 'N/A',
    totalLancamentos: data.totalRegistros || 0,
    somaTotal: somaTotal,
    tipoDocumento: data.tipo_documento || 'fatura',
  };

  return (
    <PreviewLayout
      sessionId={sessionId}
      initialFileInfo={fileInfo}
      initialTransactions={transactions}
    />
  );
}
