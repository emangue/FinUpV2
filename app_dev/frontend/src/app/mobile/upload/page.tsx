'use client'

/**
 * Upload Mobile - Página de Upload
 * 
 * Simplificado para V1.0:
 * - Seleção de arquivo (input nativo)
 * - Validação (formato, tamanho)
 * - Redirect para fluxo desktop (preview/confirm)
 * 
 * V1.1 (Futuro):
 * - Bottom sheet de configuração
 * - Preview mobile inline
 * - Histórico de uploads
 * 
 * Baseado no PRD Seção 4.5
 */

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { Upload, FileText, AlertCircle } from 'lucide-react'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'
import { cn } from '@/lib/utils'

export default function UploadMobilePage() {
  const router = useRouter()
  const fileInputRef = React.useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = React.useState(false)
  const [uploading, setUploading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    await processFile(file)
  }

  const processFile = async (file: File) => {
    try {
      setError(null)
      
      // Validar tamanho (10MB)
      const maxSizeBytes = 10 * 1024 * 1024
      if (file.size > maxSizeBytes) {
        setError('Arquivo muito grande. Máximo: 10MB')
        return
      }

      // Validar formato
      const validFormats = ['.csv', '.xls', '.xlsx', '.pdf']
      const extension = '.' + file.name.split('.').pop()?.toLowerCase()
      if (!validFormats.includes(extension || '')) {
        setError('Formato inválido. Use: CSV, Excel ou PDF')
        return
      }

      setUploading(true)

      // Fazer upload
      const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`
      
      const formData = new FormData()
      formData.append('file', file)
      
      // Parâmetros padrão (mobile simplificado)
      // TODO V1.1: Adicionar bottom sheet para configurar esses valores
      const currentDate = new Date()
      const mesFatura = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`
      
      formData.append('banco', 'outros')
      formData.append('mesFatura', mesFatura)
      formData.append('tipoDocumento', 'extrato')
      formData.append('formato', extension.includes('csv') ? 'csv' : 'Excel')

      const response = await fetchWithAuth(`${BASE_URL}/upload/preview`, {
        method: 'POST',
        body: formData
      })

      if (response.status === 401) {
        console.error('Não autenticado. Redirecionando para login...')
        router.push('/login')
        return
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.detail || `Erro ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      // Redirecionar para preview (reutilizar fluxo desktop)
      if (data.sessionId) {
        router.push(`/upload/preview/${data.sessionId}`)
      } else {
        throw new Error('Session ID não retornado')
      }

    } catch (err) {
      console.error('Erro ao processar arquivo:', err)
      setError(err instanceof Error ? err.message : 'Erro ao processar arquivo')
    } finally {
      setUploading(false)
    }
  }

  const handleClick = () => {
    if (!uploading) {
      fileInputRef.current?.click()
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const file = e.dataTransfer.files?.[0]
    if (file) {
      await processFile(file)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <MobileHeader
        title="Upload"
        showBackButton={false}
      />
      
      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5">
        {/* Upload Area */}
        <div
          onClick={handleClick}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={cn(
            'cursor-pointer transition-all duration-200',
            'bg-white rounded-2xl border-2 border-dashed p-8',
            'flex flex-col items-center justify-center',
            'min-h-[300px]',
            isDragging && 'border-black bg-gray-50',
            !isDragging && 'border-gray-200 hover:border-gray-300',
            uploading && 'opacity-50 cursor-not-allowed'
          )}
        >
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xls,.xlsx,.pdf"
            onChange={handleFileChange}
            className="hidden"
            aria-label="Selecionar arquivo"
            disabled={uploading}
          />

          {uploading ? (
            <>
              {/* Loading State */}
              <div className="w-20 h-20 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
                <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
              </div>
              <h3 className="text-lg font-semibold text-black mb-2">
                Processando...
              </h3>
              <p className="text-sm text-gray-600">
                Aguarde enquanto processamos seu arquivo
              </p>
            </>
          ) : (
            <>
              {/* Upload Icon */}
              <div className="w-20 h-20 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                <Upload className="w-10 h-10 text-gray-600" />
              </div>

              {/* Text */}
              <h3 className="text-lg font-semibold text-black mb-2">
                Importar Arquivo
              </h3>
              <p className="text-sm text-gray-600 mb-4 text-center">
                Toque para selecionar<br />
                ou arraste para cá
              </p>

              {/* Supported formats */}
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <FileText className="w-4 h-4" />
                <span>CSV, Excel, PDF (máx 10MB)</span>
              </div>
            </>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-800">Erro</p>
              <p className="text-sm text-red-600 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Info Card */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">
            Formatos suportados:
          </h4>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• <strong>Itaú:</strong> Fatura PDF ou Extrato CSV</li>
            <li>• <strong>BTG:</strong> Extrato CSV/Excel</li>
            <li>• <strong>Mercado Pago:</strong> Extrato CSV</li>
            <li>• <strong>Outros:</strong> CSV genérico</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
