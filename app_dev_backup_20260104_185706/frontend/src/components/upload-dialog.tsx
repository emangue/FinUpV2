"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { CalendarIcon, Upload, X } from "lucide-react"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Calendar } from "@/components/ui/calendar"
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
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
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

export function UploadDialog({ open, onOpenChange, onUploadSuccess }: UploadDialogProps) {
  const router = useRouter()
  const [mesFatura, setMesFatura] = React.useState<string>(format(new Date(), 'yyyy-MM'))
  const [fileFormat, setFileFormat] = React.useState("csv")
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null)
  const [password, setPassword] = React.useState("")
  const [bank, setBank] = React.useState("")
  const [creditCard, setCreditCard] = React.useState("")
  const [activeTab, setActiveTab] = React.useState("fatura")
  const [isUploading, setIsUploading] = React.useState(false)
  const [uploadError, setUploadError] = React.useState<string | null>(null)
  const [compatibility, setCompatibility] = React.useState<BankCompatibility>({})

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
      // Enviar para API de preview
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('banco', bank)
      formData.append('cartao', creditCard || '')
      formData.append('mesFatura', mesFatura)
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
    setMesFatura(format(new Date(), 'yyyy-MM'))
    setFileFormat("csv")
    setPassword("")
    setBank("")
    setCreditCard("")
    setActiveTab("fatura")
    setIsUploading(false)
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
          setCompatibility(data)
        })
        .catch(err => console.error('❌ Erro ao buscar compatibilidade:', err))
    }
  }, [open])
  
  // Filtrar bancos que têm pelo menos um formato OK para o formato selecionado
  const availableBanks = React.useMemo(() => {
    if (!compatibility || Object.keys(compatibility).length === 0) {
      return []
    }
    
    return Object.keys(compatibility).filter(bankName => {
      const formats = compatibility[bankName]
      // Verificar se tem pelo menos um formato disponível (OK ou WIP)
      return Object.values(formats).some(status => status === 'OK' || status === 'WIP')
    })
  }, [compatibility])
  
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
                <Select value={creditCard} onValueChange={setCreditCard}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o cartão" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="mastercard-4321">Mastercard 4321</SelectItem>
                    <SelectItem value="visa-1234">Visa 1234</SelectItem>
                    <SelectItem value="american-express">American Express</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>
          </Tabs>

          <div className="space-y-2">
            <Label>Mês Fatura *</Label>
            <Input
              type="month"
              value={mesFatura}
              onChange={(e) => setMesFatura(e.target.value)}
              max={format(new Date(), 'yyyy-MM')}
              className="w-full"
            />
          </div>

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