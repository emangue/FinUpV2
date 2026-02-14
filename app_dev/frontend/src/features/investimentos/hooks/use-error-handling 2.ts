/**
 * Hooks para tratamento robusto de erros e recovery
 */

'use client'

import { useState, useEffect, useCallback, useRef } from 'react'

export interface ErrorInfo {
  message: string
  stack?: string
  componentStack?: string
  errorBoundary?: boolean
  timestamp: Date
  retryCount?: number
}

export interface UseErrorHandlerOptions {
  maxRetries?: number
  retryDelay?: number
  onError?: (error: ErrorInfo) => void
  enableLogging?: boolean
}

/**
 * Hook principal para tratamento de erros
 */
export function useErrorHandler(options: UseErrorHandlerOptions = {}) {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    onError,
    enableLogging = true
  } = options

  const [errors, setErrors] = useState<ErrorInfo[]>([])
  const [isRecovering, setIsRecovering] = useState(false)
  const retryTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined)

  const logError = useCallback((error: ErrorInfo) => {
    if (enableLogging) {
      console.error('Error captured:', error)
    }
    if (onError) {
      onError(error)
    }
  }, [enableLogging, onError])

  const addError = useCallback((error: Error | string, context?: any) => {
    const errorInfo: ErrorInfo = {
      message: typeof error === 'string' ? error : error.message,
      stack: typeof error !== 'string' ? error.stack : undefined,
      timestamp: new Date(),
      retryCount: 0,
      ...context
    }

    setErrors(prev => [errorInfo, ...prev.slice(0, 9)]) // Manter últimos 10 erros
    logError(errorInfo)
  }, [logError])

  const clearErrors = useCallback(() => {
    setErrors([])
    setIsRecovering(false)
  }, [])

  const retryOperation = useCallback(async (
    operation: () => Promise<any>,
    context?: string
  ) => {
    let lastError: Error | null = null
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        setIsRecovering(true)
        const result = await operation()
        setIsRecovering(false)
        return result
      } catch (error) {
        lastError = error as Error
        
        if (attempt < maxRetries) {
          await new Promise(resolve => 
            setTimeout(resolve, retryDelay * attempt)
          )
        }
      }
    }

    setIsRecovering(false)
    addError(lastError!, { 
      context, 
      retryCount: maxRetries,
      message: `Failed after ${maxRetries} attempts: ${lastError?.message}`
    })
    
    throw lastError
  }, [maxRetries, retryDelay, addError])

  useEffect(() => {
    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current)
      }
    }
  }, [])

  return {
    errors,
    isRecovering,
    addError,
    clearErrors,
    retryOperation,
    hasErrors: errors.length > 0,
    latestError: errors[0] || null
  }
}

/**
 * Hook para async operations com error handling
 */
export function useAsyncError() {
  const [error, setError] = useState<Error | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const execute = useCallback(async <T>(
    asyncOperation: () => Promise<T>,
    onSuccess?: (result: T) => void,
    onError?: (error: Error) => void
  ) => {
    try {
      setIsLoading(true)
      setError(null)
      
      const result = await asyncOperation()
      
      if (onSuccess) {
        onSuccess(result)
      }
      
      return result
    } catch (err) {
      const error = err as Error
      setError(error)
      
      if (onError) {
        onError(error)
      }
      
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    execute,
    error,
    isLoading,
    clearError,
    hasError: error !== null
  }
}

/**
 * Hook para retry com backoff exponencial
 */
export function useRetryWithBackoff() {
  const [isRetrying, setIsRetrying] = useState(false)
  const [retryCount, setRetryCount] = useState(0)

  const retry = useCallback(async <T>(
    operation: () => Promise<T>,
    maxRetries: number = 3,
    baseDelay: number = 1000
  ): Promise<T> => {
    setIsRetrying(true)
    setRetryCount(0)

    let lastError: Error

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        setRetryCount(attempt)
        const result = await operation()
        setIsRetrying(false)
        setRetryCount(0)
        return result
      } catch (error) {
        lastError = error as Error
        
        if (attempt < maxRetries) {
          const delay = baseDelay * Math.pow(2, attempt) // Backoff exponencial
          await new Promise(resolve => setTimeout(resolve, delay))
        }
      }
    }

    setIsRetrying(false)
    setRetryCount(0)
    throw lastError!
  }, [])

  return {
    retry,
    isRetrying,
    retryCount
  }
}

/**
 * Hook para fallback de dados em caso de erro
 */
export function useFallbackData<T>(
  primaryLoader: () => Promise<T>,
  fallbackData: T | (() => T),
  options: {
    enableCache?: boolean
    cacheKey?: string
    maxAge?: number
  } = {}
) {
  const { enableCache = true, cacheKey = 'fallback', maxAge = 300000 } = options
  
  const [data, setData] = useState<T | null>(null)
  const [isUsingFallback, setIsUsingFallback] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const cacheRef = useRef<Map<string, { data: T; timestamp: number }>>(new Map())

  const getFallback = useCallback(() => {
    return typeof fallbackData === 'function' ? (fallbackData as Function)() : fallbackData
  }, [fallbackData])

  const loadData = useCallback(async () => {
    try {
      setError(null)
      setIsUsingFallback(false)

      // Verificar cache primeiro
      if (enableCache && cacheKey) {
        const cached = cacheRef.current.get(cacheKey)
        if (cached && Date.now() - cached.timestamp < maxAge) {
          setData(cached.data)
          return cached.data
        }
      }

      const result = await primaryLoader()
      
      // Salvar no cache
      if (enableCache && cacheKey) {
        cacheRef.current.set(cacheKey, {
          data: result,
          timestamp: Date.now()
        })
      }

      setData(result)
      return result
    } catch (err) {
      const error = err as Error
      setError(error)
      setIsUsingFallback(true)
      
      const fallback = getFallback()
      setData(fallback)
      return fallback
    }
  }, [primaryLoader, enableCache, cacheKey, maxAge, getFallback])

  return {
    data,
    error,
    isUsingFallback,
    loadData,
    clearCache: useCallback(() => {
      if (cacheKey) {
        cacheRef.current.delete(cacheKey)
      }
    }, [cacheKey])
  }
}

/**
 * Hook para network error handling
 */
export function useNetworkError() {
  const [isOnline, setIsOnline] = useState(typeof navigator !== 'undefined' ? navigator.onLine : true)
  const [networkError, setNetworkError] = useState<string | null>(null)

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      setNetworkError(null)
    }

    const handleOffline = () => {
      setIsOnline(false)
      setNetworkError('Sem conexão com a internet')
    }

    if (typeof window !== 'undefined') {
      window.addEventListener('online', handleOnline)
      window.addEventListener('offline', handleOffline)

      return () => {
        window.removeEventListener('online', handleOnline)
        window.removeEventListener('offline', handleOffline)
      }
    }
  }, [])

  const checkNetworkError = useCallback((error: Error) => {
    if (!isOnline) {
      setNetworkError('Sem conexão com a internet')
      return true
    }

    // Verificar se é erro de rede
    if (
      error.message.includes('fetch') ||
      error.message.includes('network') ||
      error.message.includes('Failed to fetch')
    ) {
      setNetworkError('Erro de conexão com o servidor')
      return true
    }

    return false
  }, [isOnline])

  return {
    isOnline,
    networkError,
    checkNetworkError,
    clearNetworkError: () => setNetworkError(null)
  }
}