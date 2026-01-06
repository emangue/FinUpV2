"use client"

import * as React from "react"
import DashboardLayout from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Plus, Edit, ExternalLink } from "lucide-react"

interface BankCompatibility {
  id: number
  bank_name: string
  file_format: string
  status: 'OK' | 'WIP' | 'TBD'
}

export default function ConfiguracoesPage() {
  const [activeTab, setActiveTab] = React.useState<'bancos' | 'api'>('bancos')

  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const tab = params.get('tab')
    if (tab === 'api') {
      setActiveTab('api')
    }
  }, [])

  const [bancos, setBancos] = React.useState<BankCompatibility[]>([])
  const [loadingBanks, setLoadingBanks] = React.useState(true)
  const [bankModalOpen, setBankModalOpen] = React.useState(false)
  const [bankName, setBankName] = React.useState('')
  const [bankFormats, setBankFormats] = React.useState({
    CSV: 'TBD' as 'OK' | 'WIP' | 'TBD',
    Excel: 'TBD' as 'OK' | 'WIP' | 'TBD',
    PDF: 'TBD' as 'OK' | 'WIP' | 'TBD',
    OFX: 'TBD' as 'OK' | 'WIP' | 'TBD'
  })
  const [editingBank, setEditingBank] = React.useState<string | null>(null)

  React.useEffect(() => {
    fetchBancos()
  }, [])

  const fetchBancos = async () => {
    try {
      setLoadingBanks(true)
      // TODO: Criar endpoint /api/compatibility no backend
      setBancos([
        { id: 1, bank_name: 'Itaú', file_format: 'CSV', status: 'OK' },
        { id: 2, bank_name: 'Itaú', file_format: 'Excel', status: 'OK' },
        { id: 3, bank_name: 'Santander', file_format: 'CSV', status: 'WIP' },
      ])
    } catch (error) {
      console.error('Erro ao buscar bancos:', error)
    } finally {
      setLoadingBanks(false)
    }
  }

  const handleAddBank = () => {
    setBankName('')
    setBankFormats({
      CSV: 'TBD',
      Excel: 'TBD',
      PDF: 'TBD',
      OFX: 'TBD'
    })
    setEditingBank(null)
    setBankModalOpen(true)
  }

  const handleSaveBank = async () => {
    if (!bankName.trim()) return

    try {
      alert('Funcionalidade em desenvolvimento. Backend precisa ser implementado.')
      setBankModalOpen(false)
    } catch (error) {
      console.error('Erro ao salvar banco:', error)
    }
  }

  const getStatusBadge = (status: 'OK' | 'WIP' | 'TBD') => {
    const variants: Record<string, "default" | "secondary" | "destructive"> = {
      OK: "default",
      WIP: "secondary",
      TBD: "destructive"
    }
    return <Badge variant={variants[status]}>{status}</Badge>
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Configurações</h1>
            <p className="text-muted-foreground">
              Gerencie configurações do sistema
            </p>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)}>
          <TabsList>
            <TabsTrigger value="bancos">Bancos Compatíveis</TabsTrigger>
            <TabsTrigger value="api">API Docs</TabsTrigger>
          </TabsList>

          <TabsContent value="bancos" className="space-y-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Compatibilidade de Bancos</CardTitle>
                  <CardDescription>
                    {loadingBanks ? 'Carregando...' : `${bancos.length} bancos/formatos cadastrados`}
                  </CardDescription>
                </div>
                <Button onClick={handleAddBank}>
                  <Plus className="mr-2 h-4 w-4" />
                  Novo Banco
                </Button>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Banco</TableHead>
                      <TableHead>Formato</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="w-[100px]">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {bancos.map((banco) => (
                      <TableRow key={banco.id}>
                        <TableCell className="font-medium">{banco.bank_name}</TableCell>
                        <TableCell>{banco.file_format}</TableCell>
                        <TableCell>{getStatusBadge(banco.status)}</TableCell>
                        <TableCell className="flex gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => {
                              setEditingBank(banco.bank_name)
                              setBankName(banco.bank_name)
                              setBankModalOpen(true)
                            }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="api" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Documentação da API</CardTitle>
                <CardDescription>
                  Acesse a documentação interativa da API FastAPI
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <h3 className="font-semibold">Swagger UI (Interativo)</h3>
                  <p className="text-sm text-muted-foreground">
                    Interface interativa para testar endpoints da API
                  </p>
                  <Button
                    variant="outline"
                    onClick={() => window.open('http://localhost:8000/docs', '_blank')}
                  >
                    <ExternalLink className="mr-2 h-4 w-4" />
                    Abrir Swagger UI
                  </Button>
                </div>

                <div className="space-y-2">
                  <h3 className="font-semibold">ReDoc (Documentação)</h3>
                  <p className="text-sm text-muted-foreground">
                    Documentação detalhada em formato de leitura
                  </p>
                  <Button
                    variant="outline"
                    onClick={() => window.open('http://localhost:8000/redoc', '_blank')}
                  >
                    <ExternalLink className="mr-2 h-4 w-4" />
                    Abrir ReDoc
                  </Button>
                </div>

                <div className="space-y-2">
                  <h3 className="font-semibold">OpenAPI Schema (JSON)</h3>
                  <p className="text-sm text-muted-foreground">
                    Schema OpenAPI 3.0 da API em formato JSON
                  </p>
                  <Button
                    variant="outline"
                    onClick={() => window.open('http://localhost:8000/openapi.json', '_blank')}
                  >
                    <ExternalLink className="mr-2 h-4 w-4" />
                    Ver OpenAPI JSON
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <Dialog open={bankModalOpen} onOpenChange={setBankModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingBank ? 'Editar Banco' : 'Novo Banco'}
              </DialogTitle>
              <DialogDescription>
                Configure a compatibilidade de formatos de arquivo para este banco
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="bankName">Nome do Banco</Label>
                <Input
                  id="bankName"
                  value={bankName}
                  onChange={(e) => setBankName(e.target.value)}
                  placeholder="Ex: Itaú, Santander, Bradesco"
                />
              </div>

              <div className="grid gap-2">
                <Label>Formatos Suportados</Label>
                <div className="space-y-2">
                  {Object.entries(bankFormats).map(([format, status]) => (
                    <div key={format} className="flex items-center justify-between">
                      <span className="text-sm">{format}</span>
                      <Select
                        value={status}
                        onValueChange={(value: any) =>
                          setBankFormats(prev => ({ ...prev, [format]: value }))
                        }
                      >
                        <SelectTrigger className="w-[120px]">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="OK">OK</SelectItem>
                          <SelectItem value="WIP">WIP</SelectItem>
                          <SelectItem value="TBD">TBD</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setBankModalOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSaveBank}>Salvar</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  )
}
