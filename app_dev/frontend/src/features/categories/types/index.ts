export interface Category {
  id: number
  GRUPO: string
  SUBGRUPO: string
  TipoGasto: string
}

export interface CategoryCreate {
  GRUPO: string
  SUBGRUPO: string
  TipoGasto: string
}

export interface CategoryUpdate extends CategoryCreate {}

export interface CategoryResponse {
  categories: Category[]
  total: number
}
