'use client'

/**
 * Componente - Filtros de Investimentos
 * Busca e filtros para tabela de investimentos
 */

import React from 'react'
import { Search, X } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface InvestmentFiltersProps {
  searchTerm: string
  onSearchChange: (value: string) => void
  selectedType: string
  onTypeChange: (value: string) => void
  selectedCorretora: string
  onCorretoraChange: (value: string) => void
  types: string[]
  corretoras: string[]
  onClearFilters: () => void
}

export function InvestmentFilters({
  searchTerm,
  onSearchChange,
  selectedType,
  onTypeChange,
  selectedCorretora,
  onCorretoraChange,
  types,
  corretoras,
  onClearFilters,
}: InvestmentFiltersProps) {
  const hasActiveFilters = searchTerm || selectedType !== 'all' || selectedCorretora !== 'all'

  return (
    <div className="flex items-center gap-3">
      {/* Busca por nome */}
      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Buscar investimento..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-9"
        />
        {searchTerm && (
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-1 top-1/2 h-7 w-7 -translate-y-1/2 p-0"
            onClick={() => onSearchChange('')}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Filtro por tipo */}
      <Select value={selectedType} onValueChange={onTypeChange}>
        <SelectTrigger className="w-[200px]">
          <SelectValue placeholder="Tipo de investimento" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Todos os tipos</SelectItem>
          {types.map((type) => (
            <SelectItem key={type} value={type}>
              {type}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Filtro por corretora */}
      <Select value={selectedCorretora} onValueChange={onCorretoraChange}>
        <SelectTrigger className="w-[200px]">
          <SelectValue placeholder="Corretora" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Todas as corretoras</SelectItem>
          {corretoras.map((corretora) => (
            <SelectItem key={corretora} value={corretora}>
              {corretora}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Limpar filtros */}
      {hasActiveFilters && (
        <Button variant="outline" size="sm" onClick={onClearFilters}>
          <X className="mr-2 h-4 w-4" />
          Limpar filtros
        </Button>
      )}
    </div>
  )
}
