"use client"

import { useEffect, useState } from 'react'
import { fetchWithAuth } from '@/core/utils/api-client'
import DashboardLayout from '@/components/dashboard-layout'
import { RequireAdmin } from '@/core/components/require-admin'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { API_ENDPOINTS } from '@/core/config/api.config'
import { Eye, Save, RefreshCw, ChevronDown, Home, CreditCard, BarChart3, Settings, Shield, DollarSign, Upload, TrendingUp, CheckCircle2, XCircle } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

// ESTRUTURA EXATA DA SIDEBAR - Fonte da verdade
const SIDEBAR_STRUCTURE = [
  {
    title: "Dashboard",
    icon: Home,
    parentUrl: "/dashboard",
    items: [
      { title: "Visão Geral", url: "/dashboard" },
      { title: "Métricas", url: "/dashboard/metrics" },
    ],
  },
  {
    title: "Transações",
    icon: CreditCard,
    parentUrl: "/transactions",
    items: [
      { title: "Todas", url: "/transactions?tab=all" },
      { title: "Receitas", url: "/transactions?tab=receitas" },
      { title: "Despesas", url: "/transactions?tab=despesas" },
      { title: "Migrações", url: "/transactions/migracoes" },
    ],
  },
  {
    title: "Orçamento",
    icon: DollarSign,
    parentUrl: "/budget",
    items: [
      { title: "Meta Geral", url: "/budget" },
      { title: "Meta Simples", url: "/budget/simples" },
      { title: "Meta Detalhada", url: "/budget/detalhada" },
      { title: "Planejamento", url: "/budget/planning" },
      { title: "Configurações", url: "/budget/configuracoes" },
    ],
  },
  {
    title: "Relatórios",
    icon: BarChart3,
    parentUrl: "/reports",
    items: [
      { title: "Mensal", url: "/reports/monthly" },
      { title: "Anual", url: "/reports/yearly" },
      { title: "Categorias", url: "/reports/categories" },
    ],
  },
  {
    title: "Configurações",
    icon: Settings,
    parentUrl: "/settings",
    items: [
      { title: "Perfil", url: "/settings/profile" },
      { title: "Gestão de Cartões", url: "/settings/cartoes" },
      { title: "Gestão de Categorias", url: "/settings/categorias" },
      { title: "Gestão de Grupos", url: "/settings/grupos" },
      { title: "Regras de Exclusão", url: "/settings/exclusoes" },
    ],
  },
  {
    title: "Administração",
    icon: Shield,
    parentUrl: "/admin",
    items: [
      { title: "Contas", url: "/settings/admin" },
      { title: "Visibilidade de Telas", url: "/settings/screens" },
      { title: "Gestão de Bancos", url: "/settings/bancos" },
      { title: "Backup", url: "/settings/backup" },
      { title: "Categorias Genéricas", url: "/settings/categorias-genericas" },
    ],
  },
]

// PROJECTS - Seção separada na sidebar
const SIDEBAR_PROJECTS = [
  {
    title: "Upload de Arquivos",
    icon: Upload,
    url: "/upload",
  },
  {
    title: "Análise de Tendências",
    icon: TrendingUp,
    url: "/trends",
  },
]

interface ScreenStatus {
  id: number
  screen_key: string
  status: 'P' | 'A' | 'D'
}

const STATUS_LABELS = {
  P: { label: 'Produção', badge: 'bg-green-500', description: 'Visível para todos os usuários' },
  A: { label: 'Admin', badge: 'bg-orange-500', description: 'Visível apenas para administradores' },
  D: { label: 'Development', badge: 'bg-purple-500', description: 'Visível apenas em desenvolvimento' },
}

// Função IDÊNTICA à da sidebar para mapear URLs → screen_keys
const getScreenKey = (url: string, isSubItem = false, parentUrl = '') => {
  if (isSubItem) {
    const parent = parentUrl.replace('/', '')
    
    // Tratar query params PRIMEIRO (ex: ?tab=all, ?tab=cartoes)
    if (url.includes('?tab=')) {
      const tab = url.split('?tab=')[1]
      if (tab === 'all') return `${parent}-all`
      if (tab === 'receitas') return `${parent}-receitas`
      if (tab === 'despesas') return `${parent}-despesas`
      if (tab === 'cartoes') return `${parent}-cartoes`
    }
    
    const fullPath = url.split('?')[0]
    
    // Casos especiais - se URL é exatamente igual ao parent
    if (fullPath === parentUrl) return `${parent}-geral`
    
    // Extrair última parte do path
    const lastSegment = fullPath.split('/').pop() || ''
    
    // Mapear nome do segmento para screen_key
    const segmentMap: Record<string, string> = {
      'simples': 'simples',
      'detalhada': 'detalhada',
      'planning': 'planning',
      'configuracoes': 'configuracoes',
      'monthly': 'monthly',
      'yearly': 'yearly',
      'categories': 'categories',
      'profile': 'profile',
      'cartoes': 'cartoes',
      'categorias': 'categorias',
      'grupos': 'grupos',
      'exclusoes': 'exclusoes',
      'admin': 'contas',
      'bancos': 'bancos',
      'backup': 'backup',
      'screens': 'screens',
      'metrics': 'metrics',
      'migracoes': 'migracoes',
      'categorias-genericas': 'categorias-genericas'
    }
    
    const mapped = segmentMap[lastSegment] || lastSegment
    
    return mapped === 'geral' ? `${parent}-geral` : `${parent}-${mapped}`
  }
  // Para items principais
  return url.replace('/', '')
}

export default function ScreenVisibilityPage() {
  const [screenStatuses, setScreenStatuses] = useState<Map<string, ScreenStatus>>(new Map())
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [changes, setChanges] = useState<Map<string, 'P' | 'A' | 'D'>>(new Map())
  const [notification, setNotification] = useState<{ type: 'success' | 'error', message: string } | null>(null)

  const fetchScreens = async () => {
    try {
      setLoading(true)
      const response = await fetchWithAuth(API_ENDPOINTS.SCREENS.ADMIN_ALL)
      if (!response.ok) throw new Error('Erro ao carregar telas')
      const data = await response.json()
      
      const statusMap = new Map<string, ScreenStatus>()
      data.forEach((screen: any) => {
        statusMap.set(screen.screen_key, {
          id: screen.id,
          screen_key: screen.screen_key,
          status: screen.status
        })
      })
      
      setScreenStatuses(statusMap)
      setChanges(new Map())
    } catch (error) {
      console.error('Erro ao buscar telas:', error)
      setNotification({ type: 'error', message: 'Não foi possível carregar as telas. Verifique sua conexão.' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchScreens()
  }, [])

  // Auto-fechar notificação após 5 segundos
  useEffect(() => {
    if (notification && notification.type === 'error') {
      const timer = setTimeout(() => {
        setNotification(null)
      }, 5000)
      return () => clearTimeout(timer)
    }
  }, [notification])

  const handleStatusChange = (screenKey: string, newStatus: 'P' | 'A' | 'D') => {
    setChanges(prev => new Map(prev).set(screenKey, newStatus))
  }

  const getCurrentStatus = (screenKey: string): 'P' | 'A' | 'D' => {
    const changeStatus = changes.get(screenKey)
    if (changeStatus) return changeStatus
    
    const dbStatus = screenStatuses.get(screenKey)?.status
    return dbStatus ?? 'P' // Default para P se não existir no banco
  }

  const isScreenInDatabase = (screenKey: string): boolean => {
    return screenStatuses.has(screenKey)
  }

  const hasChanges = changes.size > 0

  const handleSave = async () => {
    if (!hasChanges) return

    try {
      setSaving(true)
      
      // Filtrar apenas screens que existem no banco
      const validChanges = Array.from(changes.entries()).filter(([screenKey, status]) => {
        const screen = screenStatuses.get(screenKey)
        if (!screen) {
          console.warn(`Screen não encontrado no banco: ${screenKey} - ignorando na atualização`)
          return false
        }
        return true
      })

      if (validChanges.length === 0) {
        setNotification({ type: 'error', message: 'Nenhum screen válido encontrado para atualizar' })
        setSaving(false)
        return
      }

      const promises = validChanges.map(([screenKey, status]) => {
        const screen = screenStatuses.get(screenKey)!
        
        return fetchWithAuth(API_ENDPOINTS.SCREENS.UPDATE(screen.id), {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status }),
        })
      })

      const results = await Promise.all(promises)
      const allSuccess = results.every(r => r.ok)
      const failedCount = results.filter(r => !r.ok).length

      if (allSuccess) {
        setNotification({ type: 'success', message: `${validChanges.length} tela(s) atualizada(s) com sucesso!` })
        await fetchScreens()
        // Limpar changes apenas dos que foram processados com sucesso
        setChanges(prev => {
          const newMap = new Map(prev)
          validChanges.forEach(([screenKey]) => newMap.delete(screenKey))
          return newMap
        })
      } else {
        throw new Error(`${failedCount} atualização(ões) falharam`)
      }
    } catch (error) {
      console.error('Erro ao salvar:', error)
      setNotification({ type: 'error', message: `Erro ao salvar alterações. ${error instanceof Error ? error.message : 'Tente novamente.'}` })
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    setChanges(new Map())
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </DashboardLayout>
    )
  }

  return (
    <RequireAdmin>
      <DashboardLayout>
        <div className="container mx-auto p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
                <Eye className="h-8 w-8" />
                Visibilidade de Telas
              </h1>
              <p className="text-muted-foreground mt-2">
                Controle quais telas aparecem para diferentes tipos de usuários (estrutura da sidebar)
              </p>
            </div>

          {hasChanges && (
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleReset} disabled={saving}>
                Cancelar
              </Button>
              <Button onClick={handleSave} disabled={saving}>
                {saving ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Salvando...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Salvar {changes.size} alteração(ões)
                  </>
                )}
              </Button>
            </div>
          )}
        </div>

        {/* Notificação elegante */}
        {notification && (
          <Alert variant={notification.type === 'success' ? 'default' : 'destructive'} className="animate-in fade-in slide-in-from-top-2">
            {notification.type === 'success' ? (
              <CheckCircle2 className="h-4 w-4" />
            ) : (
              <XCircle className="h-4 w-4" />
            )}
            <AlertTitle>{notification.type === 'success' ? 'Sucesso!' : 'Erro'}</AlertTitle>
            <AlertDescription>{notification.message}</AlertDescription>
          </Alert>
        )}

        <div className="grid gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Legenda de Status</CardTitle>
              <CardDescription>
                Defina o nível de acesso de cada tela
              </CardDescription>
            </CardHeader>
            <CardContent className="flex gap-4">
              {Object.entries(STATUS_LABELS).map(([key, { label, badge, description }]) => (
                <div key={key} className="flex items-center gap-2">
                  <Badge className={`${badge} text-white`}>{key}</Badge>
                  <div>
                    <div className="font-semibold">{label}</div>
                    <div className="text-sm text-muted-foreground">{description}</div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Configuração de Telas (Sidebar)</CardTitle>
              <CardDescription>
                {SIDEBAR_STRUCTURE.length} seções • Estrutura idêntica à sidebar
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {SIDEBAR_STRUCTURE.map((section, idx) => {
                  const parentKey = getScreenKey(section.parentUrl)
                  const parentStatus = getCurrentStatus(parentKey)
                  const hasChange = changes.has(parentKey)

                  return (
                    <Collapsible key={idx} defaultOpen={false} className="group">
                      <div className="space-y-2">
                        {/* Seção pai com trigger */}
                        <div className="flex items-center gap-2">
                          <CollapsibleTrigger className="p-1 hover:bg-accent rounded-sm transition-colors">
                            <ChevronDown className="h-4 w-4 transition-transform duration-200 group-data-[state=open]:rotate-180" />
                          </CollapsibleTrigger>
                          
                          <div className="flex-1">
                            <ScreenItem
                              icon={section.icon}
                              title={section.title}
                              screenKey={parentKey}
                              currentStatus={parentStatus}
                              hasChange={hasChange}
                              onStatusChange={handleStatusChange}
                              existsInDatabase={isScreenInDatabase(parentKey)}
                            />
                          </div>
                        </div>
                        
                        {/* Sub-items colapsáveis */}
                        <CollapsibleContent className="space-y-2">
                          {section.items.map((item, itemIdx) => {
                            const itemKey = getScreenKey(item.url, true, section.parentUrl)
                            const itemStatus = getCurrentStatus(itemKey)
                            const itemHasChange = changes.has(itemKey)

                            return (
                              <div key={itemIdx} className="ml-10">
                                <ScreenItem
                                  title={item.title}
                                  screenKey={itemKey}
                                  currentStatus={itemStatus}
                                  hasChange={itemHasChange}
                                  onStatusChange={handleStatusChange}
                                  isSubItem
                                  existsInDatabase={isScreenInDatabase(itemKey)}
                                />
                              </div>
                            )
                          })}
                        </CollapsibleContent>
                      </div>
                    </Collapsible>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Seção Projects */}
          <Card>
            <CardHeader>
              <CardTitle>Projects</CardTitle>
              <CardDescription>
                {SIDEBAR_PROJECTS.length} projetos disponíveis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {SIDEBAR_PROJECTS.map((project, idx) => {
                  const projectKey = getScreenKey(project.url)
                  const projectStatus = getCurrentStatus(projectKey)
                  const hasChange = changes.has(projectKey)

                  return (
                    <ScreenItem
                      key={idx}
                      icon={project.icon}
                      title={project.title}
                      screenKey={projectKey}
                      currentStatus={projectStatus}
                      hasChange={hasChange}
                      onStatusChange={handleStatusChange}
                      existsInDatabase={isScreenInDatabase(projectKey)}
                    />
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
    </RequireAdmin>
  )
}

interface ScreenItemProps {
  icon?: any
  title: string
  screenKey: string
  currentStatus: 'P' | 'A' | 'D'
  hasChange: boolean
  onStatusChange: (screenKey: string, status: 'P' | 'A' | 'D') => void
  isSubItem?: boolean
  existsInDatabase?: boolean
}

function ScreenItem({ icon: Icon, title, screenKey, currentStatus, hasChange, onStatusChange, isSubItem = false, existsInDatabase = true }: ScreenItemProps) {
  const statusInfo = STATUS_LABELS[currentStatus]

  return (
    <div
      className={`flex items-center justify-between p-4 border rounded-lg transition-colors ${
        hasChange ? 'bg-accent/50 border-primary' : 'hover:bg-accent/30'
      } ${isSubItem ? 'border-dashed' : ''} ${!existsInDatabase ? 'opacity-60 bg-red-50 border-red-200' : ''}`}
    >
      <div className="flex items-center gap-4 flex-1">
        {Icon && <Icon className="h-5 w-5 text-muted-foreground" />}
        <Badge className={`${statusInfo.badge} text-white`}>
          {currentStatus}
        </Badge>
        <div>
          <div className={`font-semibold ${isSubItem ? 'text-sm' : ''} flex items-center gap-2`}>
            {title}
            {!existsInDatabase && (
              <Badge variant="destructive" className="text-xs">
                Não existe no banco
              </Badge>
            )}
          </div>
          <div className="text-xs text-muted-foreground">
            {screenKey}
          </div>
        </div>
      </div>

      <Select
        value={currentStatus}
        onValueChange={(value: 'P' | 'A' | 'D') => onStatusChange(screenKey, value)}
        disabled={!existsInDatabase}
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="P">
            <div className="flex items-center gap-2">
              <Badge className="bg-green-500 text-white">P</Badge>
              Produção
            </div>
          </SelectItem>
          <SelectItem value="A">
            <div className="flex items-center gap-2">
              <Badge className="bg-orange-500 text-white">A</Badge>
              Admin
            </div>
          </SelectItem>
          <SelectItem value="D">
            <div className="flex items-center gap-2">
              <Badge className="bg-purple-500 text-white">D</Badge>
              Development
            </div>
          </SelectItem>
        </SelectContent>
      </Select>
    </div>
  )
}
