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
import { Plus, Edit } from "lucide-react"

interface Marcacao {
  id: number
  GRUPO: string
  SUBGRUPO: string
  TipoGasto: string
}

interface BankCompatibility {
  id: number
  bank_name: string
  file_format: string
  status: 'OK' | 'WIP' | 'TBD'
}

export default function ConfiguracoesPage() {
  const [activeTab, setActiveTab] = React.useState<'categorias' | 'bancos' | 'api'>('categorias')

  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const tab = params.get('tab')
    if (tab === 'bancos') {
      setActiveTab('bancos')
    } else if (tab === 'api') {
      setActiveTab('api')
    }
  }, [])

  const [marcacoes, setMarcacoes] = React.useState<Marcacao[]>([])
  const [loadingMarcacoes, setLoadingMarcacoes] = React.useState(true)
  const [marcacaoModalOpen, setMarcacaoModalOpen] = React.useState(false)
  const [marcacaoGrupo, setMarcacaoGrupo] = React.useState('')
  const [marcacaoSubgrupo, setMarcacaoSubgrupo] = React.useState('')
  const [marcacaoTipoGasto, setMarcacaoTipoGasto] = React.useState('')
  const [editingMarcacao, setEditingMarcacao] = React.useState<Marcacao | null>(null)

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
    fetchMarcacoes()
    fetchBancos()
  }, [])

  const fetchMarcacoes = async () => {
    try {
      setLoadingMarcacoes(true)
      const response = await fetch('/api/marcacoes')
      if (response.ok) {
        const data = await response.json()
        setMarcacoes(data)
      }
    } catch (error) {
      console.error('Erro ao buscar marcações:', error)
    } finally {
      setLoadingMarcacoes(false)
    }
  }

  const handleAddMarcacao = () => {
    setMarcacaoGrupo('')
    setMarcacaoSubgrupo('')
    setMarcacaoTipoGasto('')
    setEditingMarcacao(null)
    setMarcacaoModalOpen(true)
  }

  const handleEditMarcacao = (marc: Marcacao) => {
    setEditingMarcacao(marc)
    setMarcacaoGrupo(marc.GRUPO)
    setMarcacaoSubgrupo(marc.SUBGRUPO)
    setMarcacaoTipoGasto(marc.TipoGasto)
    setMarcacaoModalOpen(true)
  }

  const handleSaveMarcacao = async () => {
    if (!marcacaoGrupo.trim() || !marcacaoSubgrupo.trim() || !marcacaoTipoGasto.trim()) {
      alert('Todos os campos são obrigatórios')
      return
    }

    try {
      const url = editingMarcacao ? `/api/marcacoes/${editingMarcacao.id}` : '/api/marcacoes'
      const method = editingMarcacao ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          GRUPO: marcacaoGrupo.trim(),
          SUBGRUPO: marcacaoSubgrupo.trim(),
          TipoGasto: marcacaoTipoGasto.trim()
        })
      })

      if (response.ok) {
        fetchMarcacoes()
        setMarcacaoModalOpen(false)
      } else {
        const error = await response.json()
        alert(error.error || 'Erro ao salvar')
      }
    } catch (error) {
      console.error('Erro ao salvar marcação:', error)
      alert('Erro ao salvar marcação')
    }
  }

  const fetchBancos = async () => {
    try {
      setLoadingBanks(true)
      const response = await fetch('/api/compatibility/manage')
      if (response.ok) {
        const data = await response.json()
        setBancos(data)
      }
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

  const handleEditBank = (bankName: string) => {
    const bankData = bancos.filter(b => b.bank_name === bankName)
    setBankName(bankName)
    
    const formats: any = { CSV: 'TBD', Excel: 'TBD', PDF: 'TBD', OFX: 'TBD' }
    bankData.forEach(b => {
      formats[b.file_format] = b.status
    })
    
    setBankFormats(formats)
    setEditingBank(bankName)
    setBankModalOpen(true)
  }

  const handleSaveBank = async () => {
    if (!bankName.trim()) return

    try {
      const url = '/api/compatibility/manage'
      const method = editingBank ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bank_name: bankName.trim(),
          formats: bankFormats,
          old_bank_name: editingBank
        })
      })

      if (response.ok) {
        fetchBancos()
        setBankModalOpen(false)
      }
    } catch (error) {
      console.error('Erro ao salvar banco:', error)
    }
  }

  const uniqueBanks = [...new Set(bancos.map(b => b.bank_name))]

  return (
    <DashboardLayout>
      <div className="flex flex-1 flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Configurações</h1>
            <p className="text-muted-foreground">
              Gerencie categorias e compatibilidade de bancos
            </p>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'categorias' | 'bancos' | 'api')} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="categorias">Gestão de Categorias</TabsTrigger>
            <TabsTrigger value="bancos">Disponibilidade de Arquivos</TabsTrigger>
            <TabsTrigger value="api">API / Documentação</TabsTrigger>
          </TabsList>

          <TabsContent value="categorias" className="mt-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Base de Marcações</CardTitle>
                  <CardDescription>
                    {marcacoes.length} marcações cadastradas
                  </CardDescription>
                </div>
                <Button onClick={handleAddMarcacao}>
                  <Plus className="mr-2 h-4 w-4" />
                  Nova Marcação
                </Button>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>GRUPO</TableHead>
                      <TableHead>SUBGRUPO</TableHead>
                      <TableHead>Tipo de Gasto</TableHead>
                      <TableHead className="w-[100px]">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {marcacoes.map((marc) => (
                      <TableRow key={marc.id}>
                        <TableCell className="font-medium">{marc.GRUPO}</TableCell>
                        <TableCell>{marc.SUBGRUPO}</TableCell>
                        <TableCell>{marc.TipoGasto}</TableCell>
                        <TableCell className="flex gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleEditMarcacao(marc)}
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

          <TabsContent value="api" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Documentação da API</CardTitle>
                <CardDescription>
                  Acesse a documentação interativa do backend FastAPI
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-lg border p-4 bg-blue-50">
                  <h3 className="font-semibold text-lg mb-2">Swagger UI - Documentação Interativa</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Interface completa com todos os endpoints da API, exemplos de requisições e respostas.
                  </p>
                  <a 
                    href="http://localhost:8000/docs" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    Abrir Swagger UI
                  </a>
                </div>

                <div className="rounded-lg border p-4">
                  <h3 className="font-semibold text-lg mb-2">ReDoc - Documentação Alternativa</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Visualização limpa e organizada da documentação da API.
                  </p>
                  <a 
                    href="http://localhost:8000/redoc" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    Abrir ReDoc
                  </a>
                </div>

                <div className="rounded-lg border p-4 bg-gray-50">
                  <h3 className="font-semibold text-lg mb-2">Informações Técnicas</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Backend URL:</span>
                      <code className="bg-gray-200 px-2 py-1 rounded">http://localhost:8000</code>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">API Version:</span>
                      <code className="bg-gray-200 px-2 py-1 rounded">v1</code>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Base Path:</span>
                      <code className="bg-gray-200 px-2 py-1 rounded">/api/v1</code>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Autenticação:</span>
                      <code className="bg-gray-200 px-2 py-1 rounded">JWT Bearer Token</code>
                    </div>
                  </div>
                </div>

                <div className="rounded-lg border p-4 bg-yellow-50">
                  <h3 className="font-semibold text-lg mb-2">⚠️ Importante</h3>
                  <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                    <li>O backend deve estar rodando na porta 8000</li>
                    <li>Use o token JWT obtido no login para requisições autenticadas</li>
                    <li>Consulte a documentação do Swagger para exemplos de uso</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="bancos" className="mt-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Disponibilidade de Arquivos por Banco</CardTitle>
                  <CardDescription>
                    {uniqueBanks.length} bancos cadastrados
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
                      <TableHead className="text-center">CSV</TableHead>
                      <TableHead className="text-center">Excel</TableHead>
                      <TableHead className="text-center">PDF</TableHead>
                      <TableHead className="text-center">OFX</TableHead>
                      <TableHead className="w-[100px]">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {uniqueBanks.map((bankName) => {
                      const bankData = bancos.filter(b => b.bank_name === bankName)
                      const getStatus = (format: string) => 
                        bankData.find(b => b.file_format === format)?.status || 'TBD'
                      
                      const StatusBadge = ({ status }: { status: string }) => (
                        <Badge
                          variant="outline"
                          className={
                            status === 'OK' ? 'bg-green-100 text-green-800 border-green-300' :
                            status === 'WIP' ? 'bg-yellow-100 text-yellow-800 border-yellow-300' :
                            'bg-red-100 text-red-800 border-red-300'
                          }
                        >
                          {status}
                        </Badge>
                      )

                      return (
                        <TableRow key={bankName}>
                          <TableCell className="font-medium">{bankName}</TableCell>
                          <TableCell className="text-center">
                            <StatusBadge status={getStatus('CSV')} />
                          </TableCell>
                          <TableCell className="text-center">
                            <StatusBadge status={getStatus('Excel')} />
                          </TableCell>
                          <TableCell className="text-center">
                            <StatusBadge status={getStatus('PDF')} />
                          </TableCell>
                          <TableCell className="text-center">
                            <StatusBadge status={getStatus('OFX')} />
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleEditBank(bankName)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <Dialog open={marcacaoModalOpen} onOpenChange={setMarcacaoModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingMarcacao ? 'Editar' : 'Adicionar'} Marcação
              </DialogTitle>
              <DialogDescription>
                {editingMarcacao ? 'Altere' : 'Insira'} os dados da marcação (GRUPO, SUBGRUPO e Tipo de Gasto)
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="marcGrupo">GRUPO</Label>
                <Input
                  id="marcGrupo"
                  value={marcacaoGrupo}
                  onChange={(e) => setMarcacaoGrupo(e.target.value)}
                  placeholder="Ex: Alimentação"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="marcSubgrupo">SUBGRUPO</Label>
                <Input
                  id="marcSubgrupo"
                  value={marcacaoSubgrupo}
                  onChange={(e) => setMarcacaoSubgrupo(e.target.value)}
                  placeholder="Ex: Restaurante"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="marcTipoGasto">Tipo de Gasto</Label>
                <Input
                  id="marcTipoGasto"
                  value={marcacaoTipoGasto}
                  onChange={(e) => setMarcacaoTipoGasto(e.target.value)}
                  placeholder="Ex: Ajustável - Lazer"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setMarcacaoModalOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSaveMarcacao}>
                {editingMarcacao ? 'Salvar' : 'Adicionar'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Dialog open={bankModalOpen} onOpenChange={setBankModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingBank ? 'Editar' : 'Adicionar'} Banco
              </DialogTitle>
              <DialogDescription>
                {editingBank ? 'Altere o nome e os status dos formatos' : 'Insira o nome do banco e defina o status de cada formato'}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="bankName">Nome do Banco</Label>
                <Input
                  id="bankName"
                  value={bankName}
                  onChange={(e) => setBankName(e.target.value)}
                  placeholder="Ex: Banco Itaú"
                  disabled={!!editingBank}
                />
              </div>
              
              <div className="space-y-3">
                <Label>Status dos Formatos</Label>
                
                {(['CSV', 'Excel', 'PDF', 'OFX'] as const).map((format) => (
                  <div key={format} className="flex items-center justify-between">
                    <span className="text-sm font-medium">{format}</span>
                    <Select
                      value={bankFormats[format]}
                      onValueChange={(value) => setBankFormats(prev => ({ ...prev, [format]: value as any }))}
                    >
                      <SelectTrigger className="w-[150px]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="OK">
                          <Badge className="bg-green-500">OK</Badge>
                        </SelectItem>
                        <SelectItem value="WIP">
                          <Badge className="bg-yellow-500">WIP</Badge>
                        </SelectItem>
                        <SelectItem value="TBD">
                          <Badge className="bg-red-500">TBD</Badge>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                ))}
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setBankModalOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSaveBank}>
                {editingBank ? 'Salvar' : 'Adicionar'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  )
}
