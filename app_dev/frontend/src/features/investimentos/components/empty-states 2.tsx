/**
 * Componentes de Empty States
 * Estados vazios para diferentes cenários
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Search, TrendingUp, Database } from 'lucide-react'

interface EmptyStateProps {
  title: string
  description: string
  icon?: React.ReactNode
  action?: {
    label: string
    onClick: () => void
  }
}

export function EmptyState({ title, description, icon, action }: EmptyStateProps) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center justify-center py-16 text-center">
        <div className="mb-4 text-muted-foreground">
          {icon || <Database className="h-16 w-16" />}
        </div>
        <h3 className="mb-2 text-lg font-semibold">{title}</h3>
        <p className="mb-6 max-w-md text-sm text-muted-foreground">{description}</p>
        {action && (
          <Button onClick={action.onClick}>
            {action.label}
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

export function EmptyInvestimentos({ onAdd }: { onAdd: () => void }) {
  return (
    <EmptyState
      title="Nenhum investimento cadastrado"
      description="Comece adicionando seu primeiro investimento para acompanhar seu portfólio e rentabilidade."
      icon={<TrendingUp className="h-16 w-16" />}
      action={{
        label: "Adicionar primeiro investimento",
        onClick: onAdd,
      }}
    />
  )
}

export function EmptyFilterResults({ onClearFilters }: { onClearFilters: () => void }) {
  return (
    <EmptyState
      title="Nenhum resultado encontrado"
      description="Não encontramos investimentos que correspondam aos filtros aplicados. Tente ajustar os critérios de busca."
      icon={<Search className="h-16 w-16" />}
      action={{
        label: "Limpar filtros",
        onClick: onClearFilters,
      }}
    />
  )
}

export function EmptyDistribuicao() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Distribuição por Tipo</CardTitle>
        <CardDescription>Sem dados disponíveis</CardDescription>
      </CardHeader>
      <CardContent className="flex items-center justify-center py-8">
        <p className="text-sm text-muted-foreground">
          Adicione investimentos para ver a distribuição
        </p>
      </CardContent>
    </Card>
  )
}

export function EmptyTimeline() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Evolução Temporal</CardTitle>
        <CardDescription>Sem dados disponíveis</CardDescription>
      </CardHeader>
      <CardContent className="flex items-center justify-center py-8">
        <p className="text-sm text-muted-foreground">
          Histórico será exibido conforme os meses avançam
        </p>
      </CardContent>
    </Card>
  )
}
