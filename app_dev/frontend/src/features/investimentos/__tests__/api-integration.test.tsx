/**
 * Testes de integração para APIs de investimentos
 */

describe('Investimentos API Integration', () => {
  const API_BASE_URL = 'http://localhost:8000/api/v1'

  beforeEach(() => {
    // Setup fetch mock para cada teste
    global.fetch = jest.fn()
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('GET /investimentos', () => {
    it('deve retornar lista de investimentos com status 200', async () => {
      const mockResponse = [
        {
          id: 1,
          balance_id: 'TEST001',
          nome_produto: 'Tesouro IPCA+ 2035',
          corretora: 'XP Investimentos',
          tipo_investimento: 'Renda Fixa',
          quantidade: 10,
          valor_total_inicial: '1000.00',
          ativo: true,
          created_at: '2024-01-15T10:00:00Z'
        }
      ]

      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockResponse
      })

      const response = await fetch(`${API_BASE_URL}/investimentos/`)
      const data = await response.json()

      expect(response.ok).toBe(true)
      expect(response.status).toBe(200)
      expect(Array.isArray(data)).toBe(true)
      expect(data).toHaveLength(1)
      expect(data[0]).toHaveProperty('balance_id', 'TEST001')
      expect(data[0]).toHaveProperty('nome_produto', 'Tesouro IPCA+ 2035')
    })

    it('deve aceitar parâmetros de query', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => []
      })

      await fetch(`${API_BASE_URL}/investimentos/?tipo_investimento=Renda+Fixa&limit=50`)

      expect(global.fetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/investimentos/?tipo_investimento=Renda+Fixa&limit=50`
      )
    })

    it('deve lidar com erro 404 quando nenhum investimento for encontrado', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Nenhum investimento encontrado' })
      })

      const response = await fetch(`${API_BASE_URL}/investimentos/`)
      
      expect(response.ok).toBe(false)
      expect(response.status).toBe(404)
    })

    it('deve lidar com erro 500 do servidor', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Erro interno do servidor' })
      })

      const response = await fetch(`${API_BASE_URL}/investimentos/`)
      
      expect(response.ok).toBe(false)
      expect(response.status).toBe(500)
    })
  })

  describe('GET /investimentos/resumo', () => {
    it('deve retornar resumo do portfólio', async () => {
      const mockResumo = {
        total_investido: '2500.00',
        valor_atual: '3000.00',
        rendimento_total: '500.00',
        rendimento_percentual: 20.0,
        quantidade_produtos: 2,
        produtos_ativos: 2
      }

      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockResumo
      })

      const response = await fetch(`${API_BASE_URL}/investimentos/resumo`)
      const data = await response.json()

      expect(response.ok).toBe(true)
      expect(data).toHaveProperty('total_investido', '2500.00')
      expect(data).toHaveProperty('rendimento_percentual', 20.0)
      expect(data).toHaveProperty('quantidade_produtos', 2)
    })
  })

  describe('GET /investimentos/distribuicao', () => {
    it('deve retornar distribuição por tipos', async () => {
      const mockDistribuicao = [
        {
          tipo: 'Renda Fixa',
          quantidade: 1,
          total_investido: '1000.00'
        },
        {
          tipo: 'Ação',
          quantidade: 1,
          total_investido: '1500.00'
        }
      ]

      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockDistribuicao
      })

      const response = await fetch(`${API_BASE_URL}/investimentos/distribuicao`)
      const data = await response.json()

      expect(response.ok).toBe(true)
      expect(Array.isArray(data)).toBe(true)
      expect(data).toHaveLength(2)
      expect(data[0]).toHaveProperty('tipo', 'Renda Fixa')
      expect(data[1]).toHaveProperty('tipo', 'Ação')
    })
  })

  describe('GET /investimentos/timeline', () => {
    it('deve retornar timeline de rendimentos', async () => {
      const mockTimeline = [
        {
          ano: 2024,
          mes: 1,
          anomes: 202401,
          rendimento_mes: '100.00',
          patrimonio_final: '1100.00',
          aporte_mes: '1000.00'
        },
        {
          ano: 2024,
          mes: 2,
          anomes: 202402,
          rendimento_mes: '110.00',
          patrimonio_final: '1210.00',
          aporte_mes: '0.00'
        }
      ]

      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockTimeline
      })

      const response = await fetch(`${API_BASE_URL}/investimentos/timeline?ano_inicio=2024&ano_fim=2024`)
      const data = await response.json()

      expect(response.ok).toBe(true)
      expect(Array.isArray(data)).toBe(true)
      expect(data).toHaveLength(2)
      expect(data[0]).toHaveProperty('anomes', 202401)
      expect(data[1]).toHaveProperty('anomes', 202402)
    })

    it('deve aceitar parâmetros de ano', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => []
      })

      await fetch(`${API_BASE_URL}/investimentos/timeline?ano_inicio=2023&ano_fim=2024`)

      expect(global.fetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/investimentos/timeline?ano_inicio=2023&ano_fim=2024`
      )
    })
  })

  describe('POST /investimentos', () => {
    it('deve criar novo investimento com sucesso', async () => {
      const novoInvestimento = {
        balance_id: 'NEW001',
        nome_produto: 'Novo Produto',
        corretora: 'Nova Corretora',
        tipo_investimento: 'Renda Fixa',
        quantidade: 5,
        valor_total_inicial: 500.00
      }

      const mockResponse = {
        id: 10,
        ...novoInvestimento,
        user_id: 1,
        ativo: true,
        created_at: '2024-01-16T20:00:00Z'
      }

      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 201,
        json: async () => mockResponse
      })

      const response = await fetch(`${API_BASE_URL}/investimentos/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(novoInvestimento)
      })
      const data = await response.json()

      expect(response.ok).toBe(true)
      expect(response.status).toBe(201)
      expect(data).toHaveProperty('id', 10)
      expect(data).toHaveProperty('balance_id', 'NEW001')
    })

    it('deve retornar erro 400 para dados inválidos', async () => {
      const dadosInvalidos = {
        balance_id: '', // Campo obrigatório vazio
        nome_produto: 'Produto',
        corretora: 'Corretora'
        // Campos obrigatórios faltando
      }

      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ 
          detail: 'Dados inválidos',
          errors: ['balance_id é obrigatório', 'tipo_investimento é obrigatório']
        })
      })

      const response = await fetch(`${API_BASE_URL}/investimentos/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(dadosInvalidos)
      })

      expect(response.ok).toBe(false)
      expect(response.status).toBe(400)
    })
  })

  describe('PUT /investimentos/{id}', () => {
    it('deve atualizar investimento existente', async () => {
      const dadosAtualizacao = {
        nome_produto: 'Produto Atualizado',
        quantidade: 15,
        valor_total_inicial: 1500.00
      }

      const mockResponse = {
        id: 1,
        balance_id: 'TEST001',
        ...dadosAtualizacao,
        corretora: 'XP Investimentos',
        tipo_investimento: 'Renda Fixa',
        user_id: 1,
        ativo: true,
        created_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-16T20:00:00Z'
      }

      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockResponse
      })

      const response = await fetch(`${API_BASE_URL}/investimentos/1`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(dadosAtualizacao)
      })
      const data = await response.json()

      expect(response.ok).toBe(true)
      expect(response.status).toBe(200)
      expect(data).toHaveProperty('nome_produto', 'Produto Atualizado')
      expect(data).toHaveProperty('quantidade', 15)
    })

    it('deve retornar erro 404 para investimento inexistente', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Investimento não encontrado' })
      })

      const response = await fetch(`${API_BASE_URL}/investimentos/999`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nome_produto: 'Teste' })
      })

      expect(response.ok).toBe(false)
      expect(response.status).toBe(404)
    })
  })

  describe('DELETE /investimentos/{id}', () => {
    it('deve deletar investimento com sucesso', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 204
      })

      const response = await fetch(`${API_BASE_URL}/investimentos/1`, {
        method: 'DELETE'
      })

      expect(response.ok).toBe(true)
      expect(response.status).toBe(204)
    })

    it('deve retornar erro 404 para investimento inexistente', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Investimento não encontrado' })
      })

      const response = await fetch(`${API_BASE_URL}/investimentos/999`, {
        method: 'DELETE'
      })

      expect(response.ok).toBe(false)
      expect(response.status).toBe(404)
    })
  })

  describe('Error Handling', () => {
    it('deve lidar com timeout de rede', async () => {
      ;(global.fetch as jest.Mock).mockRejectedValue(new Error('Network timeout'))

      try {
        await fetch(`${API_BASE_URL}/investimentos/`)
        fail('Deveria ter lançado erro')
      } catch (error) {
        expect(error).toBeInstanceOf(Error)
        expect((error as Error).message).toBe('Network timeout')
      }
    })

    it('deve lidar com resposta malformada', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => {
          throw new Error('Invalid JSON')
        }
      })

      const response = await fetch(`${API_BASE_URL}/investimentos/`)
      
      try {
        await response.json()
        fail('Deveria ter lançado erro')
      } catch (error) {
        expect(error).toBeInstanceOf(Error)
        expect((error as Error).message).toBe('Invalid JSON')
      }
    })
  })

  describe('Headers e Autenticação', () => {
    it('deve incluir headers corretos nas requisições', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => []
      })

      await fetch(`${API_BASE_URL}/investimentos/`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer token123'
        }
      })

      expect(global.fetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/investimentos/`,
        expect.objectContaining({
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer token123'
          }
        })
      )
    })

    it('deve retornar erro 401 para token inválido', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Token inválido' })
      })

      const response = await fetch(`${API_BASE_URL}/investimentos/`, {
        headers: {
          'Authorization': 'Bearer invalid_token'
        }
      })

      expect(response.ok).toBe(false)
      expect(response.status).toBe(401)
    })
  })
})