"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { X } from "lucide-react"

interface TransactionFiltersProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onApplyFilters: (filters: FilterValues) => void
  currentFilters: FilterValues
}

export interface FilterValues {
  estabelecimento?: string
  grupo?: string
  subgrupo?: string
  tipoGasto?: string
  banco?: string
  mesInicio?: string
  mesFim?: string
}

export function TransactionFilters({
  open,
  onOpenChange,
  onApplyFilters,
  currentFilters
}: TransactionFiltersProps) {
  const [filters, setFilters] = React.useState<FilterValues>(currentFilters)

  React.useEffect(() => {
    setFilters(currentFilters)
  }, [currentFilters])

  const handleApply = () => {
    onApplyFilters(filters)
    onOpenChange(false)
  }

  const handleClear = () => {
    const emptyFilters: FilterValues = {}
    setFilters(emptyFilters)
    onApplyFilters(emptyFilters)
    onOpenChange(false)
  }

  const activeFiltersCount = Object.values(filters).filter(v => v).length

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            Filtros Avançados
            {activeFiltersCount > 0 && (
              <span className="ml-2 text-sm font-normal text-muted-foreground">
                ({activeFiltersCount} {activeFiltersCount === 1 ? 'filtro ativo' : 'filtros ativos'})
              </span>
            )}
          </DialogTitle>
          <DialogDescription>
            Aplique filtros para refinar a busca de transações
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          {/* Estabelecimento */}
          <div className="grid gap-2">
            <Label htmlFor="estabelecimento">Estabelecimento</Label>
            <div className="flex gap-2">
              <Input
                id="estabelecimento"
                placeholder="Digite o nome do estabelecimento..."
                value={filters.estabelecimento || ''}
                onChange={(e) => setFilters({ ...filters, estabelecimento: e.target.value })}
              />
              {filters.estabelecimento && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setFilters({ ...filters, estabelecimento: '' })}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>

          {/* Grupo e Subgrupo */}
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="grupo">Grupo</Label>
              <Select
                value={filters.grupo || ''}
                onValueChange={(value) => setFilters({ ...filters, grupo: value || undefined })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value=" ">Limpar filtro</SelectItem>
                  <SelectItem value="Casa">Casa</SelectItem>
                  <SelectItem value="Carro">Carro</SelectItem>
                  <SelectItem value="Comunicação">Comunicação</SelectItem>
                  <SelectItem value="Educação">Educação</SelectItem>
                  <SelectItem value="Lazer">Lazer</SelectItem>
                  <SelectItem value="Outros">Outros</SelectItem>
                  <SelectItem value="Saúde">Saúde</SelectItem>
                  <SelectItem value="Serviços">Serviços</SelectItem>
                  <SelectItem value="Supermercado">Supermercado</SelectItem>
                  <SelectItem value="Transporte">Transporte</SelectItem>
                  <SelectItem value="Viagens">Viagens</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="subgrupo">Subgrupo</Label>
              <Input
                id="subgrupo"
                placeholder="Digite o subgrupo..."
                value={filters.subgrupo || ''}
                onChange={(e) => setFilters({ ...filters, subgrupo: e.target.value })}
              />
            </div>
          </div>

          {/* Tipo de Gasto */}
          <div className="grid gap-2">
            <Label htmlFor="tipoGasto">Tipo de Gasto</Label>
            <Select
              value={filters.tipoGasto || ''}
              onValueChange={(value) => setFilters({ ...filters, tipoGasto: value || undefined })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Selecione..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value=" ">Limpar filtro</SelectItem>
                <SelectItem value="Alimentação">Alimentação</SelectItem>
                <SelectItem value="Apps e Assinaturas">Apps e Assinaturas</SelectItem>
                <SelectItem value="Cartão de Crédito">Cartão de Crédito</SelectItem>
                <SelectItem value="Combustível">Combustível</SelectItem>
                <SelectItem value="Educação">Educação</SelectItem>
                <SelectItem value="Estacionamento">Estacionamento</SelectItem>
                <SelectItem value="Internet">Internet</SelectItem>
                <SelectItem value="Lazer">Lazer</SelectItem>
                <SelectItem value="Manutenção">Manutenção</SelectItem>
                <SelectItem value="Mercado">Mercado</SelectItem>
                <SelectItem value="Outros">Outros</SelectItem>
                <SelectItem value="Pedágio">Pedágio</SelectItem>
                <SelectItem value="Receita - Outras">Receita - Outras</SelectItem>
                <SelectItem value="Receita - Salário">Receita - Salário</SelectItem>
                <SelectItem value="Restaurante">Restaurante</SelectItem>
                <SelectItem value="Saúde">Saúde</SelectItem>
                <SelectItem value="Seguro">Seguro</SelectItem>
                <SelectItem value="Telefone">Telefone</SelectItem>
                <SelectItem value="Transferência">Transferência</SelectItem>
                <SelectItem value="Transporte">Transporte</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Banco */}
          <div className="grid gap-2">
            <Label htmlFor="banco">Banco</Label>
            <Select
              value={filters.banco || ''}
              onValueChange={(value) => setFilters({ ...filters, banco: value || undefined })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Selecione..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value=" ">Limpar filtro</SelectItem>
                <SelectItem value="Itaú">Itaú</SelectItem>
                <SelectItem value="BTG">BTG</SelectItem>
                <SelectItem value="Mercado Pago">Mercado Pago</SelectItem>
                <SelectItem value="Bradesco">Bradesco</SelectItem>
                <SelectItem value="Santander">Santander</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Período */}
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="mesInicio">Mês Início</Label>
              <Input
                id="mesInicio"
                type="month"
                value={filters.mesInicio || ''}
                onChange={(e) => setFilters({ ...filters, mesInicio: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="mesFim">Mês Fim</Label>
              <Input
                id="mesFim"
                type="month"
                value={filters.mesFim || ''}
                onChange={(e) => setFilters({ ...filters, mesFim: e.target.value })}
              />
            </div>
          </div>
        </div>

        <DialogFooter className="flex gap-2">
          <Button variant="outline" onClick={handleClear}>
            Limpar Filtros
          </Button>
          <Button onClick={handleApply}>
            Aplicar Filtros
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}