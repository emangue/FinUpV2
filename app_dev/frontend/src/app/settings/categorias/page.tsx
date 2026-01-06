"use client"

import * as React from "react"
import DashboardLayout from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Plus } from "lucide-react"
import { useCategories, CategoryFormModal, CategoriesTable, Category } from "@/features/categories"

export default function CategoriasPage() {
  const { categories, loading, error, createCategory, updateCategory } = useCategories()
  const [modalOpen, setModalOpen] = React.useState(false)
  const [editingCategory, setEditingCategory] = React.useState<Category | null>(null)

  const handleAdd = () => {
    setEditingCategory(null)
    setModalOpen(true)
  }

  const handleEdit = (category: Category) => {
    setEditingCategory(category)
    setModalOpen(true)
  }

  const handleSave = async (data: { GRUPO: string; SUBGRUPO: string; TipoGasto: string }) => {
    if (editingCategory) {
      await updateCategory(editingCategory.id, data)
    } else {
      await createCategory(data)
    }
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Gestão de Categorias</h1>
            <p className="text-muted-foreground">
              Gerencie as categorias de classificação de transações
            </p>
          </div>
        </div>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Base de Marcações</CardTitle>
              <CardDescription>
                {loading ? 'Carregando...' : `${categories.length} marcações cadastradas`}
              </CardDescription>
            </div>
            <Button onClick={handleAdd}>
              <Plus className="mr-2 h-4 w-4" />
              Nova Marcação
            </Button>
          </CardHeader>
          <CardContent>
            {error && (
              <div className="mb-4 p-4 bg-destructive/10 text-destructive rounded-md">
                {error}
              </div>
            )}
            <CategoriesTable 
              categories={categories}
              onEdit={handleEdit}
            />
          </CardContent>
        </Card>

        <CategoryFormModal
          open={modalOpen}
          onOpenChange={setModalOpen}
          category={editingCategory}
          onSave={handleSave}
        />
      </div>
    </DashboardLayout>
  )
}
