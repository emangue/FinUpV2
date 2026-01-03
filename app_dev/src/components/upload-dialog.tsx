"use client"

import * as React from "react"
import { CalendarIcon, Upload, X } from "lucide-react"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"

import { Button } from "@/components/ui/button"
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

export function UploadDialog({ open, onOpenChange, onUploadSuccess }: UploadDialogProps) {
  const [date, setDate] = React.useState<Date>(new Date())
  const [fileFormat, setFileFormat] = React.useState("pdf")
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null)
  const [password, setPassword] = React.useState("")
  const [bank, setBank] = React.useState("")
  const [creditCard, setCreditCard] = React.useState("")
  const [activeTab, setActiveTab] = React.useState("fatura")
  const [isUploading, setIsUploading] = React.useState(false)
  const [uploadError, setUploadError] = React.useState<string | null>(null)

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
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('bank', bank)
      formData.append('creditCard', creditCard)
      formData.append('date', date.toISOString())
      formData.append('fileFormat', fileFormat)
      formData.append('type', activeTab)
      
      if (fileFormat === "pdf_password") {
        formData.append('password', password)
      }
      
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })
      
      const result = await response.json()
      
      if (!response.ok) {
        throw new Error(result.error || 'Erro no upload')
      }
      
      // Sucesso - fechar dialog
      alert('Arquivo importado com sucesso!')
      onOpenChange(false)
      
      // Chamar callback para atualizar lista
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
    setDate(new Date())
    setFileFormat("pdf")
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
    }
  }, [open])

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
                    <SelectItem value="itau">Banco Itaú</SelectItem>
                    <SelectItem value="bradesco">Banco Bradesco</SelectItem>
                    <SelectItem value="santander">Banco Santander</SelectItem>
                    <SelectItem value="bb">Banco do Brasil</SelectItem>
                    <SelectItem value="btg">BTG Pactual</SelectItem>
                    <SelectItem value="nubank">Nubank</SelectItem>
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
                    <SelectItem value="itau-principal">Banco XYZ - Principal</SelectItem>
                    <SelectItem value="itau-secundario">Banco XYZ - Secundário</SelectItem>
                    <SelectItem value="bradesco">Banco Bradesco</SelectItem>
                    <SelectItem value="santander">Banco Santander</SelectItem>
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
            <Label>Data de Efetivação *</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant={"outline"}
                  className={cn(
                    "w-full justify-start text-left font-normal",
                    !date && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {date ? format(date, "dd/MM/yyyy", { locale: ptBR }) : <span>Escolha uma data</span>}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={date}
                  onSelect={(newDate) => newDate && setDate(newDate)}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>

          <div className="space-y-4">
            <Label>Formato do arquivo para importação</Label>
            <RadioGroup value={fileFormat} onValueChange={setFileFormat}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="ofx" id="ofx" />
                <Label htmlFor="ofx">OFX</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="excel" id="excel" />
                <Label htmlFor="excel">Planilha Excel (XLS/XLSX)</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="pdf" id="pdf" />
                <Label htmlFor="pdf">PDF (Beta)</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="pdf_password" id="pdf_password" />
                <Label htmlFor="pdf_password">PDF com senha</Label>
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