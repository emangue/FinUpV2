/**
 * Hook para Intersection Observer
 * Carrega componentes apenas quando estão visíveis na viewport
 */

import { useEffect, useRef, useState } from 'react'

interface UseIntersectionObserverProps {
  threshold?: number
  root?: Element | null
  rootMargin?: string
  triggerOnce?: boolean
}

export function useIntersectionObserver({
  threshold = 0.1,
  root = null,
  rootMargin = '0px',
  triggerOnce = true,
}: UseIntersectionObserverProps = {}) {
  const [isIntersecting, setIsIntersecting] = useState(false)
  const [hasTriggered, setHasTriggered] = useState(false)
  const targetRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const target = targetRef.current

    if (!target) return

    // Se já foi acionado e é triggerOnce, não faz nada
    if (triggerOnce && hasTriggered) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        const isVisible = entry.isIntersecting
        setIsIntersecting(isVisible)

        if (isVisible && triggerOnce) {
          setHasTriggered(true)
        }
      },
      {
        threshold,
        root,
        rootMargin,
      }
    )

    observer.observe(target)

    return () => {
      observer.disconnect()
    }
  }, [threshold, root, rootMargin, triggerOnce, hasTriggered])

  return {
    ref: targetRef,
    isIntersecting: triggerOnce ? (hasTriggered || isIntersecting) : isIntersecting,
    hasTriggered,
  }
}

/**
 * Hook para lazy loading de componentes pesados
 * Só renderiza o componente quando está visível
 */
export function useLazyRender(delay = 0) {
  const { ref, isIntersecting } = useIntersectionObserver({
    threshold: 0.1,
    triggerOnce: true,
  })

  const [shouldRender, setShouldRender] = useState(false)

  useEffect(() => {
    if (isIntersecting) {
      if (delay > 0) {
        const timer = setTimeout(() => {
          setShouldRender(true)
        }, delay)
        return () => clearTimeout(timer)
      } else {
        setShouldRender(true)
      }
    }
  }, [isIntersecting, delay])

  return {
    ref,
    shouldRender: shouldRender || isIntersecting,
    isIntersecting,
  }
}