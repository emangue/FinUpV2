"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { Upload, X, Plus } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
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
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import { cn } from "@/lib/utils"

interface UploadDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onUploadSuccess?: () => void
}

interface BankCompatibility {
  [bank: string]: {
    [format: string]: string  // 'OK', 'WIP', 'TBD'
  }
}

interface Card {
  id: number
  nome_cartao: string
  final_cartao: string
  banco: string
  ativo: number
}

export function UploadDialog({ open, onOpenChange, onUploadSuccess }: UploadDialogProps) {
  const router = useRouter()
  const currentDate = new Date()
  const [selectedYear, setSelectedYear] = React.useState<string>(currentDate.getFullYear().toString())
  const [selectedMonth, setSelectedMonth] = React.useState<string>(String(currentDate.getMonth() + 1).padStart(2, '0'))
  const [fileFormat, setFileFormat] = React.useState("csv")
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null)
  const [password, setPassword] = React.useState("")
  const [bank, setBank] = React.useState("")
  const [creditCard, setCreditCard] = React.useState("")
  const [activeTab, setActiveTab] = React.useState("fatura")
  const [isUploading, setIsUploading] = React.useState(false)
  const [uploadError, setUploadError] = React.useState<string | null>(null)
  const [compatibility, setCompatibility] = React.useState<BankCompatibility>({})
  const [cards, setCards] = React.useState<Card[]>([])
  const [isAddingCard, setIsAddingCard] = React.useState(false)
  const [newCardName, setNewCardName] = React.useState("")
  const [newCardFinal, setNewCardFinal] = React.useState("")
  const [isSavingCard, setIsSavingCard] = React.useState(false)

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleImport = async () => {
    if (!selectedFile) {
      setUploadError("Por favor, selecione um arquivo para importar.")
      return
    }
    
    if (activeTab === "fatura" && (!bank || !creditCard)) {
      setUploadError("Por favor, selecione o banco e cartão de crédito.")
      return
    }
    
    if (activeTab === "extrato" && !bank) {
      setUploadError("Por favor, selecione a instituição financeira.")
      return
    }
    
    if (fileFormat === "pdf_password" && !password) {
      setUploadError("Por favor, digite a senha do PDF.")
      return
    }
    
    setIsUploading(true)
    setUploadError(null)
    
    try {
      // Buscar final_cartao se cartão foi selecionado
      let finalCartao = ''
      if (creditCard) {
        const selectedCard = cards.find(c => c.id.toString() === creditCard)
        if (selectedCard) {
          finalCartao = selectedCard.final_cartao || ''
        }
      }
      
      // Enviar para API de preview
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('banco', bank)
      formData.append('cartao', creditCard || '')
      formData.append('final_cartao', finalCartao)
      formData.append('mesFatura', `${selectedYear}-${selectedMonth}`)
      formData.append('tipoDocumento', activeTab) // 'fatura' ou 'extrato'
      formData.append('formato', fileFormat) // 'csv', 'xls', etc
      
      const response = await fetch('/api/upload/preview', {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Erro ao processar arquivo')
      }
      
      const data = await response.json()
      
      // Fechar dialog
      onOpenChange(false)
      
      // Navegar para página de preview com o sessionId
      router.push(`/upload/preview/${data.sessionId}`)
      
      // Chamar callback de sucesso
      if (onUploadSuccess) {
        onUploadSuccess()
      }
      
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : 'Erro desconhecido')
    } finally {
      setIsUploading(false)
    }
  }

  const resetForm = () => {
    setSelectedFile(null)
    const now = new Date()
    setSelectedYear(now.getFullYear().toString())
    setSelectedMonth(String(now.getMonth() + 1).padStart(2, '0'))
    setFileFormat("csv")
    setPassword("")
    setBank("")
    setCreditCard("")
    setActiveTab("fatura")
    setIsUploading(false)
    setUploadError(null)
    setIsAddingCard(false)
    setNewCardName("")
    setNewCardFinal("")
  }
  
  const handleAddCard = () => {
    if (!bank) {
      setUploadError("Selecione um banco primeiro para adicionar um cartão")
      return
    }
    setIsAddingCard(true)
    setUploadError(null)
  }
  
  const handleSaveNewCard = async () => {
    if (!bank) {
      setUploadError("Selecione um banco primeiro")
      return
    }
    
    if (!newCardName.trim()) {
      setUploadError("Digite o nome do cartão")
      return
    }
    
    if (newCardFinal.length !== 4 || !/^\d+$/.test(newCardFinal)) {
      setUploadError("Final do cartão deve ter exatamente 4 dígitos")
      return
    }
    
    setIsSavingCard(true)
    setUploadError(null)
    
    try {
      // Encontrar nome real do banco
      const bankKey = Object.keys(compatibility).find(
        key => key.toLowerCase().replace(/ /g, '-') === bank
      )
      
      if (!bankKey) {
        throw new Error("Banco não encontrado")
      }
      
      const response = await fetch('/api/cards', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome_cartao: newCardName.trim(),
          final_cartao: newCardFinal.trim(),
          banco: bankKey
        })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || errorData.error || 'Erro ao salvar cartão')
      }
      
      const newCard = await response.json()
      
      // Atualizar lista de cartões
      setCards(prev => [...prev, newCard])
      
      // Selecionar automaticamente o novo cartão
      setCreditCard(newCard.id.toString())
      
      // Resetar form de adicionar cartão
      setIsAddingCard(false)
      setNewCardName("")
      setNewCardFinal("")
      
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : 'Erro ao salvar cartão')
    } finally {
      setIsSavingCard(false)
    }
  }
  
  const handleCancelAddCard = () => {
    setIsAddingCard(false)
    setNewCardName("")
    setNewCardFinal("")
    setUploadError(null)
  }

  React.useEffect(() => {
    if (open) {
      resetForm()
      
      // Buscar compatibilidade da API
      fetch('/api/compatibility')
        .then(res => res.json())
        .then(data => {
          console.log('🔍 Compatibilidade carregada:', data)
          
          // Transformar array de banks em objeto {[bank]: {[format]: status}}
          const compatibilityMap: BankCompatibility = {}
          if (data.banks && Array.isArray(data.banks)) {
            data.banks.forEach((item: any) => {
              if (!compatibilityMap[item.bank_name]) {
                compatibilityMap[item.bank_name] = {}
              }
              compatibilityMap[item.bank_name][item.file_format] = item.status
            })
          }
          console.log('📊 Compatibilidade processada:', compatibilityMap)
          setCompatibility(compatibilityMap)
        })
        .catch(err => console.error('❌ Erro ao buscar compatibilidade:', err))
      
      // Buscar cartões cadastrados
      fetch('/api/cards')
        .then(res => res.json())
        .then(data => {
          console.log('💳 Cartões carregados:', data)
          setCards(data.cards || [])
        })
        .catch(err => console.error('❌ Erro ao buscar cartões:', err))
    }
  }, [open])
  
  // Filtrar bancos que têm pelo menos um formato OK para o formato selecionado
  const availableBanks = React.useMemo(() => {
    if (!compatibility || Object.keys(compatibility).length === 0) {
      return []
    }
    
    // Retornar TODOS os bancos cadastrados (não filtrar por status)
    return Object.keys(compatibility).sort()
  }, [compatibility])
  
  // Filtrar cartões pelo banco selecionado
  const availableCards = React.useMemo(() => {
    if (!bank || cards.length === 0) {
      return cards.filter(card => card.ativo === 1)
    }
    
    // Encontrar o nome real do banco no objeto compatibility
    const bankKey = Object.keys(compatibility).find(
      key => key.toLowerCase().replace(/ /g, '-') === bank
    )
    
    if (!bankKey) {
      return cards.filter(card => card.ativo === 1)
    }
    
    // Filtrar cartões que pertencem ao banco selecionado
    return cards.filter(card => 
      card.ativo === 1 && 
      card.banco.toLowerCase().includes(bankKey.toLowerCase()) ||
      bankKey.toLowerCase().includes(card.banco.toLowerCase())
    )
  }, [bank, cards, compatibility])
  
  // Limpar cartão selecionado quando banco mudar
  React.useEffect(() => {
    if (bank && creditCard) {
      const cardStillValid = availableCards.some(
        card => card.id.toString() === creditCard
      )
      if (!cardStillValid) {
        setCreditCard("")
      }
    }
  }, [bank, availableCards, creditCard])
  
  // Verificar status de um formato específico para o banco selecionado
  const getFormatStatus = (format: string): string => {
    if (!bank || !compatibility) return 'TBD'
    
    // O banco no state está em lowercase com hífens, mas na API está com nome original
    // Precisamos encontrar o banco correto na compatibilidade
    const bankKey = Object.keys(compatibility).find(
      key => key.toLowerCase().replace(/ /g, '-') === bank
    )
    
    if (!bankKey || !compatibility[bankKey]) return 'TBD'
    return compatibility[bankKey][format] || 'TBD'
  }
  
  // Verificar se formato está disponível
  const isFormatAvailable = (format: string): boolean => {
    const status = getFormatStatus(format)
    return status === 'OK' || status === 'WIP'
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Importar Arquivo
          </DialogTitle>
          <DialogDescription>
            Faça o upload de faturas de cartão ou extratos bancários
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {uploadError && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3 text-red-700 text-sm">
              {uploadError}
            </div>
          )}

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="extrato">Extrato bancário</TabsTrigger>
              <TabsTrigger value="fatura">Fatura Cartão</TabsTrigger>
            </TabsList>
            
            <TabsContent value="extrato" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="bank-extrato">Instituição Financeira *</Label>
                <Select value={bank} onValueChange={setBank}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o banco" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableBanks.map(bankName => (
                      <SelectItem key={bankName} value={bankName.toLowerCase().replace(/ /g, '-')}>
                        {bankName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>
            
            <TabsContent value="fatura" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="bank-fatura">Instituição Financeira *</Label>
                <Select value={bank} onValueChange={setBank}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o banco" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableBanks.map(bankName => (
                      <SelectItem key={bankName} value={bankName.toLowerCase().replace(/ /g, '-')}>
                        {bankName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="credit-card">Cartão de Crédito *</Label>
                
                {!isAddingCard ? (
                  <>
                    <div className="flex gap-2">
                      <Select value={creditCard} onValueChange={setCreditCard}>
                        <SelectTrigger className="flex-1">
                          <SelectValue placeholder="Selecione o cartão" />
                        </SelectTrigger>
                        <SelectContent>
                          {availableCards.length === 0 ? (
                            <SelectItem value="none" disabled>
                              {!bank 
                                ? "Selecione um banco primeiro"
                                : "Nenhum cartão deste banco cadastrado"
                              }
                            </SelectItem>
                          ) : (
                            availableCards.map(card => (
                              <SelectItem key={card.id} value={card.id.toString()}>
                                {card.nome_cartao} •••• {card.final_cartao} ({card.banco})
                              </SelectItem>
                            ))
                          )}
                        </SelectContent>
                      </Select>
                      <Button
                        type="button"
                        variant="outline"
                        size="icon"
                        onClick={handleAddCard}
                        disabled={!bank || isAddingCard}
                      >
                        <Plus className="h-4 w-4" />
                      </Button>
                    </div>
                    {availableCards.length === 0 && bank && (
                      <p className="text-xs text-muted-foreground">
                        Clique no + para adicionar um cartão deste banco
                      </p>
                    )}
                  </>
                ) : (
                  <div className="space-y-3 border rounded-lg p-3 bg-muted/30">
                    <div className="space-y-2">
                      <Label htmlFor="new-card-name" className="text-xs">Nome do Cartão</Label>
                      <Input
                        id="new-card-name"
                        value={newCardName}
                        onChange={(e) => setNewCardName(e.target.value)}
                        placeholder="Ex: Mastercard Black"
                        className="h-9"
                        disabled={isSavingCard}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="new-card-final" className="text-xs">Final do Cartão (4 dígitos)</Label>
                      <Input
                        id="new-card-final"
                        value={newCardFinal}
                        onChange={(e) => setNewCardFinal(e.target.value.replace(/\D/g, '').slice(0, 4))}
                        placeholder="1234"
                        maxLength={4}
                        className="h-9"
                        disabled={isSavingCard}
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button
                        type="button"
                        size="sm"
                        onClick={handleSaveNewCard}
                        disabled={isSavingCard}
                        className="flex-1"
                      >
                        {isSavingCard ? "Salvando..." : "Salvar"}
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={handleCancelAddCard}
                        disabled={isSavingCard}
                      >
                        Cancelar
                      </Button>
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label>Período da Fatura *</Label>
                <div className="flex items-center gap-3">
                  <Select value={selectedYear} onValueChange={setSelectedYear}>
                    <SelectTrigger className="w-28">
                      <SelectValue placeholder="Ano" />
                    </SelectTrigger>
                    <SelectContent>
                      {Array.from({ length: 6 }, (_, i) => {
                        const year = new Date().getFullYear() - i
                        return (
                          <SelectItem key={year} value={year.toString()}>
                            {year}
                          </SelectItem>
                        )
                      })}
                    </SelectContent>
                  </Select>

                  <Select value={selectedMonth} onValueChange={setSelectedMonth}>
                    <SelectTrigger className="flex-1">
                      <SelectValue placeholder="Mês" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="01">Janeiro</SelectItem>
                      <SelectItem value="02">Fevereiro</SelectItem>
                      <SelectItem value="03">Março</SelectItem>
                      <SelectItem value="04">Abril</SelectItem>
                      <SelectItem value="05">Maio</SelectItem>
                      <SelectItem value="06">Junho</SelectItem>
                      <SelectItem value="07">Julho</SelectItem>
                      <SelectItem value="08">Agosto</SelectItem>
                      <SelectItem value="09">Setembro</SelectItem>
                      <SelectItem value="10">Outubro</SelectItem>
                      <SelectItem value="11">Novembro</SelectItem>
                      <SelectItem value="12">Dezembro</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </TabsContent>
          </Tabs>

          <div className="space-y-4">
            <Label>Formato do arquivo para importação</Label>
            <RadioGroup value={fileFormat} onValueChange={setFileFormat}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem 
                  value="csv" 
                  id="csv" 
                  disabled={!isFormatAvailable('CSV')}
                />
                <Label 
                  htmlFor="csv" 
                  className={cn(
                    "flex items-center gap-2",
                    !isFormatAvailable('CSV') && "text-muted-foreground"
                  )}
                >
                  CSV
                  {!bank ? (
                    <span className="text-xs text-muted-foreground">(selecione um banco)</span>
                  ) : (
                    <Badge 
                      variant="outline" 
                      className={cn(
                        "text-xs",
                        getFormatStatus('CSV') === 'OK' && "bg-green-100 text-green-800 border-green-300",
                        getFormatStatus('CSV') === 'WIP' && "bg-yellow-100 text-yellow-800 border-yellow-300",
                        getFormatStatus('CSV') === 'TBD' && "bg-red-100 text-red-800 border-red-300"
                      )}
                    >
                      {getFormatStatus('CSV')}
                    </Badge>
                  )}
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem 
                  value="excel" 
                  id="excel" 
                  disabled={!isFormatAvailable('Excel')}
                />
                <Label 
                  htmlFor="excel" 
                  className={cn(
                    "flex items-center gap-2",
                    !isFormatAvailable('Excel') && "text-muted-foreground"
                  )}
                >
                  Planilha Excel (XLS/XLSX)
                  {!bank ? (
                    <span className="text-xs text-muted-foreground">(selecione um banco)</span>
                  ) : (
                    <Badge 
                      variant="outline" 
                      className={cn(
                        "text-xs",
                        getFormatStatus('Excel') === 'OK' && "bg-green-100 text-green-800 border-green-300",
                        getFormatStatus('Excel') === 'WIP' && "bg-yellow-100 text-yellow-800 border-yellow-300",
                        getFormatStatus('Excel') === 'TBD' && "bg-red-100 text-red-800 border-red-300"
                      )}
                    >
                      {getFormatStatus('Excel')}
                    </Badge>
                  )}
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem 
                  value="pdf" 
                  id="pdf" 
                  disabled={!isFormatAvailable('PDF')}
                />
                <Label 
                  htmlFor="pdf" 
                  className={cn(
                    "flex items-center gap-2",
                    !isFormatAvailable('PDF') && "text-muted-foreground"
                  )}
                >
                  PDF
                  {!bank ? (
                    <span className="text-xs text-muted-foreground">(selecione um banco)</span>
                  ) : (
                    <Badge 
                      variant="outline" 
                      className={cn(
                        "text-xs",
                        getFormatStatus('PDF') === 'OK' && "bg-green-100 text-green-800 border-green-300",
                        getFormatStatus('PDF') === 'WIP' && "bg-yellow-100 text-yellow-800 border-yellow-300",
                        getFormatStatus('PDF') === 'TBD' && "bg-red-100 text-red-800 border-red-300"
                      )}
                    >
                      {getFormatStatus('PDF')}
                    </Badge>
                  )}
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem 
                  value="pdf_password" 
                  id="pdf_password" 
                  disabled={!isFormatAvailable('PDF')}
                />
                <Label 
                  htmlFor="pdf_password" 
                  className={cn(
                    "flex items-center gap-2",
                    !isFormatAvailable('PDF') && "text-muted-foreground"
                  )}
                >
                  PDF com senha
                  {!bank ? (
                    <span className="text-xs text-muted-foreground">(selecione um banco)</span>
                  ) : (
                    <Badge 
                      variant="outline" 
                      className={cn(
                        "text-xs",
                        getFormatStatus('PDF') === 'OK' && "bg-green-100 text-green-800 border-green-300",
                        getFormatStatus('PDF') === 'WIP' && "bg-yellow-100 text-yellow-800 border-yellow-300",
                        getFormatStatus('PDF') === 'TBD' && "bg-red-100 text-red-800 border-red-300"
                      )}
                    >
                      {getFormatStatus('PDF')}
                    </Badge>
                  )}
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem 
                  value="ofx" 
                  id="ofx" 
                  disabled={!isFormatAvailable('OFX')}
                />
                <Label 
                  htmlFor="ofx" 
                  className={cn(
                    "flex items-center gap-2",
                    !isFormatAvailable('OFX') && "text-muted-foreground"
                  )}
                >
                  OFX
                  {!bank ? (
                    <span className="text-xs text-muted-foreground">(selecione um banco)</span>
                  ) : (
                    <Badge 
                      variant="outline" 
                      className={cn(
                        "text-xs",
                        getFormatStatus('OFX') === 'OK' && "bg-green-100 text-green-800 border-green-300",
                        getFormatStatus('OFX') === 'WIP' && "bg-yellow-100 text-yellow-800 border-yellow-300",
                        getFormatStatus('OFX') === 'TBD' && "bg-red-100 text-red-800 border-red-300"
                      )}
                    >
                      {getFormatStatus('OFX')}
                    </Badge>
                  )}
                </Label>
              </div>
            </RadioGroup>

            {fileFormat === "pdf_password" && (
              <div className="ml-6 space-y-2">
                <Label htmlFor="password">Senha do PDF</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Digite a senha do arquivo PDF"
                />
              </div>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="file">Arquivo</Label>
            <div className="flex items-center gap-2">
              <Input
                id="file"
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.xls,.xlsx,.ofx,.csv"
                className="hidden"
              />
              <Button
                type="button"
                variant="outline"
                className="flex-1"
                onClick={() => document.getElementById("file")?.click()}
              >
                <Upload className="mr-2 h-4 w-4" />
                {selectedFile ? selectedFile.name : "Escolher Arquivo"}
              </Button>
              {selectedFile && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedFile(null)}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
            {!selectedFile && (
              <p className="text-sm text-muted-foreground">Nenhum...</p>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button 
            variant="outline" 
            onClick={() => onOpenChange(false)}
            disabled={isUploading}
          >
            Cancelar
          </Button>
          <Button 
            onClick={handleImport} 
            disabled={!selectedFile || isUploading}
          >
            {isUploading ? "Importando..." : "Importar"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}