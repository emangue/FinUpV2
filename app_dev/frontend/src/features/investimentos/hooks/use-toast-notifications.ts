/**
 * Hook - Toast Notifications para Investimentos
 * Notificações de feedback para ações do usuário
 */

import { useCallback } from 'react'
import { toast } from 'sonner'

type NotificationType = 'success' | 'error' | 'info' | 'warning'

interface ToastOptions {
  title: string
  description?: string
  duration?: number
}

export function useToastNotifications() {
  const show = useCallback((type: NotificationType, options: ToastOptions) => {
    console.log(`[${type.toUpperCase()}] ${options.title}`, options.description)
    const desc = options.description
    if (type === 'error') {
      toast.error(options.title, { description: desc })
    } else if (type === 'success') {
      toast.success(options.title, { description: desc })
    } else if (type === 'warning') {
      toast.warning(options.title, { description: desc })
    } else {
      toast.info(options.title, { description: desc })
    }
  }, [])

  return {
    success: useCallback(
      (options: ToastOptions) => show('success', options),
      [show]
    ),
    error: useCallback(
      (options: ToastOptions) => show('error', options),
      [show]
    ),
    info: useCallback(
      (options: ToastOptions) => show('info', options),
      [show]
    ),
    warning: useCallback(
      (options: ToastOptions) => show('warning', options),
      [show]
    ),
  }
}

/**
 * Mensagens pré-configuradas
 */
export const TOAST_MESSAGES = {
  // Sucesso
  INVESTMENT_ADDED: {
    title: 'Investimento adicionado',
    description: 'O investimento foi cadastrado com sucesso.',
  },
  INVESTMENT_UPDATED: {
    title: 'Investimento atualizado',
    description: 'As alterações foram salvas com sucesso.',
  },
  INVESTMENT_DELETED: {
    title: 'Investimento excluído',
    description: 'O investimento foi removido do portfólio.',
  },
  EXPORT_SUCCESS: {
    title: 'Exportação concluída',
    description: 'O arquivo foi gerado com sucesso.',
  },
  
  // Erro
  LOAD_ERROR: {
    title: 'Erro ao carregar dados',
    description: 'Não foi possível carregar os investimentos. Tente novamente.',
  },
  SAVE_ERROR: {
    title: 'Erro ao salvar',
    description: 'Não foi possível salvar as alterações. Verifique os dados e tente novamente.',
  },
  DELETE_ERROR: {
    title: 'Erro ao excluir',
    description: 'Não foi possível remover o investimento. Tente novamente.',
  },
  EXPORT_ERROR: {
    title: 'Erro na exportação',
    description: 'Não foi possível gerar o arquivo. Tente novamente.',
  },
  
  // Info
  NO_DATA: {
    title: 'Nenhum dado disponível',
    description: 'Não há dados para exibir no período selecionado.',
  },
  FILTERS_APPLIED: {
    title: 'Filtros aplicados',
    description: 'Os resultados foram atualizados conforme os filtros.',
  },
  
  // Warning
  UNSAVED_CHANGES: {
    title: 'Alterações não salvas',
    description: 'Você tem alterações não salvas. Deseja continuar?',
  },
} as const
