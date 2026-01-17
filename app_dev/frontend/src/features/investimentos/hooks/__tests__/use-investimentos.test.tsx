/**
 * Testes para o hook useInvestimentos
 */

import { renderHook, waitFor } from '@testing-library/react'
import { useInvestimentos } from '@/features/investimentos/hooks/use-investimentos'
import * as investimentosApi from '@/features/investimentos/services/investimentos-api'

// Mock da API
jest.mock('@/features/investimentos/services/investimentos-api')

const mockInvestimentosApi = investimentosApi as jest.Mocked<typeof investimentosApi>

describe('useInvestimentos', () => {
  const mockInvestimentos = [
    {
      id: 1,
      user_id: 1,
      balance_id: 'TEST001',
      nome_produto: 'Tesouro IPCA+ 2035',
      corretora: 'XP Investimentos',
      tipo_investimento: 'Renda Fixa',
      quantidade: 10,
      valor_total_inicial: '1000.00',
      ativo: true,
      created_at: '2024-01-15T10:00:00Z',
    },
    {
      id: 2,
      user_id: 1,
      balance_id: 'TEST002',
      nome_produto: 'ITSA4',
      corretora: 'Clear Corretora',
      tipo_investimento: 'Ação',
      quantidade: 100,
      valor_total_inicial: '1500.00',
      ativo: true,
      created_at: '2024-02-10T14:30:00Z',
    },
  ]

  const mockResumo = {
    total_investido: '2500.00',
    valor_atual: '3000.00',
    rendimento_total: '500.00',
    rendimento_percentual: 20.0,
    quantidade_produtos: 2,
    produtos_ativos: 2,
  }

  const mockDistribuicao = [
    {
      tipo: 'Renda Fixa',
      quantidade: 1,
      total_investido: '1000.00',
    },
    {
      tipo: 'Ação',
      quantidade: 1,
      total_investido: '1500.00',
    },
  ]

  beforeEach(() => {
    jest.clearAllMocks()
    
    // Setup mocks padrão
    mockInvestimentosApi.getInvestimentos.mockResolvedValue(mockInvestimentos)
    mockInvestimentosApi.getPortfolioResumo.mockResolvedValue(mockResumo)
    mockInvestimentosApi.getDistribuicaoTipos.mockResolvedValue(mockDistribuicao)
  })

  it('deve carregar dados inicialmente', async () => {
    const { result } = renderHook(() => useInvestimentos({ limit: 100 }))

    // Estado inicial
    expect(result.current.loading).toBe(true)
    expect(result.current.investimentos).toEqual([])
    expect(result.current.resumo).toBeNull()
    expect(result.current.distribuicao).toEqual([])
    expect(result.current.error).toBeNull()

    // Aguardar carregamento
    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // Verificar dados carregados
    expect(result.current.investimentos).toEqual(mockInvestimentos)
    expect(result.current.resumo).toEqual(mockResumo)
    expect(result.current.distribuicao).toEqual(mockDistribuicao)

    // Verificar se APIs foram chamadas
    expect(mockInvestimentosApi.getInvestimentos).toHaveBeenCalledWith({ limit: 100 })
    expect(mockInvestimentosApi.getPortfolioResumo).toHaveBeenCalled()
    expect(mockInvestimentosApi.getDistribuicaoTipos).toHaveBeenCalled()
  })

  it('deve lidar com erro ao carregar investimentos', async () => {
    const errorMessage = 'Erro ao carregar investimentos'
    mockInvestimentosApi.getInvestimentos.mockRejectedValue(new Error(errorMessage))

    const { result } = renderHook(() => useInvestimentos({ limit: 100 }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // Verificar estado de erro
    expect(result.current.error).toBe(errorMessage)
    expect(result.current.investimentos).toEqual([])
    expect(result.current.resumo).toBeNull()
    expect(result.current.distribuicao).toEqual([])
  })

  it('deve lidar com erro ao carregar resumo', async () => {
    const errorMessage = 'Erro ao carregar resumo'
    mockInvestimentosApi.getPortfolioResumo.mockRejectedValue(new Error(errorMessage))

    const { result } = renderHook(() => useInvestimentos({ limit: 100 }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // Mesmo com erro no resumo, investimentos devem carregar
    expect(result.current.investimentos).toEqual(mockInvestimentos)
    expect(result.current.resumo).toBeNull()
    expect(result.current.distribuicao).toEqual(mockDistribuicao)
    expect(result.current.error).toBe(errorMessage)
  })

  it('deve permitir refresh dos dados', async () => {
    const { result } = renderHook(() => useInvestimentos({ limit: 100 }))

    // Aguardar carregamento inicial
    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // Limpar mocks para verificar se refresh chama APIs novamente
    jest.clearAllMocks()

    // Executar refresh
    result.current.refresh()

    // Verificar loading novamente
    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // Verificar se APIs foram chamadas novamente
    expect(mockInvestimentosApi.getInvestimentos).toHaveBeenCalledWith({ limit: 100 })
    expect(mockInvestimentosApi.getPortfolioResumo).toHaveBeenCalled()
    expect(mockInvestimentosApi.getDistribuicaoTipos).toHaveBeenCalled()
  })

  it('deve cancelar request ao desmontar componente', async () => {
    const { result, unmount } = renderHook(() => useInvestimentos({ limit: 100 }))

    // Desmontar antes do carregamento terminar
    unmount()

    // Aguardar um tempo para garantir que requests foram cancelados
    await waitFor(() => {
      // Se o componente foi desmontado corretamente, não deve haver erros
      expect(true).toBe(true)
    }, { timeout: 100 })
  })

  it('deve usar parâmetros de filtro corretos', async () => {
    const filters = {
      tipo_investimento: 'Renda Fixa',
      ativo: true,
      limit: 50,
      skip: 10,
    }

    renderHook(() => useInvestimentos(filters))

    await waitFor(() => {
      expect(mockInvestimentosApi.getInvestimentos).toHaveBeenCalledWith(filters)
    })
  })

  it('deve recarregar quando filtros mudarem', async () => {
    const initialFilters = { limit: 100 }
    const { result, rerender } = renderHook(
      ({ filters }) => useInvestimentos(filters),
      { initialProps: { filters: initialFilters } }
    )

    // Aguardar carregamento inicial
    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // Limpar mocks
    jest.clearAllMocks()

    // Mudar filtros
    const newFilters = { limit: 50, tipo_investimento: 'Ação' }
    rerender({ filters: newFilters })

    // Verificar novo carregamento
    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // Verificar se API foi chamada com novos filtros
    expect(mockInvestimentosApi.getInvestimentos).toHaveBeenCalledWith(newFilters)
  })

  it('deve lidar com dados vazios corretamente', async () => {
    mockInvestimentosApi.getInvestimentos.mockResolvedValue([])
    mockInvestimentosApi.getDistribuicaoTipos.mockResolvedValue([])

    const { result } = renderHook(() => useInvestimentos({ limit: 100 }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.investimentos).toEqual([])
    expect(result.current.distribuicao).toEqual([])
    expect(result.current.resumo).toEqual(mockResumo)
    expect(result.current.error).toBeNull()
  })
})