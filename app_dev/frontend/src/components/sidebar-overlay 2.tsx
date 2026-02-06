"use client"

import { useEffect, useState } from "react"

export function SidebarOverlay() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  useEffect(() => {
    const handleDropdownChange = (e: CustomEvent) => {
      setIsDropdownOpen(e.detail.open)
    }
    window.addEventListener('dropdown-state-change', handleDropdownChange as EventListener)
    return () => window.removeEventListener('dropdown-state-change', handleDropdownChange as EventListener)
  }, [])

  // Não renderizar no servidor (evita erro de hidratação)
  if (!isMounted || !isDropdownOpen) return null

  return (
    <div 
      className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm"
      onClick={(e) => e.stopPropagation()}
    />
  )
}
