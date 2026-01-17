/**
 * Testes de integração para hook useInvestimentos
 * Verifica se o hook funciona corretamente com as APIs reais
 */

import { renderHook, act, waitFor } from '@testing-library/react'
import { useInvestimentos } from '../hooks/use-investimentos'
import * as investimentosApi from '../services/investimentos-api'

// Mock das funções da API
jest.mock('../services/investimentos-api')
const mockApi = investimentosApi as jest.Mocked<typeof investimentosApi>

describe('useInvestimentos Hook Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Estado inicial', () => {
    it('deve ter estado inicial correto ao carregar dados', async () => {
      const mockData = [
        {
          id: 1,
          balance_id: 'TEST001',
          nome_produto: 'Tesouro IPCA+ 2035',
          corretora: 'XP Investimentos',
          tipo_investimento: 'Renda Fixa',
          quantidade: 10,
          valor_total_inicial: 1000,
          ativo: true,
          created_at: '2024-01-15T10:00:00Z'
        }
      ]

      const mockResumo = {
        total_investido: 5000,
        valor_atual: 6500,
        rendimento_total: 1500,
        rendimento_percentual: 30.0,
        quantidade_produtos: 2,
        produtos_ativos: 2
      }

      const mockDistribuicao = [
        {
          tipo: 'Renda Fixa',
          quantidade: 2,
          total_investido: 6000,
          percentual: 60.0
        }
      ]

      // Mock das respostas das APIs
      mockApi.getInvestimentos.mockResolvedValue(mockData)
      mockApi.getPortfolioResumo.mockResolvedValue(mockResumo)
      mockApi.getDistribuicaoPorTipo.mockResolvedValue(mockDistribuicao)

      const { result } = renderHook(() => useInvestimentos())

      // Aguardar o carregamento inicial
      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.investimentos).toEqual(mockData)
      expect(result.current.resumo).toEqual(mockResumo)
      expect(result.current.distribuicao).toEqual(mockDistribuicao)
      expect(result.current.error).toBe(null)
    })

    it('deve iniciar com estado de loading', () => {
      mockApi.getInvestimentos.mockResolvedValue([])
      mockApi.getPortfolioResumo.mockResolvedValue({} as any)
      mockApi.getDistribuicaoPorTipo.mockResolvedValue([])

      const { result } = renderHook(() => useInvestimentos())

      expect(result.current.loading).toBe(true)
      expect(result.current.investimentos).toEqual([])
      expect(result.current.resumo).toBe(null)
      expect(result.current.error).toBe(null)
    })
  })

  describe('Carregamento com filtros', () => {
    it('deve aplicar filtros corretamente', async () => {
      const filters = {
        tipo_investimento: 'Renda Fixa',
        ativo: true,
        limit: 50
      }

      const mockData = [
        {
          id: 1,
          tipo_investimento: 'Renda Fixa',
          ativo: true
        }
      ]

      mockApi.getInvestimentos.mockResolvedValue(mockData as any)
      mockApi.getPortfolioResumo.mockResolvedValue({} as any)
      mockApi.getDistribuicaoPorTipo.mockResolvedValue([])

      const { result } = renderHook(() => useInvestimentos(filters))

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(mockApi.getInvestimentos).toHaveBeenCalledWith(filters)
      expect(result.current.investimentos).toEqual(mockData)
    })

    it('deve funcionar sem filtros', async () => {
      mockApi.getInvestimentos.mockResolvedValue([])
      mockApi.getPortfolioResumo.mockResolvedValue({} as any)
      mockApi.getDistribuicaoPorTipo.mockResolvedValue([])

      const { result } = renderHook(() => useInvestimentos())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(mockApi.getInvestimentos).toHaveBeenCalledWith(undefined)
    })
  })

  describe('Manipulação de erros', () => {
    it('deve lidar com erro de carregamento', async () => {
      const errorMessage = 'Erro na API'
      mockApi.getInvestimentos.mockRejectedValue(new Error(errorMessage))
      mockApi.getPortfolioResumo.mockRejectedValue(new Error('Erro resumo'))
      mockApi.getDistribuicaoPorTipo.mockRejectedValue(new Error('Erro distribuição'))

      const { result } = renderHook(() => useInvestimentos())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
        expect(result.current.error).toBe(errorMessage)
      })

      expect(result.current.investimentos).toEqual([])
      expect(result.current.resumo).toBe(null)
    })

    it('deve lidar com erro em uma das APIs', async () => {
      // Sucesso nos investimentos, erro no resumo
      mockApi.getInvestimentos.mockResolvedValue([])
      mockApi.getPortfolioResumo.mockRejectedValue(new Error('Erro no resumo'))
      mockApi.getDistribuicaoPorTipo.mockResolvedValue([])

      const { result } = renderHook(() => useInvestimentos())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
        expect(result.current.error).toBe('Erro no resumo')
      })
    })
  })

  describe('Função refresh', () => {
    it('deve recarregar dados quando refresh é chamado', async () => {
      // Dados iniciais
      const initialData = [{ id: 1, nome_produto: 'Produto 1' }]
      const refreshData = [
        { id: 1, nome_produto: 'Produto 1' },
        { id: 2, nome_produto: 'Produto 2' }
      ]

      mockApi.getInvestimentos
        .mockResolvedValueOnce(initialData as any)
        .mockResolvedValueOnce(refreshData as any)
      
      mockApi.getPortfolioResumo.mockResolvedValue({} as any)
      mockApi.getDistribuicaoPorTipo.mockResolvedValue([])

      const { result } = renderHook(() => useInvestimentos())

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.investimentos).toEqual(initialData)

      // Executar refresh
      await act(async () => {
        await result.current.refresh()
      })

      expect(result.current.investimentos).toEqual(refreshData)
      expect(mockApi.getInvestimentos).toHaveBeenCalledTimes(2)
    })

    it('deve lidar com erro durante refresh', async () => {
      // Sucesso inicial
      mockApi.getInvestimentos.mockResolvedValueOnce([])
      mockApi.getPortfolioResumo.mockResolvedValue({} as any)
      mockApi.getDistribuicaoPorTipo.mockResolvedValue([])

      const { result } = renderHook(() => useInvestimentos())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.error).toBe(null)

      // Erro no refresh
      mockApi.getInvestimentos.mockRejectedValueOnce(new Error('Erro no refresh'))

      await act(async () => {
        await result.current.refresh()
      })

      expect(result.current.error).toBe('Erro no refresh')
      expect(result.current.loading).toBe(false)
    })
  })

  describe('Reatividade a mudanças de filtros', () => {
    it('deve recarregar quando filtros mudarem', async () => {
      mockApi.getInvestimentos.mockResolvedValue([])
      mockApi.getPortfolioResumo.mockResolvedValue({} as any)
      mockApi.getDistribuicaoPorTipo.mockResolvedValue([])

      const { result, rerender } = renderHook(
        (filters) => useInvestimentos(filters),
        { initialProps: { tipo_investimento: 'Renda Fixa' } as any }
      )

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(mockApi.getInvestimentos).toHaveBeenCalledWith({ tipo_investimento: 'Renda Fixa' })

      // Mudar filtros
      rerender({ tipo_investimento: 'Ação' })

      await waitFor(() => {
        expect(mockApi.getInvestimentos).toHaveBeenCalledWith({ tipo_investimento: 'Ação' })
      })

      expect(mockApi.getInvestimentos).toHaveBeenCalledTimes(2)
    })

    it('deve cancelar requisições em andamento quando filtros mudam', async () => {
      let resolveFirstCall: any
      const firstPromise = new Promise((resolve) => {
        resolveFirstCall = resolve
      })

      mockApi.getInvestimentos
        .mockReturnValueOnce(firstPromise as any)
        .mockResolvedValueOnce([])
      
      mockApi.getPortfolioResumo.mockResolvedValue({} as any)
      mockApi.getDistribuicaoPorTipo.mockResolvedValue([])

      const { result, rerender } = renderHook(
        (filters) => useInvestimentos(filters),
        { initialProps: { tipo_investimento: 'Renda Fixa' } as any }
      )

      // Mudar filtros antes da primeira requisição terminar
      rerender({ tipo_investimento: 'Ação' })

      // Resolver primeira requisição (deveria ser cancelada)
      resolveFirstCall([{ id: 1, nome: 'Cancelado' }])

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // Não deveria ter os dados da primeira requisição cancelada
      expect(result.current.investimentos).not.toEqual([{ id: 1, nome: 'Cancelado' }])
    })
  })
})

// Testes para funções CRUD individuais da API
describe('API Functions Integration', () => {
  beforeEach(() => {
    global.fetch = jest.fn()
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('createInvestimento', () => {
    it('deve criar investimento com sucesso', async () => {
      const novoInvestimento = {
        balance_id: 'NEW001',
        nome_produto: 'Novo Tesouro Direto',
        corretora: 'Clear',
        tipo_investimento: 'Renda Fixa',
        quantidade: 5,
        valor_total_inicial: 750.50
      }

      const mockResponse = {
        id: 10,
        ...novoInvestimento,
        ativo: true,
        created_at: '2024-01-16T20:00:00Z'
      }

      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResponse
      })

      const result = await investimentosApi.createInvestimento(novoInvestimento)

      expect(result).toEqual(mockResponse)
      expect(global.fetch).toHaveBeenCalledWith('/api/investimentos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(novoInvestimento)
      })
    })

    it('deve lançar erro quando criação falha', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 400
      })

      await expect(
        investimentosApi.createInvestimento({} as any)
      ).rejects.toThrow('Erro ao criar investimento')
    })
  })

  describe('updateInvestimento', () => {
    it('deve atualizar investimento com sucesso', async () => {
      const dadosAtualizacao = {
        nome_produto: 'Produto Atualizado',
        quantidade: 15
      }

      const mockResponse = {
        id: 1,
        balance_id: 'TEST001',
        ...dadosAtualizacao,
        tipo_investimento: 'Renda Fixa',
        ativo: true
      }

      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResponse
      })

      const result = await investimentosApi.updateInvestimento(1, dadosAtualizacao)

      expect(result).toEqual(mockResponse)
      expect(global.fetch).toHaveBeenCalledWith('/api/investimentos/1', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dadosAtualizacao)
      })
    })

    it('deve lançar erro quando atualização falha', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404
      })

      await expect(
        investimentosApi.updateInvestimento(999, {})
      ).rejects.toThrow('Erro ao atualizar investimento')
    })
  })

  describe('deleteInvestimento', () => {
    it('deve deletar investimento com sucesso', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true
      })

      await investimentosApi.deleteInvestimento(1)

      expect(global.fetch).toHaveBeenCalledWith('/api/investimentos/1', {
        method: 'DELETE'
      })
    })

    it('deve lançar erro quando deleção falha', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404
      })

      await expect(
        investimentosApi.deleteInvestimento(999)
      ).rejects.toThrow('Erro ao deletar investimento')
    })
  })

  describe('getInvestimento', () => {
    it('deve buscar investimento específico', async () => {
      const mockInvestimento = {
        id: 1,
        balance_id: 'TEST001',
        nome_produto: 'Tesouro IPCA+',
        corretora: 'XP',
        tipo_investimento: 'Renda Fixa'
      }

      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockInvestimento
      })

      const result = await investimentosApi.getInvestimento(1)

      expect(result).toEqual(mockInvestimento)
      expect(global.fetch).toHaveBeenCalledWith('/api/investimentos/1')
    })
  })
})