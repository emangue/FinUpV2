import Link from "next/link"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Users, LayoutGrid, Building2, Database, Tags } from "lucide-react"

const sections = [
  { href: "/admin/contas", label: "Contas", description: "Gestão de usuários", icon: Users },
  { href: "/admin/screens", label: "Telas", description: "Visibilidade de telas", icon: LayoutGrid },
  { href: "/admin/bancos", label: "Bancos", description: "Compatibilidade de bancos", icon: Building2 },
  { href: "/admin/backup", label: "Backup", description: "Exportar dados", icon: Database },
  { href: "/admin/categorias-genericas", label: "Categorias Genéricas", description: "Regras de classificação", icon: Tags },
]

export default function AdminDashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard Admin</h1>
        <p className="text-muted-foreground">
          Selecione uma seção para gerenciar
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {sections.map(({ href, label, description, icon: Icon }) => (
          <Link key={href} href={href}>
            <Card className="transition-colors hover:bg-muted/50">
              <CardHeader className="flex flex-row items-center gap-4">
                <div className="rounded-lg bg-primary/10 p-3">
                  <Icon className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-lg">{label}</CardTitle>
                  <CardDescription>{description}</CardDescription>
                </div>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
