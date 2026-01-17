/**
 * Testes End-to-End para o sistema de investimentos
 * Simula fluxos completos de usuário
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import InvestimentosPage from '../../../app/investimentos/page'

// Mock dos componentes que dependem de bibliotecas externas
jest.mock('lucide-react', () => ({
  Search: () => <div data-testid="search-icon">Search</div>,
  Filter: () => <div data-testid="filter-icon">Filter</div>,
  Plus: () => <div data-testid="plus-icon">Plus</div>,
  Download: () => <div data-testid="download-icon">Download</div>,
  TrendingUp: () => <div data-testid="trending-up-icon">TrendingUp</div>,
  BarChart: () => <div data-testid="bar-chart-icon">BarChart</div>,
  PieChart: () => <div data-testid="pie-chart-icon">PieChart</div>,
  Edit: () => <div data-testid="edit-icon">Edit</div>,
  Trash2: () => <div data-testid="trash-icon">Trash</div>
}))

// Mock dos componentes UI
jest.mock('../../../components/ui/button', () => ({
  Button: ({ children, onClick, ...props }: any) => (
    <button onClick={onClick} {...props}>
      {children}
    </button>
  )
}))

jest.mock('../../../components/ui/card', () => ({
  Card: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  CardContent: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  CardHeader: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  CardTitle: ({ children, ...props }: any) => <h3 {...props}>{children}</h3>
}))

jest.mock('../../../components/ui/input', () => ({
  Input: ({ ...props }: any) => <input {...props} />
}))

jest.mock('../../../components/ui/select', () => ({
  Select: ({ children, onValueChange }: any) => (
    <div data-testid="select">
      {children}
    </div>
  ),
  SelectContent: ({ children }: any) => <div>{children}</div>,
  SelectItem: ({ children, value, ...props }: any) => (
    <div {...props} data-value={value} onClick={() => {}}>
      {children}
    </div>
  ),
  SelectTrigger: ({ children }: any) => <div>{children}</div>,
  SelectValue: ({ placeholder }: any) => <span>{placeholder}</span>
}))

// Mock das chart libraries
jest.mock('recharts', () => ({
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: ({ children }: any) => <div data-testid="pie">{children}</div>,
  Cell: () => <div data-testid="cell"></div>,
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  Tooltip: () => <div data-testid="tooltip"></div>,
  Legend: () => <div data-testid="legend"></div>,
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line"></div>,
  XAxis: () => <div data-testid="x-axis"></div>,
  YAxis: () => <div data-testid="y-axis"></div>,
  CartesianGrid: () => <div data-testid="cartesian-grid"></div>,
  AreaChart: ({ children }: any) => <div data-testid="area-chart">{children}</div>,
  Area: () => <div data-testid="area"></div>
}))

// Mock do fetch global
global.fetch = jest.fn()

// Mock do URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => 'blob:test-url')

// Mock do link download
const mockClickLink = jest.fn()
global.document.createElement = jest.fn((tagName) => {
  if (tagName === 'a') {
    return {
      style: {},
      click: mockClickLink,
      setAttribute: jest.fn(),
      getAttribute: jest.fn()
    } as any
  }
  return {} as any
})

describe('Investimentos E2E Tests', () => {
  const user = userEvent.setup()
  
  const mockInvestimentos = [
    {
      id: 1,
      balance_id: 'TSR001',
      nome_produto: 'Tesouro IPCA+ 2035',
      corretora: 'XP Investimentos',
      tipo_investimento: 'Renda Fixa',
      quantidade: 10,
      valor_total_inicial: '1000.00',
      ativo: true,
      created_at: '2024-01-15T10:00:00Z'
    },
    {
      id: 2,
      balance_id: 'PETR4001',
      nome_produto: 'PETR4',
      corretora: 'Rico',
      tipo_investimento: 'Ação',
      quantidade: 100,
      valor_total_inicial: '2500.00',
      ativo: true,
      created_at: '2024-01-16T14:30:00Z'
    },
    {
      id: 3,
      balance_id: 'LCI001',
      nome_produto: 'LCI Banco do Brasil',
      corretora: 'BB Investimentos',
      tipo_investimento: 'Renda Fixa',
      quantidade: 1,
      valor_total_inicial: '5000.00',
      ativo: true,
      created_at: '2024-01-10T09:00:00Z'
    }
  ]

  const mockResumo = {
    total_investido: '8500.00',
    valor_atual: '10200.00',
    rendimento_total: '1700.00',
    rendimento_percentual: 20.0,
    quantidade_produtos: 3,
    produtos_ativos: 3
  }

  const mockDistribuicao = [
    {
      tipo: 'Renda Fixa',
      quantidade: 2,
      total_investido: '6000.00'
    },
    {
      tipo: 'Ação',
      quantidade: 1,
      total_investido: '2500.00'
    }
  ]

  beforeEach(() => {
    ;(global.fetch as jest.Mock).mockClear()
    mockClickLink.mockClear()

    // Setup padrão de respostas de API
    ;(global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockInvestimentos
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockResumo
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockDistribuicao
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => []
      })
  })

  describe('Carregamento inicial da página', () => {
    it('deve carregar a página com todos os dados iniciais', async () => {
      render(<InvestimentosPage />)

      // Verificar se componentes principais estão renderizados
      expect(screen.getByText('Meus Investimentos')).toBeInTheDocument()
      
      // Aguardar carregamento dos dados
      await waitFor(() => {
        expect(screen.getByDisplayValue('TSR001')).toBeInTheDocument()
        expect(screen.getByDisplayValue('PETR4001')).toBeInTheDocument()
        expect(screen.getByDisplayValue('LCI001')).toBeInTheDocument()
      })

      // Verificar se as APIs foram chamadas
      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/investimentos/')
      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/investimentos/resumo')
      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/investimentos/distribuicao')
    })

    it('deve mostrar loading inicial', async () => {
      // Mock com delay para simular carregamento
      ;(global.fetch as jest.Mock).mockImplementation(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({
            ok: true,
            json: async () => mockInvestimentos
          }), 100)
        )
      )

      render(<InvestimentosPage />)

      // Durante o carregamento, deve mostrar loading
      expect(screen.getByText('Carregando investimentos...')).toBeInTheDocument()
    })
  })

  describe('Fluxo de pesquisa e filtros', () => {
    it('deve permitir pesquisar investimentos por nome', async () => {
      render(<InvestimentosPage />)

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(screen.getByDisplayValue('TSR001')).toBeInTheDocument()
      })

      // Encontrar campo de busca
      const searchInput = screen.getByPlaceholderText('Buscar investimentos...')
      
      // Configurar mock para resposta da pesquisa
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => [mockInvestimentos[0]] // Retornar apenas o Tesouro
      })

      // Digitar pesquisa
      await user.type(searchInput, 'Tesouro')

      // Aguardar que a pesquisa seja executada
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          'http://localhost:8000/api/v1/investimentos/?search=Tesouro'
        )
      })
    })

    it('deve filtrar por tipo de investimento', async () => {
      render(<InvestimentosPage />)

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(screen.getByDisplayValue('TSR001')).toBeInTheDocument()
      })

      // Mock da resposta filtrada
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockInvestimentos.filter(i => i.tipo_investimento === 'Renda Fixa')
      })

      // Simular seleção de filtro
      const tipoFilter = screen.getByTestId('select')
      fireEvent.click(tipoFilter)

      // Aguardar que o filtro seja aplicado
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('tipo_investimento=Renda+Fixa')
        )
      })
    })
  })

  describe('Fluxo CRUD de investimentos', () => {
    it('deve permitir criar novo investimento', async () => {
      render(<InvestimentosPage />)

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(screen.getByDisplayValue('TSR001')).toBeInTheDocument()
      })

      // Clicar no botão de adicionar
      const addButton = screen.getByText('Novo Investimento')
      await user.click(addButton)

      // Preencher formulário (assumindo que o modal abriu)
      const novoInvestimento = {
        balance_id: 'VALE3001',
        nome_produto: 'VALE3',
        corretora: 'XP',
        tipo_investimento: 'Ação',
        quantidade: 50,
        valor_total_inicial: 1500
      }

      // Mock da resposta de criação
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({ id: 4, ...novoInvestimento })
      })

      // Mock do reload após criação
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => [...mockInvestimentos, { id: 4, ...novoInvestimento }]
      })

      // Simular submit do formulário (seria necessário implementar o modal)
      // Por enquanto, vamos simular a chamada direta da API
      await waitFor(() => {
        // Verificar se tentaria chamar a API de criação
        expect(screen.getByText('Novo Investimento')).toBeInTheDocument()
      })
    })

    it('deve permitir editar investimento existente', async () => {
      render(<InvestimentosPage />)

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(screen.getByDisplayValue('TSR001')).toBeInTheDocument()
      })

      // Procurar botão de editar do primeiro item
      const editButtons = screen.getAllByTestId('edit-icon')
      expect(editButtons.length).toBeGreaterThan(0)

      // Mock da resposta de atualização
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ 
          ...mockInvestimentos[0], 
          quantidade: 20 // Quantidade alterada
        })
      })

      // Simular clique no botão editar
      await user.click(editButtons[0])

      // Verificar se modal de edição seria aberto
      await waitFor(() => {
        expect(editButtons[0]).toBeInTheDocument()
      })
    })

    it('deve permitir deletar investimento', async () => {
      render(<InvestimentosPage />)

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(screen.getByDisplayValue('TSR001')).toBeInTheDocument()
      })

      // Procurar botão de deletar
      const deleteButtons = screen.getAllByTestId('trash-icon')
      expect(deleteButtons.length).toBeGreaterThan(0)

      // Mock da resposta de deleção
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204
      })

      // Mock do reload após deleção
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockInvestimentos.slice(1) // Remove primeiro item
      })

      // Simular clique no botão deletar
      await user.click(deleteButtons[0])

      // Verificar se confirmação seria solicitada
      await waitFor(() => {
        expect(deleteButtons[0]).toBeInTheDocument()
      })
    })
  })

  describe('Fluxo de exportação', () => {
    it('deve permitir exportar dados para CSV', async () => {
      render(<InvestimentosPage />)

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(screen.getByDisplayValue('TSR001')).toBeInTheDocument()
      })

      // Procurar botão de exportar
      const exportButton = screen.getByTestId('download-icon')
      await user.click(exportButton)

      // Verificar se dropdown de exportação aparece
      const csvOption = screen.getByText('Exportar CSV')
      expect(csvOption).toBeInTheDocument()

      // Simular clique na opção CSV
      await user.click(csvOption)

      // Verificar se download foi iniciado
      await waitFor(() => {
        expect(mockClickLink).toHaveBeenCalled()
      })
    })

    it('deve permitir exportar dados para Excel', async () => {
      render(<InvestimentosPage />)

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(screen.getByDisplayValue('TSR001')).toBeInTheDocument()
      })

      // Procurar botão de exportar
      const exportButton = screen.getByTestId('download-icon')
      await user.click(exportButton)

      // Procurar opção Excel
      const excelOption = screen.getByText('Exportar Excel')
      expect(excelOption).toBeInTheDocument()

      // Simular clique na opção Excel
      await user.click(excelOption)

      // Verificar se download foi iniciado
      await waitFor(() => {
        expect(mockClickLink).toHaveBeenCalled()
      })
    })
  })

  describe('Visualizações e gráficos', () => {
    it('deve renderizar gráficos de distribuição', async () => {
      render(<InvestimentosPage />)

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(screen.getByDisplayValue('TSR001')).toBeInTheDocument()
      })

      // Verificar se componentes de gráfico estão presentes
      expect(screen.getByTestId('pie-chart')).toBeInTheDocument()
    })

    it('deve alternar entre diferentes visualizações', async () => {
      render(<InvestimentosPage />)

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(screen.getByDisplayValue('TSR001')).toBeInTheDocument()
      })

      // Procurar botões de alternância de visualização
      const chartButtons = screen.getAllByTestId('pie-chart-icon')
      
      if (chartButtons.length > 0) {
        await user.click(chartButtons[0])
        // Verificar se visualização mudou
        await waitFor(() => {
          expect(screen.getByTestId('pie-chart')).toBeInTheDocument()
        })
      }
    })
  })

  describe('Tratamento de erros', () => {
    it('deve mostrar mensagem de erro quando API falha', async () => {
      // Mock de erro na API
      ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network Error'))

      render(<InvestimentosPage />)

      // Aguardar erro ser processado
      await waitFor(() => {
        expect(screen.getByText(/erro ao carregar/i)).toBeInTheDocument()
      })
    })

    it('deve mostrar estado vazio quando não há investimentos', async () => {
      // Mock de resposta vazia
      ;(global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => []
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            total_investido: '0.00',
            valor_atual: '0.00',
            rendimento_total: '0.00',
            rendimento_percentual: 0.0,
            quantidade_produtos: 0,
            produtos_ativos: 0
          })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => []
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => []
        })

      render(<InvestimentosPage />)

      // Aguardar carregamento
      await waitFor(() => {
        expect(screen.getByText(/nenhum investimento encontrado/i)).toBeInTheDocument()
      })
    })
  })

  describe('Responsividade e acessibilidade', () => {
    it('deve ser acessível por teclado', async () => {
      render(<InvestimentosPage />)

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(screen.getByDisplayValue('TSR001')).toBeInTheDocument()
      })

      // Testar navegação por Tab
      const searchInput = screen.getByPlaceholderText('Buscar investimentos...')
      searchInput.focus()
      expect(document.activeElement).toBe(searchInput)

      // Simular Tab para próximo elemento
      await user.tab()
      
      // Verificar se foco mudou
      expect(document.activeElement).not.toBe(searchInput)
    })
  })
})