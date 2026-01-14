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
                  <SelectItem value="Alimentação">Alimentação</SelectItem>
                  <SelectItem value="Assinaturas">Assinaturas</SelectItem>
                  <SelectItem value="Carro">Carro</SelectItem>
                  <SelectItem value="Casa">Casa</SelectItem>
                  <SelectItem value="Doações">Doações</SelectItem>
                  <SelectItem value="Educação">Educação</SelectItem>
                  <SelectItem value="Entretenimento">Entretenimento</SelectItem>
                  <SelectItem value="Limpeza">Limpeza</SelectItem>
                  <SelectItem value="MeLi + Amazon">MeLi + Amazon</SelectItem>
                  <SelectItem value="Outros">Outros</SelectItem>
                  <SelectItem value="Presentes">Presentes</SelectItem>
                  <SelectItem value="Roupas">Roupas</SelectItem>
                  <SelectItem value="Salário">Salário</SelectItem>
                  <SelectItem value="Saúde">Saúde</SelectItem>
                  <SelectItem value="Serviços">Serviços</SelectItem>
                  <SelectItem value="Tecnologia">Tecnologia</SelectItem>
                  <SelectItem value="Transporte">Transporte</SelectItem>
                  <SelectItem value="Viagens">Viagens</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="subgrupo">Subgrupo</Label>
              <Select
                value={filters.subgrupo || ''}
                onValueChange={(value) => setFilters({ ...filters, subgrupo: value || undefined })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione..." />
                </SelectTrigger>
                <SelectContent className="max-h-[300px]">
                  <SelectItem value=" ">Limpar filtro</SelectItem>
                  <SelectItem value="Casa">Casa</SelectItem>
                  <SelectItem value="Combustível">Combustível</SelectItem>
                  <SelectItem value="Condomínio">Condomínio</SelectItem>
                  <SelectItem value="EUA">EUA</SelectItem>
                  <SelectItem value="Energia">Energia</SelectItem>
                  <SelectItem value="Estacionamento">Estacionamento</SelectItem>
                  <SelectItem value="Foz do Iguaçu">Foz do Iguaçu</SelectItem>
                  <SelectItem value="Internet">Internet</SelectItem>
                  <SelectItem value="Madrid">Madrid</SelectItem>
                  <SelectItem value="MeLi + Amazon">MeLi + Amazon</SelectItem>
                  <SelectItem value="Outros">Outros</SelectItem>
                  <SelectItem value="Portugal">Portugal</SelectItem>
                  <SelectItem value="Saúde">Saúde</SelectItem>
                  <SelectItem value="Supermercado">Supermercado</SelectItem>
                  <SelectItem value="Viagens">Viagens</SelectItem>
                  <SelectItem value="Vitoria">Vitoria</SelectItem>
                </SelectContent>
              </Select>
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
                <SelectItem value="Ajustável - Alimentação">Ajustável - Alimentação</SelectItem>
                <SelectItem value="Ajustável - Assinaturas">Ajustável - Assinaturas</SelectItem>
                <SelectItem value="Ajustável - Carro">Ajustável - Carro</SelectItem>
                <SelectItem value="Ajustável - Casa">Ajustável - Casa</SelectItem>
                <SelectItem value="Ajustável - Doações">Ajustável - Doações</SelectItem>
                <SelectItem value="Ajustável - Presentes">Ajustável - Presentes</SelectItem>
                <SelectItem value="Ajustável - Roupas">Ajustável - Roupas</SelectItem>
                <SelectItem value="Ajustável - Saídas">Ajustável - Saídas</SelectItem>
                <SelectItem value="Ajustável - Supermercado">Ajustável - Supermercado</SelectItem>
                <SelectItem value="Ajustável - Tech">Ajustável - Tech</SelectItem>
                <SelectItem value="Ajustável - Uber">Ajustável - Uber</SelectItem>
                <SelectItem value="Ajustável - Viagens">Ajustável - Viagens</SelectItem>
                <SelectItem value="Ajustável - Delivery">Ajustável - Delivery</SelectItem>
                <SelectItem value="Ajustável - Esportes">Ajustável - Esportes</SelectItem>
                <SelectItem value="Ajustável">Ajustável</SelectItem>
                <SelectItem value="Fixo">Fixo</SelectItem>
                <SelectItem value="Receita - Outras">Receita - Outras</SelectItem>
                <SelectItem value="Receita - Salário">Receita - Salário</SelectItem>
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
          <div className="grid gap-2">
            <Label>Período</Label>
            <div className="flex gap-2">
              <Select
                value={filters.mesInicio || ''}
                onValueChange={(value) => setFilters({ ...filters, mesInicio: value || undefined })}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Mês início" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value=" ">Limpar</SelectItem>
                  <SelectItem value="2026-01">Janeiro 2026</SelectItem>
                  <SelectItem value="2025-12">Dezembro 2025</SelectItem>
                  <SelectItem value="2025-11">Novembro 2025</SelectItem>
                  <SelectItem value="2025-10">Outubro 2025</SelectItem>
                  <SelectItem value="2025-09">Setembro 2025</SelectItem>
                  <SelectItem value="2025-08">Agosto 2025</SelectItem>
                  <SelectItem value="2025-07">Julho 2025</SelectItem>
                  <SelectItem value="2025-06">Junho 2025</SelectItem>
                  <SelectItem value="2025-05">Maio 2025</SelectItem>
                  <SelectItem value="2025-04">Abril 2025</SelectItem>
                  <SelectItem value="2025-03">Março 2025</SelectItem>
                  <SelectItem value="2025-02">Fevereiro 2025</SelectItem>
                  <SelectItem value="2025-01">Janeiro 2025</SelectItem>
                  <SelectItem value="2024-12">Dezembro 2024</SelectItem>
                  <SelectItem value="2024-11">Novembro 2024</SelectItem>
                  <SelectItem value="2024-10">Outubro 2024</SelectItem>
                </SelectContent>
              </Select>
              <span className="flex items-center text-muted-foreground">até</span>
              <Select
                value={filters.mesFim || ''}
                onValueChange={(value) => setFilters({ ...filters, mesFim: value || undefined })}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Mês fim" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value=" ">Limpar</SelectItem>
                  <SelectItem value="2026-01">Janeiro 2026</SelectItem>
                  <SelectItem value="2025-12">Dezembro 2025</SelectItem>
                  <SelectItem value="2025-11">Novembro 2025</SelectItem>
                  <SelectItem value="2025-10">Outubro 2025</SelectItem>
                  <SelectItem value="2025-09">Setembro 2025</SelectItem>
                  <SelectItem value="2025-08">Agosto 2025</SelectItem>
                  <SelectItem value="2025-07">Julho 2025</SelectItem>
                  <SelectItem value="2025-06">Junho 2025</SelectItem>
                  <SelectItem value="2025-05">Maio 2025</SelectItem>
                  <SelectItem value="2025-04">Abril 2025</SelectItem>
                  <SelectItem value="2025-03">Março 2025</SelectItem>
                  <SelectItem value="2025-02">Fevereiro 2025</SelectItem>
                  <SelectItem value="2025-01">Janeiro 2025</SelectItem>
                  <SelectItem value="2024-12">Dezembro 2024</SelectItem>
                  <SelectItem value="2024-11">Novembro 2024</SelectItem>
                  <SelectItem value="2024-10">Outubro 2024</SelectItem>
                </SelectContent>
              </Select>
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