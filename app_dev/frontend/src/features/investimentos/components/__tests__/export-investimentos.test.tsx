/**
 * Testes para o componente ExportInvestimentos
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ExportInvestimentos } from '@/features/investimentos/components/export-investimentos'
import type { InvestimentoPortfolio } from '@/features/investimentos/types'

// Mock dos ícones Lucide
jest.mock('lucide-react', () => ({
  Download: () => <div data-testid="download-icon" />,
  FileSpreadsheet: () => <div data-testid="spreadsheet-icon" />,
  FileText: () => <div data-testid="text-icon" />,
  Loader2: () => <div data-testid="loader-icon" />,
}))

// Mock dos componentes UI
jest.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, disabled, variant, ...props }: any) => (
    <button
      data-testid="button"
      onClick={onClick}
      disabled={disabled}
      data-variant={variant}
      {...props}
    >
      {children}
    </button>
  ),
}))

jest.mock('@/components/ui/dropdown-menu', () => ({
  DropdownMenu: ({ children }: any) => <div data-testid="dropdown-menu">{children}</div>,
  DropdownMenuContent: ({ children }: any) => <div data-testid="dropdown-content">{children}</div>,
  DropdownMenuTrigger: ({ children, asChild }: any) => 
    asChild ? children : <div data-testid="dropdown-trigger">{children}</div>,
  DropdownMenuItem: ({ children, onClick, ...props }: any) => (
    <div data-testid="dropdown-item" onClick={onClick} {...props}>{children}</div>
  ),
  DropdownMenuLabel: ({ children }: any) => <div data-testid="dropdown-label">{children}</div>,
  DropdownMenuSeparator: () => <div data-testid="dropdown-separator" />,
}))

describe('ExportInvestimentos', () => {
  const mockInvestimentos: InvestimentoPortfolio[] = [
    {
      id: 1,
      user_id: 1,
      balance_id: 'TEST001',
      nome_produto: 'Tesouro IPCA+ 2035',
      corretora: 'XP Investimentos',
      tipo_investimento: 'Renda Fixa',
      classe_ativo: 'Ativo',
      emissor: 'Tesouro Nacional',
      percentual_cdi: 120.5,
      data_aplicacao: '2024-01-15',
      data_vencimento: '2035-05-15',
      quantidade: 10,
      valor_unitario_inicial: '100.00',
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

  const mockFiltros = {
    searchTerm: 'Tesouro',
    selectedType: 'Renda Fixa',
    selectedCorretora: 'XP Investimentos',
  }

  beforeEach(() => {
    jest.clearAllMocks()
    // Mock global alert
    global.alert = jest.fn()
    // Mock console.log
    global.console.log = jest.fn()

    // Mock Blob and URL.createObjectURL
    global.Blob = jest.fn(() => ({}) as any)
    global.URL.createObjectURL = jest.fn(() => 'mock-url')
    global.URL.revokeObjectURL = jest.fn()

    // Mock document.createElement e appendChild
    const mockLink = {
      href: '',
      download: '',
      click: jest.fn(),
    }
    global.document.createElement = jest.fn(() => mockLink as any)
    global.document.body.appendChild = jest.fn()
    global.document.body.removeChild = jest.fn()
  })

  it('deve renderizar botão de exportar com contador', () => {
    render(<ExportInvestimentos investimentos={mockInvestimentos} />)

    const button = screen.getByTestId('button')
    expect(button).toBeInTheDocument()
    expect(screen.getByText('Exportar (2)')).toBeInTheDocument()
    expect(screen.getByTestId('download-icon')).toBeInTheDocument()
  })

  it('deve mostrar botão desabilitado quando não há dados', () => {
    render(<ExportInvestimentos investimentos={[]} />)

    const button = screen.getByTestId('button')
    expect(button).toBeDisabled()
    expect(screen.getByText('Exportar (sem dados)')).toBeInTheDocument()
  })

  it('deve mostrar dropdown com opções de exportação', () => {
    render(<ExportInvestimentos investimentos={mockInvestimentos} />)

    // Verificar estrutura do dropdown
    expect(screen.getByTestId('dropdown-menu')).toBeInTheDocument()
    expect(screen.getByTestId('dropdown-content')).toBeInTheDocument()
    expect(screen.getByText('Exportar Investimentos')).toBeInTheDocument()
  })

  it('deve mostrar filtros ativos no dropdown', () => {
    render(
      <ExportInvestimentos 
        investimentos={mockInvestimentos} 
        filtrosAtivos={mockFiltros}
      />
    )

    // Verificar exibição dos filtros
    expect(screen.getByText('Filtros aplicados:')).toBeInTheDocument()
    expect(screen.getByText(/Busca: "Tesouro"/)).toBeInTheDocument()
    expect(screen.getByText(/Tipo: Renda Fixa/)).toBeInTheDocument()
    expect(screen.getByText(/Corretora: XP Investimentos/)).toBeInTheDocument()
  })

  it('deve ter opções de Excel e CSV', () => {
    render(<ExportInvestimentos investimentos={mockInvestimentos} />)

    // Verificar opções de formato
    expect(screen.getByText('Exportar como Excel')).toBeInTheDocument()
    expect(screen.getByText('Formato .xls com formatação')).toBeInTheDocument()
    expect(screen.getByText('Exportar como CSV')).toBeInTheDocument()
    expect(screen.getByText('Formato texto separado por vírgulas')).toBeInTheDocument()

    // Verificar ícones
    expect(screen.getByTestId('spreadsheet-icon')).toBeInTheDocument()
    expect(screen.getByTestId('text-icon')).toBeInTheDocument()
  })

  it('deve mostrar total de registros', () => {
    render(<ExportInvestimentos investimentos={mockInvestimentos} />)

    expect(screen.getByText('Total de registros:')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('deve executar exportação CSV quando clicado', async () => {
    const user = userEvent.setup()
    render(<ExportInvestimentos investimentos={mockInvestimentos} />)

    // Clicar na opção CSV
    const csvOption = screen.getByText('Exportar como CSV')
    await user.click(csvOption)

    // Verificar se Blob foi criado
    expect(global.Blob).toHaveBeenCalledWith(
      [expect.stringContaining('ID,Produto,Corretora')],
      { type: 'text/csv;charset=utf-8;' }
    )

    // Verificar se URL.createObjectURL foi chamado
    expect(global.URL.createObjectURL).toHaveBeenCalled()

    // Verificar se link foi criado e clicado
    expect(global.document.createElement).toHaveBeenCalledWith('a')

    // Verificar feedback
    expect(global.alert).toHaveBeenCalledWith(
      expect.stringContaining('2 investimentos exportados para CSV')
    )
  })

  it('deve executar exportação Excel quando clicado', async () => {
    const user = userEvent.setup()
    render(<ExportInvestimentos investimentos={mockInvestimentos} />)

    // Clicar na opção Excel
    const excelOption = screen.getByText('Exportar como Excel')
    await user.click(excelOption)

    // Verificar se Blob foi criado com HTML
    expect(global.Blob).toHaveBeenCalledWith(
      [expect.stringContaining('<table>')],
      { type: 'application/vnd.ms-excel' }
    )

    // Verificar feedback
    expect(global.alert).toHaveBeenCalledWith(
      expect.stringContaining('2 investimentos exportados para Excel')
    )
  })

  it('deve mostrar estado de loading durante exportação', async () => {
    // Mock console.log para simular delay
    global.console.log = jest.fn().mockImplementation(() => {
      return new Promise(resolve => setTimeout(resolve, 100))
    })

    const user = userEvent.setup()
    render(<ExportInvestimentos investimentos={mockInvestimentos} />)

    // Iniciar exportação
    const csvOption = screen.getByText('Exportar como CSV')
    user.click(csvOption)

    // Verificar se botão principal mostra loading (se implementado)
    // Este teste depende da implementação do estado loading
  })

  it('deve gerar CSV com dados corretos', async () => {
    const user = userEvent.setup()
    render(<ExportInvestimentos investimentos={mockInvestimentos} />)

    const csvOption = screen.getByText('Exportar como CSV')
    await user.click(csvOption)

    // Verificar se dados estão no CSV
    const csvCall = (global.Blob as jest.Mock).mock.calls[0][0][0]
    expect(csvCall).toContain('TEST001') // balance_id
    expect(csvCall).toContain('Tesouro IPCA+ 2035') // nome_produto
    expect(csvCall).toContain('XP Investimentos') // corretora
    expect(csvCall).toContain('Renda Fixa') // tipo
    expect(csvCall).toContain('1.000,00') // valor formatado
  })

  it('deve gerar Excel com estrutura HTML correta', async () => {
    const user = userEvent.setup()
    render(<ExportInvestimentos investimentos={mockInvestimentos} />)

    const excelOption = screen.getByText('Exportar como Excel')
    await user.click(excelOption)

    // Verificar se HTML está estruturado
    const htmlCall = (global.Blob as jest.Mock).mock.calls[0][0][0]
    expect(htmlCall).toContain('<table>')
    expect(htmlCall).toContain('<thead>')
    expect(htmlCall).toContain('<tbody>')
    expect(htmlCall).toContain('TEST001')
    expect(htmlCall).toContain('Tesouro IPCA+ 2035')
  })
})