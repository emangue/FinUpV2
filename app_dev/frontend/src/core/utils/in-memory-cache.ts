/**
 * Utilitário de cache em memória — módulo isolado por usuário no browser (client-side only).
 * Centraliza o padrão get/set/inFlight usado em múltiplos serviços.
 */

interface CacheEntry<T> {
  data: T
  expiresAt: number
  inFlight?: Promise<T>
}

const store = new Map<string, CacheEntry<unknown>>()

export function getCached<T>(key: string): T | null {
  const entry = store.get(key) as CacheEntry<T> | undefined
  if (!entry) return null
  if (Date.now() > entry.expiresAt) {
    store.delete(key)
    return null
  }
  return entry.data
}

export function setCached<T>(key: string, data: T, ttlMs: number): void {
  const existing = store.get(key) as CacheEntry<T> | undefined
  store.set(key, { data, expiresAt: Date.now() + ttlMs, inFlight: existing?.inFlight })
}

export function getInFlight<T>(key: string): Promise<T> | null {
  const entry = store.get(key) as CacheEntry<T> | undefined
  return entry?.inFlight ?? null
}

export function setInFlight<T>(key: string, promise: Promise<T>): void {
  const existing = store.get(key) as CacheEntry<T> | undefined
  store.set(key, { ...(existing ?? { data: null as T, expiresAt: 0 }), inFlight: promise })
  promise.finally(() => {
    const e = store.get(key) as CacheEntry<T> | undefined
    if (e) store.set(key, { ...e, inFlight: undefined })
  })
}

export function invalidateCache(keyPrefix: string): void {
  for (const key of store.keys()) {
    if (key.startsWith(keyPrefix)) store.delete(key)
  }
}
