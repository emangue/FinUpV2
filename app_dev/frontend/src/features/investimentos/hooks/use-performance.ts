/**
 * Hook para otimização de performance
 * Debouncing, throttling, e memoização avançada
 */

import { useRef, useEffect, useCallback, useMemo, useState } from 'react'

/**
 * Hook de debounce para evitar execução excessiva de funções
 */
export function useDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
) {
  const timeoutRef = useRef<NodeJS.Timeout | undefined>(undefined)

  const debouncedCallback = useCallback(
    (...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }

      timeoutRef.current = setTimeout(() => {
        callback(...args)
      }, delay)
    },
    [callback, delay]
  )

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return debouncedCallback
}

/**
 * Hook de throttle para limitar frequência de execução
 */
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
) {
  const isThrottling = useRef(false)

  const throttledCallback = useCallback(
    (...args: Parameters<T>) => {
      if (isThrottling.current) return

      callback(...args)
      isThrottling.current = true

      setTimeout(() => {
        isThrottling.current = false
      }, delay)
    },
    [callback, delay]
  )

  return throttledCallback
}

/**
 * Hook para memoização profunda de objetos complexos
 */
export function useDeepMemo<T>(value: T, deps: React.DependencyList): T {
  const ref = useRef<T>(value)

  return useMemo(() => {
    // Comparação profunda simples (para objetos pequenos/médios)
    if (JSON.stringify(ref.current) !== JSON.stringify(value)) {
      ref.current = value
    }
    return ref.current
  }, deps)
}

/**
 * Hook para paginação virtual de listas grandes
 */
export function useVirtualPagination<T>(
  items: T[],
  itemsPerPage: number = 50
) {
  const [currentPage, setCurrentPage] = useState(1)

  const totalPages = Math.ceil(items.length / itemsPerPage)
  
  const paginatedItems = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    const endIndex = startIndex + itemsPerPage
    return items.slice(startIndex, endIndex)
  }, [items, currentPage, itemsPerPage])

  const goToPage = useCallback((page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)))
  }, [totalPages])

  const nextPage = useCallback(() => {
    goToPage(currentPage + 1)
  }, [currentPage, goToPage])

  const prevPage = useCallback(() => {
    goToPage(currentPage - 1)
  }, [currentPage, goToPage])

  return {
    currentPage,
    totalPages,
    paginatedItems,
    goToPage,
    nextPage,
    prevPage,
    hasNext: currentPage < totalPages,
    hasPrev: currentPage > 1
  }
}

/**
 * Hook para otimização de scroll em listas grandes
 */
export function useVirtualScroll<T>(
  items: T[],
  itemHeight: number,
  containerHeight: number,
  overscan: number = 5
) {
  const [scrollTop, setScrollTop] = useState(0)

  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan)
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  )

  const visibleItems = useMemo(() => {
    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      item,
      index: startIndex + index
    }))
  }, [items, startIndex, endIndex])

  const totalHeight = items.length * itemHeight
  const offsetY = startIndex * itemHeight

  const handleScroll = useThrottle((event: React.UIEvent<HTMLElement>) => {
    setScrollTop(event.currentTarget.scrollTop)
  }, 16) // ~60fps

  return {
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll,
    startIndex,
    endIndex
  }
}

/**
 * Hook para otimização de re-renders usando shouldUpdate
 */
export function useOptimizedRender<T>(
  props: T,
  compareFunction?: (prevProps: T, nextProps: T) => boolean
) {
  const prevPropsRef = useRef<T>(props)
  const shouldUpdate = useRef(true)

  const defaultCompare = useCallback((prev: T, next: T) => {
    return JSON.stringify(prev) !== JSON.stringify(next)
  }, [])

  const compare = compareFunction || defaultCompare

  if (compare(prevPropsRef.current, props)) {
    shouldUpdate.current = true
    prevPropsRef.current = props
  } else {
    shouldUpdate.current = false
  }

  return shouldUpdate.current
}

/**
 * Hook para cache em memória com TTL
 */
export function useMemoryCache<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl: number = 300000 // 5 minutos default
) {
  const cache = useRef<Map<string, { data: T; timestamp: number }>>(new Map())
  
  const getCachedData = useCallback(async () => {
    const now = Date.now()
    const cached = cache.current.get(key)

    if (cached && now - cached.timestamp < ttl) {
      return cached.data
    }

    const data = await fetcher()
    cache.current.set(key, { data, timestamp: now })
    
    return data
  }, [key, fetcher, ttl])

  const invalidateCache = useCallback(() => {
    cache.current.delete(key)
  }, [key])

  const clearCache = useCallback(() => {
    cache.current.clear()
  }, [])

  return {
    getCachedData,
    invalidateCache,
    clearCache
  }
}

/**
 * Hook para batch updates (agrupa múltiplas atualizações)
 */
export function useBatchUpdates<T>(
  initialValue: T,
  batchDelay: number = 100
) {
  const [value, setValue] = useState(initialValue)
  const pendingUpdates = useRef<Partial<T>[]>([])
  const timeoutRef = useRef<NodeJS.Timeout | undefined>(undefined)

  const batchUpdate = useCallback((updates: Partial<T>) => {
    pendingUpdates.current.push(updates)

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    timeoutRef.current = setTimeout(() => {
      const mergedUpdates = pendingUpdates.current.reduce(
        (acc, update) => ({ ...acc, ...update }),
        {} as Partial<T>
      )

      setValue(prev => ({ ...prev, ...mergedUpdates }))
      pendingUpdates.current = []
    }, batchDelay)
  }, [batchDelay])

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return [value, batchUpdate] as const
}