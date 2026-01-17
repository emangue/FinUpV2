/**
 * Testes para o componente PortfolioOverview
 */

import { render, screen } from '@testing-library/react'
import { PortfolioOverview } from '@/features/investimentos/components/portfolio-overview'
import type { PortfolioResumo } from '@/features/investimentos/types'

// Mock dos ícones Lucide
jest.mock('lucide-react', () => ({
  DollarSign: () => <div data-testid="dollar-sign-icon" />,
  TrendingUp: () => <div data-testid="trending-up-icon" />,
  Package: () => <div data-testid="package-icon" />,
  Target: () => <div data-testid="target-icon" />,
}))

// Mock dos componentes UI
jest.mock('@/components/ui/card', () => ({
  Card: ({ children, ...props }: any) => <div data-testid="card" {...props}>{children}</div>,
  CardContent: ({ children, ...props }: any) => <div data-testid="card-content" {...props}>{children}</div>,
  CardHeader: ({ children, ...props }: any) => <div data-testid="card-header" {...props}>{children}</div>,
  CardTitle: ({ children, ...props }: any) => <div data-testid="card-title" {...props}>{children}</div>,
}))

jest.mock('@/components/ui/badge', () => ({
  Badge: ({ children, variant, ...props }: any) => (
    <div data-testid="badge" data-variant={variant} {...props}>
      {children}
    </div>
  ),
}))

describe('PortfolioOverview', () => {
  const mockResumo: PortfolioResumo = {
    total_investido: '100000.00',
    valor_atual: '120000.00',
    rendimento_total: '20000.00',
    rendimento_percentual: 20.0,
    quantidade_produtos: 5,
    produtos_ativos: 4,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('deve renderizar todos os cards de resumo', () => {
    render(<PortfolioOverview resumo={mockResumo} />)

    // Verificar se todos os 4 cards são renderizados
    const cards = screen.getAllByTestId('card')
    expect(cards).toHaveLength(4)

    // Verificar títulos dos cards
    expect(screen.getByText('Total Investido')).toBeInTheDocument()
    expect(screen.getByText('Valor Atual')).toBeInTheDocument()
    expect(screen.getByText('Rendimento')).toBeInTheDocument()
    expect(screen.getByText('Produtos')).toBeInTheDocument()
  })

  it('deve formatar valores monetários corretamente', () => {
    render(<PortfolioOverview resumo={mockResumo} />)

    // Verificar formatação BRL
    expect(screen.getByText('R$ 100.000,00')).toBeInTheDocument()
    expect(screen.getByText('R$ 120.000,00')).toBeInTheDocument()
    expect(screen.getByText('R$ 20.000,00')).toBeInTheDocument()
  })

  it('deve mostrar percentual de rendimento positivo corretamente', () => {
    render(<PortfolioOverview resumo={mockResumo} />)

    // Verificar badge de rendimento positivo
    const badge = screen.getByText('+20,00%')
    expect(badge).toBeInTheDocument()
    
    const badgeElement = badge.closest('[data-testid="badge"]')
    expect(badgeElement).toHaveAttribute('data-variant', 'default')
  })

  it('deve mostrar percentual de rendimento negativo corretamente', () => {
    const resumoNegativo = {
      ...mockResumo,
      rendimento_total: '-5000.00',
      rendimento_percentual: -5.0,
    }

    render(<PortfolioOverview resumo={resumoNegativo} />)

    // Verificar badge de rendimento negativo
    const badge = screen.getByText('-5,00%')
    expect(badge).toBeInTheDocument()
    
    const badgeElement = badge.closest('[data-testid="badge"]')
    expect(badgeElement).toHaveAttribute('data-variant', 'destructive')
  })

  it('deve mostrar quantidade de produtos ativos e total', () => {
    render(<PortfolioOverview resumo={mockResumo} />)

    // Verificar contadores
    expect(screen.getByText('4')).toBeInTheDocument() // produtos ativos
    expect(screen.getByText('5 produtos')).toBeInTheDocument() // total de produtos
  })

  it('deve renderizar ícones corretos em cada card', () => {
    render(<PortfolioOverview resumo={mockResumo} />)

    // Verificar presença dos ícones
    expect(screen.getByTestId('dollar-sign-icon')).toBeInTheDocument()
    expect(screen.getByTestId('trending-up-icon')).toBeInTheDocument()
    expect(screen.getByTestId('package-icon')).toBeInTheDocument()
    expect(screen.getByTestId('target-icon')).toBeInTheDocument()
  })

  it('deve lidar com valores zero corretamente', () => {
    const resumoZero: PortfolioResumo = {
      total_investido: '0.00',
      valor_atual: '0.00',
      rendimento_total: '0.00',
      rendimento_percentual: 0.0,
      quantidade_produtos: 0,
      produtos_ativos: 0,
    }

    render(<PortfolioOverview resumo={resumoZero} />)

    // Verificar valores zero
    expect(screen.getByText('R$ 0,00')).toBeInTheDocument()
    expect(screen.getByText('0,00%')).toBeInTheDocument()
    expect(screen.getByText('0')).toBeInTheDocument()
    expect(screen.getByText('0 produtos')).toBeInTheDocument()
  })

  it('deve lidar com valores grandes corretamente', () => {
    const resumoGrande: PortfolioResumo = {
      total_investido: '1500000.50',
      valor_atual: '1750000.75',
      rendimento_total: '250000.25',
      rendimento_percentual: 16.67,
      quantidade_produtos: 25,
      produtos_ativos: 23,
    }

    render(<PortfolioOverview resumo={resumoGrande} />)

    // Verificar formatação de valores grandes
    expect(screen.getByText('R$ 1.500.000,50')).toBeInTheDocument()
    expect(screen.getByText('R$ 1.750.000,75')).toBeInTheDocument()
    expect(screen.getByText('R$ 250.000,25')).toBeInTheDocument()
    expect(screen.getByText('+16,67%')).toBeInTheDocument()
    expect(screen.getByText('23')).toBeInTheDocument()
    expect(screen.getByText('25 produtos')).toBeInTheDocument()
  })
})